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

VERSION = '_version'

revision = 'be4475027882'
down_revision = 'a490b2db8b13'
branch_labels = None
depends_on = None

###
# get_pk_constraint

table_mapping = {'org': 'orgs',
                 'corp_type': 'corp_types',
                 'product_code': 'product_codes',
                 'affidavit': 'affidavits',
                 'affidavit_status': 'affidavit_statuses',
                 'affiliation': 'affiliations',
                 'contact': 'contacts',
                 'user': 'users',
                 'entity': 'entities',
                 'contact_link': 'contact_links',
                 'invitation': 'invitations',
                 'invitation_membership': 'invitation_memberships',
                 'invitation_type': 'invitation_types',
                 'invitation_status': 'invitation_statuses',
                 'membership': 'memberships',
                 'membership_status_code': 'membership_status_codes',
                 'membership_type': 'membership_types',
                 'org_status': 'org_statuses',
                 'org_type': 'org_types',
                 'payment_type': 'payment_types',
                 'product_role_code': 'product_role_codes',
                 'product_subscription': 'product_subscriptions',
                 'product_subscription_role': 'product_subscription_roles',
                 'product_type_code': 'product_type_codes',
                 'user_status_code': 'user_status_codes',
                 }

skip_table = ['alembic', 'activity', 'transaction']


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
    metadata = MetaData(conn, reflect=True)

    table: str
    for table in tables:
        if table in skip_table or table.endswith(VERSION):
            continue
        print('<<<<Processing starting for table', table)
        _rename_obj(inspector, metadata, table, table_mapping, tables)
        print('Processing ended for table>>>', table)


def downgrade():
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    tables = inspector.get_table_names()
    metadata = MetaData(conn, reflect=True)
    table_mapping_reversed = {y: x for x, y in table_mapping.items()}
    table: str
    for table in tables:
        if table in skip_table or table.endswith(VERSION):
            continue
        print('<<<<Processing starting for table', table)
        _rename_obj(inspector, metadata, table, table_mapping_reversed, tables)
        print('Processing ended for table>>>', table)


def _rename_obj(inspector, metadata, table: str, name_dict, tables):
    _rename_fks(inspector, table, table_mapping)
    new_table_name: str = name_dict.get(table, '')
    if new_table_name:
        print(f'New name found for Table : {table} to {new_table_name}')
        _rename_indexes(inspector, new_table_name, table)
        _rename_pk(inspector, new_table_name, table)
        _rename_sequence(metadata, new_table_name, table)
        _rename_table(table, new_table_name)
        versioned_table_name = _suffix_version(table)
        if versioned_table_name in tables:
            versioned_table_new_name = _suffix_version(new_table_name)
            _rename_table(versioned_table_name, versioned_table_new_name)

        print(f'Renaming Table Done for: {table} to {new_table_name}')


def _suffix_version(table):
    return table + VERSION


def _rename_table(table, new_table_name):
    print(f'\t<<<<<<<<Renaming Table : {table} to {new_table_name} ')
    op.rename_table(table, new_table_name)
    print(f'\tRenaming Done for Table : {table} to {new_table_name} >>>>>>>>>')


def _rename_sequence(m, new_table_name, table):
    id_column = m.tables[table].columns.get('id')
    if id_column is not None and id_column.server_default is not None:
        seq = id_column.server_default.arg.text
        # format is 'nextval(\'org_id_seq\'::regclass)'
        seq_name = re.search("nextval\(\'(.*)\'::regclass", seq).group(1)
        new_seq_name = seq_name.replace(table, new_table_name, 1)
        if seq_name != new_seq_name:
            print(f'\t<<<<<<<<<Renaming PK : {seq_name} to {new_seq_name} of table {table}')
            op.execute(f'ALTER sequence {seq_name} RENAME TO {new_seq_name}')
            print(f'\tRenaming PK : {seq_name} to {new_seq_name} of table {table}>>>>>>>>>>>')


def _rename_pk(inspector, new_table_name, table):
    pk_name = inspector.get_pk_constraint(table).get('name')
    new_pk_name = pk_name.replace(table, new_table_name, 1)
    if pk_name != new_pk_name:
        print(f'\t<<<<<<<<<<Renaming PK : {pk_name} to {new_pk_name} of table {table}')
        op.execute(f'ALTER index {pk_name} RENAME TO {new_pk_name}')
        print(f'\tRenaming Done for PK : {pk_name} to {new_pk_name} of table {table}>>>>>>>>>')


def _rename_indexes(inspector, new_table_name, table):
    for index in inspector.get_indexes(table):
        old_index_name = index.get('name')
        new_index_name = old_index_name.replace(table, new_table_name, 1)
        if old_index_name != new_index_name:
            print(f'\t<<<<<<Renaming Index : {old_index_name} to {new_index_name} of table {table}')
            op.execute(f'ALTER index {old_index_name} RENAME TO {new_index_name}')
            print(f'\tRenaming Index Done for: {old_index_name} to {new_index_name} of table {table}>>>>>>>>')


def _rename_fks(inspector, table: str, name_dict):
    foreign_keys = inspector.get_foreign_keys(table)
    for fk in foreign_keys:
        fk_name = fk.get('name')
        referred_table = fk.get('referred_table')
        referred_table_new_name = name_dict.get(referred_table, '')
        if referred_table_new_name:
            new_fk_name = fk_name.replace(referred_table, referred_table_new_name)
            if fk_name != new_fk_name:
                print(f'\t<<<<<<<<<<Renaming Foriegn Key : {fk_name} to {new_fk_name} of table {table}')
                op.execute(f'ALTER table "{table}" RENAME CONSTRAINT {fk_name} TO {new_fk_name}')
                print(f'\tRenaming done for Foriegn Key : {fk_name} to {new_fk_name} of table {table}>>>>>>>>>>')
