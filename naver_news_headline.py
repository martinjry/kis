from urllib.request import urlopen
import bs4
import re
url = "https://news.naver.com/"

html = urlopen(url)
bs_obj = bs4.BeautifulSoup(html.read(),"html.parser")

ul = bs_obj.find("ul",{"class":"hdline_article_list"})
lis = ul.findAll("li")
titles = [re.sub(r"[\n\t\s]*","",li.find("a").text) for li in lis]
#공백제거 하는 방법
for title in titles:
    print("오늘의 기사는:", title)
print("--------------")
