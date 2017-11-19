#!/usr/bin/env python
# This Python file uses the following encoding: utf-8
          
import requests
from datetime import datetime, timedelta, date
from bs4 import BeautifulSoup
import re

url1 = 'https://electra7.takinfo.hu/eib_ib_S1/loginpage.hu.html'
url = 'https://electra7.takinfo.hu/eib_ib_S1/login'
year = 2017
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
s = r.get('https://electra7.takinfo.hu/eib_ib_S1/getstatementform/pdf')


for i in range(1,13):
    print i
    if i == 12:
        fromdate = str(date(year,i,01)).replace('-','.')
        todate = str(date(year+1,01,01) - timedelta(days=1)).replace('-','.')

    else:
        fromdate = str(date(year,i,01)).replace('-','.')
        todate = str(date(year,i+1,01) - timedelta(days=1)).replace('-','.')
        print fromdate, todate
    data = {
        'pageid': pageid,
        'datelist': 'ok',
        'type': "PDF",
        'from': fromdate,
        'to': todate,
        'OK': 'Rendben'
    }
    url = 'https://electra7.takinfo.hu/eib_ib_S1/getstatement'
    s = r.post(url, data=data)
    soup = BeautifulSoup(s.text, 'lxml')
    #print soup.find_all('tr')
    matches = soup.find_all('tr', {"id" : re.compile('etktable_nodatelist.*')})
    print matches
    # continue
    if not matches:
        continue
    for match in matches:
        print match
        tdate = re.findall('date\',\'(.*?)\'', str(match))
        tdate = str(tdate[0])
        print tdate
        tdatefield = str(date(int(tdate[:4]), int(tdate[4:6]), int(tdate[6:8]))).replace('-','.')
        fromdate = fromdate.replace('.','')
        todate = todate.replace('.','')
        print tdate, tdatefield
        data =  {
            'pageid': pageid,
            'type': 'PDF',
            'from': fromdate,
            'to': todate,
            'OK': 'Rendben',
            'date': tdate,
            'sourcefile': '6665.pdfstmcat.xml',
            'nodatelist': None,
            'acc': None,
            'etk_table_nodatelist_itemcount': len(matches)
        }

        print data
        s = r.post('https://electra7.takinfo.hu/eib_ib_S1/getstatement', data=data)
        dlurl = '/eib_ib_S1/getpdfstatement/5170020310012772/statement_{}_5170020310012772.pdf'.format(tdate)
        s = r.get('https://electra7.takinfo.hu' + dlurl, stream=True)
        print dlurl
        local_filename = 'statement_{}_5170020310012772.pdf'.format(tdate)
        with open(local_filename, 'wb') as f:
            for chunk in s.iter_content(chunk_size=1024):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    #f.flush() commented by recommendation from J.F.Sebastian
        print local_filename
