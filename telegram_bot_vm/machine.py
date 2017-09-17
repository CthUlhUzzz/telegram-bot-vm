from telegram.error import TimedOut
from multiprocessing import Process

TELEGRAM_API_LATENCY = 2


class VMContext:
    def __init__(self, actions, additional_properties, init_variables):
        self.position = 0
        self.actions = actions
        self.input = None
        self.variables = init_variables
        for k, v in additional_properties.items():
            self.__dict__[k] = v

    def run_next(self):
        return self.actions[self.position].exec(self)

    @property
    def active_action(self):
        return self.actions[self.position]


class BotVM:
    @classmethod
    def run(cls, actions, bot, state, mailing_queue,
            additional_properties=None, init_variables=None,
            stopped_message=None, latency=TELEGRAM_API_LATENCY):
        p = Process(target=cls._worker, args=(actions, bot, state, mailing_queue, additional_properties or {},
                                              init_variables or {}, stopped_message, latency))
        p.start()
        return p

    @staticmethod
    def _worker(actions, bot, state, mailing_queue, additional_properties, init_variables, stopped_message, latency):
        chats = {c: VMContext(actions, additional_properties, init_variables) for c in
                 state.chats}  # chat_id to context mapping
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
                            chats[chat_id] = VMContext(actions, additional_properties, init_variables)
                            state.add_chat(chat_id)
                            state.increment_visits()
                        else:
                            if stopped_message is not None:
                                bot.send_message(chat_id, stopped_message)
            except TimedOut:
                pass

            # Execute actions
            mailing_messages = None
            if not mailing_queue.empty():
                mailing_messages = mailing_queue.get()
            for chat_id, con in chats.copy().items():
                if mailing_messages is not None:
                    for message in mailing_messages:
                        bot.send_message(chat_id, message)
                if not con.position < len(con.actions):
                    result = con.run_next()
                    if result is not None:
                        for message in result:
                            bot.send_message(chat_id, message)
                    con.input = None
