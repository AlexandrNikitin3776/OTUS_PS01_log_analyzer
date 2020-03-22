#!/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip'
#                     '[$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for"'
#                     '"$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';


import sys
import os
import gzip
import re
import statistics
import json
import logging


config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
    "CONFIG_DIR": "./config",
    "LOGGING_FILE": "./monitoring.log",
    "ERROR_THRESHOLD_PERCENT": 10
}


log_format = "(?P<remote_addr>.*)\s(?P<remote_user>.*)\s\s" \
    "(?P<http_x_real_ip>.*)\s\[(?P<time_local>.*)\]\s\"" \
    "(?P<request>.*)\"\s(?P<status>.*)\s(?P<bytes_sent>.*)\s\"" \
    "(?P<http_referer>.*)\"\s\"(?P<http_user_agent>.*)\"\s\"" \
    "(?P<http_x_forwarded_for>.*)\"\s\"(?P<http_X_REQUEST_ID>.*)\"\s\"" \
    "(?P<http_X_RB_USER>.*)\"\s(?P<request_time>.*)"


request_format = "(?P<request_method>.*)\s(?P<request_url>.*)\s" \
                 "(?P<request_protocol>.*)"


def loggingsetup(config):
    """
    Настройка логирования.
    Если не указан параметр LOGGING_FILE в config, лог пишется в stdout
    """
    if config.get("LOGGING_FILE") is None:
        loggingfilename = None
    else:
        if config["LOGGING_FILE"] == "":
            loggingfilename = None
        else:
            loggingfilename = config["LOGGING_FILE"]
    logging.basicConfig(filename=loggingfilename, filemode="w",
                        format="[%(asctime)s] %(levelname).1s %(message)s",
                        datefmt="%Y.%m.%d %H:%M:%S", level=logging.INFO)
    return 0


def configupdate(config, arglist):
    """ Обновление файла конфигурации """
    # Чтение данных конфигурации вида json из файла
    if "--config" in arglist:
        try:
            configfile = open(config["CONFIG_DIR"]
                              + arglist[arglist.index("--config") + 1],
                              mode="r", encoding="utf_8")
            data = json.load(configfile)
            configfile.close()
        except FileNotFoundError:
            return 1
    # Обновление конфигурации в словаре config
    newconfig = {}
    for configkey in config:
        if data.get(configkey) is None:
            if data[configkey] is not None:
                newconfig[configkey] = config[configkey]
        else:
            newconfig[configkey] = data[configkey]
    return newconfig


def findlatestlog(config):
    """
    Ищет лог с максимальной датой в имени файла в папке LOG_DIR
    В случае отсутствия файлов в директории возвращает 0.
    Возвращает кортеж вида (дата, путь к файлу)
    """
    # Если не существует директории для с логами, завершаем программу
    if not os.path.isdir(config["LOG_DIR"]):
        return 1

    # Выполняет поиск последнего файла с логами
    # в LOG_DIR по дате в имени файла
    for dirpath, dirnames, filenames in os.walk(config["LOG_DIR"]):
        maxdate = ""
        maxfilename = ""
        maxfilepath = ""
        for filename in filenames:
            try:
                filedate = re.match(r"nginx\-access\-ui\.log\-"
                                    "(?P<filedate>\d{8})(\.gz)?", filename). \
                                    group("filedate")
                if filedate > maxdate:
                    maxdate = filedate
                    maxfilename = filename
                    maxfilepath = dirpath
            except:
                continue

    # В случае отсутствия файлов логов завершаем программу
    if maxfilename == "":
        return 2
    maxdate = maxdate[:4] + "." + maxdate[4:6] + "." + maxdate[6:8]
    return (maxdate, maxfilepath + "/" + maxfilename)


def readlog_gen(logfilepathname):
    """
    Генератор. Возвращает строки из файла с логами.
    logfilepathname - путь к файлу с именем файла.
    """
    # Чтение файла в зависимости его типа: gzip или простой
    if logfilepathname.endswith(".gz"):
        logfile = gzip.open(logfilepathname, mode="rt", encoding="utf_8")
    else:
        logfile = open(logfilepathname, mode="rt", encoding="utf_8")
    for line in logfile:
        yield line
    logfile.close()


def parselog(line, log_format, request_format):
    """
    Возвращает словарь с необходимыми для анализа данными:
    request_url и request_time
    """
    result = {}
    m = re.match(log_format, line)
    try:
        result["request_url"] = re.match(request_format, m.group("request")). \
                                         group("request_url")
        result["request_time"] = float(m.group("request_time"))
    except AttributeError:
        return 1
    return result


