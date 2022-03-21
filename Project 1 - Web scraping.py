
import requests
from bs4 import BeautifulSoup as bs
import re
import pandas as pd
import time
import random

url= "https://www.moneydj.com/funddj/yb/YP301000.djhtm"   # MoneyDJ理財網 - 國內基金種類url

row_name = ["基金類型", "基金名稱", "基金統編", "手續費", "保管費"]   # 手續費,保管費 -> 單位(%)
manager_row_name = ["經理人姓名", "性別", "學歷"]

col_name = ["經理人", "時間", "期間(月)", "操作績效(%)", "台股績效(%)"]

def combine_url(fragmented_url):
    return "https://www.moneydj.com" + fragmented_url
def get_then_soup(full_url):
    return bs(requests.get(full_url).content, 'lxml')
def filter_new_line(st):
    return st != '\n'

all_categories_funds_a_tag_list = get_then_soup(url).find("div", class_="InternalSearch").find_all("a")   # 最後面可以加[:]，指定 從哪開始 & 到哪結束
for index, cat in enumerate(all_categories_funds_a_tag_list):     # cat(category)  ex: 指數型，科技類，全球市場，一般股票型...
    l = []
    i = 1
    same_cat_fund = get_then_soup(combine_url(cat['href'])).find("table", class_="t05").tbody.find_all("tr")
    for fund in same_cat_fund:   # (same_cat_fund, fund)  ex: (指數型,富邦臺灣中小A級動能50ETF基金)，(指數型,元大台灣高股息低波動ETF基金)
        soup_funda_data = get_then_soup(combine_url(get_then_soup(combine_url(fund.find("td", attrs={'myclass': 't3t1'}).a['href'])).find("div", class_="Tab-Less").find("li").a['href']))   # soup完的"基本資料"頁面
        funda_data_table = soup_funda_data.find("table", class_="t04")
        if funda_data_table.find(string=re.compile("基金統編")) != None:   # 這行是特例，因為要爬的某筆資料的html內容有問題。
            l1 = [funda_data_table.find(string=re.compile(name)).find_parent().find_next_sibling().get_text().strip() for name in row_name]
            #print(l1)
            managers_in_same_fund = soup_funda_data.find("table", class_="t01").find_all("tr")[2:]    # a list of "tr" tags   # 直接從第三格橫列(經理人姓名)開始，到最後一個經理人
            #print(managers_in_same_fund)
            if managers_in_same_fund[0].string != "查無資料":   # "歷任基金經理人" 表格要有資料才做下面動作
                for tr in managers_in_same_fund:   # 每一個tr代表一位經理人的橫列資料
                    manager_data_table = get_then_soup(combine_url(tr.find("td").a['href'])).find("table", class_="t03")
                    if manager_data_table != None:   # 有經理人的表格資料才做下面動作
                        if manager_data_table.find(string=re.compile("經理人姓名")) != None:   # 這行是特例，因為要爬的某筆資料的html內容有問題。
                            l2 = [manager_data_table.find(string=re.compile(name)).find_parent().find_next_sibling().get_text().strip() for name in manager_row_name]
                            #print(l2)
                            manager_one_row_data = list(filter(filter_new_line, list(tr)))[:-1]  # 利用 filter(function, iterable) 過濾掉不要的東西   # [:-1] 去除掉"現任基金"資料
                            l3 = [td.get_text().strip() for td in manager_one_row_data]
                            #print(l3)
                            l.append(l1 + l2 + l3)
                            print(l1 + l2 + l3)
        print(f"同一類別下，爬完第{i}筆")
        i += 1
        time_wait = random.randint(3, 10)
        print(f'Waiting {time_wait} seconds...')
        time.sleep(time_wait)
    output = pd.DataFrame(data=l, columns=row_name + manager_row_name + col_name)
    output.to_csv(f"C:/Users/曹仕依/Desktop/碩論/碩論/爬蟲- MoneyDJ/MoneyDJ_fund_data/fund_category{index}.csv", index=False, encoding='utf-8-sig')   # encoding='utf-8-sig'
    wait_time = random.randint(30, 40)
    print(f'\n\nWaiting {wait_time} seconds, then to next round!\n\n')
    time.sleep(wait_time)
