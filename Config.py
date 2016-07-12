# Base URL
# Ctrip
BASE_URL = {
    'ctrip' : 'http://flights.ctrip.com/international/round-{dp_pin}-{rp_pin}-{dp}-{rp}?{dt}&{rt}&y#builtUp',
    'ctrip_ow' : 'http://flights.ctrip.com/international/{dp_pin}-{rp_pin}-{dp}-{rp}?{dt}&y',
    'qunar' : 'http://flight.qunar.com/site/interroundtrip_compare.htm?fromCity={dp}&toCity={rp}&fromDate={dd}&toDate={rd}&fromCode={dp2}&toCode={rp2}',
    'qunar_ow' : 'http://flight.qunar.com/site/oneway_list_inter.htm?searchDepartureAirport={dp}&searchArrivalAirport={rp}&searchDepartureTime={dd}&searchArrivalTime={rd}&fromCode={dp2}&toCode={rp2}&from=flight_int_search&lowestPrice=null&favoriteKey=&showTotalPr=0',
    'alitrip' : 'https://h5.m.taobao.com/trip/iflight/searchlist/index.html?depCityCode={dp}&arrCityCode={rp}&leaveDate={dt}&backDate={rt}&htmlPage=3&_projVer=0.9.5#/?htmlPage=3',
    'alitrip_ow' : 'https://h5.m.taobao.com/trip/iflight/searchlist/index.html?depCityCode={dp}&arrCityCode={rp}&leaveDate={dt}&htmlPage=3&_projVer=0.9.5#/?htmlPage=3'
}


SLEEP_TIME = {
    'ctrip' : 30,
    'qunar' : 20,
    'alitrip' : 60,
}

MAX_SEARCH_NUM = {
    'ctrip' : 3,
    'qunar' : 2,
    'alitrip' : 1
}

REPEAT_TIME = {
    'ctrip' : 2,
    'qunar' : 2,
    'alitrip' : 0
}
