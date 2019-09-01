import pandas as pd

df = pd.DataFrame({'Animal' : ['Falcon', 'Falcon',
                               'Parrot', 'Parrot'],
                   'Max Speed' : [380., 370., 24., 26.]})

print(df)

a = df.groupby(['Animal']).agg({ "Max Speed": 'min'})
print(a)

a = df.groupby(['Animal']).agg({ "Max Speed": 'min'}).reset_index()
print(a)

