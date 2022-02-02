import pandas as pd
from pandas import DataFrame
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

metrics = [
    'simple_expected_difference',
    'simple_expected_difference_loc',
    'simple_expected_total_value',
    'simple_expected_total_value_loc',
    'expected_difference',
    'expected_difference_loc',
    'expected_total',
    'expected_total_loc',
]


class StrategyResult:
    def __init__(self, games_df, metrics_df):
        self.games_df = games_df
        self.metrics_df = metrics_df


def filter_correct_games(df: DataFrame):
    return df.loc[
        (df.odds_open_win1 > 0) & (df.odds_close_win1 > 0) &
        (df.odds_open_draw > 0) & (df.odds_close_draw > 0) &
        (df.odds_open_win2 > 0) & (df.odds_close_win2 > 0) &
        (df.odds_open_tb25 > 0) & (df.odds_close_tb25 > 0) &
        (df.odds_open_tm25 > 0) & (df.odds_close_tm25 > 0)
    ].copy()


def filter_correct_unfinished_games(df: DataFrame):
    return df.loc[
        (df.odds_open_win1 > 0) &
        (df.odds_open_draw > 0) &
        (df.odds_open_win2 > 0) &
        (df.odds_open_tb25 > 0) &
        (df.odds_open_tm25 > 0)
    ].copy()


def populate_metrics(df: DataFrame):
    populate_unfinished_metrics(df)
    df['difference'] = df.team_1_goal - df.team_2_goal
    df['total'] = df.team_1_goal + df.team_2_goal
    df['profit_win1_open'] = (df.difference > 0) * df.odds_open_win1 - 1
    df['profit_win1_close'] = (df.difference > 0) * df.odds_close_win1 - 1
    df['profit_draw_open'] = (df.difference == 0) * df.odds_open_draw - 1
    df['profit_draw_close'] = (df.difference == 0) * df.odds_close_draw - 1
    df['profit_win2_open'] = (df.difference < 0) * df.odds_open_win2 - 1
    df['profit_win2_close'] = (df.difference < 0) * df.odds_close_win2 - 1
    df['profit_tm25_open'] = (df.total < 2.5) * df.odds_open_tm25 - 1
    df['profit_tm25_close'] = (df.total < 2.5) * df.odds_close_tm25 - 1
    df['profit_tb25_open'] = (df.total > 2.5) * df.odds_open_tb25 - 1
    df['profit_tb25_close'] = (df.total > 2.5) * df.odds_close_tb25 - 1


def populate_unfinished_metrics(df: DataFrame):
    df['udi_win1'] = df.odds_open_win1 / df.odds_close_win1 - 1
    df['udi_draw'] = df.odds_open_draw / df.odds_close_draw - 1
    df['udi_win2'] = df.odds_open_win2 / df.odds_close_win2 - 1
    df['udi_tm25'] = df.odds_open_tm25 / df.odds_close_tm25 - 1
    df['udi_tb25'] = df.odds_open_tb25 / df.odds_close_tb25 - 1
    df['simple_expected_difference'] = df.team1_all_classic_xg90 - df.team2_all_classic_xg90
    df['simple_expected_difference_loc'] = df.team1_home_classic_xg90 - df.team2_away_classic_xg90
    df['simple_expected_total_value'] = df.team1_all_classic_xg90 + df.team2_all_classic_xg90 + df.team1_all_classic_xga90 + df.team2_all_classic_xga90
    df['simple_expected_total_value_loc'] = df.team1_home_classic_xg90 + df.team2_away_classic_xg90 + df.team1_home_classic_xga90 + df.team2_away_classic_xga90
    df['expected_difference'] = df.team1_all_xgpower_xg_xg90noindex * df.team2_all_xgpower_xg_xga90index - df.team2_all_xgpower_xg_xg90noindex * df.team1_all_xgpower_xg_xga90index
    df['expected_total'] = df.team1_all_xgpower_xg_xg90noindex * df.team2_all_xgpower_xg_xga90index + df.team2_all_xgpower_xg_xg90noindex * df.team1_all_xgpower_xg_xga90index
    df['expected_difference_loc'] = df.team1_home_xgpower_xg_xg90noindex * df.team2_away_xgpower_xg_xga90index - df.team2_away_xgpower_xg_xg90noindex * df.team1_home_xgpower_xg_xga90index
    df['expected_total_loc'] = df.team1_home_xgpower_xg_xg90noindex * df.team2_away_xgpower_xg_xga90index + df.team2_away_xgpower_xg_xg90noindex * df.team1_home_xgpower_xg_xga90index


