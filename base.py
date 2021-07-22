# -*- coding: utf-8 -*-
"""
Created on Sun Jun 28 17:21:14 2020

@author: jokebill
"""
from notifiers import GMail, SMS
from selenium.webdriver.common.keys import Keys
from splinter import Browser
from utils import SBreak, MBreak, LBreak, SLBreak
from utils import Timer, Now, PageError, SelectDates

class Base(object):
    def __init__(
            self,
            browser=None,
            multi_window=False,
            alerter=''):
        if browser:
            self.b = browser
        else:
            self.b = Browser(driver_name='chrome')
        self.multi_window = multi_window
        self.windows = []
        if alerter:
            if isinstance(alerter, str):
                if alerter == 'gmail':
                    self.alerter = GMail()
                elif alerter == 'sms':
                    self.alerter = SMS()
                else:
                    raise ValueError(f'Unexpected alerter type {alerter}')
            else:
                self.alerter = alerter
        else:
            self.alerter = None
            
    def SendAlert(self, subject, text):
        print(Now(), subject, text)
        if self.alerter is not None:
            self.alerter.Send(subject, text)

    def ClickById(self, id, wait_time=10):
        if not self.b.is_element_present_by_id(id, wait_time):
            raise PageError(f'Cannot find id: {id}')
        try:
            self.b.find_by_id(id).click()
        except Exception as e:
            raise PageError(
                f'Failed to click {id}. Error: {e!s}')


    def ClickByXpath(self, xpath, wait_time=10):
        if not self.b.is_element_present_by_xpath(xpath, wait_time):
            raise PageError(f'Cannot find xpath: {xpath}')
        if not self.b.is_element_visible_by_xpath(xpath, wait_time):
            raise PageError(f'Xpath {xpath} is not visible')
        try:
            self.b.find_by_xpath(xpath).click()
        except Exception as e:
            raise PageError(
                f'Failed to click {xpath}. Error: {e!s}')
    
    def TypeById(self, id, text, press_after=Keys.ENTER, wait_time=10):
        if not self.b.is_element_present_by_id(id, wait_time):
            raise PageError(f'Cannot find id: {id}')
        try:
            inputbox = self.b.find_by_id(id)
            if inputbox.value:
                inputbox.type(Keys.END)
                inputbox.type(Keys.SHIFT+Keys.HOME)
                inputbox.type(Keys.DELETE)
            inputbox.type(text)
            if press_after:
                MBreak()
                inputbox.type(press_after)
        except Exception as e:
            raise PageError(
                f'Failed to type {text} to id {id}. Error: {e!s}')

    def TypeByXpath(self, xpath, text, press_after=None, wait_time=10):
        if not self.b.is_element_present_by_xpath(xpath, wait_time):
            raise PageError(f'Cannot find xpath: {xpath}')
        try:
            inputbox = self.b.find_by_xpath(xpath)
            if inputbox.value:
                inputbox.type(Keys.END)
                inputbox.type(Keys.SHIFT+Keys.HOME)
                inputbox.type(Keys.DELETE)
            inputbox.type(text)
            if press_after:
                MBreak()
                inputbox.type(press_after)
        except Exception as e:
            raise PageError(
                f'Failed to type {text} to xpath {xpath}. Error: {e!s}')