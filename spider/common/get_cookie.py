# -*- coding: UTF-8 -*-
from math import cos,pi,floor

"""
    分析网页js源码，获取请求头信息，携带信息重新发送获取cookies
"""
def get_challenge_answer(challenge):
    """
    Solve the math part of the challenge and get the result
    """
    arr = list(challenge)
    last_digit = int(arr[-1])
    arr.sort()
    min_digit = int(arr[0])
    subvar1 = (2 * int(arr[2])) + int(arr[1])
    subvar2 = str(2 * int(arr[2])) + arr[1]
    power = ((int(arr[0]) * 1) + 2) ** int(arr[1])
    x = (int(challenge) * 3 + subvar1)
    y = cos(pi * subvar1)
    answer = x * y
    answer -= power
    answer += (min_digit - last_digit)
    answer = str(int(floor(answer))) + subvar2
    return answer

def parse_challenge(page):
    top = page.split('<script>')[1].split('\n')
    challenge = top[1].split(';')[0].split('=')[1]
    challenge_id = top[2].split(';')[0].split('=')[1]
    return {'challenge': challenge, 'challenge_id': challenge_id, 'challenge_result': get_challenge_answer(challenge)}


# set cookie
def get_cookie(session,url,page,para=None):

    d = parse_challenge(page)
    head =  {
        'X-AA-Challenge': d['challenge'],
        'X-AA-Challenge-ID': d['challenge_id'],
        'X-AA-Challenge-Result': d['challenge_result'],
        'Content-Type': 'text/plain'
        }

    result = session.post(url, headers=head,params=para)
    print('Successfully obtained cookies', result.cookies)



