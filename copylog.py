#!/usr/bin/env python
# -*- coding: utf-8 -*-


def main(args):
    """
    Создание копии лога с помощью команды:
    python3 copylog.py <original file name> <copy file name> <log size to copy: integer>

    example:
    python3 copylog.py ./log/nginx-access-ui.log-20170630.gz ./log/nginx-access-ui.log-20170631.gz 1000
    """
    originalname = args[1]
    copyname = args[2]
    logsize = int(args[3])
    if originalname.endswith(".gz"):
        file1 = gzip.open(originalname, mode = "rt", encoding = "UTF_8")
        file2 = gzip.open(copyname, mode = "wt", encoding = "UTF_8")
    else:
        file1 = open(originalname, mode = "rt", encoding = "UTF_8")
        file2 = open(copyname, mode = "wt", encoding = "UTF_8")
    i = 0
    while i < logsize:
        line = file1.readline()
        file2.write(line)
        i += 1
    file1.close()
    file2.close()
    print("Копирование завершено успешно.")
    return 0

if __name__ == '__main__':
    import sys
    import os
    import gzip
    sys.exit(main(sys.argv))
