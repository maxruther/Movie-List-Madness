import pandas as pd
import pickle



# print(not 0.0)




test_radar_df = pd.read_csv('data/showtimes/test_radar.csv',
                            dtype={
                                'Release Year': 'object',
                                'Runtime': 'object'
                                }
                            )
print(test_radar_df)
print(test_radar_df.dtypes)

test_radar_df.to_pickle('data/showtimes/test_radar.pkl')





# test_radar_dict = {
#     'Title': "THE IMPORTANCE OF BEING EARNEST",
#     'Release Year': 2025,
#     'Runtime': 180.0,
#     'Director': 'Max Webster',
# }



# with open('data/showtimes/test_radar.pkl', 'wb') as file:
#     pickle.dump(test_radar_dict, file)
