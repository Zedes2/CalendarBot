import re

reg = re.compile("(.+) (\d+)")
month = "harvest moon 30"
monthData = reg.match(month)
print(monthData.groups())
print(monthData[0])
print(monthData[1])
print(monthData[2])

#p = re.compile(r'\W+')
#print(p.split('This is a test, short and sweet, of split().'))