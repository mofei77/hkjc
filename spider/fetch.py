# -*- coding: UTF-8 -*-
import requests,time,pprint
from spider.common.get_cookie import get_cookie
headers = {
'Connection': 'keep-alive',
'Pragma': 'no-cache',
'Cache-Control': 'no-cache',
'Accept': '*/*',
'X-Requested-With': 'XMLHttpRequest',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
'Content-Type': 'application/json; charset=utf-8',
'Sec-Fetch-Site': 'same-origin',
'Sec-Fetch-Mode': 'cors',
'Sec-Fetch-Dest': 'empty',
'Accept-Encoding': 'gzip, deflate',
'Accept-Language': 'zh-CN,zh;q=0.9',
}
url = 'https://bet.hkjc.com/football/getJSON.aspx'
sess = requests.Session()
gids = ['536e1fff-be6a-4712-9b57-5e47e09619cb', 'e00b7f57-d4d7-423e-992a-5abef1f97ad4']



params = {'jsontype':'odds_allodds.aspx','matchid':'3749932a-45af-46b1-ab91-f46da862bb41'}

def main():
      r = sess.get(url=url, params=params)
      if r.headers['Content-Type'] != 'application/json; charset=utf-8':
         get_cookie(sess, url, r.text, para=None)
         print('响应不是json')
         return main()
      return r.json()




info = '@@@@@@@@@@@@@@@@@@@@@|松永昌博|湯窪幸雄|川村禎彥|湯窪幸雄|大久保龍志|大橋勇樹|武幸四郎|昆貢|石坂正|笹田和秀|西園正都|中竹和也|齋藤誠|矢作芳人|莊野靖志|高野友和;;||||||||||||||||'.split('@@@')

print(info)








