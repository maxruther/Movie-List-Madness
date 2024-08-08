import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('mysql://root:yos@localhost/moviedb')
conn = engine.connect()

query = "SELECT * FROM critic_ratings"

cr_df = pd.read_sql_query(query, engine, index_col='Movie_ID')
# cr_df

ebert_df = pd.read_csv('ebert_ratings.csv', index_col='Movie_ID')
ebert_df['Year'] = ebert_df['Year'].astype(str)
# ebert_df

merged_df = cr_df.merge(ebert_df, how='left', on=['Title','Year'])
merged_df.index = range(1, len(merged_df)+1)
cr_plus_ebert_df = merged_df

cr_plus_ebert_df.to_sql('critic_ratings', engine, if_exists='replace',
                        index=True)
