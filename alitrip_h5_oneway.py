from selenium import webdriver
from lxml import html
import time
import re
import csv
import os
import pickle

import Config
from FlightQuote import FlightQuote
from multiprocessing import Pool
from query_reader import query_lst

import json
with open('ctrip_src/ctrip_di.txt','r') as f:
    CTRIP_DICT = json.load(f)

# Uncomment this to stay login.
# driver = webdriver.Firefox()
# driver.get('https://h5.m.taobao.com/trip/iflight/searchlist/index.html?depCityCode=SHA&arrCityCode=LAX&leaveDate=2016-07-30&backDate=2016-08-06&htmlPage=3&_projVer=0.9.16#/?htmlPage=3')
# cookies = pickle.load(open('ali_cookie.pkl' ,'rb'))
# for cookie in cookies:
#     driver.add_cookie(cookie)

##################   FIXED SETTINGS   #################
SLEEP_TIME = Config.SLEEP_TIME['alitrip']
MAX_SEARCH_NUM = Config.MAX_SEARCH_NUM['alitrip']
REPEAT_TIME = Config.REPEAT_TIME['alitrip']
ALI_BASE = Config.BASE_URL['alitrip_ow']

##########################
# round trip
# sample_url = 'https://h5.m.taobao.com/trip/iflight/searchlist/index.html?depCityCode=SHA&arrCityCode=LON&leaveDate=2016-06-08&backDate=2016-06-24&htmlPage=3&_projVer=0.9.5#/?htmlPage=3'
# one-way trip
# sample_url = 'https://h5.m.taobao.com/trip/iflight/searchlist/index.html?depCityCode=SHA&arrCityCode=LON&leaveDate=2016-06-08&depCityName=&htmlPage=3&_projVer=0.9.5#/?htmlPage=3'
def get_response(query, url_base):
    dp = query[0].dp
    rp = query[0].rp
    dp = query[1].get(dp,[[],dp])[1]
    rp = query[1].get(rp,[[],rp])[1]

    ali_url = url_base.format(dp=dp,rp=rp,dt=query[0].dt)
    print ali_url

    driver = webdriver.Firefox()
    driver.get(ali_url)
    time.sleep(SLEEP_TIME)
    page = driver.execute_script("return document.documentElement.innerHTML;")
    tree = html.fromstring(page)

    return driver, tree

def parse_quote(query, src='Alitrip'):
    driver, tree = get_response(query, ALI_BASE)
    fq = FlightQuote(query[0].dp, query[0].rp, query[0].dt, query[0].rt, src)

    try:
        price, flights = parse_detail(tree)
        print price
        print flights
        fq.add_price(price)
        fq.add_out(flights[0][0], flights[0][1])

        driver.close()
        return [fq,'']
    except:
        print('error occurs!')
        driver.close()
        return ['', query]
    # price, flights = parse_detail(tree)
    # print price
    # print flights
    # fq.add_price(price)
    # fq.add_out(flights[0][0], flights[0][1])
    # # fq.add_in(flights[1][0],flights[1][1])
    # driver.close()
    # fq.print_detail()
    # return [fq,'']

def parse_detail(tree):
    cheap_item = tree.xpath('//section[@class="list-wrap"]/div[@class="list-item-box"]')[0]
    cheap_flights = cheap_item.xpath('.//div[@class="flight-num"]/text()')
    cheap_durations = cheap_item.xpath('.//span[@class="duration-time"]/text()')
    cheap_price = cheap_item.xpath('.//div[@class="price-info"]//span/text()')[1]
    cheap_flights = [x.split('/') for x in cheap_flights]
    flights = []

    for cheap_flight in cheap_flights:
        flights.append([])
        for flight in cheap_flight:
            flight = re.search('([A-Z].*)',flight).group(1)
            if flight.find('(') != -1:
                flight = flight[:flight.find('(')]
            flights[-1].append(flight)

    return cheap_price, zip(flights,cheap_durations)

#
def quote_mind(query_item):
    dp = query_item[0].dp
    rp = query_item[0].rp
    print('in progress! ...\t'+dp+'\t'+rp +'\t')
    query_item[0].print_detail()
    quote = parse_quote(query_item)
    # quote = parse_quote(query_item[0], query_item[1])
    print('job done!!!  ...\t'+dp+'\t'+rp +'\t')
    return quote

def multi_search(query_items):
    p = Pool(MAX_SEARCH_NUM)
    results = p.map(quote_mind, query_items)
    p.close()
    p.join()
    return results

def init_files(dir_path):
    filename1 = dir_path + '/oneway_alitrip_quotes.csv'
    if not os.path.exists(os.path.dirname(filename1)):
        try:
            os.makedirs(os.path.dirname(filename1))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    filename2 = dir_path + '/oneway_alitrip_fails.csv'
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


def alitrip_scraper_oneway(query_lst, dir_path):
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
        fails_formatted = [x[1][0].format_info() for x in results if x[0] == '']
        successes = [x[0].format_info() for x in results if x[0] != '']

        save_to_csv(failure_file, fails_formatted, 'w')
        save_to_csv(success_file, successes, 'a')

# parse_quote([query_lst[0],CTRIP_DICT], src='Alitrip')
