import argparse
from loguru import logger
import sqlBoolInjectTool
import sqlTimeInjectTool
import common
import os

if __name__ == "__main__":
    os.system("cls")
    common.Banner()
    parser = argparse.ArgumentParser(description='渗透测试工具测试版！', prog='渗透测试工具！')
    parser.add_argument('--url', type=str, help='输入目标测试网站url！')
    parser.add_argument('--gpmode', type=str, default='post', help='输入传参模式：post/get')
    parser.add_argument('--mode', type=str, default='time', help='sql注入模式：bool/time/error/union/stack')
    parser.add_argument('--get', type=str, default='all',
                        help='输入要爆破出的数据库信息：database/table/columninfo/infomation/all')
    args = parser.parse_args()
    url = args.url
    if not url:exit()
    get = args.get
    mode = args.mode
    if mode == 'time':
        sqlTimeInjectTool.run(url, get)
    elif mode == 'bool':
        sqlBoolInjectTool.run(url, get)
    else:
        logger.error('抱歉，该模式还未实现...')
