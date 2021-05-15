"""Provision Database

Revision ID: 1
Revises:
Create Date: 2021-05-14 17:29:16.482707

"""
import uuid

import sqlalchemy as sa
from alembic import op
from sqlalchemy import Enum
from sqlalchemy.dialects import postgresql

from application.user.enums import Permission

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
        sa.Column(
            'permission',
            Enum(
                'write', 'execute', 'read',
                name='Task',
                validate_strings=True
            ),
            nullable=False,
        ),
    )
    op.execute('INSERT INTO users (uuid, email, password, permission) VALUES (\'{0}\', \'{1}\', \'{2}\', \'{3}\')'
        .format(
            str(uuid.uuid4()),
            'read_user@mail.test',
            '123456',
            Permission.read.value)
        )
    op.execute('INSERT INTO users (uuid, email, password, permission) VALUES (\'{0}\', \'{1}\', \'{2}\', \'{3}\')'
        .format(
            str(uuid.uuid4()),
            'write_user@mail.test',
            '123456',
            Permission.write.value)
        )
    op.execute('INSERT INTO users (uuid, email, password, permission) VALUES (\'{0}\', \'{1}\', \'{2}\', \'{3}\')'
        .format(
            str(uuid.uuid4()),
            'execute_user@mail.test',
            '123456',
            Permission.execute.value)
        )


def downgrade():
    # Downgrading commented out for not dropping the table by mistake.
    # op.drop_table('users')
    pass
