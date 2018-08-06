#!/usr/bin/env python3

import os
import threading

from bencode import bdecode


class TorrentParser(object):
    # 构造函数
    def __init__(self, file_path_name):
        self.file_path_name = file_path_name
        with open(file_path_name, 'rb') as fObj:
            self.fileDic = bdecode(fObj.read())

    # 获得tracker服务器的URL列表
    def get_announce_list(self):
        retval = []

        if 'announce-list' in self.fileDic:
            arr = self.fileDic['announce-list']

            for childArr in arr:
                if isinstance(childArr, list):
                    for item in childArr:
                        retval.append(item.decode('utf-8', 'ignore'))
                else:
                    retval.append(childArr.decode('utf-8', 'ignore'))

        return retval


def socket_is_opened(url, tracker_file):
    from urllib.parse import urlparse
    result = urlparse(url)

    import socket
    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sk.settimeout(5)
    try:
        if result.port is None:
            if result.scheme is 'http':
                sk.connect(result.hostname, 80)
            if result.scheme is 'https':
                sk.connect(result.hostname, 443)
        else:
            sk.connect((result.hostname, result.port))
        print(url + ' is alive!')
        try:
            with open(tracker_file, 'a') as file_write:
                file_write.write(url + '\n')
        except IOError as e:
            print(e)
    except socket.error:
        print(url + ' is not alive!')
    sk.close()


def duplicate_removal(tracker_file):
    try:
        with open(tracker_file, 'r+') as file:
            tracker_list_old = []
            for i in file.readlines():
                if i != '\n' and i != '\r\n':
                    ii = i.strip()
                    tracker_list_old.append(ii)
            file.seek(0, 0)
            file.truncate()
            tracker_list_new = []
            for j in tracker_list_old:
                if j not in tracker_list_new:
                    tracker_list_new.append(j)
                    file.writelines(j + '\n')
    except IOError as e:
        print(e)


def torrent_parser(file_path_name, tracker_file):
    tp = TorrentParser(file_path_name)
    print(tp.get_announce_list())

    file_write_thread_list = []
    for i in range(len(tp.get_announce_list())):
        file_write = threading.Thread(target=socket_is_opened,
                                      args=(tp.get_announce_list()[i], tracker_file, ))
        file_write_thread_list.append(file_write)
        file_write.start()
        for j in range(0, len(file_write_thread_list)):
            file_write_thread_list[j].join()


def main():
    path = "D:\\下载文件夹"
    tracker_file = 'tracker.txt'
    file_list = os.listdir(path)
    torrent_file_list = []
    for i in range(0, len(file_list)):
        if os.path.splitext(file_list[i])[-1][1:] == 'torrent':
            print(file_list[i])
            torrent_file_list.append(path + '\\' + file_list[i])

    t_thread_list = []
    for j in range(0, len(torrent_file_list)):
        t = threading.Thread(target=torrent_parser, args=(torrent_file_list[j], tracker_file, ))
        t_thread_list.append(t)
        t.start()
    for k in range(0, len(t_thread_list)):
        t_thread_list[k].join()

    duplicate_removal(tracker_file)


main()
