import math
import numpy as np
import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
rf=0.02
cr=1
coupon=200
rd=0.1
def putcallred(spot_price):
    red=spot_price*1.1
    putcall=spot_price*1.09
    return red,putcall
def stock_list(company_code):
    close_price=[]
    for page in range(1,10):
        url = "https://finance.naver.com/item/sise_day.nhn?code={}&page=".format(company_code)+ str(page)
        result = requests.get(url)
        bs_obj = BeautifulSoup(result.content,"html.parser")
    #     print(bs_obj)
        days = bs_obj.findAll("span",{"class":"tah p10 gray03"})
        close_prices = bs_obj.findAll("span",{"class":"tah p11"})
    #     print(close_prices)
        close = 1
        for day in days:
            prices=close_prices[close].text.replace(",","")
            close_price.append(int(prices))
            day=day.text
            close = close + 5#웹데이터 구조가 td*5구조임
    return close_price
def stock_stochastic(close_price):
    for i in range(close_price.count(0)):#0인 row없애기
        close_price.remove(0)
    rt=[]
    for i in range(len(close_price)-1):
        day_price= close_price[i]
        ex_price=close_price[i+1]
        rt_price=np.log(day_price/ex_price)
        rt.append(round(rt_price,2))
    mean=np.mean(rt)#일별평균
    variance =np.var(rt) # 분산
    sigma=np.std(rt) # 표준편차
    u=math.exp(sigma)
    d=1/u
    p = (1+rf-d)/(u-d)
    return close_price[0],u,d,p,mean,sigma
#[주가, VE,VB,HV,V]
def stock_matrix(spot_price,maturity,u,d):
    s = []
    for i in range(maturity):
        s1=[]
        for j in range(0,i+1):
            stock_spread = round(spot_price*(u**(i-j))*(d**j),2)
            s1.append({'노드':(i,j),'주가': stock_spread, '지분가치': None, '부채가치': None, '전환사채가치': None, '보유가치': None, '전환여부': None, '전략': None})
        s.append(s1)

    return s
def set_maturity_matrix(s,maturity,putcall_maturity,red,putcall):
    for i in range(maturity):
        if s[maturity-1][i]['주가']*cr>red:
            s[maturity-1][i]['지분가치']=s[maturity-1][i]['주가']*cr
            s[maturity-1][i]['부채가치']=0
            s[maturity-1][i]['전환사채가치']=s[maturity-1][i]['지분가치']+s[maturity-1][i]['부채가치']
            s[maturity-1][i]['전환여부']=1
            s[maturity-1][i]['전략']="conversion"
        else:
            s[maturity-1][i]['지분가치']=0
            s[maturity-1][i]['부채가치']=red
            s[maturity-1][i]['전환사채가치']=s[maturity-1][i]['지분가치']+s[maturity-1][i]['부채가치']
            s[maturity-1][i]['전환여부']=0
            if (maturity)==(putcall_maturity):
                s[maturity-1][i]['전략']="put or call"
                s[maturity-1][i]['부채가치']=putcall
            else:
                s[maturity - 1][i]['부채가치'] = red
                s[maturity-1][i]['전략']="redemtion"
    return s
