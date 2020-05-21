import logging

from telegram.ext import CallbackQueryHandler

from .RequestsManager import RequestsManager

from .handlers.callback.requests import requests_callback_handler

from modules.pytg.ModulesLoader import ModulesLoader

def load_callback_handlers(dispatcher):
    module_id = ModulesLoader.get_module_id("requests")

    dispatcher.add_handler(CallbackQueryHandler(requests_callback_handler, pattern="requests,.*"), group=module_id)

def initialize():
    logging.info("Initializing requests module...")

    RequestsManager.initialize()

def connect():
    logging.info("Connecting requests module...")

    bot_manager = ModulesLoader.load_manager("bot")

    load_callback_handlers(bot_manager.updater.dispatcher)

def load_manager():
    return RequestsManager.load()

def depends_on():
    return ["bot", "forms"]