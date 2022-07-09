import pandas as pd
from pandas import DataFrame


class StrategyResult:
    def __init__(self, games_df, metrics_df):
        self.games_df = games_df
        self.metrics_df = metrics_df


def print_result(df: DataFrame, profit_open_column, profit_last_column, udi_column):
    sum_df = df[[profit_open_column, profit_last_column]].sum()
    count = df.shape[0]

    bets_df = df[[profit_open_column, profit_last_column]].sort_index().cumsum()

    print('Count:', count)
    print('Open profit:', sum_df[profit_open_column])
    print('Close profit:', sum_df[profit_last_column])
    print('Open ROI:', sum_df[profit_open_column] / count)
    print('Close ROI:', sum_df[profit_last_column] / count)
    print('UDI:', df[udi_column].mean())
    print(bets_df.plot())


def analyze_avg_udi(df: DataFrame, columns: list, udi_column, low_udi, high_udi):
    low_udi_df = df.loc[(df[udi_column] <= low_udi)]
    low = low_udi_df[columns].mean()
    low.name = 'low'

    high_udi_df = df.loc[(df[udi_column] >= high_udi)]
    high = high_udi_df[columns].mean()
    high.name = 'high'

    result_df = pd.concat([low, high], axis=1)
    result_df['diff'] = abs(result_df['high'] - result_df['low'])

    return result_df.sort_values(by=['diff'], ascending=False)


def create_strategy_by_udi(df: DataFrame, metrics: list, udi_column, iterations=2, max_metrics_count=2, low_udi=0,
                           high_udi=0.1) -> StrategyResult:
    analyze_result_df = analyze_avg_udi(df, metrics, udi_column, low_udi, high_udi)

    result_df = df

    new_metrics = []
    for index in analyze_result_df[0:max_metrics_count].index:
        new_metrics.append(index)
        low_value = analyze_result_df.loc[index].low
        high_value = analyze_result_df.loc[index].high

        if low_value > high_value:
            result_df = result_df.loc[(result_df[index] <= high_value)]
        else:
            result_df = result_df.loc[(result_df[index] >= high_value)]

    iterations = iterations - 1

    if iterations <= 0:
        metrics_df = analyze_result_df[0:max_metrics_count].copy()
        metrics_df = metrics_df.rename(columns={'high': 'value'})
        metrics_df['condition'] = '>='
        metrics_df.loc[analyze_result_df['low'] > analyze_result_df['high'], 'condition'] = '<='
        return StrategyResult(result_df, metrics_df[['value', 'condition']])

    return create_strategy_by_udi(result_df, new_metrics, udi_column, iterations, max_metrics_count, low_udi, high_udi)


def analyze_correlation(df: DataFrame, base_column: str, columns: list) -> DataFrame:
    columns_list = [base_column] + columns

    base_df = df[columns_list]
    correlation_df = base_df.corr()
    result_df = correlation_df[0:1].transpose()
    result_df['absolute'] = abs(result_df[base_column])
    result_df = result_df.sort_values(by=['absolute'], ascending=False)
    result_df.rename(columns={base_column: 'correlation'}, inplace=True)

    return result_df[['correlation']][1:]


def print_home_win_result(df: DataFrame):
    print_result(df, 'profit_home_open', 'profit_home_last', 'udi_home')


def print_draw_result(df: DataFrame):
    print_result(df, 'profit_draw_open', 'profit_draw_last', 'udi_draw')


def print_away_win_result(df: DataFrame):
    print_result(df, 'profit_away_open', 'profit_away_last', 'udi_away')


def print_total_under_result(df: DataFrame):
    print_result(df, 'profit_total_under_2_5_open', 'profit_total_under_2_5_last', 'udi_total_under_2_5')


def print_total_over_result(df: DataFrame):
    print_result(df, 'profit_total_over_2_5_open', 'profit_total_over_2_5_last', 'udi_total_over_2_5')


def analyze_home_win_avg_udi(df: DataFrame, columns: list, low_udi=0, high_udi=0.1):
    return analyze_avg_udi(df, columns, 'udi_home', low_udi, high_udi)


def analyze_draw_avg_udi(df: DataFrame, columns: list, low_udi=0, high_udi=0.1):
    return analyze_avg_udi(df, columns, 'udi_draw', low_udi, high_udi)


def analyze_away_win_avg_udi(df: DataFrame, columns: list, low_udi=0, high_udi=0.1):
    return analyze_avg_udi(df, columns, 'udi_away', low_udi, high_udi)


def analyze_total_under_avg_udi(df: DataFrame, columns: list, low_udi=0, high_udi=0.1):
    return analyze_avg_udi(df, columns, 'udi_total_under_2_5', low_udi, high_udi)


def analyze_total_over_avg_udi(df: DataFrame, columns: list, low_udi=0, high_udi=0.1):
    return analyze_avg_udi(df, columns, 'udi_total_over_2_5', low_udi, high_udi)


def create_home_win_strategy_by_udi(df: DataFrame, metrics: list, iterations=2, max_metrics_count=2, low_udi=0,
                                    high_udi=0.1) -> StrategyResult:
    return create_strategy_by_udi(df, metrics, 'udi_home', iterations, max_metrics_count, low_udi, high_udi)


def create_draw_strategy_by_udi(df: DataFrame, metrics: list, iterations=2, max_metrics_count=2, low_udi=0,
                                high_udi=0.1) -> StrategyResult:
    return create_strategy_by_udi(df, metrics, 'udi_draw', iterations, max_metrics_count, low_udi, high_udi)


def create_away_win_strategy_by_udi(df: DataFrame, metrics: list, iterations=2, max_metrics_count=2, low_udi=0,
                                    high_udi=0.1) -> StrategyResult:
    return create_strategy_by_udi(df, metrics, 'udi_away', iterations, max_metrics_count, low_udi, high_udi)


def create_total_under_strategy_by_udi(df: DataFrame, metrics: list, iterations=2, max_metrics_count=2, low_udi=0,
                                       high_udi=0.1) -> StrategyResult:
    return create_strategy_by_udi(df, metrics, 'udi_total_under_2_5', iterations, max_metrics_count, low_udi, high_udi)


def create_total_over_strategy_by_udi(df: DataFrame, metrics: list, iterations=2, max_metrics_count=2, low_udi=0,
                                      high_udi=0.1) -> StrategyResult:
    return create_strategy_by_udi(df, metrics, 'udi_total_over_2_5', iterations, max_metrics_count, low_udi, high_udi)


def prepare_metrics_list(metrics: dict):
    return list(metrics.keys())


def prepare_short_table(df: DataFrame, odds_column):
    return df[['date_match', 'country_name', 'team_1_name', 'team_2_name', odds_column]]
