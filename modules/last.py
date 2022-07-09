import pandas
from pandas import DataFrame


class LastStorage:

    def __init__(self, data_path = 'data/'):
        self.data_path = data_path

    def filter(self, df: DataFrame) -> DataFrame:
        try:
            last_df = self.read()
        except FileNotFoundError:
            return df

        df = df.reset_index()

        df['id'] = df['id'].astype(int)
        df['bet_type'] = df['bet_type'].astype(str)

        last_df['id'] = last_df['id'].astype(int)
        last_df['bet_type'] = last_df['bet_type'].astype(str)

        merged_df = df.merge(last_df, on=['id', 'bet_type'], how='left', indicator=True)

        return merged_df.loc[merged_df['_merge'] == 'left_only'].drop(['_merge'], axis=1).dropna(axis='columns')

    def read(self) -> DataFrame:
        path = self.data_path + '/last.csv'

        return pandas.read_csv(path)

    def save(self, df: DataFrame):
        df.to_csv(self.data_path + '/last.csv', index=False)

