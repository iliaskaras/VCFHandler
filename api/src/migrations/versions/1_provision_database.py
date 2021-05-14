"""Provision Database

Revision ID: 1
Revises:
Create Date: 2021-05-14 17:29:16.482707

"""
import uuid

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('uuid', postgresql.UUID(as_uuid=True), unique=True, nullable=False),

        sa.Column('email', sa.String(), unique=True, nullable=False),
        sa.Column('password', sa.String(), nullable=False),
    )
    op.execute('INSERT INTO users (uuid, email, password) VALUES (\'{0}\', \'{1}\', \'{2}\')'.format(
        str(uuid.uuid4()),
        'user@mail.test',
        '123456')
    )


def downgrade():
    # Downgrading commented out for not dropping the table by mistake.
    # op.drop_table('users')
    pass