def print_result(df: DataFrame, profit_open_column, profit_close_column, udi_column):
    sum_df = df[[profit_open_column, profit_close_column]].sum()
    count = df.shape[0]

    bets_df = df[[profit_open_column, profit_close_column]].cumsum()

    print('Count:', count)
    print('Open profit:', sum_df[profit_open_column])
    print('Close profit:', sum_df[profit_close_column])
    print('Open ROI:', sum_df[profit_open_column] / count)
    print('Close ROI:', sum_df[profit_close_column] / count)
    print('UDI:', df[udi_column].mean())
    print(bets_df.plot())


def analyze_avg_udi(df: DataFrame, metrics, udi_column, low_udi=0, high_udi=0.1):
    low_udi_df = df.loc[(df[udi_column] <= low_udi)]
    low = low_udi_df[metrics].mean()
    low.name = 'low'

    high_udi_df = df.loc[(df[udi_column] >= high_udi)]
    high = high_udi_df[metrics].mean()
    high.name = 'high'

    result_df = pd.concat([low, high], axis=1)
    result_df['diff'] = abs(result_df['high'] - result_df['low'])

    return result_df.sort_values(by=['diff'], ascending=False)


def create_strategy_by_udi(df: DataFrame, metrics, udi_column, iterations=2, metrics_count=2, low_udi=0, high_udi=0.1) -> StrategyResult:
    analyze_result_df = analyze_avg_udi(df, metrics, udi_column, low_udi, high_udi)

    result_df = df

    new_metrics = []
    for index in analyze_result_df[0:metrics_count].index:
        new_metrics.append(index)
        low_value = analyze_result_df.loc[index].low
        high_value = analyze_result_df.loc[index].high

        if low_value > high_value:
            result_df = result_df.loc[(result_df[index] <= high_value)]
        else:
            result_df = result_df.loc[(result_df[index] >= high_value)]

    iterations = iterations - 1

    if iterations <= 0:
        metrics_df = analyze_result_df[0:metrics_count].copy()
        metrics_df = metrics_df.rename(columns={'high': 'value'})
        metrics_df['condition'] = '>='
        metrics_df.loc[analyze_result_df['low'] > analyze_result_df['high'], 'condition'] = '<='
        return StrategyResult(result_df, metrics_df[['value', 'condition']])

    return create_strategy_by_udi(result_df, new_metrics, udi_column, iterations, metrics_count, low_udi, high_udi)


def analyze_correlation(df: DataFrame, base_column: str, columns: list) -> DataFrame:
    columns_list = [base_column] + columns

    base_df = df[columns_list]
    correlation_df = base_df.corr()
    result_df = correlation_df[0:1].transpose()
    result_df['absolute'] = abs(result_df[base_column])
    result_df = result_df.sort_values(by=['absolute'], ascending=False)
    result_df.rename(columns={base_column: 'correlation'}, inplace=True)

    return result_df[['correlation']][1:]

def print_home_win_result(df: DataFrame):
    print_result(df, 'profit_win1_open', 'profit_win1_close', 'udi_win1')


def print_away_win_result(df: DataFrame):
    print_result(df, 'profit_win2_open', 'profit_win2_close', 'udi_win2')


def print_draw_result(df: DataFrame):
    print_result(df, 'profit_draw_open', 'profit_draw_close', 'udi_draw')


def print_total_under_result(df: DataFrame):
    print_result(df, 'profit_tm25_open', 'profit_tm25_close', 'udi_tm25')


def print_total_over_result(df: DataFrame):
    print_result(df, 'profit_tb25_open', 'profit_tb25_close', 'udi_tb25')


def prepare_short_table(df: DataFrame, odds_column):
    return df[['date_match', 'country_name', 'team_1_name', 'team_2_name', odds_column]]


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
