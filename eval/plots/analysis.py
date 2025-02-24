import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import os

def analysis(data: pd.DataFrame, metric: str, save_path: str, filename: str):
    sns.histplot(data[metric] if metric != 'Mos' else data[metric].apply(pd.Series), kde=True, bins=20)
    plt.title(f'{filename}')
    plt.xlabel(f'{metric} score')
    plt.ylabel("Frequency")
    plt.savefig(save_path)
    plt.close()
