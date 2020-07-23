import pandas as pd
df = pd.read_json("./realestate.json")
#print(df.count())
# dfSum = df.groupby("bloggername").count()
# print(dfSum)
title  = df['title']
print(title)