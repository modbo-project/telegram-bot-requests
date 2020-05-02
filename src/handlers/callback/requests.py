import telegram, logging

from modules.pytg.ModulesLoader import ModulesLoader

def requests_callback_handler(update, context):
    bot = context.bot

    query = update.callback_query
    query_data = query.data.split(",")
    user_id = query.from_user.id

    username = query.message.chat.username
    chat_id = query.message.chat_id
    message_id = query.message.message_id

    logging.info("Handling requests callback data from {}: {}".format(chat_id, query_data))

    request_id = query_data[1]
    response = query_data[2]

    requests_manager = ModulesLoader.load_manager("requests")

    requests_manager.digest_manager.digest(bot, chat_id, message_id, request_id, response)