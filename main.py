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
    d_api.sid = 'e1638d6b82c189beefd2487c6d4b57b0'
    if not d_api.sid and not d_api.auth(username, password):
        print(d_api.error)
        exit()
    print(d_api.sid)
    #lst = d_api.post_get()
    #lst__ = list(lst)
    #print(lst__[:2])
    #post_id = lst__[0][0]
    #lst = d_api.comment_get(post_id)
    #print(lst__[:2])
    for post_id, post_data, comments in d_api.post_and_comments(type_='by_id', ids=['201289904',]):
        print(post_id)
        
