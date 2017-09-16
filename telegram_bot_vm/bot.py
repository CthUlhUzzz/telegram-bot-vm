from multiprocessing import Queue
from telegram import Bot as TelegramBot
from .machine import BotVM


class Bot:
    def __init__(self, actions, state, additioanal_properties=None,
                 init_variables=None, stopped_message='Bot stopped, please /start to connect!'):
        self.mailing_queue = None
        self.process = None
        self.init_variables = init_variables
        self.additional_properties = additioanal_properties
        self.state = state
        self.actions = actions
        self.stopped_message = stopped_message

    def stop(self):
        if self.process is not None:
            self.process.terminate()
            self.process = None
            self.mailing_queue = None

    def mail_all(self, message):
        if self.mailing_queue is not None:
            self.mailing_queue.put_nowait(message)

    def run(self, token):
        bot = TelegramBot(token)
        self.mailing_queue = Queue()
        self.process = BotVM.run(self.actions, bot, self.state, self.mailing_queue,
                                 self.additional_properties or {}, self.init_variables or {},
                                 self.stopped_message)
