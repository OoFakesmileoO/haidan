import os
import re
import cloudscraper

MAGIC_NUM = 0.0
ERROR = 0
BASEURL = 'https://www.haidan.video/index.php'
SIGNURL = 'https://www.haidan.video/signin.php'
scraper = None
HEADERS = {}
PRIVACY = ''

def sign():
    global ERROR, MAGIC_NUM
    print('-> 正在尝试签到...')
    HEADERS['Referer'] = BASEURL
    try:
        r = scraper.get(SIGNURL, headers=HEADERS, timeout=20)
        print(f"签到页面状态码: {r.status_code}")
        if r.status_code not in (200, 302):
            print(f"!! 签到请求失败，状态码：{r.status_code}")
            print(f"响应预览: {r.text[:400]}")
            ERROR = 1
            return
        
        data = r.text.lower()
        if any(word in data for word in ['已签到', '已经签到', '今日已签', '重复签到', 'signed in', 'already signed']):
            print('-> 检测到已签到提示，今日无需重复')
            return
        
        # 尝试找签到成功的魔力增加
        get_magic(data, is_sign_response=True)
    
    except Exception as e:
        print(f"签到异常: {str(e)}")
        ERROR = 1

def get_magic(data, is_sign_response=False):
    global ERROR, MAGIC_NUM
    # 魔力值常见格式：数字 + 逗号 + 可选括号/今日增加等
    patterns = [
        r'([0-9,]+(?:\.\d+)?)\s*(?:\(|（|\[|魔力值|points|magic|积分|剩余|当前).*?\)',
        r'魔力值.*?([0-9,]+(?:\.\d+)?)',
        r'([0-9,]+(?:\.\d+)?)\s*\(\s*今日\s*[+\-]?',
    ]
    for pat in patterns:
        m = re.search(pat, data, re.I)
        if m:
            try:
                val = float(m.group(1).replace(',', ''))
                if is_sign_response:
                    print(f'-> 签到响应中找到魔力值: {val}')
                else:
                    MAGIC_NUM = val
                    print(f'-> 当前魔力值: {MAGIC_NUM}')
                return
            except:
                pass
    print('!! 未匹配到魔力值')
    if '魔力' in data or '积分' in data:
        print(f"魔力相关文本预览: {data[data.find('魔力')-50:data.find('魔力')+200] if '魔力' in data else data[:300]}")
    ERROR = 3

def get_status():
    global ERROR, MAGIC_NUM
    print('-> 正在获取用户首页...')
    try:
        r = scraper.get(BASEURL, headers=HEADERS, timeout=20)
        print(f"首页状态码: {r.status_code}")
        if r.status_code != 200:
            print(f"!! 首页访问失败，状态码：{r.status_code}")
            print(f"响应预览: {r.text[:400]}")
            ERROR = 1
            return

        data = r.text
        data_lower = data.lower()

        # Debug: 输出页面关键部分
        print("=== DEBUG: 页面前1200字符预览 ===")
        print(data[:1200])
        print("=== DEBUG 结束 ===")

        # 检测是否为登录页
        login_indicators = [
            '用户名', '密码', '登陆', '登录', 'captcha', 'verifycode', '找回密码',
            'signup.php', 'recover.php', 'confirm_resend.php', '自动登出'
        ]
        if any(ind in data_lower for ind in login_indicators):
            print("!! 检测到登录页面特征 → Cookie 失效、过期或不匹配当前IP/浏览器指纹")
            print("请立即在浏览器中重新登录 haidan.video 并更新 Secrets 中的所有 c_secure_* 和 cf_clearance 值")
            ERROR = 2
            return

        # 用户名提取 - 多模式尝试
        username_patterns = [
            r'userdetails\.php\?id=\d+[^>]*?>([^<]+?)</a>',               # 链接中的用户名
            r'<(?:b|strong)[^>]*>([^<]+)</(?:b|strong)>',                  # <b> 或 <strong>
            r'(?:欢迎回来|Hi|Hello|欢迎)[，, ]*([^<,\s]+)',                 # 欢迎消息
            r'class="[^"]*?(?:user|name|account)[^"]*?"[^>]*>([^<]+)<',    # class 相关
            r'>([^<]{3,20})</a>\s*(?:<img|\s*\[)',                         # 宽松链接后用户名
        ]
        uname = None
        for pattern in username_patterns:
            m = re.search(pattern, data, re.I | re.DOTALL)
            if m:
                uname = m.group(1).strip()
                break

        if uname:
            print(f"-> 成功提取用户名: {uname}")
            if PRIVACY == '2':
                print('-> 当前用户: [已保护]')
            elif PRIVACY == '3':
                print(f'-> 当前用户: {uname}')
            else:
                masked = '*' * len(uname) if len(uname) < 4 else f"*{uname[1:-1]}*"
                print(f'-> 当前用户: {masked}')
        else:
            print('!! 未能在页面中提取到用户名（可能页面结构变化或仍未真正登录）')
            ERROR = 2
            return

        # 提取魔力值
        get_magic(data)

        # 如果到这里，尝试签到
        sign()

    except Exception as e:
        print(f"获取状态异常: {str(e)}")
        ERROR = 1

