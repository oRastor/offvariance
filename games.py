from notebooks.modules.client import OffVarianceClient
import notebooks.modules.strategy as strategy
import notebooks.modules.utils as utils
from dotenv import dotenv_values

config = dotenv_values('.env')

client = OffVarianceClient(config.get('OFF_VARIANCE_KEY'), data_path='data')
games_df = client.get_unfinished_games()
games_df = utils.filter_correct_unfinished_games(games_df)

utils.populate_unfinished_metrics(games_df)

print(strategy.filter_games(games_df))
