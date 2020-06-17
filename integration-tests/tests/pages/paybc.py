class PayBCPage(object):

    def __init__(self, driver):
        self.driver = driver

    def run(self, url: str, creditcard: str, cvv: str):
        self.visit(url)
        if self.is_redirect_to_paybc():
            self.click_pay_list_button()
            self.pay(creditcard, cvv)

    def visit(self, url):
        self.driver.visit(url)

    def is_redirect_to_paybc(self):
        return self.driver.get('#paylistbutton').is_displayed()

    def click_pay_list_button(self):
        self.driver.get('#paylistbutton').click()

    def pay(self, creditcard, cvv):
        self.driver.get('#credit_payBtn').click()
        self.driver.wait().until(lambda x: x.find_element_by_name('submitButton').is_displayed())
        self.driver.contains('Enter Payment Information')
        self.driver.get('input[name=trnCardNumber]').type(creditcard)
        self.driver.get('input[name=trnCardCvd]').type(cvv)
        self.driver.get('input[name=submitButton]').submit()
