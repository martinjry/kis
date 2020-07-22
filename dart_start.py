from kislib.dart import company_list
from kislib.dart import set_code_excel
from kislib.dart import get_company_code
from kislib.dart import company_dir
from kislib.dart import find_excel_darts
from kislib.dart import find_dcm_no
from kislib.dart import download_excel
from kislib.dart import download_excel_total
from kislib.dart import extract_income
from kislib.dart import extract_incomes#기간별 eps,per를 구하기 위한 당기순이익 기간별 추출
from kislib.dart import extract_stock_count
from kislib.dart import connect_stock_count
from kislib.dart import setexcellist
from kislib.dart import mergeexcel
from kislib.dart import company_name_upper

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"
stock_df=company_list()#종목정보 가져오기
stock_df=set_code_excel(stock_df)#종목코드 다운로드 및 종목코드 0없어지는 현상 제거

company_name='sk하이닉스' #ui에서 input값으로 가져오기
report_day = '2019.03'#분기별로 적으면 됨 ui로 대체예정
company_name=company_name_upper(company_name)

company_code = get_company_code(company_name,stock_df)#입력한 종목이름의 종목코드 가져오기
company_dir(company_name)#리턴값없이 입력한 종목이름의 새폴더 만들기
crtfc_key = 'e31a7f481d4275bf5f187ca241d3f045e6a19f3b'#내 전용키
rcept_nos,report_nm_periods=find_excel_darts(crtfc_key,company_code,user_agent)
dcm_no_list = find_dcm_no(rcept_nos)#dcm_no을 추출

for period,rcept_no,dcm_no in zip(report_nm_periods,rcept_nos,dcm_no_list):#개별기업 폴더 내에 재무제표 엑셀 저장
    download_excel(rcept_no,dcm_no,period,company_name,user_agent)

stock_asset,stock_income,stock_cash =setexcellist()
for rcept_no, dcm_no, period in zip(rcept_nos, dcm_no_list, report_nm_periods):#분기별 재무,손익 합치기
    asset, income,cash = download_excel_total(rcept_no, dcm_no, period, company_name,user_agent)
    stock_asset=mergeexcel(stock_asset,asset)
    stock_income=mergeexcel(stock_income, income)
    stock_cash = mergeexcel(stock_cash, cash)
stock_asset.to_csv("{}_재무제표모음.csv".format(company_name),encoding="euc-kr")
stock_income.to_csv("{}_손익계산서모음.csv".format(company_name),encoding="euc-kr")
stock_cash.to_csv("{}_현금흐름표모음.csv".format(company_name),encoding="euc-kr")


term_income = extract_income(report_day,company_name,report_nm_periods)#단일 손익계산서 기를 엑셀로 다운로드
match_day = []
for report_period in report_nm_periods:
    if report_day in report_period:
        match_day.append(report_period)
extract_rcept_no = rcept_nos[report_nm_periods.index(match_day[0])]
dcm_no,eleld,offset,length=connect_stock_count(extract_rcept_no)
term_stock_count = extract_stock_count(extract_rcept_no,dcm_no[0],eleld[0],offset[0],length[0])
eps = term_income/term_stock_count
print("eps:",eps)