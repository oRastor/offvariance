from pandas import DataFrame
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def notify_games_list(bot: TeleBot, df: DataFrame, chat_id: int):
    for i in range(df.shape[0]):
        item = df[i:i + 1]
        bet_callback = "bet " + str(item.iloc[0].id) + " " + str(item.iloc[0].bet_type)
        close_callback = "close " + str(item.iloc[0].id) + " " + str(item.iloc[0].bet_type)

        markup = InlineKeyboardMarkup()
        bet = InlineKeyboardButton('Place Bet', callback_data=bet_callback)
        close = InlineKeyboardButton('Close', callback_data=close_callback)
        markup.add(bet, close)

        bot.send_message(chat_id, game_row_to_string(item), reply_markup=markup)


def game_row_to_string(row: DataFrame):
    return "#" + row.to_string(header=False, index=False)
