from telegram import Bot
from telegram.error import TimedOut
from multiprocessing import Process


class BotVM:
    @classmethod
    def run(cls, actions, token, add_properties=None, init_vals=None,
            stopped_message='Bot stopped, please /start to connect!', latency=2):
        bot = Bot(token)
        p = Process(target=cls._worker, args=(actions, bot, add_properties or {},
                                              init_vals or {}, stopped_message, latency))
        p.start()
        return p

    @staticmethod
    def _worker(actions, bot, add_properties, init_vals, stopped_message, latency):
        chats = {}  # chat_id to context mapping
        update_id = None
        try:
            update_id = bot.get_updates()[0].update_id
        except IndexError:
            pass
        while True:
            # Prepare contexts
            try:
                for update in bot.get_updates(offset=update_id, allowed_updates=['message'], read_latency=latency):
                    update_id = update.update_id + 1
                    text = update.message.text
                    chat_id = update.message.chat_id
                    if chat_id not in chats:
                        if text == '/start':
                            chats[update.message.chat_id] = VMContext(actions, add_properties, init_vals)
                        else:
                            bot.send_message(chat_id, stopped_message)
                    else:
                        if text == '/stop':
                            chats[update.message.chat_id].stopped = True
                        else:
                            if chat_id in chats:
                                chats[chat_id].input = text
            except TimedOut:
                pass

            # Execute actions
            for chat_id, con in chats.copy().items():
                if not con.stopped and con.position < len(con.actions):
                    result = con.run_next()
                    if result is not None:
                        bot.send_message(chat_id, result)
                    con.input = None
                else:
                    bot.send_message(chat_id, stopped_message)
                    del chats[chat_id]


class VMContext:
    def __init__(self, actions, add_properties, init_vals):
        self.position = 0
        self.actions = actions
        self.input = None
        self.stopped = False
        self.variables = init_vals
        for k, v in add_properties.items():
            self.__dict__[k] = v

    def run_next(self):
        return self.actions[self.position].exec(self)

    @property
    def active_action(self):
        return self.actions[self.position]
