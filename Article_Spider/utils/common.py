# -*- coding: utf-8 -*-
import hashlib

__author__ = "Eilene HE"
__date__ = '2017/10/4 21:40'


def get_md5(url):
    if isinstance(url, str):
        url = url.encode('utf-8')

    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


if __name__ == '__main__':

    print(get_md5('http://www.baidu.com'))