#!/usr/bin/env python3

from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import TimeoutException
from twilio.rest import Client
import time

#Enter klekt Link and sizes prefered prices here.
#Example "US10" :"€50"
shoelink_klekt = "https://www.klekt.com/product/sb-dunk-low-what-the-p-rod-2021"
user_dict = {
    "US10" :"€50",
    "US3.5" :"€50",
    "US11.5" :"€999"
}

#Enter stockx Link and sizes prefered prices here.
#Example "US 10" :"€700"
shoelink_stockx = "https://stockx.com/nike-sb-dunk-low-travis-scott"
user_dict_stockx = {
    "US 10" :"€700",
    "US 10.5" :"€2000",
    "US 11.5" :"€180"
}

#Twilio client info.
client = Client("XXXX", "XXXX")

#Makes browser Incognito.
option = webdriver.ChromeOptions()
option.add_argument("headless")
option.add_argument("incognito")

#webdriver functionality.
browser = webdriver.Chrome(executable_path='./chromedriver', options=option)

browser.get(shoelink_klekt)

try:
    WebDriverWait(browser,60).until(EC.visibility_of_element_located((By.XPATH,"/html/body/div[1]/div/header/div[1]/div[1]/a/img")))

except TimeoutException:
    print("Timed out.")
    browser.quit()

#Scans sizes, puts them in a string.
sizes_scan = browser.find_elements_by_xpath("/html/body/div[1]/div/div[1]/div[4]/div/div[1]/div[1]/div/div[3]/div/div")

#Makes the scan sizes_scan human readable.
nolist = [x.text for x in sizes_scan]

#Cleans sizes_scan string. Makes a proper list.
nolist = nolist[0] 
nolist = nolist.split('\n')

#Divides the sizes and Euro and puts them in a Dictionary.
size_list = []
euro_list = []

for x in nolist:
    if x.startswith("€"):
        euro_list.append(x)
    else:
        size_list.append(x)

size_price_dict = dict(zip(size_list, euro_list))
print(size_price_dict)

sep = '/'
shoename = shoelink_klekt.split(sep, -1)[4]

#Compares set prices and current prices. Sleep is used to space out text messages.
for keys in user_dict:
    time.sleep(1)
    try:
        if size_price_dict[keys] <= user_dict[keys]:
            print(keys +" " + shoename)
            print("Target price reached!")
            client.messages.create(
                body=keys +" " + shoename + "\nIs available below/at your target price at Klekt! Current price: " + size_price_dict[keys] + "| Target price: " + user_dict[keys]+"|\n"+str(shoelink_klekt),from_="+14142061841",to="+310642875999")
            
        else:
            print("Target price hasn't been reached...\nCurrent price: " + size_price_dict[keys] + "| Target price: " + user_dict[keys]+"|")
        print()

    except KeyError:
        print(keys+" " + shoename + " is currently not available.")
        print()
        

'''
STOCK X SECTION
'''
#Going to page. adding a cookie to bypass country select screen. After that refresh.
browser.get(shoelink_stockx)
browser.add_cookie({'name' : 'stockx_market_country', 'value' : "NL", })
browser.add_cookie({'name' : 'language_code', 'value' : "en" })
browser.add_cookie({'name' : 'stockx_dismiss_modal', 'value' : "true" })
browser.get(shoelink_stockx)

WebDriverWait(browser,60).until(EC.visibility_of_element_located((By.XPATH,"/html/body/div[1]/div[1]/div[2]/div[2]/span/div[2]/div[1]/div/div[1]/div[2]/div[1]/div/div/button")))
browser.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[2]/span/div[2]/div[1]/div/div[1]/div[2]/div[1]/div/div/button').click()
sizes_list = browser.find_elements_by_class_name("title")
price_list = browser.find_elements_by_class_name("subtitle")

#Makes the scan sizes_scan human readable.
#nolist = [x.text for x in sizes_scan]
sizes_list= [x.text for x in sizes_list]
price_list= [x.text for x in price_list]

#List sanitation.
sizes_list = list(filter(None, sizes_list))
price_list = list(filter(None, price_list))


size_price_dict_stockx = dict(zip(sizes_list, price_list))

shoenamestockx = shoelink_stockx.split(sep, -1)[3]

#removing commas inside products over 1000 Euros.
#removing € sign because of some sort of int() issue.
for x in size_price_dict_stockx:
    size_price_dict_stockx[x] = size_price_dict_stockx[x].replace(',', '')
    size_price_dict_stockx[x] = size_price_dict_stockx[x].replace('€', '')

for x in user_dict_stockx:
    user_dict_stockx[x] = user_dict_stockx[x].replace(',', '')
    user_dict_stockx[x] = user_dict_stockx[x].replace('€', '')

#Compare set prices and current prices. Twilio can only send 1 message per second.

for keys in user_dict_stockx:
    time.sleep(1)
    try:
        if int(size_price_dict_stockx[keys]) <= int(user_dict_stockx[keys]):

            client.messages.create(
                body=keys +" " + shoenamestockx + "\nIs available below/at your target price at Stockx! Current price: €" + size_price_dict_stockx[keys] + "| Target price: €" + user_dict_stockx[keys]+"|"+"|\n"+str(shoelink_stockx),from_="+14142061841",to="+310642875999")
        else:
            print(keys +" " + shoenamestockx + " target not reached")
            print("Target price hasn't been reached...\nCurrent price: €" + size_price_dict_stockx[keys] + "| Target price: €" + user_dict_stockx[keys]+"|")
        print()

    except KeyError:
        print(keys+" " + shoenamestockx + " is currently not available.")
        print()

browser.quit()
quit()