def main():
    print("=================================================")
    print("||      HaiDan Auto Sign - 2025 Updated        ||")
    print("||     Cloudscraper + cf_clearance support     ||")
    print("=================================================")

    global HEADERS, scraper, PRIVACY, ERROR
    ERROR = 0

    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'mobile': False
        },
        delay=10,
        captcha={'provider': None},
        debug=False
    )

    PRIVACY = os.getenv('HAIDAN_PRIVACY') or '1'

    _uid = os.getenv('HAIDAN_UID') or 'NDI0MjU%3D'
    _pass = os.getenv('HAIDAN_PASS') or '7d90ea6a90c03810e9dd18e2104f2fb4'
    _login = os.getenv('HAIDAN_LOGIN') or 'bm9wZQ%3D%3D'
    _ssl = os.getenv('HAIDAN_SSL') or 'eWVhaA%3D%3D'
    _tracker_ssl = os.getenv('HAIDAN_TRACKER_SSL') or 'eWVhaA%3D%3D'
    _cf_clearance = os.getenv('HAIDAN_CF_CLEARANCE') or ''

    # 使用你提供的最新 cf_clearance（如果 Secrets 有更新，会覆盖）
    if not _cf_clearance:
        _cf_clearance = 'kABhK6Dz0k69HollJ7aVob63Wvyeh945NioXVhSWEXE-1769866269-1.2.1.1-rD2Tj7tXMy9VXNNjWYUYyLvqY1gmiBbPkJIY2q4ylnGi8dVPVXv5cu2Qy.cxgKxXRjI.GTiigyyFSOgAXyCmqF8.Y3r38n7THHKEiFWIkQ8i4IveVizAfNAVXrmtwA40e7k9NCYf2bMVyZzk7Xn3NxKWydIbiU1C2apqcHBH.IOCtlxGmKBBiqgVqJb5nOWdQTaeRMf1LcZkUtA1e1qo_qPCcDM6VHGmqsJDyOGzQM0'

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
        'cookie': (
            f'c_secure_login={_login}; '
            f'c_secure_uid={_uid}; '
            f'c_secure_pass={_pass}; '
            f'c_secure_tracker_ssl={_tracker_ssl}; '
            f'c_secure_ssl={_ssl}; '
            f'cf_clearance={_cf_clearance}'
        ).strip('; '),
    }

    print('-> 使用 Cookie (含 cf_clearance):')
    print(f"   cf_clearance: {_cf_clearance[:40]}... (长度 {len(_cf_clearance)})")
    print('-> 开始执行签到逻辑')

    get_status()

    print('-> 任务执行完毕')
    if ERROR == 0:
        print('-> 看起来一切正常（但请检查是否真的签到成功）')
    else:
        print(f'!! 任务有错误 (code {ERROR})，请查看上面日志')
    exit(ERROR)

if __name__ == '__main__':
    main()
