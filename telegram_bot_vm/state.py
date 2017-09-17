class BotState:
    @property
    def chats(self):
        """ List of active chats """
        raise NotImplementedError

    def add_chat(self, chat):
        """ Add new chat """
        raise NotImplementedError

    def increment_visits(self):
        """ Increment bot visits """
        raise NotImplementedError
