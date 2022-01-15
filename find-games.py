import telebot

from notebooks.modules.client import OffVarianceClient
from notebooks.modules.last import LastStorage
import notebooks.modules.strategy as strategy
import notebooks.modules.utils as utils
from dotenv import dotenv_values

from notebooks.modules.history import HistoryStorage

history_storage = HistoryStorage('data')
last_storage = LastStorage('data')

config = dotenv_values('.env')

user_id = config.get('TELEGRAM_USER_ID')

if len(user_id) == 0:
    print("Please specify telegram user id")
    exit(0)

bot = telebot.TeleBot(config.get('TELEGRAM_API_KEY'), parse_mode=None)
client = OffVarianceClient(config.get('OFF_VARIANCE_KEY'), data_path='data')
games_df = client.get_unfinished_games()
games_df = utils.filter_correct_unfinished_games(games_df)

utils.populate_unfinished_metrics(games_df)

filtered_games_df = strategy.filter_games(games_df)
new_games_df = last_storage.filter(filtered_games_df)
result_df = history_storage.filter(new_games_df)

utils.notify_games_list(bot, result_df, int(user_id))

last_storage.save(filtered_games_df)