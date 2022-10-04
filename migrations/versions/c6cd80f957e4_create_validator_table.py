"""Create validator table

Revision ID: c6cd80f957e4
Revises: 3001d0eab0bf
Create Date: 2022-10-04 15:56:29.419838

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c6cd80f957e4'
down_revision = '3001d0eab0bf'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('validator',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('wallet_address', sa.Unicode(), nullable=False),
    sa.Column('adnl_address', sa.Unicode(), nullable=False),
    sa.Column('public_key', sa.Unicode(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_validator_adnl_address'), 'validator', ['adnl_address'], unique=False)
    op.create_index(op.f('ix_validator_public_key'), 'validator', ['public_key'], unique=False)
    op.create_index(op.f('ix_validator_wallet_address'), 'validator', ['wallet_address'], unique=False)
    op.create_table('validator_statistic',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('efficiency', sa.DECIMAL(), nullable=False),
    sa.Column('online', sa.Boolean(), nullable=False),
    sa.Column('validator_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['validator_id'], ['validator.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_validator_statistic_efficiency'), 'validator_statistic', ['efficiency'], unique=False)
    op.create_index(op.f('ix_validator_statistic_online'), 'validator_statistic', ['online'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_validator_statistic_online'), table_name='validator_statistic')
    op.drop_index(op.f('ix_validator_statistic_efficiency'), table_name='validator_statistic')
    op.drop_table('validator_statistic')
    op.drop_index(op.f('ix_validator_wallet_address'), table_name='validator')
    op.drop_index(op.f('ix_validator_public_key'), table_name='validator')
    op.drop_index(op.f('ix_validator_adnl_address'), table_name='validator')
    op.drop_table('validator')
    # ### end Alembic commands ###
