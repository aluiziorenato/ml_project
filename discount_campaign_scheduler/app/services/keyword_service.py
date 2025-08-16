import pandas as pd
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from sqlmodel import Session, select
from fastapi import HTTPException
from app.models import Keyword, KeywordUploadBatch, KeywordSuggestionMatch, ItemSuggestion
import logging
import io

logger = logging.getLogger(__name__)


class KeywordService:
    """Service for processing Google Keyword Planner CSV uploads and keyword management"""
    
    def __init__(self):
        self.expected_columns = {
            'keyword': ['keyword', 'Keyword', 'KEYWORD', 'search_term', 'Search Term'],
            'search_volume': ['search_volume', 'Search Volume', 'Avg. monthly searches', 'volume'],
            'competition': ['competition', 'Competition', 'COMPETITION'],
            'competition_score': ['competition_score', 'Competition (indexed value)', 'Competition Score'],
            'bid_low': ['top_of_page_bid_low', 'Top of page bid (low range)', 'Low Bid'],
            'bid_high': ['top_of_page_bid_high', 'Top of page bid (high range)', 'High Bid']
        }

    async def process_csv_upload(
        self, 
        file_content: bytes, 
        filename: str, 
        seller_id: str, 
        session: Session
    ) -> Dict:
        """Process uploaded CSV file with keyword data"""
        
        batch_id = str(uuid.uuid4())
        
        # Create upload batch record
        upload_batch = KeywordUploadBatch(
            id=batch_id,
            seller_id=seller_id,
            filename=filename,
            status="processing"
        )
        session.add(upload_batch)
        session.commit()
        
        try:
            # Read CSV file
            csv_data = io.StringIO(file_content.decode('utf-8'))
            df = pd.read_csv(csv_data)
            
            logger.info(f"Processing CSV with {len(df)} rows for seller {seller_id}")
            
            # Map columns to expected format
            column_mapping = self._map_columns(df.columns.tolist())
            if not column_mapping:
                raise ValueError("CSV format not recognized. Please ensure it contains keyword data.")
            
            # Process keywords
            processed_keywords = []
            failed_count = 0
            
            for idx, row in df.iterrows():
                try:
                    keyword_data = self._extract_keyword_data(row, column_mapping)
                    if keyword_data:
                        keyword = Keyword(
                            seller_id=seller_id,
                            upload_batch_id=batch_id,
                            **keyword_data
                        )
                        session.add(keyword)
                        processed_keywords.append(keyword)
                    else:
                        failed_count += 1
                except Exception as e:
                    logger.warning(f"Failed to process row {idx}: {e}")
                    failed_count += 1
            
            # Update batch statistics
            upload_batch.total_keywords = len(df)
            upload_batch.processed_keywords = len(processed_keywords)
            upload_batch.failed_keywords = failed_count
            upload_batch.status = "completed"
            upload_batch.completed_at = datetime.utcnow()
            
            session.commit()
            
            # Generate keyword matches with existing suggestions
            await self._generate_keyword_matches(seller_id, batch_id, session)
            
            return {
                "batch_id": batch_id,
                "filename": filename,
                "total_keywords": len(df),
                "processed_keywords": len(processed_keywords),
                "failed_keywords": failed_count,
                "status": "completed",
                "upload_summary": {
                    "unique_keywords": len(set(k.keyword.lower() for k in processed_keywords)),
                    "high_volume_keywords": len([k for k in processed_keywords if k.search_volume > 1000]),
                    "high_competition": len([k for k in processed_keywords if k.competition == "High"]),
                    "categories_detected": len(set(k.category_match for k in processed_keywords if k.category_match))
                }
            }
            
        except Exception as e:
            # Update batch with error
            upload_batch.status = "failed"
            upload_batch.error_message = str(e)
            upload_batch.completed_at = datetime.utcnow()
            session.commit()
            
            logger.error(f"Failed to process CSV upload {batch_id}: {e}")
            raise HTTPException(status_code=400, detail=f"Failed to process CSV: {str(e)}")

    def _map_columns(self, csv_columns: List[str]) -> Optional[Dict[str, str]]:
        """Map CSV columns to expected keyword data fields"""
        mapping = {}
        
        for field, possible_names in self.expected_columns.items():
            found = False
            for col in csv_columns:
                if col.strip() in possible_names:
                    mapping[field] = col.strip()
                    found = True
                    break
            
            # Keyword column is required
            if field == 'keyword' and not found:
                return None
        
        return mapping if 'keyword' in mapping else None

    def _extract_keyword_data(self, row: pd.Series, column_mapping: Dict[str, str]) -> Optional[Dict]:
        """Extract keyword data from a CSV row"""
        try:
            keyword = str(row[column_mapping['keyword']]).strip()
            if not keyword or keyword.lower() in ['nan', 'null', '']:
                return None
            
            data = {'keyword': keyword}
            
            # Extract search volume
            if 'search_volume' in column_mapping:
                vol = row[column_mapping['search_volume']]
                try:
                    # Handle different volume formats (e.g., "1K-10K", "1,000", etc.)
                    if isinstance(vol, str):
                        vol = vol.replace(',', '').replace('K', '000').replace('k', '000')
                        if '-' in vol:
                            vol = vol.split('-')[1]  # Take higher range
                    data['search_volume'] = int(float(vol)) if vol and str(vol) != 'nan' else 0
                except:
                    data['search_volume'] = 0
            
            # Extract competition
            if 'competition' in column_mapping:
                comp = str(row[column_mapping['competition']]).strip()
                if comp.lower() in ['high', 'medium', 'low']:
                    data['competition'] = comp.title()
                else:
                    data['competition'] = 'Medium'  # Default
            else:
                data['competition'] = 'Medium'
            
            # Extract competition score
            if 'competition_score' in column_mapping:
                score = row[column_mapping['competition_score']]
                try:
                    data['competition_score'] = float(score) if score and str(score) != 'nan' else None
                except:
                    data['competition_score'] = None
            
            # Extract bid ranges
            for bid_field in ['bid_low', 'bid_high']:
                if bid_field in column_mapping:
                    bid = row[column_mapping[bid_field]]
                    try:
                        # Remove currency symbols and convert to float
                        if isinstance(bid, str):
                            bid = bid.replace('$', '').replace('R$', '').replace(',', '')
                        field_name = f"top_of_page_{bid_field}"
                        data[field_name] = float(bid) if bid and str(bid) != 'nan' else None
                    except:
                        data[f"top_of_page_{bid_field}"] = None
            
            # Calculate relevance score based on search volume and competition
            data['relevance_score'] = self._calculate_relevance_score(data)
            
            return data
            
        except Exception as e:
            logger.warning(f"Error extracting keyword data: {e}")
            return None

    def _calculate_relevance_score(self, keyword_data: Dict) -> float:
        """Calculate relevance score for a keyword"""
        try:
            volume = keyword_data.get('search_volume', 0)
            competition = keyword_data.get('competition', 'Medium')
            
            # Base score from search volume (log scale)
            import math
            volume_score = math.log10(max(volume, 1)) / 6  # Normalize to 0-1
            
            # Competition weight (lower competition = higher score)
            comp_weights = {'Low': 1.0, 'Medium': 0.7, 'High': 0.4}
            comp_score = comp_weights.get(competition, 0.7)
            
            # Combined relevance score
            relevance = (volume_score * 0.6) + (comp_score * 0.4)
            return min(max(relevance, 0.0), 1.0)  # Clamp to 0-1
            
        except:
            return 0.5  # Default moderate relevance

    async def _generate_keyword_matches(self, seller_id: str, batch_id: str, session: Session):
        """Generate matches between keywords and existing product suggestions"""
        try:
            # Get keywords from this batch
            keywords_stmt = select(Keyword).where(
                Keyword.seller_id == seller_id,
                Keyword.upload_batch_id == batch_id,
                Keyword.is_active == True
            )
            keywords = session.exec(keywords_stmt).all()
            
            # Get existing suggestions for this seller
            suggestions_stmt = select(ItemSuggestion).where(
                ItemSuggestion.seller_id == seller_id,
                ItemSuggestion.is_active == True
            )
            suggestions = session.exec(suggestions_stmt).all()
            
            # Simple keyword matching based on title similarity
            for suggestion in suggestions:
                title_words = set(suggestion.title.lower().split())
                
                for keyword in keywords:
                    keyword_words = set(keyword.keyword.lower().split())
                    
                    # Calculate simple overlap score
                    overlap = len(title_words.intersection(keyword_words))
                    total_words = len(title_words.union(keyword_words))
                    
                    if overlap > 0 and total_words > 0:
                        match_score = overlap / total_words
                        
                        if match_score > 0.2:  # Only create matches with reasonable similarity
                            match = KeywordSuggestionMatch(
                                suggestion_id=suggestion.id,
                                keyword_id=keyword.id,
                                match_score=match_score,
                                match_type="broad" if match_score < 0.5 else "phrase"
                            )
                            session.add(match)
            
            session.commit()
            logger.info(f"Generated keyword matches for batch {batch_id}")
            
        except Exception as e:
            logger.error(f"Failed to generate keyword matches: {e}")

    def get_keywords_for_seller(self, seller_id: str, session: Session) -> List[Keyword]:
        """Get all active keywords for a seller"""
        stmt = select(Keyword).where(
            Keyword.seller_id == seller_id,
            Keyword.is_active == True
        ).order_by(Keyword.search_volume.desc())
        
        return session.exec(stmt).all()

    def get_upload_batches(self, seller_id: str, session: Session) -> List[KeywordUploadBatch]:
        """Get upload batch history for a seller"""
        stmt = select(KeywordUploadBatch).where(
            KeywordUploadBatch.seller_id == seller_id
        ).order_by(KeywordUploadBatch.uploaded_at.desc())
        
        return session.exec(stmt).all()


# Global service instance
keyword_service = KeywordService()