from selenium import webdriver
from lxml import html
from multiprocessing import Pool

import time
import csv
import json
import os


import Config
from FlightQuote import FlightQuote
from query_reader import query_lst


##################   FIXED SETTINGS   #################

SLEEP_TIME = Config.SLEEP_TIME['qunar']
MAX_SEARCH_NUM = Config.MAX_SEARCH_NUM['qunar']
REPEAT_TIME = Config.REPEAT_TIME['qunar']
QUNAR_BASE = Config.BASE_URL['qunar']

#######################################################
###
def get_response(query, url_base):
    qunar_url = url_base.format(dp=query.dp,rp=query.rp,dd=query.dt,rd=query.rt,dp2=query.dp,rp2=query.rp)
    driver = webdriver.Firefox()
    driver.get(qunar_url)
    time.sleep(SLEEP_TIME)

    page = driver.execute_script("return document.documentElement.innerHTML;")
    tree = html.fromstring(page)
    return tree, driver


def parse_quote(query, src='Qunar'):
    tree, driver = get_response(query, QUNAR_BASE)
    fq = FlightQuote(query.dp, query.rp, query.dt, query.rt, src)
    ITER_PANEL_XPATH = "//*[@id='lp_hdivResultPanel']"
    # ITER_PANEL_XPATH = "//*[@id='hdivResultPanel']"
    iter_panel = tree.xpath(ITER_PANEL_XPATH)[0]


    try:
        price = get_price(tree)
        print price
        fq.add_price(price)

        flights = get_flights(iter_panel)
        durations = get_duration(iter_panel)
        fq.add_out(flights[0], durations[0])
        fq.add_in(flights[1], durations[1])

        driver.close()
        return [fq,'']

    except:
        print('error_occurs')
        driver.close()
        return ['',query]


# def get_price(driver):
    # driver.find_elements_by_xpath("//a[@class='btn_book']")[0].click()
def get_price(tree):
    PRICE_XPATH = "//*[@id='curPriceData']/i"
    return tree.xpath(PRICE_XPATH)[0].tail

def get_flights(iter_panel):
    ITER_XPATH = "./div[1]//div[@class='a_model']/span"
    iters = iter_panel.xpath(ITER_XPATH)
    iter_details = []
    for i in iters:
        iter_details.append([i.text, i.attrib.get('title')])

    iter_list = [[],[]]
    for i in iter_details:
        if i[1] == u'\u9009\u4e3a\u53bb\u7a0b':
            iter_list[0].append(i[0].split(' ')[0])
        elif i[1] == u'\u9009\u4e3a\u56de\u7a0b':
            iter_list[1].append(i[0].split(' ')[0])
    return iter_list

def get_duration(iter_panel):
    iters = iter_panel.xpath("./div[1]//div[@class='a-tm-be']")
    durations = []
    for i in iters:
        if i.text != None:
            durations.append(i.text.encode('utf-8'))
        else:
            durations.append('')
    return durations

#
#
def quote_mind(query_item):
    dp = query_item.dp
    rp = query_item.rp
    print('in progress! ...\t'+dp+'\t'+rp +'\t')
    query_item.print_detail()
    quote = parse_quote(query_item)
    print('job done!!!  ...\t'+dp+'\t'+rp +'\t')
    return quote

def multi_search(query_items):
    p = Pool(MAX_SEARCH_NUM)
    results = p.map(quote_mind, query_items)
    p.close()
    p.join()
    return results

def init_files(dir_path):
    filename1 = dir_path + '/round_qunar_quotes.csv'
    if not os.path.exists(os.path.dirname(filename1)):
        try:
            os.makedirs(os.path.dirname(filename1))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    filename2 = dir_path + '/round_qunar_fails.csv'
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


def qunar_scraper_round(query_lst, dir_path):
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
