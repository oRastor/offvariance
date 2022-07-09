import pandas
import telebot
from xgclient.client import create_fixtures_dataframe, create_events_dataframe
import os
from dotenv import dotenv_values
import sys
import settings
from modules import notification
from modules.aggregate import aggregate_season, populate_metrics
from modules.factory import create_client
from modules.storage import get_season_fixtures_path, get_season_events_path, update_final_storage, \
    get_final_storage, get_upcoming_path, get_finished_path, get_fixtures_odds
from modules.strategy import find_games_by_strategies, find_new_games_by_strategies
from settings import game_aggregations_metrics, season_aggregations_metrics

config = dotenv_values('.env')
telegram_user_id = config.get('TELEGRAM_USER_ID')

client = create_client(config)

bot = telebot.TeleBot(config.get('TELEGRAM_API_KEY'), parse_mode=None)

if len(sys.argv) < 2:
    print('command expected')
    exit(1)

command = sys.argv[1]

if command == 'download':
    for country in client.countries():
        for tournament in client.tournaments(country['id']):
            for season in client.seasons(tournament['id']):
                print(country['name'], tournament['name'], season['name'], '#' + str(season['id']))

                fixtures_file_path = get_season_fixtures_path(season['id'])
                events_file_path = get_season_events_path(season['id'])

                season_fixtures = client.fixtures(season['id'])
                fixtures_df = create_fixtures_dataframe(season_fixtures)

                if os.path.exists(fixtures_file_path):
                    available_fixtures_df = pandas.read_csv(fixtures_file_path)
                    if fixtures_df['update_time'].max() == available_fixtures_df['update_time'].max():
                        print('Season database not updated')
                        continue

                events_df = create_events_dataframe(season_fixtures)

                if fixtures_df.size > 0:
                    fixtures_df.to_csv(fixtures_file_path, index=False)

                if events_df.size > 0:
                    events_df.to_csv(events_file_path, index=False)

                print('Season database updated')
elif command == 'aggregate-seasons':
    for country in client.countries():
        for tournament in client.tournaments(country['id']):
            for season in client.seasons(tournament['id']):
                print(country['name'], tournament['name'], season['name'], '#' + str(season['id']))

                fixtures_file_path = get_season_fixtures_path(season['id'])
                events_file_path = get_season_events_path(season['id'])

                if not os.path.exists(fixtures_file_path) or not os.path.exists(events_file_path):
                    print('Data not exists')
                    continue

                aggregate_season(season['id'], game_aggregations_metrics, season_aggregations_metrics)

                print('Season aggregation updated')
elif command == 'aggregate-season':
    if len(sys.argv) < 3:
        print('Season id expected')
        exit(1)

    aggregate_season(int(sys.argv[2]), game_aggregations_metrics, season_aggregations_metrics)
elif command == 'update-core':
    for country in client.countries():
        for tournament in client.tournaments(country['id']):
            for season in client.seasons(tournament['id']):
                print(country['name'], tournament['name'], season['name'], '#' + str(season['id']))

                fixtures_file_path = get_season_fixtures_path(season['id'])
                events_file_path = get_season_events_path(season['id'])

                if not os.path.exists(fixtures_file_path) or not os.path.exists(events_file_path):
                    print('Data not exists')
                    continue

                update_final_storage(season['id'])

                print('Updated')
elif command == 'update-finished':
    final_df = get_final_storage()
    final_df = final_df.loc[(final_df['home_score_first_half'] >= 0) & (final_df['away_score_first_half'] >= 0)]

    populate_metrics(final_df, settings.udi_metrics)
    populate_metrics(final_df, settings.composite_metrics)
    populate_metrics(final_df, settings.composite_finished_metrics)

    final_df.to_csv(get_finished_path())
elif command == 'update-upcoming':
    fixtures_odds_df = get_fixtures_odds(client)
    final_df = get_final_storage()

    keys = []
    for index in fixtures_odds_df.index:
        if index in final_df.index:
            final_df.loc[index, fixtures_odds_df.columns.tolist()] = fixtures_odds_df.loc[index].values
            keys.append(index)

    final_df = final_df.loc[keys]
    populate_metrics(final_df, settings.udi_metrics)
    populate_metrics(final_df, settings.composite_metrics)

    final_df.to_csv(get_upcoming_path())
elif command == 'find-games':
    filtered_games_df = find_games_by_strategies(settings.strategies)

    print(filtered_games_df.sort_values(by=['start_time']))
elif command == 'find-new-games':
    if len(telegram_user_id) > 0:
        telegram_user_id = int(telegram_user_id)
    else:
        print("Please specify telegram user id")
        exit(0)

    filtered_games_df = find_new_games_by_strategies(settings.strategies)

    notification.notify_games_list(bot, filtered_games_df, telegram_user_id)
