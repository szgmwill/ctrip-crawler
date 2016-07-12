# Search Round Flights from Ctrip
#
# save all successful results in '/round_ctrip_quotes.csv'
# save all unsuccessful query condition in '/round_ctrip_fails.csv'
#
import time
import csv
import re
import os
import multiprocessing

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from lxml import html
from multiprocessing import Pool

import Config
from FlightQuote import FlightQuote

##################   FIXED SETTINGS   #################
SLEEP_TIME = Config.SLEEP_TIME['ctrip']
MAX_SEARCH_NUM = Config.MAX_SEARCH_NUM['ctrip']
REPEAT_TIME = Config.REPEAT_TIME['ctrip']
CTRIP_BASE = Config.BASE_URL['ctrip']


#######################################################
### get_response
#  1. parse query parameters -> dp, rp, dp_pin, rp_pin
#  2. build up URL
#  3. start a browser and fill the target url.
#
### Params
#   query           Type(Query) -> see FlightQuote.py
#   url_base        String with parameters to fill -> see Config.py
#   ctrip_di        Dictionary -> see ctrip_di.txt
#
### Return
#
#   driver          selenium.webdriver -> driver is returned because there are buttons to be clicked.
#   tree            lxml - html
#
### Sample URL: http://flights.ctrip.com/international/round-beijing-london-bjs-lon?2016-07-28&2016-08-05&y#buildup
### Notice: 3-Digit City IATA code Should be found in ctrip_di.txt(should keep updating it)
#       e.g. PEK should not be used in search for flights related to Beijing(BJS).
def get_response(query, url_base, ctrip_di):
    dp = query.dp
    rp = query.rp
    dp = ctrip_di.get(dp,[[],dp])[1]
    rp = ctrip_di.get(rp,[[],rp])[1]
    dp_pin = ctrip_di.get(dp,['biubiu',[]])[0]
    rp_pin = ctrip_di.get(rp,['biubiu',[]])[0]

    #myselenium_hub_url = 'http://grid.selenium.test.skyscanner.local:4444/wd/hub'
    myselenium_hub_url = 'http://192.168.99.100:4444/wd/hub'
    caps = DesiredCapabilities.FIREFOX
    caps['environment'] = 'TAS TESTS'

    c_url = url_base.format(dp_pin=dp_pin,rp_pin=rp_pin,dp=dp,rp=rp,dt=query.dt,rt=query.rt)
    print c_url
    #driver = webdriver.Firefox()
    driver = webdriver.Remote(command_executor=myselenium_hub_url, desired_capabilities=caps)
    driver.implicitly_wait(10)
    driver.get(c_url)
    time.sleep(SLEEP_TIME)
    page = driver.execute_script("return document.documentElement.innerHTML;")
    tree = html.fromstring(page)
    return driver, tree


#######################################################
### parse_quote(query, src='Ctrip')
#
#  1. create a FlightQuote object
#  2. if successes, save the Object
#  3. if fails, save the Query
#
### Params
#   query           Type(Query) -> see FlightQuote.py
#   src             string      -> to mark the source website
#
### Return
#   [FlightQuote, Query] -> if successes, [FlightQuote, '']
#                        -> if fails,     ['', Query]
def parse_quote(query, ctrip_di, src='Ctrip'):
    fq = FlightQuote(query.dp, query.rp, query.dt, query.rt, src)
    driver, tree = get_response(query, CTRIP_BASE, ctrip_di)

    try:
        cheapest_price, supplier = parse_price(tree)
        fq.add_price(cheapest_price)
        fq.add_agent(supplier)

        durations = parse_duration(tree)
        DETAIL_BTN = '//div[@class=\'flight-action-more\']/a'
        click_button(driver, DETAIL_BTN)
        flights = check_iters(tree)

        duration0 = re.findall(r"([0-9a-zA-Z]+)",durations[0])[0]
        duration1 = re.findall(r"([0-9a-zA-Z]+)",durations[1])[0]

        fq.add_out(flights[0],duration0)
        fq.add_in(flights[1],duration1)

        driver.close()
        return [fq,'']

    except:
        print('error occur!')
        driver.close()
        return ['', query]

#######################################################
### parse_duration(tree, is_round=True)
#
#  get duration(flight time) -> Ctrip Returns Total Oneway Time
#
### Params
#   tree            ->  lxml - html
#
### Return
#   durations       -> string/int
def parse_duration(tree, is_round=True):
    duration_lst = tree.xpath('//div[@class="flight-total-time"]')
    if is_round == True:
        durations = [x.text for x in duration_lst[:2]]
    else:
        durations = [x.text for x in duration_lst[:1]]
    return durations

