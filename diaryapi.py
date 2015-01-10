#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API for http://diary.ru web service.
"""
import hashlib
import requests
import json

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
        self._index = 0

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

    def _log_json(self, js_data, method):
        with open('{method}_{index}.json'\
                    .format(index=self._index, method=method),\
                 'w') as fp:
            json.dump(js_data,fp)
        self._index += 1

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
        Return num, generator
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
            if __debug__:
                self._log_json(js, 'post_get')
            if len(js.get('posts', {}).items()) == 0:
                return (({},{}))
            return ((post_id, data)
                    for post_id, data
                    in js.get('posts', {}).items())

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
            if __debug__:
                self._log_json(js, 'comment_get')
            if len(js.get('comments', {}).items()) == 0:
                return (({},{}),)
            return ((comment_id, comment_data)
                    for comment_id, comment_data
                    in js.get('comments', {}).items())

    def journal_get(self, userid=None, shortname=None, fields=None, unset=None):
        para = {'method': 'journal.get',}
        if userid: para['userid'] = userid
        if shortname: para['shortname'] = shortname
        if fields: para['fields'] = fields
        if unset: para['unset'] = unset
        js = self._get(params=para).json()
        if __debug__:
            self._log_json(js, 'journal_get')
        if js['result'] != '0':
            self.error = js['error']
            raise Exception(self.error)
        else:
            return js['journal']

    ## END COMMENT region
    def post_and_comments(self, type_='diary', juser_id=None,
                        shortname=None, from_=0, src=1, ids=None):
        js = self.journal_get(userid = juser_id, shortname=shortname)
        posts_cont = int(js['posts'])
        counter = from_
        while counter <= posts_cont:
            for post_id, data in self.post_get(type_, juser_id=juser_id,
                                    shortname=shortname, from_=counter, src=src, ids=ids):
                comment_count = int(data.get('comments_count_data', 0))
                c_c = 0
                comments = []
                if comment_count != 0:
                    while c_c <= comment_count:
                        for comment_id, comment_data in \
                                    self.comment_get(post_id, from_=c_c):
                            c_c += 1
                            comments.append(comment_data)
                yield post_id, data, comments
                counter += 1

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
            if __debug__:
                self._log_json(js, 'umail_get_folders')
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
            if __debug__:
                self._log_json(js, 'umail_get')
            return int(js['count']), js['umail']

    def umail_get_iter(self, folder_id=None, unread=0):
        from_ = 0
        count = 1
        while from_ < count:
            count, umail_dct = self.umail_get(folder_id, unread,
                                        from_, limit, umail_id)
            for umail_id, umail_unit_dct in umail_dct.items():
                yield umail_id, umail_unit_dct    

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

    # APENDIX
    def find_post(self, pattern, type_='diary', juser_id=None, shortname=None):
        post_list = []
        comment_list = []
        for _, data, comments in self.post_and_comments(type_=type_, \
                                    juser_id=juser_id, shortname=shortname):
            message_data = data.get('message_html', None) or data.get('message_src', None)
            if message_data and pattern in message_data:
                u = "http://{shortname}.diary.ru/p{postid}.htm".format(shortname=data['shortname'], postid=data['postid'])
                post_list.append(u)
                for c in comments:
                    comment_data = c.get('message_html', None) or c.get('message_src', None)
                    if comment_data and pattern in c['message_html']:
                        uu = u + '#' + c['commentid']
                        comment_list.append(uu)
        import itertools.chain
        return [x for x in itertools.chain(post_list, comment_list)]


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
        for post_id, post_data, comments in d_api\
                        .post_and_comments(type_='by_id', ids=['201289904',]):
            print(post_id)
