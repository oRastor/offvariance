import os

from xganalyzer.events_aggregator import GamesEventsAggregator, CalculateContext, CalculateType, CalculateLocation
from notebooks.modules.client import OffVarianceClient
from dotenv import dotenv_values

config = dotenv_values('.env')

client = OffVarianceClient(config.get('OFF_VARIANCE_KEY'), data_path='data')
finished_games_df = client.get_finished_games()
events_df = client.get_events()

dirname = os.path.dirname(__file__)


aggregator = GamesEventsAggregator(finished_games_df, events_df)
result_df = aggregator.aggregate({
    'xg': CalculateContext(calculate_type=CalculateType.EXPECTED_GOALS, calculate_location=CalculateLocation.TOTAL),
    'duration': CalculateContext(calculate_type=CalculateType.DURATION, calculate_location=CalculateLocation.TOTAL)
}, True)

result_df.to_csv(os.path.join(dirname, 'data/game_metrics.csv'))