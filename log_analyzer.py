#!/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';
import sys
import os
import gzip
# import io
import re

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}

def findlatestlog(config):
    ### Проверить существование директории с помощью path.exists
    ### Проверить наличие файлов логов в директории
    ### Структура переменных (аттрибуты)
    # Выполняет поиск последнего файла с логами в LOG_DIR по дате в имени файла
    for dirpath, dirnames, filenames in os.walk(config['LOG_DIR']):
        maxdate = []
        maxfilename = ''
        maxfilenamepath = ''
        for filename in filenames:
            filedate = re.findall(r'\d{8}',filename)
            if filedate > maxdate:
                maxdate = filedate
                maxfilename = filename
                maxfilenamepath = dirpath
    return (maxfilename, maxfilenamepath)


def main():
    # Если есть ключи во время запуска приложения, открыть файл и обновить ключи
    if '--config' in sys.argv:
        print('This is sysargv', sys.argv[sys.argv.index('--config') + 1], 'end')
    #Поиск последнего файла в LOG_DIR по дате в имени файла
    print(findlatestlog(config))
    # Открытие файла с логом с помощью gzip.open или с помощью os.open, если файл простой
    
    try:
        # gzip.open(filename, mode='rb', compresslevel=9, encoding=None, errors=None, newline=None)
        logfile = gzip.open(config['LOG_DIR'] + '/nginx-access-ui.log-20170630.gz', mode='rt')
    except:
        logfile = os.open(config['LOG_DIR'] + '/nginx-access-ui.log-20170630.gz', mode='rt')
    #Чтение по строке (должен быть генератор)
    #print(re.split(r'[[,],-]',logfile.readline()))
    print('\n')
    print(logfile.readline())
    return 0

if __name__ == "__main__":
    main()
