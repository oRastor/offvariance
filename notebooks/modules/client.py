import requests
import pandas


class OffVarianceResponse:
    def __init__(self, data, modification_date):
        self.data = data
        self.modification_date = modification_date


class OffVarianceClient:
    BASE_URI = 'https://offvariance.com/api/public'
    RESOURCE_FINISHED = 'finished'
    RESOURCE_UNFINISHED = 'unfinished'
    RESOURCE_UNFINISHED_ODDS = 'unfinished-odds'
    RESOURCE_FINISHED_URI = '/csv/matches/finished/'
    RESOURCE_UNFINISHED_URI = '/csv/matches/future/'
    RESOURCE_UNFINISHED_ODDS_URI = '/csv/odds/future/'

    __modification_dates = {}

    def __init__(self, key, data_path = 'data/', use_in_memory_states = False):
        self.key = key
        self.data_path = data_path
        self.use_in_memory_states = use_in_memory_states

    def get_finished_games(self, use_cache = False):
        if not use_cache:
            local_modification_date = self.get_modification_date(self.RESOURCE_FINISHED)
            modification_date = self.request_modification_date(self.RESOURCE_FINISHED_URI)

            if local_modification_date != modification_date:
                response = self.request_data(self.RESOURCE_FINISHED_URI)
                self.set_modification_date(self.RESOURCE_FINISHED, response.modification_date)
                self.store_data(self.RESOURCE_FINISHED, response.data)

        return self.read_data(self.RESOURCE_FINISHED)

    def get_unfinished_games(self, use_cache = False):
        if not use_cache:
            local_modification_date = self.get_modification_date(self.RESOURCE_UNFINISHED)
            modification_date = self.request_modification_date(self.RESOURCE_UNFINISHED_URI)

            if local_modification_date != modification_date:
                response = self.request_data(self.RESOURCE_UNFINISHED_URI)
                self.set_modification_date(self.RESOURCE_UNFINISHED, response.modification_date)
                self.store_data(self.RESOURCE_UNFINISHED, response.data)

            odds_local_modification_date = self.get_modification_date(self.RESOURCE_UNFINISHED_ODDS)
            odds_modification_date = self.request_modification_date(self.RESOURCE_UNFINISHED_ODDS_URI)

            if odds_local_modification_date != odds_modification_date:
                response = self.request_data(self.RESOURCE_UNFINISHED_ODDS_URI)
                self.set_modification_date(self.RESOURCE_UNFINISHED_ODDS, response.modification_date)
                self.store_data(self.RESOURCE_UNFINISHED_ODDS, response.data)

        main_df = self.read_data(self.RESOURCE_UNFINISHED)
        odds_df = self.read_data(self.RESOURCE_UNFINISHED_ODDS)

        return main_df.merge(odds_df, on='id', suffixes=('_old',''))

    def get_modification_date(self, resource_name):
        if not self.use_in_memory_states:
            return self.prepare_modification_date(resource_name)

        try:
            return self.__modification_dates[resource_name]
        except KeyError:
            return self.prepare_modification_date(resource_name)

    def prepare_modification_date(self, resource_name):
        try:
            self.__modification_dates[resource_name] = self.read_modification_date(resource_name)
        except FileNotFoundError:
            self.__modification_dates[resource_name] = ''

        return self.__modification_dates[resource_name]

    def set_modification_date(self, resource_name, modification_date):
        self.store_modification_date(resource_name, modification_date)
        self.__modification_dates[resource_name] = modification_date

    def store_modification_date(self, resource_name, modification_date):
        path = self.data_path + '/last-modification/' + resource_name + '.txt'
        self.store_file(path, modification_date)

    def read_modification_date(self, resource_name):
        path = self.data_path + '/last-modification/' + resource_name + '.txt'

        return self.read_file(path)

    def store_data(self, resource_name, data):
        path = self.data_path + '/' + resource_name + '.csv'
        self.store_file(path, data, 'wb')

    def request_modification_date(self, resource_uri):
        response = requests.head(self.BASE_URI + resource_uri, params={'key': self.key})

        self.validate_response(response)

        return response.headers['Last-Modified']

    def request_data(self, resource_uri):
        response = requests.get(self.BASE_URI + resource_uri, params={'key': self.key})

        self.validate_response(response)

        return OffVarianceResponse(response.content, response.headers['Last-Modified'])

    def read_data(self, resource_name):
        path = self.data_path + '/' + resource_name + '.csv'

        return pandas.read_csv(path)

    @staticmethod
    def store_file(path, data, mode ='w'):
        handle = open(path, mode)
        handle.write(data)
        handle.close()

    @staticmethod
    def read_file(path, mode ='r'):
        handle = open(path, mode)
        result = handle.read()
        handle.close()

        return result

    @staticmethod
    def validate_response(response):
        if response.status_code == 401:
            raise Exception('Unauthorised')

        if response.status_code != 200:
            raise Exception('Unexpected response')
