
#推送消息到微信
import requests
import time
import os

url = "https://sc.ftqq.com/SCU76735Tde7652a4a3c6657970d0aaafa71a59e35e1610c5d5b74.send?"


def push():
    try:
        for file in os.listdir('.'):
            if '.log' in file:
                with open(file, 'r') as f:
                    f=f.read()
        content ={'text': f, 'desp': 'spider status'}
    
        r = requests.get(url,params=content)
    except Exception as ex:
        print(ex)





    