def hv_set_matrix(s,maturity,putcall_maturity,p,red,putcall):
#     '주가''지분가치''부채가치''전환사채가치'=v,'보유가치'=hv,'전환여부''전략'
    for i in range(maturity-2,putcall_maturity-1,-1):#만기와 putcall기간 사이 구하기,
        for j in range(i+1):
            s[i][j]['보유가치']=(p*s[i+1][j]['지분가치']+(1-p)*s[i+1][j+1]['지분가치'])/(1+rf)+(p*s[i+1][j]['부채가치']+(1-p)*s[i+1][j+1]['부채가치'])/(1+rd)+coupon
            if max(s[i][j]['보유가치'],s[i][j]['주가']*cr)==s[i][j]['주가']*cr:
                s[i][j]['지분가치']=s[i][j]['주가']*cr
                s[i][j]['부채가치']=0
                s[i][j]['전환사채가치']=s[i][j]['지분가치']+s[i][j]['부채가치']
                s[i][j]['전환여부']=1
                s[i][j]['전략']='conversion'
            elif max(s[i][j]['보유가치'],s[i][j]['주가']*cr)==s[i][j]['보유가치']:
                s[i][j]['지분가치']=(p*s[i+1][j]['지분가치']+(1-p)*s[i+1][j+1]['지분가치'])/(1+rf)
                s[i][j]['부채가치']=(p*s[i+1][j]['부채가치']+(1-p)*s[i+1][j+1]['부채가치'])/(1+rd)+coupon
                s[i][j]['전환사채가치']=s[i][j]['지분가치']+s[i][j]['부채가치']
                s[i][j]['전환여부']=0
                s[i][j]['전략']='holding'
    for i in range(putcall_maturity-1,-1,-1):#putcall부터 0시점까지
        for j in range(i+1):
            if putcall_maturity-1==i:
                s[i][j]['보유가치']=(p*s[i+1][j]['지분가치']+(1-p)*s[i+1][j+1]['지분가치'])/(1+rf)+(p*s[i+1][j]['부채가치']+(1-p)*s[i+1][j+1]['부채가치'])/(1+rd)+coupon
                if max(s[i][j]['보유가치'],s[i][j]['주가']*cr,putcall)==s[i][j]['주가']*cr:
                    s[i][j]['지분가치']=s[i][j]['주가']*cr
                    s[i][j]['부채가치']=0
                    s[i][j]['전환사채가치']=s[i][j]['지분가치']+s[i][j]['부채가치']
                    s[i][j]['전환여부']=1
                    s[i][j]['전략']='conversion'
                elif max(s[i][j]['보유가치'],s[i][j]['주가']*cr,putcall)==s[i][j]['보유가치'] and s[i][j]['주가']*cr<putcall:
                    s[i][j]['지분가치']=0
                    s[i][j]['부채가치']=putcall
                    s[i][j]['전환사채가치']=s[i][j]['지분가치']+s[i][j]['부채가치']
                    s[i][j]['전환여부']=0
                    s[i][j]['전략']='put'
                elif max(s[i][j]['보유가치'],s[i][j]['주가']*cr,putcall)==s[i][j]['보유가치']:
                    s[i][j]['지분가치']=(p*s[i+1][j]['지분가치']+(1-p)*s[i+1][j+1]['지분가치'])/(1+rf)
                    s[i][j]['부채가치']=(p*s[i+1][j]['부채가치']+(1-p)*s[i+1][j+1]['부채가치'])/(1+rd)+coupon
                    s[i][j]['전환사채가치']=s[i][j]['지분가치']+s[i][j]['부채가치']
                    s[i][j]['전환여부']=0
                    s[i][j]['전략']='holding'
                elif max(s[i][j]['보유가치'],s[i][j]['주가']*cr,putcall)==putcall:
                    s[i][j]['지분가치']=0
                    s[i][j]['부채가치']=putcall
                    s[i][j]['전환사채가치']=s[i][j]['지분가치']+s[i][j]['부채가치']
                    s[i][j]['전환여부']=0
                    s[i][j]['전략']='put'
            else:
                s[i][j]['보유가치']=(p*s[i+1][j]['지분가치']+(1-p)*s[i+1][j+1]['지분가치'])/(1+rf)+(p*s[i+1][j]['부채가치']+(1-p)*s[i+1][j+1]['부채가치'])/(1+rd)+coupon
                if max(s[i][j]['보유가치'],s[i][j]['주가']*cr)==s[i][j]['주가']*cr:
                    s[i][j]['지분가치']=s[i][j]['주가']*cr
                    s[i][j]['부채가치']=0
                    s[i][j]['전환사채가치']=s[i][j]['지분가치']+s[i][j]['부채가치']
                    s[i][j]['전환여부']=1
                    s[i][j]['전략']='conversion'
                elif max(s[i][j]['보유가치'],s[i][j]['주가']*cr)==s[i][j]['보유가치']:
                    s[i][j]['지분가치']=(p*s[i+1][j]['지분가치']+(1-p)*s[i+1][j+1]['지분가치'])/(1+rf)
                    s[i][j]['부채가치']=(p*s[i+1][j]['부채가치']+(1-p)*s[i+1][j+1]['부채가치'])/(1+rd)+coupon
                    s[i][j]['전환사채가치']=s[i][j]['지분가치']+s[i][j]['부채가치']
                    s[i][j]['전환여부']=0
                    s[i][j]['전략']='holding'

    return s
def stock_calculate(spot_price,maturity,putcall_maturity,u,d,p,red,putcall):
    s= stock_matrix(spot_price,maturity,u,d)#s로 주가 2차원 리스트로 추출
    s= set_maturity_matrix(s,maturity,putcall_maturity,red,putcall)
    # print("set_maturity_matrix",s)
    s=hv_set_matrix(s,maturity,putcall_maturity,p,red,putcall)
    # s=total_set_matrix(s,s3,maturity)
    return s
def matrix_excel2(s,maturity):
    node = []
    for i in range(maturity):
        node2=[]
        for j in range(i+1):
            node2=node2+list(s[i][j].values())
        node.append(node2)
    return node
