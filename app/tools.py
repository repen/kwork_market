import logging, os, hashlib

def hash_(string):
    return hashlib.sha1(string.encode()).hexdigest()

def log(*args, **kwargs):
    name_logger = args[0]
    path_file   = args[1]
    write = kwargs.setdefault("write", False)
    # создаём logger
    logger = logging.getLogger(name_logger)
    logger.setLevel( logging.DEBUG )

    # создаём консольный handler и задаём уровень
    if not write:
        ch = logging.StreamHandler()
    else:
        # log write in disk
        ch = logging.FileHandler("/".join( [ os.getcwd(), path_file] ))

    ch.setLevel(logging.DEBUG)

    # создаём formatter
    formatter = logging.Formatter('%(asctime)s : line %(lineno)-3s : %(name)s : %(levelname)s : %(message)s')
    # %(lineno)d :
    # добавляем formatter в ch
    ch.setFormatter(formatter)

    # добавляем ch к logger
    logger.addHandler(ch)
    # Api
    # logger.debug('debug message')
    # logger.info('info message')
    # logger.warn('warn message')
    # logger.error('error message')
    # logger.critical('critical message')
    return logger

def divide_message(text):
    rows = text.split("=" * 20)
    rows = list(filter(lambda x : x, rows))
    return rows

if __name__ == '__main__':
    with open("text.txt") as f:
        data = f.read()
    res = divide_message(data)
    print(res)