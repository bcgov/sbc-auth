"""payment change

Revision ID: 959d8ff75e82
Revises: 66ae9d618842
Create Date: 2020-09-28 07:34:51.175055

"""
from typing import List, Dict

import sqlalchemy as sa
from alembic import op
from flask import current_app

from auth_api.models import AccountPaymentSettingsDeprecated, Org
from auth_api.services.rest_service import RestService
from auth_api.utils.enums import OrgType

revision = '959d8ff75e82'
down_revision = '66ae9d618842'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('org', sa.Column('bcol_account_id', sa.String(length=20), nullable=True))
    op.add_column('org', sa.Column('bcol_user_id', sa.String(length=20), nullable=True))
    op.add_column('org_version', sa.Column('bcol_account_id', sa.String(length=20), autoincrement=False, nullable=True))
    op.add_column('org_version', sa.Column('bcol_user_id', sa.String(length=20), autoincrement=False, nullable=True))

    # iterate over each org and invoke payment api to create payment records

    conn = op.get_bind()
    org_list: List[Org] = conn.execute(f"select * from org o where status_code = 'ACTIVE';")

    token = RestService.get_service_account_token()
    print('token--------------------------', token)

    account_payment_list: List[AccountPaymentSettingsDeprecated] = conn.execute(
        f"select * from account_payment_settings where is_active;")
    account_payment_dict: Dict[int, AccountPaymentSettingsDeprecated] = {account_payment.org_id: account_payment for
                                                                         account_payment in account_payment_list}

    pay_url = current_app.config.get('PAY_API_URL')

    for org in org_list:
        # invoke pay-api for each org
        account_payment_detail = account_payment_dict.get(org.id)
        pay_request = {
            'accountId': org.id,
            'accountName': org.name,
            'paymentInfo': {
                'methodOfPayment': account_payment_detail.preferred_payment_code,
                'billable': org.billable
            }
        }
        if is_premium := org.type_code == OrgType.PREMIUM.value:
            pay_request['bcolAccountNumber'] = account_payment_detail.bcol_account_id
            pay_request['bcolUserId'] = account_payment_detail.bcol_user_id

        accounts_url = f'{pay_url}/accounts/{org.id}'
        RestService.put(endpoint=accounts_url,
                        data=pay_request, token=token, raise_for_status=False)

        if is_premium:
            op.execute(
                f"update org set bcol_account_id = '{account_payment_detail.bcol_account_id}' , "
                f"bcol_user_id = '{account_payment_detail.bcol_user_id}' where id={org.id}")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('org_version', 'bcol_user_id')
    op.drop_column('org_version', 'bcol_account_id')
    op.drop_column('org', 'bcol_user_id')
    op.drop_column('org', 'bcol_account_id')
    # ### end Alembic commands ###
