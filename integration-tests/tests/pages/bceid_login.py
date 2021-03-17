import os
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from urllib.request import urlretrieve

import zxing
from pyotp import TOTP


class BCEIDLoginPage(object):

    def __init__(self, driver):
        self.driver = driver

    def run(self, url: str, username: str, password: str):
        self.visit(url)
        if self.is_redirect_to_bceid():
            self.login_as(username, password)
            self.topt()
            self.confirm_back()

    def visit(self, url):
        self.driver.visit(url)

    def is_redirect_to_bceid(self):
        return self.driver.get('#user').is_displayed()

    def login_as(self, username, password):
        self.driver.get('#user').type(username)
        self.driver.get('#password').type(password)
        self.driver.get('input[name="btnSubmit"]').click()

    def topt(self):
        self.driver.get("#totp").is_displayed()
        img = self.driver.get('#kc-totp-secret-qr-code').get_attribute('src')

        # download the qr code image
        current_dir = Path(__file__)
        bceid_png = Path(f"{current_dir.parent}/bceid.png")
        urlretrieve(img, bceid_png.name)

        # read the qr code from the image and get the secret
        reader = zxing.BarCodeReader()
        barcode = reader.decode(bceid_png.name)
        parsed = urlparse(barcode.parsed)
        query = parse_qs(parsed.query)
        qr_secret = query['secret'][0]
        # bceid_png.unlink()

        # generate token
        totp = TOTP(qr_secret)
        token = totp.now()
        self.driver.get('#totp').type(token)
        self.driver.get('.btn-primary').click()

    def confirm_back(self):
        self.driver.get('.user-name')
