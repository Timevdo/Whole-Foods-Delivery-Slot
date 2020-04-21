import bs4

from selenium import webdriver

import sys
import time
import os
import winsound

from twilio.rest import Client

import config as cfg

my_number = cfg.my_number

#Text alert added by Timevdo
def sms_alert(number):
   client = Client(cfg.twilio_name, cfg.twilio_auth)
   from_number = "+19892828024"

   client.messages.create(to=number, from_=from_number, body="Your Amazon Delivery has a slot availible. Please go to your computer to complete the purchase")
   print('\a')

def getWFSlot(productUrl):
   headers = {
       'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
   }

   driver = webdriver.Chrome()
   driver.get(productUrl)           
   html = driver.page_source
   soup = bs4.BeautifulSoup(html, "html.parser")
   time.sleep(60)
   no_open_slots = True

   start_time = time.time()

   iteration = 0

   while no_open_slots:
      driver.refresh()

      print(iteration, "refreshed")
      iteration += 1

      html = driver.page_source
      soup = bs4.BeautifulSoup(html, "html.parser")
      time.sleep(4)

      try:
         slot_opened_text = "Not available"
         all_dates = soup.findAll("div", {"class": "ufss-date-select-toggle-text-availability"})
         for each_date in all_dates:
            if slot_opened_text not in each_date.text:
               print('SLOTS OPEN 2!')
               sms_alert(my_number)
               no_open_slots = False
               time.sleep(1400)
      except AttributeError:
         pass

      try:
         no_slot_pattern = 'No delivery windows available. New windows are released throughout the day.'
         if no_slot_pattern == soup.find('h4', class_ ='a-alert-heading').text:
            print("NO SLOTS!")
      except AttributeError: 
            print('SLOTS OPEN 3!')
            sms_alert(my_number)
            no_open_slots = False


      slot_patterns = ['Next available', '1-hour delivery windows', '2-hour delivery windows']
      try:
         next_slot_text = str([x.text for x in soup.findAll('h4', class_ ='ufss-slotgroup-heading-text a-text-normal')])
         if any(next_slot_text in slot_pattern for slot_pattern in slot_patterns):
            print('SLOTS OPEN!')
            print('\a')
            no_open_slots = False

            autoCheckout(driver)
            
      except AttributeError:
         pass

   print(f"Slot found in {(time.time - start_time)/60} minutes")

#sms_alert(my_number)
getWFSlot('https://www.amazon.com/gp/buy/shipoptionselect/handlers/display.html?hasWorkingJavascript=1')



