class BCSCInvitationLoginPage(object):

    def __init__(self, driver):
        self.driver = driver

    def run(self, url: str, username: str, password: str):
        self.visit(url)
        if self.is_login_button():
            self.click_login_button()
            if self.is_redirect_to_bcsc():
                self.click_virtural_card_option()
                self.login_as(username, password)
                self.confirm_back()
                self.username_display()

    def visit(self, url):
        self.driver.visit(url)

    def is_login_button(self):
        return self.driver.contains('Log in with BC Services Card').is_displayed()

    def click_login_button(self):
        self.driver.contains('Log in with BC Services Card').click()

    def is_redirect_to_bcsc(self):
        return self.driver.get('#tile_virtual_device_div_id').is_displayed()

    def click_virtural_card_option(self):
        self.driver.get('#tile_virtual_device_div_id').click()

    def login_as(self, username, password):
        self.driver.get('#csn').type(username)
        self.driver.get('#continue').click()
        self.driver.get('#passcode').type(password)
        self.driver.get('#btnSubmit').click()

    def confirm_back(self):
        self.driver.get('[id="form_setConfirmation"] button').click()

    def username_display(self):
        self.driver.get('.user-name')
