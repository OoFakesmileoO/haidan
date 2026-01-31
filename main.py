import os
import re
import cloudscraper

MAGIC_NUM = 0
ERROR = 0
BASEURL = 'https://www.haidan.video/index.php'
SIGNURL = 'https://www.haidan.video/signin.php'
scraper = None
HEADERS = {}
PRIVACY = ''

def sign():
    global ERROR
    global MAGIC_NUM

    print('-> 正在签到...')
    HEADERS['Referer'] = BASEURL
    try:
        r = scraper.get(SIGNURL, headers=HEADERS, timeout=15)
        print(f"签到响应状态码: {r.status_code}")

        if r.status_code not in (200, 302):
            print(f"!! 签到失败，状态码：{r.status_code}")
            print(f"响应开头预览: {r.text[:300]}")  # debug 用
            ERROR = 1
            return
        
        data = r.text
        
        # 检查是否已签到（根据常见中文提示匹配，可根据实际日志调整）
        if any(word in data for word in ['已签到', '已经签到', '今日已签', '重复签到', 'Signed in']):
            print('-> 今日已签到，无需重复')
            return
        
        get_magic(data)
    
    except Exception as e:
        print(f"签到异常: {str(e)}")
        ERROR = 1

def get_magic(data):
    global ERROR
    global MAGIC_NUM
    
    pattern = re.compile(r'([0-9,\.]+)\s*\([\s\S]*?\)')
    mn = re.search(pattern, data)
    if mn:
        try:
            mn_value = float(mn.group(1).replace(',', ''))
            d = mn_value - MAGIC_NUM
            if d > 0:
                print(f'-> 签到成功，获得魔力值：{d}')
            else:
                print('-> 签到响应正常，但魔力无变化（可能已签到或解析偏移）')
        except:
            print('!! 魔力值解析失败')
            ERROR = 3
    else:
        print('!! 未在响应中找到魔力值模式')
        print(f"响应预览（前500字符）: {data[:500]}")
        ERROR = 3

def get_status():
    global ERROR
    global MAGIC_NUM

    print('-> 正在获取用户状态...')
    try:
        r = scraper.get(BASEURL, headers=HEADERS, timeout=15)
        print(f"状态页响应状态码: {r.status_code}")
                # Debug: 打印页面前1500字符，帮助定位用户名和魔力位置
        print("=== DEBUG: index.php 页面内容预览 (前1500字符) ===")
        print(data[:1500])
        print("=== DEBUG 结束 ===")
        
        # 额外尝试打印是否包含常见关键词
        if '欢迎' in data or '用户' in data or '魔力' in data or '积分' in data:
            print("页面包含关键词：欢迎/用户/魔力/积分 → 很可能已登录")
        else:
            print("页面未包含常见登录后关键词 → 可能仍为登录页或重定向")        
        if r.status_code != 200:
            print(f"!! 错误的状态： {r.status_code}")
            print(f"响应开头预览: {r.text[:300]}")
            ERROR = 1
            return
        
        data = r.text
        
        # 用户名（部分隐藏等隐私逻辑）
        pattern = re.compile(r'\s*\*\*\s*(.+?)\s*\*\*\s*')
        username = re.search(pattern, data)
        if username:
            uname = username.group(1).strip()
            if PRIVACY == '2':
                print('-> 当前用户：[保护]')
            elif PRIVACY == '3':
                print(f'-> 当前用户：{uname}')
            else:
                if len(uname) > 2:
                    print(f'-> 当前用户：*{uname[1:-1]}*')
                else:
                    print(f'-> 当前用户：{uname}')
        else:
            print('-> 未找到用户名，可能登录失效或页面结构变化')
            ERROR = 2
            return

        # 魔力值
        pattern = re.compile(r'([0-9,\.]+)\s*\([\s\S]*?\)')
        mn = re.search(pattern, data)
        if mn:
            MAGIC_NUM = float(mn.group(1).replace(',', ''))
            print(f'-> 当前魔力值：{MAGIC_NUM}')
        else:
            print('-> 未找到魔力值，可能登录失效')
            ERROR = 2
            return

        # 执行签到
        sign()
    
    except Exception as e:
        print(f"获取状态异常: {str(e)}")
        ERROR = 1

def main():
    print("=================================================")
    print("||              HaiDan Auto Sign               ||")
    print("||         Fixed version with cloudscraper     ||")
    print("=================================================")

    global HEADERS
    global scraper
    global PRIVACY
    global ERROR
    ERROR = 0

    # 初始化 cloudscraper，模拟真实浏览器
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'mobile': False,
            'desktop': True
        },
        delay=8,          # 轻微延迟，模拟人类
        debug=False
    )

    PRIVACY = os.getenv('HAIDAN_PRIVACY') or '1'

    _uid = os.getenv('HAIDAN_UID') or ''
    _pass = os.getenv('HAIDAN_PASS') or ''
    _login = os.getenv('HAIDAN_LOGIN') or 'bm9wZQ%3D%3D'
    _ssl = os.getenv('HAIDAN_SSL') or 'eWVhaA%3D%3D'
    _tracker_ssl = os.getenv('HAIDAN_TRACKER_SSL') or 'eWVhaA%3D%3D'
    _multi = os.getenv('HAIDAN_MULTI') or False

    if not _uid or not _pass:
        if not _multi:
            print('!! 缺少必要 Secrets：HAIDAN_UID 和 HAIDAN_PASS')
            exit(4)

    accounts = []
    if _multi:
        print('-> 多账户模式已启用')
        for acc in _multi.split(','):
            acc = acc.strip()
            if '@' in acc:
                uid, pw = acc.split('@', 1)
                accounts.append((uid.strip(), pw.strip()))
    else:
        accounts = [(_uid, _pass)]

    for idx, (uid, pw) in enumerate(accounts, 1):
        print(f'-> 处理账户 {idx}/{len(accounts)}')
        HEADERS = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'cookie': f'c_secure_login={_login}; c_secure_uid={uid}; c_secure_pass={pw}; '
                      f'c_secure_tracker_ssl={_tracker_ssl}; c_secure_ssl={_ssl}',
        }

        get_status()

    print('-> 本次任务完成')
    if ERROR != 0:
        print('!! 任务有错误，请检查日志')
        exit(ERROR)
    else:
        print('-> 全部成功')
        exit(0)

if __name__ == '__main__':
    main()
