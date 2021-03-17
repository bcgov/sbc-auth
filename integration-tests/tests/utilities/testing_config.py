import requests
import urllib.request
from typing import List
from pydantic import BaseModel


class TestingConfig(BaseModel):
    login_as: str = ''
    access_type: str = ''
    keycloak_token: str = ''
    auth_api_url: str = ''
    pay_api_url: str = ''
    legal_api_url: str = ''
    bcol_api_url: str = ''
    reset_api_url: str = ''
    status_api_url: str = ''
    minio_api_url: str = ''

    terms_version: str = ''
    accepted_terms: bool = True
    username: str = ''
    user_id: str = ''
    org_id: str = ''
    org_type: str = ''
    notification_id: str = ''
    member_id: str = ''
    invitation_token: str = ''
    invitation_json: str = ''
    business_identifier: str = ''
    document_key: str = ''

    payment_id: str = ''
    invoice_id: str = ''
    transaction_id: str = ''
    pay_system_url: str = ''
    paybc_status: str = ''
    payment_status: str = ''
    payment_method: str = ''

    test_data: str = None


class TestedUser(BaseModel):

    config: List[TestingConfig] = []
