import telebot
from telebot.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import dotenv_values
from notebooks.modules.history import HistoryStorage

from notebooks.modules import utils, strategy
from notebooks.modules.client import OffVarianceClient

config = dotenv_values('.env')

user_id = config.get('TELEGRAM_USER_ID')

if len(user_id) > 0:
    user_id = int(user_id)

bot = telebot.TeleBot(config.get('TELEGRAM_API_KEY'), parse_mode=None)
client = OffVarianceClient(config.get('OFF_VARIANCE_KEY'), data_path='data')
history = HistoryStorage('data')

handle = open('bot/commands.txt', 'r')
commands = handle.read()
handle.close()

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if message.chat.id == user_id:
        bot.send_message(message.chat.id, commands)

    if len(user_id) == 0:
        bot.send_message(message.chat.id, "Hi, your id is " + str(message.chat.id))

@bot.message_handler(commands=['list'])
def send_list(message: Message):
    if message.chat.id != user_id:
        return

    games_df = client.get_unfinished_games()
    games_df = utils.filter_correct_unfinished_games(games_df)
    utils.populate_unfinished_metrics(games_df)

    filtered_games_df = history.filter(strategy.filter_games(games_df))

    if filtered_games_df.shape[0] == 0:
        bot.send_message(message.chat.id, 'List is empty')

    utils.notify_games_list(bot, filtered_games_df, message.chat.id)

@bot.callback_query_handler(func=lambda call: True)
def test_callback(callback: CallbackQuery):
    request = callback.data.split()
    if request[0] == 'bet':
        history.store_action(request[0], int(request[1]), request[2])
        bot.send_message(callback.message.chat.id, "Bet " + request[2] + ' placed for game #' + request[1])

    if request[0] == 'close':
        history.store_action(request[0], int(request[1]), request[2])
        bot.send_message(callback.message.chat.id, "Bet " + request[2] + ' for game #' + request[1] + ' closed')

bot.infinity_polling()