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
    myHeaders1={
        'Host': 'www.amazon.fr',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch, br',
        'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh-TW;q=0.4'
        }
    myHeaders2={
        'Host': 'www.amazon.fr',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/601.6.17 (KHTML, like Gecko) Version/9.1.1 Safari/601.6.17',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch, br',
        'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh-TW;q=0.4'
        }  

    headerList=[myHeaders1,myHeaders2]
    headerChosen=rd.randint(0,1)
    print 'using header:', headerChosen

    r= requests.get(url,timeout=10,headers=headerList[headerChosen])


    soup = bs(r.content)
    priceSpan=soup.findAll(id="priceblock_ourprice")
    if len( priceSpan)>1:
        print 'find more than one results.'
    if len(priceSpan)==0:
	    print "didn't find price information"
	    return -1
    priceString= priceSpan[0].getText()
    print priceString
    commaIndex=priceString.index(",")
    return float(priceString[4:commaIndex]+"."+priceString[commaIndex+1:])


def getNextTime(gap):
    timeNow=time.time()
    rd.seed()
    adj=rd.randint(0,4*gap)
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
    sent=False
    count=0
    while not sent:
        count=count+1
        if count>10:
            print 'ERROR: FAILED TO SEND EMAIL.'
            break
        try:
            smtpObj = smtplib.SMTP()
            smtpObj.connect(host,25)
            smtpObj.login(user,pwd)
            smtpObj.sendmail(sender, receivers, message.as_string())
            print "result sent to",receivers 
            sent=True
        except :
            print "sth. wrong when sending email. retrying..."
            sent=False
            time.sleep(rd.randint(5,20))
            #raise


if __name__=='__main__':
    alertPrice=410
    timeGap=10000
    receivers=['luochenqu@foxmail.com','zgz07ie@gmail.com']
    url="https://www.amazon.fr/dp/B00U654VS6/ref=cm_sw_r_other_apa_E6ryxbFTJT0XP"
    url2="www.baidu.com"
    timeStamps=[]
    priceRecords=[]
    nextTime=0
    maxRecords=50
    daily=False
    

    while True:
        if time.time()>nextTime:
            nextTime=getNextTime(timeGap)
            priceNow=getPrice(url)
            timeStamps.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            priceRecords.append(priceNow)
            if getNum(priceNow)<=alertPrice:
                sendmail(receivers,'Price Dropped to %d!'%(getNum(priceNow)),timeStamps,priceRecords)

        hourNow=int(datetime.datetime.now().strftime("%H"))

        if (hourNow==13 or hourNow==21) and (not daily): 
            daily=True
            sendmail(receivers,'daily price report',timeStamps,priceRecords)
            if len(priceRecords)>maxRecords:
                priceRecords=priceRecords[-maxRecords:]
                timeStamps=timeStamps[-maxRecords:]
            time.sleep(100)
        elif not (hourNow==13 or hourNow==21):
            daily=False

        time.sleep(1200)
        getPrice(url2)
        print 'still working... current time is %s'%(datetime.datetime.now().strftime("%H:%M:%S"))



