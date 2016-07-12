import pickle
from selenium import webdriver


driver = webdriver.Firefox()
# Please Login and copy paste url here -> assign to Logined_URL
Logined_URL = 'https://h5.m.taobao.com/trip/iflight/searchlist/index.html?depCityCode=SHA&arrCityCode=LON&leaveDate=2016-08-08&backDate=2016-08-24&htmlPage=3&_projVer=0.9.16#/?htmlPage=3'
driver.get(Logined_URL)
pickle.dump(driver.get_cookies(), open('ali_cookie.pkl','wb'))
