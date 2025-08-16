"""Initial database setup with default strategies and special dates

Revision ID: 001
Revises: 
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
import json

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create strategic_modes table
    strategic_modes_table = op.create_table(
        'strategic_modes',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('acos_min', sa.Decimal(5, 2)),
        sa.Column('acos_max', sa.Decimal(5, 2)),
        sa.Column('budget_multiplier', sa.Decimal(3, 2)),
        sa.Column('bid_adjustment', sa.Decimal(3, 2)),
        sa.Column('margin_threshold', sa.Decimal(5, 2)),
        sa.Column('automation_rules', sa.JSON()),
        sa.Column('alert_thresholds', sa.JSON()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    
    # Create special_dates table
    op.create_table(
        'special_dates',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('budget_multiplier', sa.Decimal(3, 2), default=1.0),
        sa.Column('acos_adjustment', sa.Decimal(3, 2), default=0.0),
        sa.Column('strategy_override_id', sa.Integer(), sa.ForeignKey('strategic_modes.id')),
        sa.Column('peak_hours', sa.JSON()),
        sa.Column('priority_categories', sa.JSON()),
        sa.Column('custom_settings', sa.JSON()),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    
    # Create strategy_configurations table
    op.create_table(
        'strategy_configurations',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('active_strategy_id', sa.Integer(), sa.ForeignKey('strategic_modes.id'), nullable=False),
        sa.Column('custom_settings', sa.JSON()),
        sa.Column('special_date_overrides', sa.JSON()),
        sa.Column('notification_channels', sa.JSON()),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('last_applied_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    
    # Create strategy_performance_log table
    op.create_table(
        'strategy_performance_log',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('strategy_id', sa.Integer(), sa.ForeignKey('strategic_modes.id'), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('total_spend', sa.Decimal(10, 2)),
        sa.Column('total_sales', sa.Decimal(10, 2)),
        sa.Column('average_acos', sa.Decimal(5, 2)),
        sa.Column('roi', sa.Decimal(5, 2)),
        sa.Column('profit', sa.Decimal(10, 2)),
        sa.Column('campaigns_count', sa.Integer()),
        sa.Column('active_campaigns', sa.Integer()),
        sa.Column('paused_campaigns', sa.Integer()),
        sa.Column('conversions', sa.Integer()),
        sa.Column('clicks', sa.Integer()),
        sa.Column('impressions', sa.Integer()),
        sa.Column('metrics', sa.JSON()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    
    # Create strategy_alerts table
    op.create_table(
        'strategy_alerts',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('strategy_id', sa.Integer(), sa.ForeignKey('strategic_modes.id')),
        sa.Column('alert_type', sa.String(50), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('is_resolved', sa.Boolean(), default=False),
        sa.Column('resolved_at', sa.DateTime(timezone=True)),
        sa.Column('metadata', sa.JSON()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    
    # Create automation_actions table
    op.create_table(
        'automation_actions',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('strategy_id', sa.Integer(), sa.ForeignKey('strategic_modes.id')),
        sa.Column('action_type', sa.String(50), nullable=False),
        sa.Column('service', sa.String(50), nullable=False),
        sa.Column('campaign_id', sa.String(100)),
        sa.Column('before_state', sa.JSON()),
        sa.Column('after_state', sa.JSON()),
        sa.Column('parameters', sa.JSON()),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('error_message', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('executed_at', sa.DateTime(timezone=True)),
    )
    
    # Insert default strategic modes
    strategic_modes = table('strategic_modes',
        column('name', sa.String),
        column('description', sa.Text),
        column('acos_min', sa.Decimal),
        column('acos_max', sa.Decimal),
        column('budget_multiplier', sa.Decimal),
        column('bid_adjustment', sa.Decimal),
        column('margin_threshold', sa.Decimal),
        column('automation_rules', sa.JSON),
        column('alert_thresholds', sa.JSON),
    )
    
    op.bulk_insert(strategic_modes, [
        {
            'name': 'Maximizar Lucro',
            'description': 'Foco na maximização da margem de lucro por venda',
            'acos_min': 10,
            'acos_max': 15,
            'budget_multiplier': 0.7,
            'bid_adjustment': -20,
            'margin_threshold': 40,
            'automation_rules': json.dumps({
                "bid_adjustment": {"acos_threshold": 15, "action": "decrease", "percent": 10},
                "campaign_pause": {"acos_threshold": 20, "action": "pause"},
                "budget_reallocation": {"roi_threshold": 1.5, "action": "increase_budget"}
            }),
            'alert_thresholds': json.dumps({
                "acos_high": 20,
                "margin_low": 35,
                "roi_negative": True
            })
        },
        {
            'name': 'Escalar Vendas',
            'description': 'Maximizar volume de vendas mantendo rentabilidade',
            'acos_min': 15,
            'acos_max': 25,
            'budget_multiplier': 0.85,
            'bid_adjustment': 15,
            'margin_threshold': 30,
            'automation_rules': json.dumps({
                "bid_adjustment": {"conversion_rate": 0.05, "action": "increase", "percent": 15},
                "keyword_expansion": {"performance_score": 8, "action": "expand"},
                "budget_increase": {"sales_growth": 0.2, "action": "increase_budget"}
            }),
            'alert_thresholds': json.dumps({
                "acos_high": 30,
                "volume_drop": 20,
                "budget_low": 10
            })
        },
        {
            'name': 'Proteger Margem',
            'description': 'Manter margem mesmo com aumento de competição',
            'acos_min': 8,
            'acos_max': 12,
            'budget_multiplier': 0.6,
            'bid_adjustment': -30,
            'margin_threshold': 45,
            'automation_rules': json.dumps({
                "competitor_monitoring": {"price_change": 0.1, "action": "adjust_bids"},
                "campaign_pause": {"acos_threshold": 15, "action": "pause"},
                "margin_protection": {"margin_drop": 0.25, "action": "reduce_bids"}
            }),
            'alert_thresholds': json.dumps({
                "acos_high": 15,
                "margin_low": 25,
                "competitor_activity": True
            })
        },
        {
            'name': 'Campanhas Agressivas',
            'description': 'Conquistar market share através de investimento agressivo',
            'acos_min': 25,
            'acos_max': 40,
            'budget_multiplier': 1.2,
            'bid_adjustment': 50,
            'margin_threshold': 20,
            'automation_rules': json.dumps({
                "max_bids": {"position": 3, "action": "increase_to_top"},
                "keyword_activation": {"suggested_keywords": True, "action": "activate_all"},
                "continuous_campaigns": {"special_dates": True, "action": "24_7_campaigns"}
            }),
            'alert_thresholds': json.dumps({
                "acos_high": 50,
                "position_low": 3,
                "budget_limit": True
            })
        }
    ])

def downgrade():
    op.drop_table('automation_actions')
    op.drop_table('strategy_alerts')
    op.drop_table('strategy_performance_log')
    op.drop_table('strategy_configurations')
    op.drop_table('special_dates')
    op.drop_table('strategic_modes')