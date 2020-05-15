import logging

from modules.pytg.ModulesLoader import ModulesLoader

class DigestManager:
    def __init__(self):
        self.digesters = {}

    def add_digester(self, request_type, digester):
        self.digesters[request_type] = digester

    def digest(self, bot, chat_id, message_id, request_id, response):
        logging.info("Digesting request {} (Response: {})".format(request_id, response))

        # Load request's data
        data_manager = ModulesLoader.load_manager("data")
        request_data = data_manager.load_data("requests", request_id, module="requests")

        # Call the digester function
        self.digesters[request_data["type"]](bot, chat_id, message_id, request_id, request_data, response)

        # Delete request's data
        data_manager.delete_data("requests", request_id, module="requests")

        # Remove reply markup
        try:
            bot.editMessageReplyMarkup(
                chat_id = chat_id,
                message_id = message_id,
                reply_markup = None
            )
        except:
            logging.warning("Unable to remove reply markup. Digester may've altered the original message")