import pandas as pd
import matplotlib.pyplot as plt
import time, datetime
from datetime import timedelta, date
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

login_details = {'username': 'xxx',
                 'password': 'xxx',
                 'dni': 'xxx'}

start_date = datetime.date(year=2019, month=12, day=15)








def site_login(login_details):
    url = "https://www.r4.com/portal?TX=goto&FWD=PLUSVALIASFONDOS"
    driver.get(url)
    time.sleep(1)
    
    while "MI PATRIMONIO" not in driver.page_source:
        login_url = "https://www.r4.com/login"
        driver.get(login_url)
        time.sleep(1)
        driver.find_element_by_xpath("/html/body/div[1]/div/div[1]/div[1]/div[3]/div[2]/div[2]/div/div[2]/div/div/div/div[2]/div[1]/div/div/h1").click()

        html = driver.find_element_by_tag_name('html')
        html.send_keys(Keys.DOWN)
        html.send_keys(Keys.DOWN)
        html.send_keys(Keys.DOWN)
        html.send_keys(Keys.DOWN)
        html.send_keys(Keys.DOWN)
        html.send_keys(Keys.DOWN)
        driver.find_element_by_name("USUARIO").send_keys(login_details['username'])
        driver.find_element_by_name("PASSWORD").send_keys(login_details['password'])
        driver.find_element_by_name("EF_DNI").send_keys(login_details['dni'])
        time.sleep(1)
        driver.find_element_by_xpath("//*[@id=\"T_LOGIN_FORM_P\"]/div/div[6]/input").click()
        time.sleep(1.5)
        url = "https://www.r4.com/portal?TX=goto&FWD=PLUSVALIASFONDOS"
        driver.get(url)

def daterange(date1, date2):
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + timedelta(n)
    
    
def check_plusvalias(date):
    driver.find_element_by_name("latente_datePicker").clear()
    driver.find_element_by_name("latente_datePicker").send_keys(date)
    driver.find_element_by_xpath("//*[@id=\"mw_contenedor\"]/div[4]/div[2]/div").click()
    time.sleep(0.7)
    
    if "Es necesario disponer de fondos en cartera, hasta la fecha indicada." in driver.page_source:
        return False, False, False
    
    invested = driver.find_element_by_xpath("//*[@id=\"informePlusvaliasLatentesFondos\"]/div[2]/div/div/div/table/tbody/tr[last()]/td[2]").text
    invested = invested.replace(".", "").replace(",", ".")
    invested = float(invested)
    
    value = driver.find_element_by_xpath("//*[@id=\"informePlusvaliasLatentesFondos\"]/div[2]/div/div/div/table/tbody/tr[last()]/td[3]").text
    value = value.replace(".", "").replace(",", ".")
    value = float(value)
    
    profitloss = driver.find_element_by_xpath("//*[@id=\"informePlusvaliasLatentesFondos\"]/div[2]/div/div/div/table/tbody/tr[last()]/td[4]").text
    profitloss = profitloss.replace(".", "").replace(",", ".")
    profitloss = float(profitloss)
    
    #print('%s - %.2f, %.2f, %.2f' % (date, invested, value, profitloss))
    
    return invested, value, profitloss

def add_dates(start_date, end_date, results):
    for date in daterange(start_date, end_date):
        dateFormatted = date.strftime("%d/%m/%Y")
        invested, value, profitloss = check_plusvalias(dateFormatted)
        if invested != False:
            row = pd.Series(data = {
                'invested': invested,
                'value': value,
                'profitloss': profitloss
            }, name=date)
            results = results.append(row, ignore_index=False)
    return results


driver = webdriver.Chrome()
site_login(login_details)

try: results = pd.read_pickle('Renta4_Progress.pkl')
except: results = pd.DataFrame()

if results.empty:
    start_date = datetime.date(year=2019, month=12, day=15)
else:
    start_date = results.index[-1] + timedelta(days=1)
    
end_date = date.today() - timedelta(days=1)

results = add_dates(start_date, end_date, results)

driver.quit()

results.to_pickle('Renta4_Progress.pkl')
