import re


def format_message(message, variables):
    for m in re.finditer('{{(\w{1,100})}}', message):
        var = m.group(1)
        variable = variables.get(var)
        if variable is not None:
            message = message.replace('{{%s}}' % var, variable)
    return message
