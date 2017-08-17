import random
import re
import string

ALPHABET = string.ascii_lowercase + string.ascii_uppercase + string.digits


def random_string(length=16):
    return ''.join(random.choice(ALPHABET) for _ in range(length))


def format_message(message, variables):
    for m in re.finditer('{{(\w{1,100})}}', message):
        var = m.group(1)
        variable = variables.get(var)
        if variable is not None:
            message = message.replace('{{%s}}' % var, variable)
    return message


ZSET = 0
HASH = 1


def redis_iter(redis, key, type):
    """ Helper generator for iterating sequences """
    assert type in (ZSET, HASH)
    index = 0
    scan_function = None
    if type == ZSET:
        scan_function = redis.zscan
    elif type == HASH:
        scan_function = redis.hscan
    while True:
        index, elements = scan_function(key, index)
        if isinstance(elements, dict):
            for e in elements.items():
                yield e
        else:
            for e in elements:
                yield e[0]
        if index == 0:
            break
