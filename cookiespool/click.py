import requests
from hashlib import md5
import time
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import ActionChains

CHAOJIYING_USERNAME='flyingrogue'
CHAOJIYING_PASSWORD='ljb1994917..'
CHAOJIYING_SOFT_ID=893590
CHAOJIYING_KIND=9004

EMAIL='qwer'
PASSWORD='asdf'

class Chaojiying(object):
    def __init__(self,username,password,soft_id):
        self.username=username
        self.password=md5(password.encode('utf-8')).hexdigest()
        self.soft_id=soft_id
        self.base_params={
            'user':self.username,
            'pass2':self.password,
            'softid':self.soft_id,
        }
        self.headers={
            'Connection':'Keep-Alive',
            'User-Agent':'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0',
        }

    def post_pic(self,im,codetype):
        params={
            'codetype':codetype,
        }
        params.update(self.base_params)
        files={'userfile':('ccc.jpg',im)}
        r=requests.post('http://upload.chaojiying.net/Upload/Processing.php',data=params,files=files,headers=self.headers)
        return r.json()

    def report_erro(self,im_id):
        params={
            'id':im_id,
        }
        params.update(self.base_params)
        r=requests.post('http://upload.chaojiying.net/Upload/ReportError.php',data=params,headers=self.headers)
        return r.json()

class TestClick():
    def __init__(self,browser,wait):
        self.url='https://auth.geetest.com/login/'
        self.browser=browser
        self.wait=wait
        self.email = EMAIL
        self.password = PASSWORD
        self.chaojiying=Chaojiying(CHAOJIYING_USERNAME,CHAOJIYING_PASSWORD,CHAOJIYING_SOFT_ID)

    def __del__(self):
        self.browser.close()

    def get_geetest_botton(self):
        button=self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME,'geetest_radar_tip')))
        return button


    def get_img_element(self):
        img = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'geetest_widget')))
        return img

    def get_position(self):
        img=self.get_img_element()
        time.sleep(1)
        location=img.location
        print(location)
        size=img.size
        print(size)
        top,bottom,left,right=location['y'],location['y']+size['height'],location['x'],location['x']+size['width']
        return (top,bottom,left,right)

    def get_captcha(self):
        top,bottom,left,right=self.get_position()
        print('验证码位置',top,bottom,left,right)

        screenshot=self.browser.get_screenshot_as_png()

        screenshot=Image.open(BytesIO(screenshot))
        screenshot.save('capdsds.png')
        captcha=screenshot.crop((left,top,right,bottom))
        captcha.save('captcha.png')
        return captcha

    def get_points(self):
        image=self.get_captcha()
        bytes_array=BytesIO()
        image.save(bytes_array,format='PNG')
        result=self.chaojiying.post_pic(bytes_array.getvalue(),CHAOJIYING_KIND)
        print('识别结果',result)
        groups=result.get('pic_str').split('|')
        locations=[[int(number) for number in group.split(',')]for group in groups]
        return locations

    def touch_click_words(self,locations):
        for location in locations:
            ActionChains(self.browser).move_to_element_with_offset(self.get_img_element(),location[0],location[1]).click().perform()
            time.sleep(1)

    def touch_click_verify(self):
        button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_commit')))
        button.click()

    def open(self):
        self.browser.get(self.url)
        email=self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'input[type="email"]')))
        password=self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'input[type="password"]')))
        email.send_keys(self.email)
        password.send_keys(self.password)

    def is_success(self):
        try:
            return bool(WebDriverWait(self.browser,5).until(EC.presence_of_element_located((By.CLASS_NAME,'geetest_success_btn'))))
        except TimeoutException:
            return False

    def main(self):
        self.open()
        button = self.get_geetest_botton()
        button.click()
        locations=self.get_points()
        self.touch_click_words(locations)
        self.touch_click_verify()
        if self.is_success():
            print('success')
        else:
            print('fail')


if __name__=='__main__':
    # chrome_options=webdriver.ChromeOptions()
    # chrome_options.add_argument('--headless')
    browser=webdriver.Chrome()
    wait=WebDriverWait(browser,5)
    a=TestClick(browser,wait)
    a.main()



