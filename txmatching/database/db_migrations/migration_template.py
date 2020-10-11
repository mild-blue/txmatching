# revision identifiers, used by Alembic.
from txmatching.database.db_migrations.migration_base import execute


def upgrade():
    execute('FILE_UP')


def downgrade():
    execute('FILE_DOWN')
