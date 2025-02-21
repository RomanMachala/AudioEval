import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import os

def analysis(data: pd.DataFrame, metric: str, save_path: str):
    sns.histplot(data[metric], kde=True, bins=20)
    plt.title(f'Rozložení hodnot {metric}')
    plt.xlabel(f'{metric}')
    plt.ylabel("Počet vzorků")
    plt.savefig(save_path)
    plt.close()
