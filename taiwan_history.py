from urllib3 import PoolManager, request
import json
#import plotly as plt
import ssl
import sys
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import pandas as pd

print(sys.version_info)

url=r'https://corona.lmao.ninja/v2/historical'

http=PoolManager()
r=http.request('GET',url)

data=json.loads(r.data)
taiwan=data[207]
#print (f'{data[207]}')
#print (taiwan['timeline'])
cases = taiwan['timeline']['cases']
deaths=taiwan['timeline']['deaths']
recovered = taiwan['timeline']['recovered']

df=pd.DataFrame.from_dict(taiwan['timeline'])
df['date']=df.index
#df.columns=['date','cases','deaths','recovered']
df['acc']=df['cases']-df['cases'].shift(1)
#df['date']=df[0].to_datetime(format='%m/%d/%Y')
df['date2']=pd.to_datetime(df['date'])

fig,ax1 = plt.subplots()
ax2=ax1.twinx()
ax1.scatter(x=df['date2'],y=df['acc'],alpha=0.5,marker='o',color='blue')
ax1.set_ylabel('new cases by day',color='blue')
ax2.scatter(x=df['date2'],y=df['cases'],marker='.',color='red')
ax2.set_ylabel('accumlate cases',color='red')
ax1.set_xlabel('Date')

print(type(df['date']))
ax1.xaxis.set_major_locator(mdates.DayLocator(interval=14))
ax1.xaxis.set_minor_locator(mdates.DayLocator(interval=3))
ax1.xaxis.grid(True,which='both')
ax1.set_xticklabels(df['date2'],rotation=90)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
plt.title(f'COV-19, Taiwan\ndata from {url}')
plt.show()
