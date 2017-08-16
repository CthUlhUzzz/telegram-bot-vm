from telegram import Bot
from telegram.error import TimedOut
from multiprocessing import Process


class BotVM:
    def __init__(self):
        self.working_bots = []

    def run(self, actions, token, operators=None, stopped_message='Bot stopped, please /start to connect!'):
        bot = Bot(token)
        p = Process(target=self._worker_new, args=(actions, bot, operators, stopped_message))
        p.start()
        self.working_bots.append(p)

    @staticmethod
    def _worker_new(actions, bot, operators_manager, stopped_message):
        chats = {}  # chat_id to context mapping
        update_id = None
        try:
            update_id = bot.get_updates()[0].update_id
        except IndexError:
            pass
        while True:
            # Working with incoming messages
            updates = {}
            try:
                for update in bot.get_updates(offset=update_id, allowed_updates=['message'], read_latency=1):
                    update_id = update.update_id + 1
                    text = update.message.text
                    chat_id = update.message.chat_id
                    if chat_id not in chats:
                        if text == '/start':
                            chats[update.message.chat_id] = VMContext(actions)
                        else:
                            bot.send_message(chat_id, stopped_message)
                    else:
                        if text == '/stop':
                            chats[update.message.chat_id].stopped = True
                        else:
                            if chat_id not in updates:
                                updates[chat_id] = [text]
                            else:
                                updates[chat_id].append(text)
            except TimedOut:
                pass

            # Working with operators
            # operators_manager.update()

            # Working with contexts
            result = []
            for chat_id, con in chats.copy().items():
                if not con.stopped and con.position < len(con.actions):
                    if con.active_action.input_required:
                        if chat_id in updates:
                            for text in updates[chat_id]:
                                con.input = text
                                result.append((chat_id, con.run_next()))
                    else:
                        result.append((chat_id, con.run_next()))
                else:
                    bot.send_message(chat_id, stopped_message)
                    del chats[chat_id]
            for r in filter(lambda x: x[1] is not None, result):
                bot.send_message(*r)


class VMContext:
    def __init__(self, actions, operator_manager=None):
        self.position = 0
        self.actions = actions
        self.input = None
        self.stopped = False
        self.variables = {}
        self.operator_manager = operator_manager

    def run_next(self):
        return self.actions[self.position].exec(self)

    @property
    def active_action(self):
        return self.actions[self.position]
