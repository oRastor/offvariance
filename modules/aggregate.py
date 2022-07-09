import os
import pandas
from pandas import DataFrame
from xganalyzer.events_aggregator import GamesEventsAggregator
from xganalyzer.final_aggregator import FinalAggregator
from xganalyzer.season_aggregator import SeasonAggregator

from modules.storage import get_season_fixtures_path, get_season_events_path, get_season_game_aggregations_path, \
    get_season_aggregations_path, get_season_final_aggregations_path

dirname = os.path.dirname(__file__)


def aggregate_season(season_id: int, game_aggregations_metrics: dict,
                     season_aggregations_metrics: dict):
    fixtures_file_path = get_season_fixtures_path(season_id)
    events_file_path = get_season_events_path(season_id)
    game_aggregations_file_path = get_season_game_aggregations_path(season_id)
    metrics_aggregations_file_path = get_season_aggregations_path(season_id)
    final_aggregations_file_path = get_season_final_aggregations_path(season_id)

    if not os.path.exists(fixtures_file_path) or not os.path.exists(events_file_path):
        return

    games_df = pandas.read_csv(fixtures_file_path)
    events_df = pandas.read_csv(events_file_path)

    aggregator = GamesEventsAggregator(games_df, events_df)
    game_aggregations_df = aggregator.aggregate(game_aggregations_metrics, print_progress=False)

    game_aggregations_df.to_csv(game_aggregations_file_path)

    game_aggregations_df = pandas.read_csv(game_aggregations_file_path)

    aggregator = SeasonAggregator(games_df, game_aggregations_df)
    metrics_aggregations_df = aggregator.aggregate(season_aggregations_metrics)
    metrics_aggregations_df.to_csv(metrics_aggregations_file_path)

    metrics_aggregations_df = pandas.read_csv(metrics_aggregations_file_path)
    aggregator = FinalAggregator(games_df, metrics_aggregations_df)
    result_df = aggregator.aggregate()
    result_df.to_csv(final_aggregations_file_path)


def populate_metrics(df: DataFrame, metrics: dict):
    for key, value in metrics.items():
        df[key] = value(df)
