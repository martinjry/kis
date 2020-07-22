import requests
import pandas as pd #테이블형 데이터
from io import BytesIO #byte형 자료
from bs4 import BeautifulSoup
import re
import csv
from urllib.request import urlopen
import os
pd.set_option('display.max_row', 500)
pd.set_option('display.max_columns', 100)

def company_name_upper(company_name):
    company_name = company_name.upper()
    return company_name
def company_list():#종목코드 다운로드
    stock_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0]
    return stock_df
def set_code_excel(stock_df):
    stock_df.종목코드=stock_df.종목코드.map('{:06d}'.format)# 종목코드 0없어지는 현상 막기
    return stock_df
# 회사이름으로 종목코드 알아내기 함수
def get_company_code(company_name,stock_df):
    company_name = stock_df[(stock_df['회사명']==company_name)]
    company_code = company_name['종목코드'].values[0]
    return company_code
def company_dir(company_name):
    path = './{}'.format(company_name)
    os.makedirs(path, exist_ok=True)
# 종목코드와 인증키로 해당 종목 사업보고서 불러오기

def find_excel_darts(crtfc_key,company_code,user_agent):
    dart = 'https://opendart.fss.or.kr/api/list.xml?crtfc_key={}&page_count=100&corp_code={}&bgn_de=19990101&pblntf_detail_ty=A001&pblntf_detail_ty=A002&pblntf_detail_ty=A003'.format(crtfc_key,company_code)
    dart_result = requests.get(dart, headers={"user-agent": user_agent})
    dart_web = dart_result.content.decode('utf-8')
    rcept_nos  = re.findall(r"<rcept_no>(.*?)</rcept_no>",dart_web)
    report_nm_periods=re.findall(r"<report_nm>(.*?)</report_nm>",dart_web)
    return rcept_nos,report_nm_periods
def find_dcm_no(rcept_nos):
    dcm_no_list = []
    for rcept_no in rcept_nos[:5]:#5개만 하도록
        dcm_result = requests.get('http://dart.fss.or.kr/dsaf001/main.do?rcpNo={}'.format(rcept_no))
        web_dcm=dcm_result.content.decode('utf-8')
        dcm_no = re.findall(r"{}', '(.*?)',".format(rcept_no),web_dcm)[0]
        dcm_no_list.append(dcm_no)
    return dcm_no_list


def download_excel(rcept_no, dcm_no, period, company_name,user_agent):
    url = "http://dart.fss.or.kr/pdf/download/excel.do?rcp_no={}&dcm_no={}&lang=ko".format(rcept_no, dcm_no)
    result = requests.get(url, headers={"user-agent": user_agent})
    table = BytesIO(result.content)
    pockets = ["연결 재무상태표", "연결 포괄손익계산서", "연결 자본변동표", "연결 현금흐름표"]

    for pocket in pockets:
        corporation = pd.read_excel(table, sheet_name=pocket, skiprows=1)
        print(corporation)
        print("-----------------------")
        corporation.to_csv("{}\{}_{}_{}.csv".format(company_name, str(period), company_name, pocket), encoding="euc-kr")
def setexcellist():
    stock_asset = pd.DataFrame(columns=['0', '1'])
    stock_income = pd.DataFrame(columns=['0', '1'])
    stock_cash = pd.DataFrame(columns=['0', '1'])
    return stock_asset,stock_income,stock_cash
def mergeexcel(asset1,asset2):
    asset1 = pd.merge(asset1, asset2, on="0", how="outer")
    return asset1
