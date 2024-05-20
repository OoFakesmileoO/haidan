import os
import re
import urllib3
import logging

def setup_logging():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    return logging.getLogger()

logger = setup_logging()

def fetch_page(http, url, headers):
    try:
        r = http.request('GET', url, headers=headers)
        if r.status != 200:
            logger.error('Request failed, status code: %d', r.status)
            return None
        return r.data.decode('utf-8')
    except Exception as e:
        logger.exception('Exception during HTTP request: %s', e)
        return None

def extract_magic_number(data):
    pattern = re.compile(r'<span\s*id=[\'|"]magic_num[\'|"]>([0-9,\.]+)\([\s\S]+\)</span>')
    match = re.search(pattern, data)
    if match:
        return float(match.group(1).replace(',', ''))
    return None

def extract_username(data, privacy):
    pattern = re.compile(r'<a\s*href=[\'|"]userdetails\.php\?id=\d+[\'|"]\s*class=[\'|"].+[\'|"]\s*>\s*<b>\s*(.+)</b>\s*</a>')
    match = re.search(pattern, data)
    if match:
        username = match.group(1)
        if privacy == '2':
            return '[Protected]'
        elif privacy == '3':
            return username
        elif privacy == '1':
            return '*' + username[1:-1] + '*'
        else:
            logger.error('Invalid privacy setting')
            return None
    return None

def check_sign_in_status(data):
    pattern = re.compile(r'<input\s*type=[\'|"]submit[\'|"]\s*id=[\'|"]modalBtn[\'|"]\s*class=[\'|"]dt_button[\'|"]\s*value=[\'|"]已经打卡[\'|"][\s]*/[\s]*>')
    return bool(re.search(pattern, data))

def sign_in(http, sign_url, headers):
    logger.info('Attempting to sign in...')
    page_data = fetch_page(http, sign_url, headers)
    if page_data is None:
        logger.error('Sign in failed')
        return False
    logger.info('Sign in successful')
    return True

def get_status(http, base_url, headers, privacy, magic_num):
    logger.info('Fetching user status...')
    page_data = fetch_page(http, base_url, headers)
    if page_data is None:
        logger.error('Failed to fetch user status')
        return None, None

    username = extract_username(page_data, privacy)
    if username is None:
        logger.error('Failed to extract username')
        return None, None
    logger.info('Current user: %s', username)

    current_magic_num = extract_magic_number(page_data)
    if current_magic_num is None:
        logger.error('Failed to extract magic number')
        return None, None
    logger.info('Current magic number: %f', current_magic_num)

    if not check_sign_in_status(page_data):
        if sign_in(http, SIGNURL, headers):
            logger.info('Sign in successful, fetching updated magic number...')
            page_data = fetch_page(http, base_url, headers)
            if page_data is None:
                return username, current_magic_num
            current_magic_num = extract_magic_number(page_data)
            if current_magic_num is not None:
                logger.info('Updated magic number: %f', current_magic_num)
                gained_magic = current_magic_num - magic_num
                logger.info('Magic points gained: %f', gained_magic)
            else:
                logger.error('Failed to fetch updated magic number')
    else:
        logger.info('Already signed in for today')

    return username, current_magic_num

def main():
    logger.info("=================================================")
    logger.info("||                 HaiDan Sign                 ||")
    logger.info("||                Author: Jokin                ||")
    logger.info("||               Version: v0.0.6               ||")
    logger.info("=================================================")

    base_url = 'https://www.haidan.video/index.php'
    sign_url = 'https://www.haidan.video/signin.php'
    http = urllib3.PoolManager()

    privacy = os.getenv('HAIDAN_PRIVACY', '1')
    multi_account = os.getenv('HAIDAN_MULTI', False)

    accounts = []
    if not multi_account:
        uid = os.getenv('HAIDAN_UID')
        pwd = os.getenv('HAIDAN_PASS')
        login = os.getenv('HAIDAN_LOGIN', 'bm9wZQ%3D%3D')
        ssl = os.getenv('HAIDAN_SSL', 'eWVhaA%3D%3D')
        tracker_ssl = os.getenv('HAIDAN_TRACKER_SSL', 'eWVhaA%3D%3D')

        if not uid or not pwd or not login:
            logger.error('Missing environment variables/Secrets')
            exit(4)
        accounts.append((uid, pwd, login, ssl, tracker_ssl))
    else:
        logger.info('Multi-account support enabled')
        account_data = multi_account.split(',')
        for data in account_data:
            account = data.strip().split('@')
            if len(account) != 2:
                logger.error('Invalid multi-account format')
                exit(5)
            uid, pwd = account
            accounts.append((uid, pwd))

    for i, account in enumerate(accounts):
        logger.info('Processing account %d/%d', i + 1, len(accounts))
        uid, pwd, login, ssl, tracker_ssl = account
        headers = {
            'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36 Edg/124.0.0.0',
            'cookie': f'c_secure_login={login}; c_secure_uid={uid}; c_secure_pass={pwd}; c_secure_tracker_ssl={tracker_ssl}; c_secure_ssl={ssl}',
        }
        magic_num = 0
        username, magic_num = get_status(http, base_url, headers, privacy, magic_num)
        if username is None or magic_num is None:
            logger.error('Task failed for account %d', i + 1)
            exit(1)

    logger.info('Task completed successfully')

if __name__ == '__main__':
    main()
