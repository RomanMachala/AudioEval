"""
    This script contains logic for graphs generation and table value calcultion.
"""

__author__      = "Roman Machala"
__date__        = "09.03.2025"

import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

def analysis(data: pd.DataFrame, metric: str, save_path: str, filename: str) -> bool:
    """
        Function for graph generation. 

        Params:
            data:       pandas dataframe, containing data
            metric:     name of the metric being displayed
            save_path:  path of the final graph
            filename:   name of the filename (used for title of the graph)
    """

    if metric == "Mos" and data[metric].apply(lambda x: pd.isna(x) or (isinstance(x, dict) and not x)).all():
        return False
    else:
        if data[metric].isna().all():
            return False
    sns.histplot(data[metric] if metric != 'Mos' else data[metric].apply(pd.Series), kde=True, bins=40 if metric == 'Mos' else 20)
    plt.title(f'{filename}')
    plt.xlabel(f'{metric} score')
    plt.ylabel("Frequency")
    plt.savefig(save_path)
    plt.close()
    return True

def mosHandler(data: pd.DataFrame, column: str, metric: str) -> list[int]:
    """
        Helper function for value calculation.

        Params:
            data:       pandas dataframe containing data
            column:     which column to calculate from
            metric:     name of the metric

        Returns:
            calculated values as a list of integers (4)
    """
    return [data[metric].apply(pd.Series).loc[:, column].mean(), data[metric].apply(pd.Series).loc[:, column].median(),
                data[metric].apply(pd.Series).loc[:, column].min(), data[metric].apply(pd.Series).loc[:, column].max()]

def table(data: pd.DataFrame, metric: str) -> list[int]:
    """
        Function to calculate values for table.

        Params:
            data:       pandas dataframe containing data
            metric:     name of the metric

        Returns:
            calculated values as a list of integers or a list of lists for MOS
    """
    if metric == 'Mos':
        return [mosHandler(data, 'ovrl_mos', metric), mosHandler(data, 'sig_mos', metric),
                mosHandler(data, 'bak_mos', metric), mosHandler(data, 'p808_mos', metric)]
    else:
        return [data.loc[:, metric].mean(), data.loc[:, metric].median(), data.loc[:, metric].min(), data.loc[:, metric].max()]