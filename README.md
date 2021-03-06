# OTUS_PS01_log_analyzer
Решение домашнего задания про анализ логов веб-интерфейса из файлов вида `nginx-access-ui.log-20170630.gz`.

## Основная функциональность:
1. Скрипт обрабатывает последний лог из `LOG_DIR`.
2. Вычисляет необходимые поля для отчёта и считает статистику по url.
3. Выводит отчёт размером `REPORT_SIZE` URL'ов в файл вида `report-2017.06.30.html` в `REPORT_DIR`.


## Конфигурация
Конфигурация осуществляется путём передачи файла формата json через `--config`.

* "REPORT_SIZE" - количество ссылок в отчёте (по умолчанию - 1000);
* "REPORT_DIR" - путь для сохранения отчётов (по умолчанию - "./reports");
* "LOG_DIR" - путь для поиска логов (по умолчанию - "./log");
* "CONFIG_DIR" - путь для файлов кофигурации (по умолчанию - "./config");
* "LOGGING_FILE" - путь файла логгирования (по умолчанию - "./monitoring.log");
* "ERROR_THRESHOLD_PERCENT" - ограничение на количество ошибок в файле (по умолчанию - 10).

## Поля отчёта
* count - сколько раз встречается URL, абсолютное значение;
* count_perc - сколько раз встречается URL, в процентнах относительно общего числа запросов;
* time_sum - суммарный \$request_time для данного URL'а, абсолютное значение;
* time_perc - суммарный \$request_time для данного URL'а, в процентах относительно общего $request_time всех запросов;
* time_avg - средний \$request_time для данного URL'а;
* time_max - максимальный \$request_time для данного URL'а;
* time_med - медиана \$request_time для данного URL'а.

## Мониторинг:
В процессе работы скрипт пишет лог в файл monitoring.log.

###### После отработки замечаний code_review_01