def analyzelog(latestlogpath, log_format, request_format, config):
    """
    Возвращает словарь url из словарей с ключами:
    count - сколько раз встречается URL, абсолютное значение,
    count_perc - сколько раз встречается URL, в процентнах относительно
        общего числа запросов,
    time_sum - суммарный $request_time для данного URL'а, абсолютное
        значение,
    time_perc - суммарный $request_time для данного URL'а, в процентах
        относительно общего $request_time всех запросов,
    time_avg - средний $request_time для данного URL'а,
    time_max - максимальный $request_time для данного URL'а,
    time_med - медиана $request_time для данного URL'а
    """
    # Генератор чтения лога
    latestlog = readlog_gen(latestlogpath)
    # Начальные значения переменных
    result = {}
    totalcount = 0
    totaltime = 0
    errorlines = 0
    # Сбор $request_time для каждого URL
    for line in latestlog:
        pars = parselog(line, log_format, request_format)
        if pars == 1:
            totalcount += 1
            errorlines += 1
            continue
        if result.get(pars["request_url"]) is None:
            result[pars["request_url"]] = {}
            result[pars["request_url"]]["request_time"] = [pars["request_time"]]
        else:
            result[pars["request_url"]]["request_time"].append(pars["request_time"])
        totalcount += 1
        totaltime += pars["request_time"]
    # Рассчёт необходимых значений
    for url in result:
        result[url]["count"] = len(result[url]["request_time"])
        result[url]["count_perc"] = round(result[url]["count"]
                                          / totalcount * 100, 3)
        result[url]["time_sum"] = round(sum(result[url]["request_time"]), 3)
        result[url]["time_perc"] = round(result[url]["time_sum"]
                                         / totaltime * 100, 3)
        result[url]["time_avg"] = round(result[url]["time_sum"]
                                        / result[url]["count"], 3)
        result[url]["time_max"] = max(result[url]["request_time"])
        result[url]["time_med"] = \
            round(statistics.median(result[url]["request_time"]), 3)
        result[url]["url"] = url
        # Удаление списка с $request_time
        result[url].pop("request_time")
    logging.info("Анализ логов завершён.\n"
                 "Обработано %d логов.\n"
                 "Суммарное request time логов составляет %.3f.\n"
                 "Ошибок парсинга %d." % (totalcount, totaltime, errorlines))

    if config.get("ERROR_THRESHOLD_PERCENT") is not None and totalcount > 0:
        if errorlines / totalcount * 100 >= config["ERROR_THRESHOLD_PERCENT"]:
            return 1
    return result


def reportsizing(parsedlog, config):
    """  Формирование отчёта размером REPORT_SIZE"""
    result = list(parsedlog.values())
    result.sort(key=lambda x: x["time_sum"], reverse=True)
    return result[:config["REPORT_SIZE"]]


def writereport(analyzeresult, reportpath, config):
    # Если не существует директории для отчетов, создать её
    if not os.path.isdir(config["REPORT_DIR"]):
        os.mkdir(config["REPORT_DIR"])
        logging.info("Создана директория отчётов %s." % config["REPORT_DIR"])

    # Подготовка данных для записи
    reporttext = str(reportsizing(analyzeresult, config)).replace("\'", "\"")

    # Создание файла отчёта из шаблона
    reporttemplate = open("report.html", mode="rt", encoding="utf_8")
    report = open(reportpath, mode="wt", encoding="utf_8")
    report.write(reporttemplate.read().replace("$table_json", reporttext))
    reporttemplate.close()
    report.close()
    return 0


def main(args, config):
    try:
        # Чтение конфигурации из другого файла через --config
        # Если есть ключи во время запуска приложения,
        # открыть файл и обновить ключи
        if "--config" in args:
            newconfig = configupdate(config, args)
            if newconfig == 1:
                sys.exit("Файл конфигурации не найден")
            else:
                config = newconfig

        # Настройка логирования
        loggingsetup(config)

        # Поиск последнего файла в LOG_DIR по дате в имени файла
        logging.info("Начало программы анализа логов nginx.")
        latestlogpath = findlatestlog(config)
        if latestlogpath == 1:
            logging.error("Директории LOG_DIR \"%s\" не существует."
                          % config["LOG_DIR"])
            sys.exit("Директории с логами не существует.")
        elif latestlogpath == 1:
            logging.error("Директория LOG_DIR \"%s\" пустая."
                          % config["LOG_DIR"])
            sys.exit("Логов в директории" + config["LOG_DIR"]
                     + "не найдено.")
        logging.info("Найден лог с именем \"%s\"" % latestlogpath[1])

        # Если существует отчет для лога на последнюю дату, завершить программу
        reportpath = "".join([config["REPORT_DIR"], "/report-",
                              latestlogpath[0],".html"])
        if os.path.isfile(reportpath):
            logging.info("Работа программы окончена. Отчёт от %s "
                         "с именем %s уже существует."
                         % (latestlogpath[0], reportpath))
            sys.exit("Файл отчёта для последнего лога от %s существует."
                     % latestlogpath[0])

        # Анализ логов
        logging.info("Начинаю анализ.")
        analyzeresult = analyzelog(latestlogpath[1], log_format, request_format, config)
        if analyzeresult == 1:
            logging.error("Число ошибок парсинга превысило порог.")
            sys.exit("Число ошибок парсинга превысило порог.")

        # Запись результатов анализа
        writereport(analyzeresult, reportpath, config)
        logging.info("Создан отчёт %s.\nРабота программы завершена успешно."
                     % reportpath)
    except BaseException:
        pass
    except:
        logging.exception("Анализ прерван. Трейсбек", exc_info=True)
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv, config))
