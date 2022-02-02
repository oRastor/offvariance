import pandas as pd
from pandas import DataFrame


def filter_games(df: DataFrame) -> DataFrame:
    away_win_games_df = filter_away_win_games(df)
    away_win_games_df['bet_type'] = '2'
    away_win_games_df['odds_open'] = away_win_games_df['odds_open_win2']
    away_win_games_df['odds_close'] = away_win_games_df['odds_close_win2']
    away_win_games_df['udi'] = away_win_games_df['udi_win2']

    total_under_games_df = filter_total_under_games(df)
    total_under_games_df['bet_type'] = 'U2.5'
    total_under_games_df['odds_open'] = total_under_games_df['odds_open_tm25']
    total_under_games_df['odds_close'] = total_under_games_df['odds_close_tm25']
    total_under_games_df['udi'] = total_under_games_df['udi_tm25']

    result_df = pd.concat([away_win_games_df, total_under_games_df])
    result_df = result_df.sort_values(by=['date_match'])

    return result_df[
        [
            'id',
            'date_match',
            'country_name',
            'team_1_name',
            'team_2_name',
            'bet_type',
            'odds_open',
            'odds_close',
            'odds_min',
            'udi'
        ]
    ]

def filter_games_segment(df: DataFrame, conditions, open_column, expected_udi_value):
    result = df.loc[conditions].copy()
    result['odds_min'] = result[open_column] / (expected_udi_value + 1)

    return result

def filter_total_under_games(df: DataFrame) -> DataFrame:
    return filter_games_segment(
        df,
        (df['team1_home_classic_minutes'] >= 90 * 3) & (df['team2_away_classic_minutes'] >= 90 * 3) &
        (
            (
                (df['odds_open_win1'] >= 1.8) & (df['odds_open_win1'] <= 2.8) &
                (df['odds_open_tm25'] >= 2.0) & (df['odds_open_tm25'] <= 2.5) &
                (df['expected_total'] <= 2.03) & (df['expected_total_loc'] <= 1.91)
            )
        ),
        'odds_open_tm25',
        0.05
    )


def filter_away_win_games(df: DataFrame) -> DataFrame:
    return pd.concat([
        filter_games_segment(
            df,
            (df['team1_home_classic_minutes'] >= 90 * 3) & (df['team2_away_classic_minutes'] >= 90 * 3) &
            (
                (
                        (df['odds_open_win2'] >= 1.8) & (df['odds_open_win2'] <= 2.7) &
                        (df['odds_open_tb25'] >= 2.0) & (df['odds_open_tb25'] <= 2.5) &
                        (df['expected_difference'] <= -0.77) & (df['expected_difference_loc'] <= -0.97)
                )
            ),
            'odds_open_win2',
            0.05
        ),
        filter_games_segment(
            df,
            (df['team1_home_classic_minutes'] >= 90 * 3) & (df['team2_away_classic_minutes'] >= 90 * 3) &
            (
                (
                        (df['odds_open_win2'] >= 1.8) & (df['odds_open_win2'] <= 2.7) &
                        (df['odds_open_tb25'] >= 1.6) & (df['odds_open_tb25'] <= 2) &
                        (df['expected_difference_loc'] <= -1.02) & (df['expected_difference'] <= -0.81)
                )
            ),
            'odds_open_win2',
            0.07
        )
    ])
