from kislib.T_Fandhull import stock_list
from kislib.T_Fandhull import stock_stochastic
from kislib.dart import company_list
from kislib.dart import set_code_excel
from kislib.dart import get_company_code
import numpy as np
import matplotlib.pyplot as plt
import math
from scipy.stats import norm
from tabulate import tabulate
#종목선정하고 spot_price 및 90일 평균, 변동성 가져오기
company_name='SK하이닉스' #ui에서 input값으로 가져오기
stock_df=company_list()#종목정보 가져오기
stock_df=set_code_excel(stock_df)#종목코드 다운로드 및 종목코드 0없어지는 현상 제거
company_code = get_company_code(company_name,stock_df)#입력한 종목이름의 종목코드 가져오기
close_price=stock_list(company_code)
close_price[0],u,d,p,mean,sigma=stock_stochastic(close_price)

#위험자산 구성
T=1
N=10000
st = close_price[0]*np.exp((mean-0.5*sigma**2)*T+sigma*np.sqrt(T)*np.random.randn(N))
# plt.hist(st,bins=50)
# plt.xlabel('price at maturity')
# plt.ylabel('frequency')
# plt.show() #로그정규분포 skweed positive
#VaR
var_90 = norm.ppf(1-0.9,mean,sigma)
var_95 = norm.ppf(1-0.95,mean,sigma)
var_99 = norm.ppf(1-0.99,mean,sigma)
print(tabulate([['90%',var_90],['95%',var_95],['99%',var_99]],headers=['confidence level','value at risk']))

#몬테카를로
D = 252
dt = T/D
s = np.zeros((D+1,N))
s[0] = close_price[0]
#줄(일) 단위 행렬계산
for t in range(1,D+1):
    s[t] = s[t-1]*np.exp((mean-0.5*sigma**2)*dt+sigma*np.sqrt(dt)*np.random.randn(N))
plt.plot(s[:,:10000])#모든 시나리오 출력
plt.xlabel('day')
plt.ylabel('price')
plt.grid(True)
plt.show()
