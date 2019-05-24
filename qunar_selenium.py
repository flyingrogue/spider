# -*- coding:utf-8 -*-

'''
var t = function(e) {
            var t = "123456789poiuytrewqasdfghjklmnbvcxzQWERTYUIPLKJHGFDSAZXCVBNM";
            var n = "";
            for (var r = 0; r < e; r++) {
                n += t.charAt(Math.ceil(Math.random() * 1e8) % t.length)
            }
            return n
        };
'''
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
import time
from lxml import etree
import pymysql

chrome_options=webdriver.ChromeOptions()
#chrome_options.add_argument('--headless')
chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])

browser=webdriver.Chrome(chrome_options=chrome_options)
#browser=webdriver.PhantomJS()
# browser.set_window_size(1920,1080)
# browser.maximize_window()
wait=WebDriverWait(browser,10)


def get_page(fromCity,toCity,dateTime):
    #try:
        browser.get('https://www.qunar.com/')
        input1=browser.find_element_by_xpath("//div[@id='js_flighttype_tab_domestic']//input[@name='fromCity']")
        ActionChains(browser).move_to_element(input1).click().perform()
        #input=wait.until(EC.presence_of_element_located((By.XPATH,"//div[@id='js_flighttype_tab_domestic']//input[@name='fromCity']")))
        city1=wait.until(EC.presence_of_element_located((By.XPATH,"//div[@data-panel='domesticfrom-flight-hotcity-from']//a[@class='js-hotcitylist' and text()='{}']".format(fromCity))))
        #city=browser.find_element_by_xpath("//div[@data-panel='domesticfrom-flight-hotcity-from']//a[@class='js-hotcitylist' and text()='{}']".format(fromCity))
        city1.click()
        input2=browser.find_element_by_xpath("//div[@id='js_flighttype_tab_domestic']//input[@name='toCity']")
        ActionChains(browser).move_to_element(input2).click().perform()
        city2=wait.until(EC.presence_of_element_located((By.XPATH,"//div[@data-panel='domesticto-flight-hotcity-to']//a[@class='js-hotcitylist' and text()='{}']".format(toCity))))
        city2.click()
        date=browser.find_element_by_xpath("//input[@id='js_domestic_fromdate']")
        date.clear()
        date.send_keys(dateTime)
        submit=browser.find_element_by_xpath("//button[@class='button-search']")
        submit.click()
        time.sleep(3)
        return browser.page_source

        # source_list=[]
        # flag=True
        # while flag:
        #     try:
        #         next=wait.until(EC.presence_of_element_located((By.XPATH,"//div[@class='m-page']//a[@class='page-link']")))
        #         source=browser.page_source
        #         source_list.append(source)
        #         next.click()
        #     except TimeoutException:
        #         source_list.append(browser.page_source)
        #         flag=False

    # except TimeoutException:
    #     get_page(fromCity,toCity,dateTime)

def parse_page(page):
    html=etree.HTML(page)
    lis=html.xpath('//*[@id="content"]//div[@class="mb-10"]/div[@class="m-airfly-lst"]//div[@class="b-airfly"]')
    #print(lis[0].xpath('./div[@class="e-airfly"]//text()'))
    for li in lis:
        item={}
        item['air']=li.xpath('./div[@class="e-airfly"]//div[@class="air"]//span//text()')[0]
        item['num']=li.xpath('./div[@class="e-airfly"]//div[@class="num"]//span//text()')
        item['fromTime']=li.xpath('./div[@class="e-airfly"]//div[@class="sep-lf"]//h2//text()')[0]
        item['toTime']=li.xpath('./div[@class="e-airfly"]//div[@class="sep-rt"]//h2//text()')[0]
        item['midTime']=li.xpath('./div[@class="e-airfly"]//div[@class="sep-ct"]//div[@class="range"]//text()')[0]
        item['fromAirport']=li.xpath('./div[@class="e-airfly"]//div[@class="sep-lf"]//p[@class="airport"]//text()')
        item['toAirport']=li.xpath('./div[@class="e-airfly"]//div[@class="sep-rt"]//p[@class="airport"]//text()')
        item['discount']=li.xpath('./div[@class="e-airfly"]//div[@class="vim"]//span//text()')[0]
        bes=li.xpath('./div[@class="e-airfly"]//span[@class="fix_price"]//b')
        if len(bes)>0:
            temp=bes[0].xpath('.//text()')
            for b in bes[1:]:
                text=b.xpath('./text()')[0]
                num=int(b.xpath('./@style')[0][18:20])//16
                temp[-num]=text
        else:
            temp=bes[0].xpath('.//text()')
        item['price']=''.join(temp)
        print(item)

def storage(item):
    db = pymysql.connect(host='localhost', user='root', password='aaaaaa', port=3306, db='qunar')
    cursor = db.cursor()
    sql = 'INSERT INTO ticket(air,num,fromTime,toTime,midTime,fromAirport,toAirport,discount,price) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    try:
        cursor.execute(sql, tuple(item.values()))
        db.commit()
    except:
        db.rollback()

if __name__=='__main__':
    page=get_page('上海','北京','2019-04-10')
    browser.quit()
    parse_page(page)