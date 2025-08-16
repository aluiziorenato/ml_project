"""
Core storage module for ML project.
Provides data management and persistence capabilities.
"""

from .data_manager import DataManager, DataQuery, DataResult

__all__ = [
    "DataManager",
    "DataQuery", 
    "DataResult"
]