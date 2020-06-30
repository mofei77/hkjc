# -*- coding: UTF-8 -*-

from spider import *

import threading
import re

match_func = re.compile('odds.*')

def run():
    funlist = []
    thread_num = []
    for key in globals():
        if match_func.findall(key):
            funlist.append(globals().get(key))

    for i in range(len(funlist)):
        t = threading.Thread(target=funlist[i])

        t.start()
        thread_num.append(t)

    for thread in thread_num:
        thread.join()

if __name__ == '__main__':
    run()


