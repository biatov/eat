import json
with open('mobile.json') as f:
    data = json.load(f)


with open('new.json') as f:
    data0 = json.load(f)


subcategories = [d['subcategory'] for d in data]

from collections import Counter
a = [k + ' - ' + str(v) for k, v in Counter(subcategories).items()]
a.sort()

# for i in a:
#     print(i)





subcategories0 = [d['subcategory'] for d in data0]

b = [k + ' - ' + str(v) for k, v in Counter(subcategories0).items()]
b.sort()

# for i in b:
#     print(i)

for i, j in zip(a,b):
    one = int(i.split(' ')[-1])
    tw0 = int(j.split(' ')[-1])
    if one < tw0:
        print(i , j)