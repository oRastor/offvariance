import os
import pandas
from pandas import DataFrame
from xgclient.client import create_fixture_odds


def get_data_path():
    dirname = os.path.dirname(__file__)
    return os.path.join(dirname, '../data')


def get_season_fixtures_path(season_id: int):
    dirname = os.path.dirname(__file__)
    return os.path.join(dirname, '../data/season-fixtures-' + str(season_id) + '.csv')


def get_season_events_path(season_id: int):
    dirname = os.path.dirname(__file__)
    return os.path.join(dirname, '../data/season-events-' + str(season_id) + '.csv')


def get_season_game_aggregations_path(season_id: int):
    dirname = os.path.dirname(__file__)
    return os.path.join(dirname, '../data/season-game-aggregations-' + str(season_id) + '.csv')


def get_season_aggregations_path(season_id: int):
    dirname = os.path.dirname(__file__)
    return os.path.join(dirname, '../data/season-aggregations-' + str(season_id) + '.csv')


def get_season_final_aggregations_path(season_id: int):
    dirname = os.path.dirname(__file__)
    return os.path.join(dirname, '../data/season-final-' + str(season_id) + '.csv')


def get_final_aggregations_path():
    dirname = os.path.dirname(__file__)
    return os.path.join(dirname, '../data/final.csv')


def get_finished_path():
    dirname = os.path.dirname(__file__)
    return os.path.join(dirname, '../data/finished.csv')


def get_upcoming_path():
    dirname = os.path.dirname(__file__)
    return os.path.join(dirname, '../data/upcoming.csv')


def update_final_storage(season_id: int):
    global_file_path = get_final_aggregations_path()
    season_file_path = get_season_final_aggregations_path(season_id)

    if os.path.exists(global_file_path):
        final_aggregations_df = pandas.read_csv(global_file_path)
    else:
        final_aggregations_df = pandas.DataFrame()

    season_aggregations_df = pandas.read_csv(season_file_path)
    season_aggregations_df = season_aggregations_df.set_index(['id'])

    if final_aggregations_df.size == 0:
        season_aggregations_df.to_csv(global_file_path)
        return

    final_aggregations_df = final_aggregations_df.set_index(['id'])

    for index in season_aggregations_df.index:
        final_aggregations_df.loc[index, :] = season_aggregations_df.loc[index]

    final_aggregations_df.to_csv(global_file_path)


def get_fixtures_odds(client):
    fixtures_odds_df = create_fixture_odds(client.upcoming_odds())
    return fixtures_odds_df.set_index(['id'])


def get_final_storage() -> DataFrame:
    result_df = pandas.read_csv(get_final_aggregations_path(), low_memory=False)

    return result_df.set_index(['id'])


def get_finished_games() -> DataFrame:
    result_df = pandas.read_csv(get_finished_path(), low_memory=False)

    return result_df.set_index(['id'])


def get_upcoming_games() -> DataFrame:
    result_df = pandas.read_csv(get_upcoming_path())

    return result_df.set_index(['id'])
