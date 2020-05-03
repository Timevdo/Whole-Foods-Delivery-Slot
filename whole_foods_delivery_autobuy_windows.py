import bs4

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from twilio.rest import Client

import sys
import time
import os

import winsound
import logging

import config as cfg 

my_number = cfg.my_number
logging.basicConfig(filename='autbuy_log.log', filemode='w', format='%(name)s - %(asctime)s - %(levelname)s - %(message)s')

#Text alert added by Timevdo
def sms_alert(number):
   if cfg.send_text_alert:
      client = Client(cfg.twilio_name, cfg.twilio_auth)
      from_number = "+19892828024"

      client.messages.create(to=number, from_=from_number, body="Your automatic slotfinder has found a delivery slot on Amazon! Please go to your computer now to continue, as slots may expire if left unattended")

   print('\a')

def autoCheckout(driver):
   driver = driver
   duration = 1000
   freq = 440
   
   time.sleep(4)
   driver.execute_script("window.scrollTo(0, 200)")

   logging.debug('autocheckout start')

   try:
      slot_select_button = driver.find_element_by_xpath('/html/body/div[5]/div[1]/div/div[2]/div/div/div/div/div[1]/div[4]/div[2]/div/div[3]/div/div/ul/li/span/span/div/div[2]/span/span/button')
      slot_select_button.click()
      print("Clicked open slot")
   except NoSuchElementException:
      slot_select_button = driver.find_element_by_xpath('/html/body/div[5]/div[1]/div/div[2]/div/div/div/div/div[1]/div[4]/div[2]/div/div[4]/div/div/ul/li/span/span/div/div[2]/span/span/button')
      slot_select_button.click()

   slot_continue_button = driver.find_element_by_xpath('/html/body/div[5]/div[1]/div/div[2]/div/div/div/div/div[2]/div[3]/div/span/span/span/input')
   slot_continue_button.click()
   print("Selected slot and continued to next page")
   
   try:
      time.sleep(6)
      outofstock_select_continue = driver.find_element_by_xpath('/html/body/div[5]/div/form/div[25]/div/div/span/span/input')
      outofstock_select_continue.click()
      print("Passed out of stock")
   except NoSuchElementException:
      pass

   try:
      time.sleep(6)
      payment_select_continue = driver.find_element_by_xpath('/html/body/div[5]/div[1]/div[2]/div[2]/div[4]/div/form/div[3]/div[1]/div[2]/div/div/div/div[1]/span/span/input')
      payment_select_continue.click()
      print("Payment method selected")


      time.sleep(6)
      try:
         review_select_continue = driver.find_element_by_xpath('/html/body/div[5]/div[1]/div[2]/form/div/div/div/div[2]/div/div[1]/div/div[1]/div/span/span/input')
         review_select_continue.click()
         print("Order reviewed")
      except NoSuchElementException:
         review_select_continue = driver.find_element_by_xpath('/html/body/div[5]/div[1]/div[2]/form/div/div/div/div[2]/div[2]/div/div[1]/span/span/input')
         review_select_continue.click()
         print("Order reviewed")

      print("Order Placed!")
      print('\a')
   except NoSuchElementException:
      print("Found a slot but it got taken, run script again.")
      print('\a') 
      time.sleep(1400)

def getWFSlot(productUrl):
   headers = {
       'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
   }
   duration = 1000
   freq = 440

   driver = webdriver.Chrome()
   driver.get(productUrl)
   driver.maximize_window()         
   html = driver.page_source
   soup = bs4.BeautifulSoup(html, "html.parser")
   time.sleep(60)
   no_open_slots = True

   logging.info('autorefreshing start')
   while no_open_slots:
      driver.refresh()
      print("refreshed")
      html = driver.page_source
      soup = bs4.BeautifulSoup(html, "html.parser")
      time.sleep(4)

      slot_patterns = ['Next available', '1-hour delivery windows', '2-hour delivery windows']
      try:
         next_slot_text = str([x.text for x in soup.findAll('h4', class_ ='ufss-slotgroup-heading-text a-text-normal')])
         if any(next_slot_text in slot_pattern for slot_pattern in slot_patterns):
            print('SLOTS OPEN!')
            sms_alert(my_number)
            no_open_slots = False

            autoCheckout(driver)
            logging.info('slot found')
            
      except AttributeError:
         pass

      try:
         slot_opened_text = "Not available"
         all_dates = soup.findAll("div", {"class": "ufss-date-select-toggle-text-availability"})
         for each_date in all_dates:
            if slot_opened_text not in each_date.text:
               print('SLOTS OPEN!')
               sms_alert(my_number)
               no_open_slots = False
               logging.info('slot found')

               autoCheckout(driver)

      except AttributeError:
         pass

      try:
         no_slot_pattern = 'No delivery windows available. New windows are released throughout the day.'
         if no_slot_pattern == soup.find('h4', class_ ='a-alert-heading').text:
            print("NO SLOTS!")
      except AttributeError: 
            print('SLOTS OPEN!')
            sms_alert(my_number)
            no_open_slots = False
            logging.info('slot found')

            autoCheckout(driver)

logging.info('start of program')
getWFSlot('https://www.amazon.com/gp/buy/shipoptionselect/handlers/display.html?hasWorkingJavascript=1')


