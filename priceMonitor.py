#coding=utf-8
import pdb
import time
import datetime
import random as rd
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import parseaddr, formataddr
from email import encoders
from email.mime.multipart import MIMEMultipart
import requests
from bs4 import BeautifulSoup as bs



def getPrice(url):
    myHeaders={
        'Host': 'www.amazon.fr',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch, br',
        'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh-TW;q=0.4'
        }

    r= requests.get(url,timeout=5,headers=myHeaders)


    soup = bs(r.content)
    priceSpan=soup.findAll(id="priceblock_ourprice")
    if len( priceSpan)>1:
        print 'find more than one results.'
        
    priceString= priceSpan[0].getText()
    commaIndex=priceString.index(",")
    return float(priceString[4:commaIndex]+"."+priceString[commaIndex+1:])

def getNextTime(gap):
    timeNow=time.time()
    rd.seed()
    adj=rd.randint(0,3*gap)
    adj=adj-gap+10
    print 'time gap now is:',adj+gap
    return timeNow+adj+gap


def getNum(priceString):
    return float(priceString) 

def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr(( \
        Header(name, 'utf-8').encode(), \
        addr.encode('utf-8') if isinstance(addr, unicode) else addr))

def sendmail(receivers,subject,times,prices):
    sender = 'shinsyzgz@sohu.com'
    size=len(prices)

    msgString=('From: %s\r\nTo: %s\r\n\n'%(sender, ','.join(receivers)))

    msgString=msgString+'Current price is:\n\n\t\t\t%s\n\nPrice history for this day until now is shown below.\n\n'%(prices[size-1])

    for i in range(size-1, -1,-1):
        msgString=msgString+'\tTime:\t%s\t\tPrice:\t%s\n'%(times[i],prices[i])


    message = MIMEText(msgString, 'plain', 'utf-8')
    message['From'] =_format_addr( "Guangzhi ZHANG<%s>"%(sender))
    message['To'] = _format_addr("To Whom It May Concern<%s>"%(','.join(receivers)))

    message['Subject'] = subject

    host="smtp.sohu.com"
    user="shinsyzgz@sohu.com"
    pwd="881028zgz"
    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(host,25)
        smtpObj.login(user,pwd)
        smtpObj.sendmail(sender, receivers, message.as_string())
        print "result sent to",receivers 
    except :
        print "sth. wrong when sending email."
        #raise


if __name__=='__main__':
    alertPrice=410
    timeGap=1800
    receivers=['luochenqu@foxmail.com','shinsyzgz@163.com','shinsy@foxmail.com']
    url="https://www.amazon.fr/dp/B00U654VS6/ref=cm_sw_r_other_apa_E6ryxbFTJT0XP"
    timeStamps=[]
    priceRecords=[]
    nextTime=0
    maxRecords=50
    

    while True:
        if time.time()>nextTime:
            nextTime=getNextTime(timeGap)
            priceNow=getPrice(url)
            timeStamps.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            priceRecords.append(priceNow)
            if getNum(priceNow)<=alertPrice:
                sendmail(receivers,'Price Dropped to %d!'%(getNum(priceNow)),timeStamps,priceRecords)

        hourNow=int(datetime.datetime.now().strftime("%H"))

        if hourNow==13 or hourNow==21: 
            sendmail(receivers,'daily price report',timeStamps,priceRecords)
            if len(priceRecords)>maxRecords:
                priceRecords=priceRecords[-maxRecords:]
                timeStamps=timeStamps[-maxRecords:]

        time.sleep(10)
        print 'still working... current time is %s'%(datetime.datetime.now().strftime("%H:%M:%S"))



