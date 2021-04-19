import re

reg = re.compile("(.+) (\d+)")
month = "harvest moon 30"
month_data = reg.match(month)
print(month_data.groups())
print(month_data[0])
print(month_data[1])
print(month_data[2])

#p = re.compile(r'\W+')
#print(p.split('This is a test, short and sweet, of split().'))