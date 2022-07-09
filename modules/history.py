import pandas
from pandas import DataFrame


class HistoryStorage:

    def __init__(self, data_path = 'data/'):
        self.data_path = data_path

    def store_action(self, action: str, game_id: int, bet_type: str):
        new_df = DataFrame([[game_id, bet_type, action]], columns=['id', 'bet_type', 'action'])

        try:
            df = self.read()
            self.save(df.append(new_df))
        except FileNotFoundError:
            self.save(new_df)

    def filter(self, df: DataFrame) -> DataFrame:
        try:
            history_df = self.read()
        except FileNotFoundError:
            return df

        df = df.reset_index()

        df['id'] = df['id'].astype(int)
        df['bet_type'] = df['bet_type'].astype(str)

        history_df['id'] = history_df['id'].astype(int)
        history_df['bet_type'] = history_df['bet_type'].astype(str)

        merged_df = df.merge(history_df, on=['id', 'bet_type'], how='left', indicator=True)

        return merged_df.loc[merged_df['_merge'] == 'left_only'].drop(['action', '_merge'], axis=1)

    def read(self) -> DataFrame:
        path = self.data_path + '/history.csv'

        return pandas.read_csv(path)

    def save(self, df: DataFrame):
        df.to_csv(self.data_path + '/history.csv', index=False)

