#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API for http://diary.ru web service.
"""
import hashlib
import requests

class Diary_API:
    '''
    API for http://diary.ru web service.
    '''

    def __init__(self, session=None, appkey=None, key=None,
                 ok=None, pk=None):
        '''
        appkey is ok
        key is pk
        '''
        self.__session = session or requests
        self.error = None
        self.sid = None
        self._appkey = appkey or ok
        self._key = key or pk

    def password_crypt(self, password):
        s = '{key}{password}'.format(key=self._key,
                                     password=password)
        md5 = hashlib.md5(s.encode('utf-8'))
        return md5.hexdigest()

    def auth(self, username, password):
        self.sid, self.error = None, None
        self.__auth_params = {
                                'username': username.encode('windows-1251'),
                                'password': self.password_crypt(password),
                                'method': 'user.auth',
                                'appkey': self._appkey,
                                }
        js = self.__session.get('http://www.diary.ru/api/',
                        params = self.__auth_params,
                        allow_redirects=False).json()
        if js['result'] == '0':
            self.sid = js['sid']
            return True
        else:
            self.error = js['error']
            return False

    def _auth_twice(self):
        self.sid, self.error = None, None
        js = self.__session.get('http://www.diary.ru/api/',
                        params = self.__auth_params,
                        allow_redirects=False).json()
        if js['result'] == '0':
            self.sid = js['sid']
            return True
        else:
            self.error = js['error']
            return False

    def _get(self, params, data=None):
        self.error = None
        if self.sid is None:
            raise Exception('You no authorized')
        if params:
            params['sid'] = self.sid
        if data:
            data['sid'] = self.sid
        return self.__session.get('http://www.diary.ru/api/',
                                params=params,
                                data=data)

    def _post(self, params, data=None):
        self.error = None
        if self.sid is None:
            raise Exception('You no authorized')
        if params:
            params['sid'] = self.sid
        if data:
            data['sid'] = self.sid
        return self.__session.get('http://www.diary.ru/api/',
                                params=params,
                                data=data)

    ### USER region
    def user_get(self, user_id=None):
        para = {'method': 'user.get',
                'unset': ['readers','community.member',
                        'birthday', 'joindate', 'favs'],
                }
        if user_id:
            para['userid'] = user_id
        js = self._get(params=para).json()
        if js['result'] == '0':
            return js['user']
        else:
            self.error = js['error']

    def user_get_favorites(self, user_id=None):
        js = self.user_get(user_id)
        return ((user_id, user_name)
                for user_id, user_name
                in js['favs2'].items())

    def user_get_readers(self, user_id=None):
        js = self.user_get(user_id)
        return ((user_id, user_name)
                for user_id, user_name
                in js['favs2'].items())

    ## END USER region

    ## POST region
    def post_get(self, type_='diary', juser_id=None, shortname=None,
                    from_=0, src=1, ids=None):
        '''
        type_ must be one of: ['diary', 'favorites', 'quotes',
        'notepad', 'draft', 'last', 'by_id']
        '''
        if ids:
            if not isinstance(ids, (list, tuple)):
                raise Exception('ids mut be list, tuple or None!')
        lst = ['diary', 'favorites', 'quotes',
                        'notepad', 'draft', 'last', 'by_id']
        if type_ not in lst:
            raise Exception('type_ must be one of: {}'.format(str(lst)))
        para = {'method': 'post.get',
                'type': type_,
                'from': from_,
                'src': src, }
        if juser_id: para['juserid'] = juser_id
        if shortname: para['shortname'] = shortname
        if ids: para['ids'] = ids
        js = self._get(params=para).json()
        if js['result'] != '0':
            self.error = js['error']
            raise Exception(self.error)
        else:
            return ((post_id, data)
                    for post_id, data
                    in js['posts'].items())

    def post_delete(self, juser_id, post_id):
        js = self._get(params={'method':'post.delete',
                                'juserid': juserid,
                                'postid': post_id}).json()
        if js['result'] != '0':
            self.error = js['error']
            raise Exception(self.error)
        else:
            return True
    ## END POST region

    ## COMMENT region
    def comment_get(self, post_id, from_=0):
        js = self._get(params={'method':'comment.get',
                                'postid': post_id,
                                'from': from_}).json()
        if js['result'] != '0':
            self.error = js['error']
            raise Exception(self.error)
        else:
            return ((comment_id, comment_data)
                    for comment_id, comment_data
                    in js['comments'])
    ## END COMMENT region

    ## UMAIL region
    def umail_get_folders(self):
        '''
        Return:
        folder_id, name, count
        '''
        js = self._get(params={'method':'umail.get_folders',}).json()
        if js['result'] != '0':
            self.error = js['error']
            raise Exception(self.error)
        else:
            folders2 = js['folders2']
            if not '1' in folders2:
                folders2['1'] = {'name': 'Входящие',
                                    'count':'-1'}
            if not '2' in folders2:
                folders2['2'] = {'name': 'Отправленные',
                                    'count':'-1'}
            if not '3' in folders2:
                folders2['3'] = {'name': 'Удалённые',
                                    'count':'-1'}
            for folder_id, data in folders2.items():
                yield folder_id, data['name'], data['count']

    def umail_get(self, folder_id=None, unread=0,
                    from_=0, limit=20, umail_id=None):
        '''
        unread = 0 - all
        unread = 1 - only unread
        '''
        folderid = folder_id or 1
        para = {'method':'umail.get',
                'unread': unread,
                'limit': limit, }
        if from_ != 0: para['from'] = from_
        if umail_id: para['umailid'] = umail_id
        js = self._get(params=para).json()
        if js['result'] != '0':
            self.error = js['error']
            raise Exception(self.error)
        else:
            return int(js['count']), js['umail']

    def umail_get_iter(self, folder_id=None, unread=0,
                    from_=0, limit=20, umail_id=None):
        count, umail_dct = self.umail_get(folder_id, unread,
                                    from_, limit, umail_id)
        return ((umail_id, umail_unit_dct)
                for umail_id, umail_unit_dct
                in umail_dct.items())
    

    def umail_send(self, user_id, username, title,
                    message, save_copy=True, need_receipt=False):
        js = self._post(data={'method': 'umail.send',
                'userid': user_id,
                'username': username.encode('windows-1251'),
                'title': title.encode('windows-1251'),
                'message': message.encode('windows-1251'),
                'save_copy': save_copy,
                'need_receipt': need_receipt,
            }).json()
        if js['result'] != '0':
            self.error = js['error']
            raise Exception(self.error)
        else:
            return True

    def umail_delete(self, umail_id_list):
        if not isinstance(umail_id_list, (list, tuple)):
            umail_id_list = tuple(umail_id_list)
        js = self._get(params={'method': 'umail.delete',
                                'umailid': umail_id_list,
                                }).json()
        if js['result'] != '0':
            self.error = js['error']
            raise Exception(self.error)
        else:
            return True
    ## END UMAIL region

if __name__ == '__main__':
    username = ''
    password = ''
    appkey = '' #ok
    key = '' #pk
    with requests.Session() as sess:
        d_api = Diary_API(sess, appkey=appkey,
                          key=key)
        #d_api.sid = ''
        if not d_api.sid and not d_api.auth(username, password):
            print(d_api.error)
            exit()
        print(d_api.sid)
        #print(d_api.user_get())
        #print(list(d_api.umail_get_iter())[:2])
        print(list(d_api.post_get(type_='by_id', ids=['id as int',]))[:2])
        print(list(d_api.comment_get('id as int'))[:2])