#######################################################
### parse_price(tree)
#
#  1. Get all prices for first selection
#  2. Get all suppliers for each price
#  3. Get real Cheapest Price(price + extra charge)
#  4. Match supplier to cheapest price
#
### Params
#   tree            ->  lxml - html
#
### Return
#   cheapest_price  ->  float
#   supplier        ->  string -> tagname or detailed name
def parse_price(tree):
    seats = tree.xpath('//div[@class="seats-list"][1]/div')

    price = []
    suppliers = []
    for seat in seats:
        try:
            price.append([float(seat.xpath('.//div[@class="seat-price"]/span[1]/dfn')[0].tail)])
        except:
            price.append([0])
    #
        try:
            price_extra = float(seat.xpath('.//div[@class="seat-bonus"]//span[1]/dfn')[0].tail)
            price[-1].append(price_extra)
        except:
            price[-1].append(0)

        try:
            # supplier = seat.xpath('.//div[@class="seat-special"]')[0].getchildren()[0].text
            supplier = seat.xpath('.//div[@class="seat-special"]')[0].getchildren()[0].attrib.get('class')
            if supplier == 'tag-text':
                if seat.xpath('.//div[@class="seat-special"]')[0].getchildren()[0].text != None:
                    supplier = seat.xpath('.//div[@class="seat-special"]')[0].getchildren()[0].text
                elif seat.xpath('.//div[@class="seat-special"]')[0].getchildren()[0].tail != None and seat.xpath('.//div[@class="seat-special"]')[0].getchildren()[0].tail.strip() != '':
                    supplier = seat.xpath('.//div[@class="seat-special"]')[0].getchildren()[0].tail
            suppliers.append(supplier)
        except:
            suppliers.append('')

    price2 = [x[0]+x[1] for x in price]
    price3 = filter(lambda x: x != 0, price2)
    cheapest_price = min(price3)
    supplier = suppliers[price2.index(cheapest_price)]

    return cheapest_price, supplier

#######################################################
### check_iters(tree)
#
#  Get all carriers and flight number
#
### Params
#   tree            ->  lxml - html
#
### Return
#   iter_list       ->  [[depart_flight, depart_flight,...],[return_flight, return_flight,...]]
def check_iters(tree):
    ITERS_XPATH = "//div[@class='flight-detail-expend']"

    try:
        iter_expend = tree.xpath(ITERS_XPATH)[0]
        iter_sections = iter_expend.xpath("./div[@class='flight-detail-section']")

        iter_details = []
        for i in iter_sections:
            air_id = i.xpath(".//span[@class='flight-No']")[0].text
            try:
                tag = i.xpath(".//span[@class='tag-dir']")[0].text
            except:
                tag = ''
            iter_details.append([air_id, tag])

        iter_list = []
        for i in iter_details:
            if i[1] == u'\u53bb':
                iter_list.append([i[0]])
            elif i[1] == u'\u8fd4':
                iter_list.append([i[0]])
            else:
                iter_list[-1].append(i[0])

    except:
        iter_list = [[],[]]

    return iter_list

#######################################################
### click_button(driver, button_path)
#
#  click expend detail button
#
### Params
#   driver          -> selenium.webdriver
#   button_path     -> string -> xpath of the expend detail button
#
### Return
#   tree            -> lxml - html
def click_button(driver, button_path):
    driver.find_elements_by_xpath(button_path)[0].click()
    time.sleep(SLEEP_TIME)
    page = driver.execute_script("return document.documentElement.innerHTML;")
    tree = html.fromstring(page)
    return tree

#######################################################
### multi_search(query_items)
#
#  query_items     -> list of Query objects
#  used Multi Processing
def multi_search(query_items):
    p = Pool(MAX_SEARCH_NUM)
    results = p.map(quote_mind, query_items)
    p.close()
    p.join()
    return results

#######################################################
### quote_mind(query_item)
### Params
#  query_item   -> Query object
#
### Return
#  quote        -> [FlightQuote objects, ctrip_dictionary]
def quote_mind(query_item):
    dp = query_item[0].dp
    rp = query_item[0].rp
    print('in progress! ...\t'+dp+'\t'+rp +'\t')
    query_item[0].print_detail()
    quote = parse_quote(query_item[0], query_item[1])
    print('job done!!!  ...\t'+dp+'\t'+rp +'\t')
    return quote

def init_files(dir_path):
    filename1 = dir_path + '/round_ctrip_quotes.csv'
    if not os.path.exists(os.path.dirname(filename1)):
        try:
            os.makedirs(os.path.dirname(filename1))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    filename2 = dir_path + '/round_ctrip_fails.csv'
    if not os.path.exists(os.path.dirname(filename2)):
        try:
            os.makedirs(os.path.dirname(filename2))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    return filename1, filename2


def save_to_csv(filename, data, save_method='w'):
    with open(filename, save_method) as f:
        f.write('\xEF\xBB\xBF')
        writer = csv.writer(f)
        writer.writerows(data)


def ctrip_scraper_round(query_lst, dir_path):
    results = multi_search(query_lst)
    successes = [x[0].format_info() for x in results if x[0] != '']
    fails = [x[1] for x in results if x[0] == '']

    success_file, failure_file = init_files(dir_path)
    save_to_csv(success_file, successes, 'a')

    # Repeat is used to go over the failed searches.
    count = REPEAT_TIME
    while count > 0 and len(fails) > 0:
        print('--- Round ' + str(count) + '   ---   Count ' + str(len(fails)) + ' ---')
        count -= 1
        results = multi_search(fails)

        successes = [x[0].format_info() for x in results if x[0] != '']
        fails = [x[1] for x in results if x[0] == '']
        save_to_csv(success_file, successes, 'a')

    if len(fails) > 0:
        fails_formatted = [x[1].format_info() for x in results if x[0] == '']
        successes = [x[0].format_info() for x in results if x[0] != '']

        save_to_csv(failure_file, fails_formatted, 'w')
        save_to_csv(success_file, successes, 'a')
