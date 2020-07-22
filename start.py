from kislib.T_Fandhull import stock_list
from kislib.T_Fandhull import stock_stochastic
from kislib.T_Fandhull import stock_matrix
from kislib.T_Fandhull import set_maturity_matrix
from kislib.T_Fandhull import hv_set_matrix
from kislib.T_Fandhull import stock_calculate
from kislib.T_Fandhull import putcallred
from kislib.T_Fandhull import matrix_excel2
from kislib.dart import company_list
from kislib.dart import set_code_excel
from kislib.dart import get_company_code
from kislib.dart import company_name_upper
import pandas as pd
company_name ="sk하이닉스"#종목이름 입력값으로 종목코드 추출하는 간단한 UI제작 예정
company_name= company_name_upper(company_name)
stock_df = company_list()
set_code_excel(stock_df)#종목코드 0 없애기
company_code=get_company_code(company_name,stock_df)

close_price=stock_list(company_code)

close_price[0],u,d,p,mean,sigma=stock_stochastic(close_price)

red,putcall = putcallred(close_price[0])#당연히 spot_price를 상회하는 금액
maturity=10 #노드 갯수
putcall_maturity = 5#풋콜 가능 노드 시점
print(close_price[0])
s=stock_calculate(close_price[0],maturity,putcall_maturity,u,d,p,red,putcall)#spot_price, maturity,putcall_maturity,u,d,p

# s=stock_calculate(10000,4,3,1.49182,0.67032,0.42566)
print(s[0])
# s.to_csv("티에프.csv", encoding="euc-kr")
###엑셀 추출하고자 할때
node = matrix_excel2(s,maturity)
# df=matrix_excel2(s,maturity) #len 오류가 있다고 해서 다시작성 쥬피터에서 돌아감
tree = pd.DataFrame(node)
tree = tree.T
print(tree)
tree.to_csv("tf.csv",encoding='euc-kr')