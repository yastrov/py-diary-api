#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
from diaryapi import Diary_API
from authloader import load_user, load_app_info

username, password = load_user()
appkey, key = load_app_info()

with requests.Session() as sess:
    d_api = Diary_API(sess, appkey=appkey,
                      key=key)
    #d_api.sid = ''
    if not d_api.auth(username, password):
        print(d_api.error)
        exit()
    print(list(d_api.post_get())[:2])
