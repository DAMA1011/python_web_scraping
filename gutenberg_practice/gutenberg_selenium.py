from pyautogui import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common import by
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import json, os, time, re
from pprint import pprint
from urllib import parse

# 隨機取得 User-Agent
from fake_useragent import UserAgent
ua = UserAgent(cache=True)
my_headers = {
    'user-agent': ua.random
}

# 建立資料夾
folderPath = 'contentse'
if not os.path.exists(folderPath):
    os.makedirs(folderPath)

# 設定 Chrome 瀏覽器開啟時的狀態
my_options = webdriver.ChromeOptions()
my_options.add_argument('--incognito')
my_options.add_argument('disable-popup-blocking')
my_options.add_argument(f'--user-agent={ua.random}')
my_options.add_experimental_option("detach", True)

# 設定 Chrome 的 WebDriver
my_service = Service(executable_path='./chromedriver.exe')

# 建立操控 Chrome 瀏覽器的變數
my_driver = webdriver.Chrome(
    options = my_options,
    service = my_service
)

url = 'https://www.gutenberg.org/browse/languages/zh'

list_book = []  # 第一頁中文書名及網頁連結

# 取得小說的主要連結
def getBooksName():
    # 走訪首頁
    my_driver.get(url)
    aFirstLinks = my_driver.find_elements(By.CSS_SELECTOR, 'div.pgdbbylanguage li.pgdbetext a')

    for a in aFirstLinks:
        regex = r'\b[\u4E00-\u9FFF]+.*\b'
        bookname = re.match(regex, a.get_attribute('innerText'))
        if bookname != None:
            list_book.append(a.get_attribute('innerText'))
    
def getContents():
    try:
        for i in range(200):

            my_driver.find_element(By.LINK_TEXT, list_book[i]).click()
            # sleep(2)

            my_driver.find_element(By.LINK_TEXT, 'Plain Text UTF-8').click()
            # sleep(2)

            # 寫入資料
            body = my_driver.find_element(By.CSS_SELECTOR, '*')
            content = body.get_attribute('innerText')
            
            regex = r'\b[\u4E00-\u9FFF]+\W+\b'
            result = re.findall(regex, content)

            title = re.sub(r'\n|:', ' ', list_book[i])

            with open(f'contentse/[{i+1}]{title}.txt', mode='w', encoding='utf-8') as file:
                for str in result:
                    file.write(str)      
                print(f'{[i+1]}{list_book[i]} 已完成')

            my_driver.get(url)
            # sleep(2)

    except TimeoutException:
        print('等待逾時!')

def close():
    my_driver.quit()

if __name__ == '__main__':
    time1 = time.time()
    getBooksName()
    getContents()
    close()
    print(f'執行總花費時間: {time.time() - time1}')