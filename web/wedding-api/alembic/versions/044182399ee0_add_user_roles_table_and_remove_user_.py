"""add user_roles table and remove user.role

Revision ID: 044182399ee0
Revises: de4a5673559f
Create Date: 2025-11-24 14:08:06.168668

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '044182399ee0'
down_revision: Union[str, Sequence[str], None] = 'de4a5673559f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Create table
    op.create_table('user_roles',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('role', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'role')
    )
    
    # 2. Migrate data: users.role -> user_roles
    op.execute("""
        INSERT INTO user_roles (user_id, role)
        SELECT id, role::text FROM users
    """)

    # 3. Drop old column
    op.drop_column('users', 'role')


def downgrade() -> None:
    """Downgrade schema."""
    # 1. Add column back (nullable first)
    op.add_column('users', sa.Column('role', postgresql.ENUM('ADMIN', 'MANAGER', 'PLANNER', 'VENDOR', 'FINANCE', name='roletype'), autoincrement=False, nullable=True, comment='用户角色，决定权限范围'))
    
    # 2. Migrate data back: user_roles -> users.role (Take the first one found)
    op.execute("""
        UPDATE users
        SET role = ur.role::roletype
        FROM user_roles ur
        WHERE users.id = ur.user_id
    """)

    # 3. Make not nullable if needed (skip for now to be safe or set default)
    # op.alter_column('users', 'role', nullable=False)

    # 4. Drop table
    op.drop_table('user_roles')