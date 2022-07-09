import telebot
from telebot.types import Message, CallbackQuery
from dotenv import dotenv_values
import settings
from modules import notification
from modules.history import HistoryStorage
from modules.storage import get_data_path
from modules.strategy import find_games_by_strategies

config = dotenv_values('.env')

user_id = config.get('TELEGRAM_USER_ID')

if len(user_id) > 0:
    user_id = int(user_id)

bot = telebot.TeleBot(config.get('TELEGRAM_API_KEY'), parse_mode=None)
history = HistoryStorage(get_data_path())

handle = open('bot_commands.txt', 'r')
commands = handle.read()
handle.close()


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if message.chat.id == user_id:
        bot.send_message(message.chat.id, commands)

    if not isinstance(user_id, int):
        bot.send_message(message.chat.id, "Hi, your id is " + str(message.chat.id))


@bot.message_handler(commands=['list'])
def send_list(message: Message):
    if message.chat.id != user_id:
        return

    filtered_games_df = find_games_by_strategies(settings.strategies).reset_index()

    if filtered_games_df.size == 0:
        bot.send_message(message.chat.id, 'List is empty')

    notification.notify_games_list(bot, filtered_games_df, message.chat.id)


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
