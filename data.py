import pandas as pd
import numpy as np

data = pd.read_csv('results.csv')
data['game'] = data['home_team'] + ' vs ' + data['away_team']
print(data.head())