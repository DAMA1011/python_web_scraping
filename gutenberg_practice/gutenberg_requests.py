import os, re, time
import requests as req
from bs4 import BeautifulSoup as bs

# 隨機取得 User-Agent
# from fake_useragent import UserAgent
# ua = UserAgent(cache = True)  # cache=True 表示從已經儲存的列表中提取
# my_headers = {
#     'user-agent': ua.random
# }

# 建立資料夾
folderPath = 'contentre'
if not os.path.exists(folderPath):
    os.makedirs(folderPath)

# 目標網頁
url = 'https://www.gutenberg.org/browse/languages/zh'

list_book = []  # 第一頁中文書名及網頁連結
list_content = []  # 第二頁網頁連結

# 1) 取得第一頁的所有中文書名連結
def getFirstLinks():
    # 用 requests 的 get 方法把網頁抓下來
    # resFirst = req.get(url, headers = my_headers)
    resFirst = req.get(url)
    # 指定 lxml 作為解析器
    soupFirst = bs(resFirst.text, 'lxml')

    # 取得第一頁所有連結的元素
    for aFirstLinks in soupFirst.select('div.pgdbbylanguage li.pgdbetext a'):
        # 篩選中文書名及處理例外符號
        regex = r'\b[\u4E00-\u9FFF]+.*\b'
        findall = re.findall(regex, aFirstLinks.text)
        for word in findall:
            sub = re.sub(r'\r|:', ' ', word)
        
        # 寫入第一頁中文書名及網頁連結
            list_book.append({
                'title': sub,
                'firstlink': 'https://www.gutenberg.org' + aFirstLinks['href'],
                'secondlink': []
                })

# 2) 取得第二頁的所有"Plain Text UTF-8"連結
def getSecondLinks():    
    for i in range(200):
        # 用 requests 的 get 方法把網頁抓下來
        # resSecond = req.get(list_book[i]['firstlink'], headers = my_headers)
        resSecond = req.get(list_book[i]['firstlink'])
        # 指定 lxml 作為解析器
        soupSecond = bs(resSecond.text, 'lxml')

        # 取得第二頁所有連結的元素
        for aSecondLinks in soupSecond.select('table.files  tr[about] td.noscreen'):

            # 篩選指定網址
            regex = r'\b.*txt\b'
            match = re.match(regex, aSecondLinks.text)

            # 寫入第二頁網頁連結
            if match != None:
                list_book[i]['secondlink'].append(aSecondLinks.text)

# 3) 取得所有"Plain Text UTF-8"連結內部的內容，並寫出成 .txt 檔案
def writeConten():
    for i in range(200):
        # 用 requests 的 get 方法把網頁抓下來
        # resContent = req.get(list_content[i], headers = my_headers)
        for link in list_book[i]['secondlink']:
            resContent = req.get(link)
            # 指定回傳資料的編碼
            resContent.encoding = 'utf-8'
            # 指定 lxml 作為解析器
            soupContent = bs(resContent.text, 'lxml')

            # 透過選擇所有屬性來取得文字內容
            content = soupContent.select_one('*').text
            # 篩選中文內容
            regex = r'\b[\u4E00-\u9FFF]+\W+\b'
            result = re.findall(regex, content)

            # 透過 with open 將內容寫出成 .txt 檔
            with open(f'contentre/[{i+1}]{list_book[i]["title"]}.txt', mode='w', encoding='utf-8') as file:
                for str in result:
                    file.write(str)
                print(f'[{i+1}]{list_book[i]["title"]} 已完成')

# 執行程序
if __name__ == '__main__':
    time1 = time.time()
    getFirstLinks()
    getSecondLinks()
    writeConten()
    print(f'執行總花費時間: {time.time() - time1}')  # 676 s