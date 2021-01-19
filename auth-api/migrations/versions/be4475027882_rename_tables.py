"""rename tables

Revision ID: be4475027882
Revises: a490b2db8b13
Create Date: 2021-01-18 06:27:37.050548

"""
from alembic import op
from sqlalchemy import create_engine
from sqlalchemy.engine import reflection
from sqlalchemy import MetaData
import re

# revision identifiers, used by Alembic.
from sqlalchemy.engine.reflection import Inspector

revision = 'be4475027882'
down_revision = 'a490b2db8b13'
branch_labels = None
depends_on = None


###
# get_pk_constraint


def upgrade():
    """
    have to change
        1. primary key
        2. index name
        3. sequence name
        4. foriegn key name

    """
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    tables = inspector.get_table_names()
    name_dict = {'org': 'orgs', 'corp_type': 'corp_types', 'product_code': 'product_codes'}
    m = MetaData(conn, reflect=True)
    for table in tables:
        fks = inspector.get_foreign_keys(table)
        for fk in fks:
            fk_name = fk.get('name')
            referred_table = fk.get('referred_table')
            if new_table_name := name_dict.get(referred_table, None):
                new_fk_name = fk_name.replace(referred_table, new_table_name)
                op.execute(f'ALTER table {table} RENAME CONSTRAINT {fk_name} TO {new_fk_name}')

        if new_table_name := name_dict.get(table, None):
            for index in inspector.get_indexes(table):
                old_index_name = index.get('name')
                new_index_name = old_index_name.replace(table, new_table_name, 1)
                op.execute(f'ALTER index {old_index_name} RENAME TO {new_index_name}')
            pk_name = inspector.get_pk_constraint(table).get('name')
            new_pk_name = pk_name.replace(table, new_table_name, 1)
            op.execute(f'ALTER index {pk_name} RENAME TO {new_pk_name}')
            id_column = m.tables[table].columns.get('id')
            if id_column is not None:
                seq = id_column.server_default.arg.text
                # format is 'nextval(\'org_id_seq\'::regclass)'
                seq_name = re.search("nextval\(\'(.*)\'::regclass", seq).group(1)
                new_seq_name = seq_name.replace(table, new_table_name, 1)
                op.execute(f'ALTER sequence {seq_name} RENAME TO {new_seq_name}')
            op.rename_table(table, new_table_name)


def downgrade():
    pass
