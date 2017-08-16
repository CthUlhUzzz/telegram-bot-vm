from telegram_bot_vm.actions import *
from telegram_bot_vm.machine import BotVM

token = None
with open('test_token') as t:
    token = t.read()

actions = [SendMessageAction('Hello, what is your name?'),
           GetInputAction('name'),
           SendMessageAction('{{name}}, ti pidor!'),
           SendMessageAction('Again? (yes/no)'),
           GetInputAction('again'),
           ForwardToPositionAction(0, variable_name='again', condition_regex='yes'),
           SendMessageAction('Do vstrechi pidor!')]
vm = BotVM()
vm.run(actions, token)
