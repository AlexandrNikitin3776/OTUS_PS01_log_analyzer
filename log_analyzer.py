#!/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';


import sys
import os
import gzip
import io
import re
import json


config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}


def configupdate(config, arglist, path = './'):
    """ Обновление файла конфигурации """
    # Чтение данных json из файла
    if '--config' in arglist:
        try:
            configfile = open(path + arglist[arglist('--config') + 1], mode='r')
            data = json.load(configfile)
            configfile.close()
        except FileNotFoundError:
            sys.exit("Файл конфигурации не найден")
    # Обновление конфигурации в словаре config
    newconfig = {}
    for configkey in config:
        if config.get(configkey) == None:
            newconfig[configkey] = config[configkey]
        else:
            newconfig[configkey] = data[configkey]
    return newconfig


def findlatestlog(config):
    """
    Ищет лог с максимальной датой в имени файла в папке LOG_DIR
    В случае отсутствия файлов в директории возвращает 0.
    Возвращает путь к файлу.
    """
    ### Проверить существование директории с помощью path.exists
    ### Проверить наличие файлов логов в директории
    # Логов в директории может не быть. Вывести сообщение и завершить программу
    ### Структура переменных (аттрибуты)
    # Выполняет поиск последнего файла с логами в LOG_DIR по дате в имени файла
    for dirpath, dirnames, filenames in os.walk(config['LOG_DIR']):
        maxdate = []
        maxfilename = ''
        maxfilepath = ''
        for filename in filenames:
            filedate = re.findall(r'\d{8}',filename)
            if filedate > maxdate:
                maxdate = filedate
                maxfilename = filename
                maxfilepath = dirpath
    if maxfilename == '':
        return 0
    return maxfilepath + '/' + maxfilename


def readlog(logfilepathname):
    """
    Генератор. Возвращает строки из файла с логами.
    logfilepathname - путь к файлу с именем файла.
    """
    # Чтение файла в зависимости его типа: gzip или простой
    if logfilepathname.endswith('.gz'):
        logfile = gzip.open(config['LOG_DIR'] + '/nginx-access-ui.log-20170630.gz', mode='rt')
    else:
        logfile = open(config['LOG_DIR'] + '/nginx-access-ui.log-20170630.gz', mode='rt')
    for line in logfile:
        yield line
    logfile.close()


def main(config):
    '''
        отчет должен содержать count, count_perc, time_sum, time_perc, time_avg, time_max, time_med
    '''
    # Считать конфиг из другого файла через --config
    # Поиск последнего по дате в имени файла лога
    # Логов в директории может не быть. Вывести сообщение и завершить программу
    # Если удачно обработал, то при повторном запуске, если есть файл отчета, оставить как есть

    # Прочесть лог
    # Провести анализ и парсить нужные поля
    # Подготовка отчета в шаблон во временный файл
    # Подстановка в шаблон и переименование файла
    # Перенести к себе jquery

    # В процессе работы должен вестись файл лога через библиотеку logging. Использовать logging.basicConfig
    # Уровни info, error, exception
    return 0

if __name__ == "__main__":
    #main(config)
    # Считать конфиг из другого файла через --config
    # Если есть ключи во время запуска приложения, открыть файл и обновить ключи
    if '--config' in sys.argv:
        config = configupdate(config, sys.argv)

    #Поиск последнего файла в LOG_DIR по дате в имени файла
    latestlog = findlatestlog(config)
    print(latestlog)
    #### Если существует отчет с таким именем, завершаем программу
    print(next(readlog(latestlog)))
        
        
