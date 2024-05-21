# -*- coding: utf-8 -*-

import os
import re
import urllib3

    global HEADERS

    global SIGNURL
    SIGNURL = 'https://www.haidan.video/signin.php'

    global HTTP
    HTTP = urllib3.PoolManager()

        HEADERS = {
            'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36 Edg/125.0.0.0',
            'cookie': 'c_secure_uid=NDI0MjU%3D; c_secure_pass=7d90ea6a90c03810e9dd18e2104f2fb4; c_secure_ssl=eWVhaA%3D%3D; c_secure_tracker_ssl=eWVhaA%3D%3D; c_secure_login=bm9wZQ%3D%3D',
        }

   r = HTTP.request('GET', SIGNURL, headers=HEADERS)
