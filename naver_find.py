import requests
from urllib.parse import urlparse

keyword = "주식"
url = "https://openapi.naver.com/v1/search/blog?query=" + keyword # json 결과
result = requests.get(urlparse(url).geturl(),headers={"X-Naver-Client-Id":"iFsSyGdriWeXujQLvyjV",
                                                     "X-Naver-Client-Secret":"OEYR9FJXzW"})
json_obj = result.json()
print(json_obj)