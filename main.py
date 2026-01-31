import os
import re
import urllib3

MAGIC_NUM = 0
ERROR = 0
BASEURL = 'https://www.haidan.video/index.php'
SIGNURL = 'https://www.haidan.video/signin.php'
HTTP = None
HEADERS = {}
PRIVACY = ''

def sign():
    global ERROR
    global MAGIC_NUM

    print('-> 正在签到...')
    HEADERS['referer'] = BASEURL  # 添加 referer 以模拟正常访问
    r = HTTP.request('GET', SIGNURL, headers=HEADERS)
    if r.status != 200 and r.status != 302:
        print('!! 签到失败，状态码：' + str(r.status))
        ERROR = 1
        return
    data = r.data.decode('utf-8', errors='ignore')

    # 检查响应是否表示已签到
    if '已签到' in data or '已经签到' in data or '今日已签' in data:
        print('-> 今日已签到，无需重复')
        return

    get_magic(data)

def get_magic(data):
    global ERROR
    pattern = re.compile(r'([0-9,\.]+)\([\s\S]+\)')
    mn = re.search(pattern, data)
    if mn:
        mn = float(mn.group(1).replace(',', ''))
        d = mn - MAGIC_NUM
        if d > 0:
            print('-> 签到成功，获得魔力值：' + str(d))
        else:
            print('-> 签到无变化（可能已签到或解析失败）')
    else:
        print('!! 获取最新魔力值失败')
        ERROR = 3

def get_status():
    global ERROR
    global MAGIC_NUM

    print('-> 正在获取用户状态...')
    r = HTTP.request('GET', BASEURL, headers=HEADERS)
    if r.status != 200:
        print('!! 错误的状态： ' + str(r.status))
        ERROR = 1
        return
    data = r.data.decode('utf-8', errors='ignore')

    # 用户名
    pattern = re.compile(r'\s*\*\*\s*(.+)\*\*\s*')  # 更新正则以匹配可能的用户名格式
    username = re.search(pattern, data)
    if username:
        uname = username.group(1)
        if PRIVACY == '2':
            print('-> 当前用户：[保护]')
        elif PRIVACY == '3':
            print('-> 当前用户：' + uname)
        else:
            print('-> 当前用户：*' + uname[1:len(uname) - 1] + '*')
    else:
        print('-> 登录身份过期或程序失效')
        ERROR = 2
        return

    # 魔力值
    pattern = re.compile(r'([0-9,\.]+)\([\s\S]+\)')
    mn = re.search(pattern, data)
    if mn:
        MAGIC_NUM = float(mn.group(1).replace(',', ''))
        print('-> 当前魔力值：' + str(MAGIC_NUM))
    else:
        print('-> 登录身份过期或程序失效')
        ERROR = 2
        return

    # 始终尝试签到
    sign()

def main():
    print("=================================================")
    print("||                 HaiDan Sign                 ||")
    print("||                Author: Jokin                ||")
    print("||               Version: v0.0.6               ||")
    print("=================================================")

    global HEADERS
    global HTTP
    global PRIVACY
    global ERROR
    ERROR = 0

    HTTP = urllib3.PoolManager()

    PRIVACY = os.getenv('HAIDAN_PRIVACY') if os.getenv('HAIDAN_PRIVACY') else '1'

    _uid = os.getenv('HAIDAN_UID') if os.getenv('HAIDAN_UID') else False
    _pass = os.getenv('HAIDAN_PASS') if os.getenv('HAIDAN_PASS') else False
    _login = os.getenv('HAIDAN_LOGIN') if os.getenv('HAIDAN_LOGIN') else 'bm9wZQ%3D%3D'
    _ssl = os.getenv('HAIDAN_SSL') if os.getenv('HAIDAN_SSL') else 'eWVhaA%3D%3D'
    _tracker_ssl = os.getenv('HAIDAN_TRACKER_SSL') if os.getenv('HAIDAN_TRACKER_SSL') else 'eWVhaA%3D%3D'
    _multi = os.getenv('HAIDAN_MULTI') if os.getenv('HAIDAN_MULTI') else False

    if _multi == False:
        if not _uid or not _pass:
            print('!! 缺少设置： 环境变量/Secrets')
            exit(4)
        _multi = _uid + '@' + _pass
    else:
        print('-> 多账户支持已经启用')

    # 多账户解析
    sp = _multi.split(',')
    for i in range(0, len(sp)):
        print('-> 当前进度： ' + str(i + 1) + '/' + str(len(sp)))
        account = sp[i].strip().split('@')
        if len(account) != 2:
            print('!! 多账户设置格式错误')
            exit(5)
        _uid = account[0]
        _pass = account[1]
        MAGIC_NUM = 0
        HEADERS = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
            'cookie': 'c_secure_login=' + _login + '; c_secure_uid=' + _uid + '; c_secure_pass=' + _pass + '; c_secure_tracker_ssl=' + _tracker_ssl + '; c_secure_ssl=' + _ssl,
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }

        get_status()

    print('-> 已经完成本次任务')
    if ERROR != 0:
        print('!! 本次任务出现错误，请及时查看日志')
    else:
        print('-> 任务圆满完成')
    exit(ERROR)

if __name__ == '__main__':
    main()
