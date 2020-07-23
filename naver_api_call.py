from kislib.naver_api_caller import get1000Result
import json
list = []
result = get1000Result("채권")
result2 = get1000Result("부동산")
list = list + result + result2

file = open("./realestate.json","w+")
file.write(json.dumps(list))
