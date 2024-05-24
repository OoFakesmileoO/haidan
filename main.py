import os
import re
import urllib3

def sign_in():
    # Define global variables
    global HEADERS
    global BASEURL
    global SIGNURL
    global HTTP

    # Initialize SIGNURL
    BASEURL = 'https://www.haidan.video/index.php'
    SIGNURL = 'https://www.haidan.video/signin.php'

    # Initialize HTTP PoolManager
    HTTP = urllib3.PoolManager()

    # Initialize HEADERS
    HEADERS = {
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36 Edg/125.0.0.0',
        'cookie': 'c_secure_uid=NDI0MjU%3D; c_secure_pass=7d90ea6a90c03810e9dd18e2104f2fb4; c_secure_ssl=eWVhaA%3D%3D; c_secure_tracker_ssl=eWVhaA%3D%3D; c_secure_login=bm9wZQ%3D%3D',
    }

    # Make the request
    r = HTTP.request('GET', BASEURL, headers=HEADERS)
    r = HTTP.request('GET', SIGNURL, headers=HEADERS)

    # Check the response status
    if r.status == 200:
        print('-> 签到请求成功')
    else:
        print('!! 签到失败，错误的状态： ' + str(r.status))

# Call the function to sign in
sign_in()
