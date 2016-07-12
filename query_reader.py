import csv
import datetime
import re

filename = 'sample_query.csv'

class Query:
    def __init__(self, dp_full, rp_full, dp, rp, dt, rt=''):
        self.dp_full = dp_full
        self.rp_full = rp_full
        self.dp = dp
        self.dt = dt
        self.rp = rp
        self.rt = rt

    def format_info(self):
        return [self.dp_full, self.rp_full, self.dp, self.dt, self.rp, self.rt]

    def print_detail(self):
        formatted = self.format_info()
        print '\t'.join(formatted)

def get_dep_rtn_time():
    dep_date = datetime.datetime.today() + datetime.timedelta(days=30)
    rtn_date = dep_date + datetime.timedelta(days=7)
    return dep_date.strftime('%Y-%m-%d').decode("utf-8"), rtn_date.strftime('%Y-%m-%d').decode("utf-8")



def parse_query_csv(fn=filename):
    with open(filename, 'r') as f:
        data = [x.split(',') for x in f.readlines()[1:]]

    dt, rt = get_dep_rtn_time()

    full_comb = [re.findall(r"\([\w]+\)",x[0]) for x in data]
    full_comb = [[x[0].replace('(','').replace(')',''),x[1].replace('(','').replace(')','')] for x in full_comb]
    iata_comb = [[x[2].split('/')[0],x[4].split('/')[0]] for x in data]

    query_lst = []
    for i in range(0,len(full_comb)):
        query_lst.append(Query(full_comb[i][0],full_comb[i][1],iata_comb[i][0],iata_comb[i][1],dt,rt))

    return query_lst

def print_query_lst(query_lst):
    for x in query_lst:
        x.print_detail()

query_lst = parse_query_csv()
# query_lst = parse_query_csv()
# for x in query_lst:
    # x.print_detail()
