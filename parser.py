#!\usr\bin\python

import os
import glob
import pandas as pd


''' '''
path = os.getcwd() + '\\inv_json\\'
print(path)
''' '''
all_files = glob.glob(os.path.join(path, '*.json'))

for i in all_files:
    print(i)

files = (pd.read_json(f) for f in all_files)
df = pd.concat(files)

df.to_csv('inventory.csv', index=False)

result = pd.read_csv('inventory.csv')
print(result)