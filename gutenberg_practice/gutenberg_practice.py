# 操作 browser 的 API
from selenium.webdriver.chrome.service import Service
from selenium import webdriver

# 處理逾時例外的工具
from selenium.common.exceptions import TimeoutException

# 面對動態網頁，等待某個元素出現的工具，通常與 exptected_conditions 搭配
from selenium.webdriver.support.ui import WebDriverWait

# 搭配 WebDriverWait 使用，對元素狀態的一種期待條件，若條件發生，則等待結束，往下一行執行
from selenium.webdriver.support import expected_conditions as EC

# 期待元素出現要透過什麼方式指定，通常與 EC、WebDriverWait 一起使用
from selenium.webdriver.common.by import By

# 強制等待 (執行期間休息一下)
from time import sleep

# 執行 command 的時候用的
import os

# 匯入 regex 套件
import re

# 使用 requests 工具
import requests as req

# 使用 Beautiful Soup 抓取與解析網頁資料
from bs4 import BeautifulSoup as bs


# 遇到問題:
# 1) 如何過濾重複的文章
# 2) 出現難以處理的錯誤 ex.'臺灣通史\r唐山過海的故事'


folderPath = "content"
if not os.path.exists(folderPath):
    os.makedirs(folderPath)

# # 啟動瀏覽器工具的選項
# my_options = webdriver.ChromeOptions()
# # my_options.add_argument('--headless')  # 不開啟實體瀏覽器背景執行
# my_options.add_argument('--incognito')  # 開啟無痕模式
# my_options.add_argument("--disable-popup-blocking")  # 禁用彈出攔截
# my_options.add_argument("--disable-notifications")  # 取消 chrome 推播通知
# my_options.add_argument("--lang=zh-TW")  # 設定為正體中文
# my_options.add_experimental_option("detach", True)  # 讓瀏覽器不會自動關閉

# my_service = Service(executable_path = './chromedriver.exe')
# driver = webdriver.Chrome(
#     options = my_options,
#     service = my_service
#     )

# driver.get('https://www.gutenberg.org/browse/languages/zh')
# html = driver.page_source
# soup = bs(html, 'lxml')

# 目標網頁
url = 'https://www.gutenberg.org/browse/languages/zh'
# 用 requests 的 get 方法把網頁抓下來
res = req.get('https://www.gutenberg.org/browse/languages/zh')
# 指定 lxml 作為解析器
soup = bs(res.text, 'lxml')

# 建立空 list 來放所有目標網址和目標書名
list_book = []
list_bookname = []

# 控制生成文件的編號與對應的書本名稱
i = 1

# 取得首頁所有目標的元素 a
for a_book in soup.select('div.pgdbbylanguage li.pgdbetext a'):
    # 透過 class 名稱取得該屬性的屬性值，將完整網址存入 list 中
    regex = r'\b[\u4E00-\u9FFF]+.*\b'
    match = re.match(regex, a_book.text)

    # 對應到的值放入空 list 中
    if match != None:
        list_book.append("https://www.gutenberg.org" + a_book['href'])
        list_bookname.append(a_book.text)  

# 出現難以處理的錯誤，只好這樣 debug    
regex = r'臺灣通史\r唐山過海的故事'
change = re.sub(regex, '臺灣通史 唐山過海的故事 ', list_bookname[121])
list_bookname[121] = change

# 走訪每一個 a link，並印出網頁內文
for index, link_book in enumerate(list_book):
    res_book = req.get(link_book)
    soup_book = bs(res_book.text, 'lxml')

    # 判斷文件是否存在:
    # 存在的話就不讀取資料並返回迴圈讀取下一個網址
    # 不存在的話就讀取資料並生成文件
    if os.path.exists(f'content/[{i}]{list_bookname[i-1]}.txt'):
        print(f'[{i}]{list_bookname[i-1]} 已存在')
        i += 1
        continue
    else:
        # 進到下一層網頁，取得元素 a
        for a_content in soup_book.select('table.files tr.odd td.unpadded a'):
            # 判斷網址的名稱是否為目標
            regex = r'Plain Text UTF-8'
            match_UTF = re.match(regex, a_content.text)
            if match_UTF != None:
                res_content = req.get("https://www.gutenberg.org" + a_content['href'])
                # 指定回傳資料的編碼
                res_content.encoding = 'utf-8'
                soup_content = bs(res_content.text, 'lxml')

                # 到達最終層網頁，透過選擇所有屬性來取得文字內容
                content = soup_content.select_one('*').text
                # 利用正規表達式，篩選中文內容
                regex = r'\b[\u4E00-\u9FFF]+\W+\b'
                result = re.findall(regex, content)

                # 透過 with open 將內容寫出成 .txt 檔
                with open(f"content/[{i}]{list_bookname[i-1]}.txt", mode="x", encoding="utf-8") as file:
                    for str in result:
                        file.write(str)    
                    print(f'[{i}]{list_bookname[i-1]} 已完成')

                i += 1

                # 休眠
                sleep(3)





# # 單一爬取
# url = 'https://www.gutenberg.org/browse/languages/zh'
# res = req.get('https://www.gutenberg.org/browse/languages/zh')
# soup = bs(res.text, 'lxml')

# a_book = soup.select_one('div.pgdbbylanguage li.pgdbetext a[href="/ebooks/25557"]')
# res_book = req.get("https://www.gutenberg.org" + a_book['href'])
# soup_book = bs(res_book.text, 'lxml')

# a_content = soup_book.select('table.files tr.odd td.unpadded a')
# res_content = req.get("https://www.gutenberg.org" + a_content[2]['href'])
# res_content.encoding = 'utf-8'
# soup_content = bs(res_content.text, 'lxml')

# content = soup_content.select_one('*').text
# regex = r'\b[\u4E00-\u9FFF]+\W+\b'
# result = re.findall(regex, content)

# with open(f"data.txt", mode="w", encoding="utf-8") as file:
#     for str in result:
#         file.write(str)
# print("data 已完成")







# 關閉瀏覽器
# driver.quit()