# This Python file uses the following encoding: utf-8
          
import requests
from datetime import datetime, timedelta, date
from bs4 import BeautifulSoup
import re

url1 = 'https://ibank.takarekpont.hu/eib/loginpage.hu.html/'
url = 'https://ibank.takarekpont.hu/eib/login'
year = 2016
user = ''
passwd = ''


def data2dict(data):
    newdata = dict()
    data = data.split("&")
    for value in data:
        key, value = value.split("=")
        newdata.update({key: value})
    return newdata
        
r = requests.Session()
s = r.get(url1)
jar = s.cookies
soup = BeautifulSoup(s.text)
inputs = soup.find_all('input', attrs={'name':'pageid', 'type':'hidden'})

for inputfield in inputs:
    pageid = inputfield.get('value')

data = "pageid={}&lang=hu&cgcode=&group=&user={}&uid={}&pwd={}&B1=Bejelentkez%E9s".format(pageid, user, user, passwd)
values = data2dict(data)
print values
s = r.post(url, data=values)
s = r.get('https://ibank.takarekpont.hu/eib/getstatementform/pdf')


for i in range(1,13):
    print i
    if i == 12:
        fromdate = str(date(year,i,01)).replace('-','.')
        todate = str(date(year+1,01,01) - timedelta(days=1)).replace('-','.')

    else:
        fromdate = str(date(year,i,01)).replace('-','.')
        todate = str(date(year,i+1,01) - timedelta(days=1)).replace('-','.')
        print fromdate, todate
    data = "pageid={}&datelist=ok&type=PDF&from={}&to={}&OK=Rendben".format(pageid, fromdate, todate)

    url = 'https://ibank.takarekpont.hu/eib/getstatement'
    s = r.post(url, data=data2dict(data))

    pattern = 'cO3\(\'(.*?)\''
    matches = re.findall(pattern, s.text)
    for match in matches:
        tdate = str(match)
        tdatefield = str(date(int(tdate[:4]), int(tdate[4:6]), int(tdate[6:8]))).replace('-','.')
        fromdate = fromdate.replace('.','')
        todate = todate.replace('.','')
        print tdate, tdatefield
        data = "pageid={}&datelist_back=ok&type=PDF&from={}&to={}&OK=Rendben&date={}&date_field={}".format(pageid, fromdate, todate, tdate, tdatefield)
        print data
        s = r.post('https://ibank.takarekpont.hu/eib/getstatement', data=data2dict(data))
        dlurl = '/eib/getpdfstatement/5170020310012772/statement_{}_5170020310012772.pdf'.format(tdatefield)
        s = r.get('https://ibank.takarekpont.hu' + dlurl, stream=True)
        local_filename = 'statement_{}_5170020310012772.pdf'.format(tdatefield)
        with open(local_filename, 'wb') as f:
            for chunk in s.iter_content(chunk_size=1024):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    #f.flush() commented by recommendation from J.F.Sebastian
        print local_filename
