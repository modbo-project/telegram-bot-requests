import yaml, telegram, logging

from modules.pytg.Manager import Manager

from modules.pytg.ModulesLoader import ModulesLoader

from .DigestManager import DigestManager

class RequestsManager(Manager):
    @staticmethod
    def initialize():
        RequestsManager.__instance = RequestsManager()

        return

    @staticmethod
    def load():
        return RequestsManager.__instance

    def __init__(self):
        self.digest_manager = DigestManager()

    def add_digester(self, request_type, digester):
        self.digest_manager.add_digester(request_type, digester)

    def create_request(self, bot, author_chat_id, request_type, entries, lang=None):
        logging.info("Creating request from {} of type {} with entries: {}".format(author_chat_id, request_type, entries))

        if not lang:
            config_manager = ModulesLoader.load_manager("config")
            lang_settings = config_manager.load_settings_file("lang")
            lang = lang_settings["default"]

        # Generate request's ID
        idgen_manager = ModulesLoader.load_manager("idgen")
        request_id = idgen_manager.generate_id("requests")

        # Save request data
        request_data = self.__save_request_data(request_id, author_chat_id, request_type, entries)

        # Send message to admins
        self.__send_request_message(bot, request_id, request_data, lang)

    def __data_replace(self, text, entries):
        for key in entries.keys():
            text = text.replace("[{}]".format(key), str(entries[key]))

        return text

    def __send_request_message(self, bot, request_id, request_data, lang):
        routes = self.__load_routes()

        request_type = request_data["type"]

        # Load routes and format
        chat_id = routes[request_type]
        request_format = self.__load_format(request_type, lang)

        # Replace entries in text
        text = self.__data_replace(request_format["text"], request_data["entries"])

        # Load reply markup
        menu_manager = ModulesLoader.load_manager("menu")

        menu_meta = request_data["entries"]
        menu_meta["request_id"] = request_id

        reply_markup = menu_manager.create_reply_markup(request_format["reply_markup_id"], lang, meta = menu_meta)

        bot.sendMessage(
            chat_id = chat_id,
            text = text,
            reply_markup = reply_markup,
            parse_mode = telegram.ParseMode.MARKDOWN
        )

    def __save_request_data(self, request_id, author_chat_id, request_type, entries):
        data_manager = ModulesLoader.load_manager("data")

        request_data = data_manager.create_data("requests", request_id)

        request_data["author"] = author_chat_id
        request_data["type"] = request_type 
        request_data["entries"] = entries 

        data_manager.save_data("requests", request_id, request_data)

        return request_data

    def __load_routes(self):
        file_path = "{}/routes.yaml".format(ModulesLoader.get_module_content_folder("requests"))

        return yaml.safe_load(open(file_path, 'r'))

    def __load_format(self, format_id, lang):
        file_path = "{}/formats/{}/{}.yaml".format(ModulesLoader.get_module_content_folder("requests"), lang, format_id)

        return yaml.safe_load(open(file_path, 'r'))
