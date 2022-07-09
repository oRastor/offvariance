from enum import Enum
import pandas
from pandas import DataFrame
from modules.history import HistoryStorage
from modules.last import LastStorage
from modules.storage import get_upcoming_games, get_data_path


class BetType(Enum):
    HOME = 'home'
    DRAW = 'draw'
    AWAY = 'away'
    TOTAL_OVER_2_5 = 'total_over_2_5'
    TOTAL_UNDER_2_5 = 'total_under_2_5'


class Strategy:
    def __init__(self, bet_type: BetType, conditions, expected_udi_value: float):
        self.bet_type = bet_type
        self.conditions = conditions
        self.expected_udi_value = expected_udi_value

    def filter(self, df: DataFrame) -> DataFrame:
        df = df.loc[self.conditions(df)].copy()
        df['odds_min'] = df[self.get_bet_open_key()] / (self.expected_udi_value + 1)
        df['bet_type'] = self.bet_type.value
        df['odds_open'] = df[self.get_bet_open_key()]
        df['odds_close'] = df[self.get_bet_close_key()]
        df['udi'] = df[self.get_udi_key()]

        return df[
            [
                'start_time',
                'tournament_name',
                'home_team_name',
                'away_team_name',
                'bet_type',
                'odds_open',
                'odds_close',
                'odds_min',
                'udi'
            ]
        ]

    def get_bet_open_key(self):
        return 'odds_' + self.bet_type.value + '_open'

    def get_bet_close_key(self):
        return 'odds_' + self.bet_type.value + '_last'

    def get_udi_key(self):
        return 'udi_' + self.bet_type.value


def find_games_by_strategies(strategies):
    games_df = get_upcoming_games()

    result_df = DataFrame()
    for strategy in strategies:
        result_df = pandas.concat([result_df, strategy.filter(games_df)])

    return result_df.sort_values(by=['start_time'])


def find_new_games_by_strategies(strategies):
    history_storage = HistoryStorage(get_data_path())
    last_storage = LastStorage(get_data_path())

    filtered_games_df = find_games_by_strategies(strategies)

    new_games_df = last_storage.filter(filtered_games_df)
    unplaced_new_games_df = history_storage.filter(new_games_df)
    last_storage.save(filtered_games_df.reset_index())

    if unplaced_new_games_df.size == 0:
        return unplaced_new_games_df.reset_index()

    return unplaced_new_games_df.reset_index().sort_values(by=['start_time'])
