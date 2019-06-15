import degrees
from datetime import datetime

t = ["2019-06-08T05:55:36.205Z", "2019-06-08T02:55:36.205Z"]

l = [-97.504585270000, -97.504585270000]

x = (degrees.getCorrespondingTime(l, t))

hr = str(x[:])[11:13]

#m = degrees.findMonth(x)
print(x[0])

print(hr)