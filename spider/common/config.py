from bs4 import BeautifulSoup
from copy import deepcopy
BASE_URL = 'https://bet.hkjc.com/football/getJSON.aspx'
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
map_item = {
    'hadodds':'主客和','fhaodds':'半场主客和','crsodds':'波胆','fcsodds':'半场波胆','ftsodds':'第一队入球',
    'ooeodds':'入球单双','ttgodds': '总入球','hftodds':'半全场','hhaodds':'让球主客和','hdcodds':'让球',
    'hilodds':'入球大细','fhlodds':'半场入球大细','chlodds':'角球大细','spcodds':'特别项目','tqlodds':'晋级队伍',
    'fgsodds': '首名入球','ntsodds': '下一队入球','chpodds':'冠军','tpsodds':'神射手'
            }
collect = 'sports'

fresh_by_jsontype = 60*3

timeout = 3
rollball_stop = 60
stop = 30 * 60

import requests

sess = requests.session()












