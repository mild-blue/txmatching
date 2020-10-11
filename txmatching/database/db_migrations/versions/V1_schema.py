"""schema

Revision ID: 1
Revises: 
Create Date: 2020-10-11 10:40:50.975626

"""

revision = '1'
down_revision = None
branch_labels = None
depends_on = None


# revision identifiers, used by Alembic.
from txmatching.database.db_migrations.migration_base import execute

def upgrade():
    execute('V1_schema_up.sql')


def downgrade():
    execute('V1_schema_down.sql')
