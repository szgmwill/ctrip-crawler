import json
import datetime
import ctrip_simple
import ctrip_simple_ow
import qunar
import qunar_ow
import alitrip_h5
import alitrip_h5_oneway

from query_reader import query_lst
from multiprocessing import freeze_support

if __name__ == '__main__':
    freeze_support()

    # query_lst = query_lst[:10]
    # query_lst
    with open('ctrip_src/ctrip_di.txt','r') as f:
        CTRIP_DICT = json.load(f)

    dir_path = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')
    ctrip_simple.ctrip_scraper_round([[x, CTRIP_DICT] for x in query_lst], dir_path)
    #ctrip_simple_ow.ctrip_scraper_oneway([[x, CTRIP_DICT] for x in query_lst], dir_path)

    #qunar.qunar_scraper_round(query_lst, dir_path)
    #qunar_ow.qunar_scraper_oneway(query_lst, dir_path)

    # alitrip_h5.alitrip_scraper_round([[x, CTRIP_DICT] for x in query_lst], dir_path)
    # alitrip_h5_oneway.alitrip_scraper_oneway([[x, CTRIP_DICT] for x in query_lst], dir_path)