def download_excel_total(rcept_no, dcm_no, period, company_name,user_agent):
    url = "http://dart.fss.or.kr/pdf/download/excel.do?rcp_no={}&dcm_no={}&lang=ko".format(rcept_no, dcm_no)
    result = requests.get(url, headers={"user-agent": user_agent})
    table = BytesIO(result.content)
    pockets = ["연결 재무상태표", "연결 포괄손익계산서", "연결 자본변동표", "연결 현금흐름표"]
    col = []
    asset = pd.DataFrame(columns=['0', '1'])
    income = pd.DataFrame(columns=['0', '1'])
    for pocket in pockets:
        corporation = pd.read_excel(table, sheet_name=pocket, skiprows=3)

        for i in range(0, len(corporation.columns)):#각 보고서에 맨앞컬럼이 최근의 정보이기에 그것만 추출함.
            col.append(str(i))
        if pocket == "연결 재무상태표":
            corporation.columns = col
            asset = corporation.loc[:, '0':'1']

        if pocket == "연결 포괄손익계산서":
            corporation.columns = col
            # corporation = corporation.drop(corporation.index[7:15], axis=0)
            # 위에 버전은 merge과정에서 삼성전자 기준 만들었음
            # 밑에 버전은 각 기업별로 당기순이익 표현 방식이 달라 만들었음.
            # corporation=corporation.loc[corporation['0'].str.contains('분기순이익',na=False)|corporation['0'].str.contains('당기순이익',na=False)|corporation['0'].str.contains('반기순이익',na=False),:]
            #최종버전은 지분이 들어간 부분만 제거하면 된다는 계산이 섰음.
            corporation = corporation.loc[corporation['0'].str.contains('지분') == False]
            income = corporation.loc[:, '0':'1']
        if pocket == "연결 현금흐름표":
            corporation.columns = col
            # corporation = corporation.drop(corporation.index[7:15], axis=0)
            cash = corporation.loc[:, '0':'1']


        # samsung.to_csv("{}_{}_{}.csv".format(company_name, str(period), pocket), encoding="euc-kr")#개별기간 재무제표 동일 패스에 저장
        col.clear()
    return asset, income, cash
def extract_income(period,company,report_nm_periods):#단일 보고서만
    match_day = []
    for report_period in report_nm_periods:
        if period in report_period:
            match_day.append(report_period)
    income_df = pd.read_csv('{}\{}_{}_연결 포괄손익계산서.csv'.format(company,match_day[0],company),encoding='euc-kr')
    column = []
    for i in range(len(income_df.columns)):
        column.append("{}".format(i))
    income_df.columns = column
    incomes= income_df.loc[income_df['1'].str.contains('분기순이익',na=False)|income_df['1'].str.contains('당기순이익',na=False)|income_df['1'].str.contains('반기순이익',na=False)]
    count = income_df[income_df['1']=='(단위 : 백만원)']
    income =int(incomes['2'].values[0])
    if count['1'].values[0]=='(단위 : 백만원)':
        income =int(incomes['2'].values[0])*1000000
    print(income)
    return income
def extract_incomes(report_nm_periods,company):#여러개 보고서
    income =[]
    for period in report_nm_periods[:5]:
        income_df = pd.read_csv('{}\{}_{}_연결 포괄손익계산서.csv'.format(period,company),encoding='euc-kr')
        income_df.columns = ['0','1','2','3','4','5']
        incomes= income_df.loc[income_df['1'].str.contains('분기순이익',na=False)|income_df['1'].str.contains('당기순이익',na=False)|income_df['1'].str.contains('반기순이익',na=False)]
        income=int(incomes['2'].values[0])
        print(income)

def extract_stock_count(rcept_no, dcm_no, eleld, offset, length):
    stock = requests.get("http://dart.fss.or.kr/report/viewer.do?rcpNo={}&dcmNo={}&eleId={}&offset={}&length={}&dtd=dart3.xsd".format(rcept_no, dcm_no, eleld, offset, length))
    stock1 = BeautifulSoup(stock.content, 'html.parser')
    stock2 = stock1.findAll('tbody')
    stock3 = stock2[1].findAll('tr')[7]
    stock_total = int(stock3.findAll('td')[3].text.replace(',', ''))
    return stock_total
def connect_stock_count(rcept_no):
    web_code1 = requests.get('http://dart.fss.or.kr/dsaf001/main.do?rcpNo={}'.format(rcept_no)).text
    web_code = web_code1.replace("\n","")
    web_code = web_code.replace("\\","")
    texts = re.findall('주식의 총수(.*?);',web_code)
    text=""
    for text in texts:
        text = text+text
    web_code = text.replace("\t","")
    web_code = web_code.replace("\'","")
    dcm_no = re.findall(r"{}, (.*?),".format(rcept_no),web_code)
    eleld = re.findall(r"{}, (.*?),".format(dcm_no[0]),web_code)
    offset = re.findall(r"{}, (.*?),".format(eleld[0]),web_code)
    length = re.findall(r"{}, (.*?),".format(offset[0]),web_code)
    return dcm_no,eleld,offset,length
