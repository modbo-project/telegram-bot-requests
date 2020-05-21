import yaml, telegram, logging

from telegram import InputMediaPhoto

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
            lang_settings = config_manager.load_settings_file("requests", "lang")
            lang = lang_settings["default"]

        # Generate request's ID
        request_id = self.__generate_request_id()

        # Save request data
        request_data = self.__save_request_data(request_id, author_chat_id, request_type, entries)

        # Send message to admins
        self.__send_request_message(bot, request_id, request_data, lang)

        return request_id

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

        media_info = None
        if "media" in request_format.keys():
            media_info = request_format["media"]

        if media_info:
            if media_info["type"] == "photo":
                if media_info["identifier"] == "local_path":
                    photo_data = open(request_data["entries"][media_info["entry_id"]], "rb")
                else:
                    photo_data = request_data["entries"][media_info["entry_id"]]

                bot.sendPhoto(
                    chat_id = chat_id,
                    caption = text,
                    photo = photo_data,
                    reply_markup = reply_markup,
                    parse_mode = telegram.ParseMode.MARKDOWN
                )
        else:
            bot.sendMessage(
                chat_id = chat_id,
                text = text,
                reply_markup = reply_markup,
                parse_mode = telegram.ParseMode.MARKDOWN
            )

    def __save_request_data(self, request_id, author_chat_id, request_type, entries):
        data_manager = ModulesLoader.load_manager("data")

        request_data = data_manager.create_data("requests", request_id, module="requests")

        request_data["author"] = author_chat_id
        request_data["type"] = request_type 
        request_data["entries"] = entries 

        data_manager.save_data("requests", request_id, request_data, module="requests")

        return request_data

    def __load_routes(self):
        file_path = "{}/routes.yaml".format(ModulesLoader.get_module_content_folder("requests"))

        return yaml.safe_load(open(file_path, 'r'))

    def __load_format(self, format_id, lang):
        file_path = "{}/formats/{}/{}.yaml".format(ModulesLoader.get_module_content_folder("requests"), lang, format_id)

        return yaml.safe_load(open(file_path, 'r'))

    def __generate_request_id(self):
        file_path = "{}/ids.yaml".format(ModulesLoader.get_module_content_folder("requests"))

        current_ids = yaml.safe_load(open(file_path, 'r'))

        request_id = current_ids["last_request_id"] + 1
        current_ids["last_request_id"] = request_id

        yaml.safe_dump(current_ids, open(file_path, 'w'))

        return request_id
