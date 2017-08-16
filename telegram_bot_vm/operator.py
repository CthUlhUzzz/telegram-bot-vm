class OperatorsManager:
    def __init__(self, redis_connection, operators):
        self.operators = {token: operator for token, operator in operators}
        self.pubsub = redis_connection.pubsub(ignore_subscribe_messages=True)
        self.pubsub.subscribe('operator_connected', 'operator_disconnected')
        self.available_operators = set()
        self.conversations = {}

    def get_free_operator(self):
        """ return most free operator token """
        min_conversations = 0
        operator = None
        for token, conversations in self.conversations.items():
            conversations_count = len(conversations)
            if min_conversations <= conversations_count:
                min_conversations = conversations_count
                operator = token
        return operator

    def get_conversation(self):
        """ return new conversation if free operator available else None """
        if len(self.available_operators) != 0:
            operator = self.get_free_operator()
            if operator is not None:
                self.pubsub.publish('conversation_started:')
            # return conversation

    # def _get_messages(self):
    #     pass
    # def release_operator(self):
    #     pass
    #
    # def _send_messages(self):
    #     pass

    def update(self):
        """ Update information about available operators """
        while True:
            message = self.pubsub.get_message()
            if message is not None:
                if message.type == 'message':
                    channel = message.channel.decode()
                    message = message.data.decode()
                    if channel == 'operator_connected':
                        self.available_operators.add(message)
                    elif channel == 'operator_disconnected':
                        if message in self.available_operators:
                            self.available_operators.remove(message)
            else:
                break


                # class Conversation:
                #     def __init__(self, id_):
                #         self.id = id_
                #         self.connected=False

                # def send_message(self):
                #     pass

                # def get_message(self):
                #     pass


class Operator:
    def __init__(self, id_, redis_pubsub):
        self.id = id_
        self.redis = redis_pubsub

    def start(self):
        self.redis.subscribe('messages:to_user:%s' % self.token, )

    @property
    def token(self):
        pass

    @token.setter
    def token(self):
        pass

    def send_message(self):
        pass

    def receive_message(self):
        self.redis.get_message()

    def stop(self):
        self.redis.subscribe('messages:to_user:%s' % self.token)

    def __eq__(self, other):
        return self.id == other.id
