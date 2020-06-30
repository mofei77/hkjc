
import requests

import time
import logging
import datetime


logger = logging.getLogger()
# 设置此logger的最低日志级别，之后添加的Handler级别如果低于这个设置，则以这个设置为最低限制
logger.setLevel(logging.INFO)

# 创建一个FileHandler，将日志输出到文件
log_file = 'log/sys_%s.log' % datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')
file_handler = logging.FileHandler(log_file)
# 设置此Handler的最低日志级别
file_handler.setLevel(logging.WARNING)
# 设置此Handler的日志输出字符串格式
log_formatter = logging.Formatter('%(asctime)s[%(levelname)s]: %(message)s')
file_handler.setFormatter(log_formatter)

# 创建一个StreamHandler，将日志输出到Stream，默认输出到sys.stderr
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)

# 将不同的Handler添加到logger中，日志就会同时输出到不同的Handler控制的输出中
# 注意如果此logger在之前使用basicConfig进行基础配置，因为basicConfig会自动创建一个Handler，所以此logger将会有3个Handler
# 会将日志同时输出到3个Handler控制的输出中
logger.addHandler(file_handler)
logger.addHandler(stream_handler)
