import os
from selenium import webdriver
import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import time


driver = webdriver.Chrome("chromeDriver/chromedriver.exe", options=webdriver.ChromeOptions())


class Login:
    def __init__(self):
        self.site = "https://demo-trader.markets.com/trading-platform/#login"
        self.username = os.environ['USERNAME']
        self.password = os.environ['PASSWORD']
        self.usernamePath = '//*[@id="view61"]/div/div/div/div/div/div/form/div/div[3]/div[1]/input'
        self.passwordPath = '//*[@id="view61"]/div/div/div/div/div/div/form/div/div[3]/div[2]/input'
        self.loginPath = '//*[@id="auth-button-login"]'

    def login(self):
        driver.get(self.site)
        while True:
            try:
                driver.find_element_by_xpath(xpath=self.usernamePath).is_displayed()
                break
            except selenium.common.exceptions.NoSuchElementException:
                time.sleep(1)

        driver.find_element_by_xpath(xpath=self.usernamePath).send_keys(self.username)
        driver.find_element_by_xpath(xpath=self.passwordPath).send_keys(self.password)
        driver.find_element_by_xpath(xpath=self.loginPath).click()


class Market:
    def __init__(self):
        self.close = '//*[@id="view6806"]/div/div/div/div/div/div/div[2]/div[1]/button/span'
        self.stocks = self.details()

    def details(self):
        driver.fullscreen_window()

        try:
            close = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, self.close))
            )
            close.click()
        except TimeoutException:
            print("Timed out waiting for page to load")

        time.sleep(10)

        soup = BeautifulSoup(driver.page_source, 'lxml')
        names = soup.find_all("span", {"class": "instrument-name-cell"})
        rates = soup.find_all("div", {"class": "change equally"})

        markets = {}
        print(len(names), len(rates))
        for i in range(0, len(names), 2):
            num = (i / 2) + 1
            try:
                markets[names[i].get_text()] = {'sell': rates[i].get_text(), 'buy': rates[i + 1].get_text(),
                                                'sell path': driver.find_element_by_xpath(xpath=self.path_format(kind='sell', no=num)),
                                                'buy path': driver.find_element_by_xpath(xpath=self.path_format(kind='buy', no=num))}
            except IndexError:
                break
        return markets

    @staticmethod
    def path_format(kind, no):
        kind_dict = {'sell': 2, 'buy': 3}
        return f'//*[@id="wrapper"]/div[4]/div/div/div[2]/div[1]/div[1]/div/div/section/div[1]/div/div/table/tbody/div[1]/div/div[1]/div/div/div[{no}]/div/div[2]/td[{kind_dict[kind]}]/div/div[2]/button'

    def place_trade(self, kind, name):
        # kind = sell, buy | name = EUR/USD,  EUR/GBP, GBP/AUD...
        stake_path = '//*[@id="trade-create-EUR/USD-152"]/div/form/div[2]/div[2]/div[2]/input'
        stop_loss_path = '//*[@id="trade-create-EUR/USD-152"]/div/form/div[2]/div[3]/div/div[1]/label/span[1]'
        take_profit_path = '//*[@id="trade-create-EUR/USD-152"]/div/form/div[2]/div[3]/div/div[2]/label/span[1]'
        place_order_path = '//*[@id="trade-create-EUR/USD-152"]/div/form/div[2]/div[4]/button'
        stop_loss_input_path = {'pips': '//*[@id="trade-create-EUR/USD-152"]/div/form/div[2]/div[3]/div/div[1]/div/div[1]/div[2]/label/span[1]',
                                'GBP': '//*[@id="trade-create-EUR/USD-152"]/div/form/div[2]/div[3]/div/div[1]/div/div[1]/div[3]/label/span[1]',
                                '%': '//*[@id="trade-create-EUR/USD-152"]/div/form/div[2]/div[3]/div/div[1]/div/div[1]/div[4]/label/span[1]',
                                'rate': '//*[@id="trade-create-EUR/USD-152"]/div/form/div[2]/div[3]/div/div[1]/div/div[1]/div[1]/label/span[1]',
                                'input': '//*[@id="trade-create-EUR/USD-152"]/div/form/div[2]/div[3]/div/div[1]/div/div[2]/div/input'}

        take_profit_input_path = {'input': '//*[@id="trade-create-EUR/USD-152"]/div/form/div[2]/div[3]/div/div[2]/div/div[2]/div/input',
                                  'pips': '//*[@id="trade-create-EUR/USD-152"]/div/form/div[2]/div[3]/div/div[2]/div/div[2]/div/input',
                                  'GBP': '//*[@id="trade-create-EUR/USD-152"]/div/form/div[2]/div[3]/div/div[2]/div/div[1]/div[3]/label/span[1]',
                                  '%': '//*[@id="trade-create-EUR/USD-152"]/div/form/div[2]/div[3]/div/div[2]/div/div[1]/div[4]/label/span[1]',
                                  'rate': '//*[@id="trade-create-EUR/USD-152"]/div/form/div[2]/div[3]/div/div[2]/div/div[1]/div[4]/label/span[1]'}
        confirm_order = '//*[@id="trade-create-EUR/USD-152"]/div/div/div/div[1]'

        self.stocks[name][f'{kind} path'].click()
        time.sleep(1)
        stake_input = driver.find_element_by_xpath(xpath=stake_path)
        stake_input.clear()
        stake_input.send_keys("1000")
        driver.find_element_by_xpath(xpath=stop_loss_path).click()
        driver.find_element_by_xpath(xpath=take_profit_path).click()
        driver.find_element_by_xpath(xpath=place_order_path).click()
        time.sleep(1)
        driver.find_element_by_xpath(xpath=confirm_order).click()

    @staticmethod
    def close_all_positions():
        open_positions = '//*[@id="instruments-tree-open-positions"]/div[2]'
        close_all_positions = '//*[@id="wrapper"]/div[4]/div/div/div[2]/div[1]/div[1]/div/div/section/div[1]/div/div/table/thead/tr/th[6]/button'
        yes_close = '//*[@id="view6849"]/div/div/div/div/div/div/div[2]/div[2]/button/span'
        back_to_trade = '//*[@id="wrapper"]/div[4]/div/div/div[1]/div[1]/div[2]/div/section/div[1]/div/div/div[2]/div/div[1]/div[2]/div[1]/div/div[2]'

        driver.find_element_by_xpath(xpath=open_positions).click()
        time.sleep(1)
        driver.find_element_by_xpath(xpath=close_all_positions).click()
        time.sleep(1)
        driver.find_element_by_xpath(xpath=yes_close).click()
        time.sleep(1)
        driver.find_element_by_xpath(xpath=back_to_trade).click()


class TradeHistory:
    def __init__(self):
        pass


Login().login()
myTrade = Market()
time.sleep(1)
myTrade.place_trade(kind='sell', name='EUR/USD')
time.sleep(10)
myTrade.close_all_positions()
