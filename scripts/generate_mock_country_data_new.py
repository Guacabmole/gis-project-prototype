import pandas as pd

country_data = pd.read_csv("../data/mock_country_data.csv")

coords = pd.read_csv("../data/centroids.csv")
coords.columns = ['country_code', 'name', 'lat', 'lon']

regions = pd.read_csv("../data/continents2.csv")
regions = regions[['alpha-3','region']]
regions.columns = ['country_code','region']

income = pd.read_csv("../data/world-bank-income-groups.csv")
income = income[income['Year'] == 2023]
income = income[["Code", "World Bank's income classification"]]
income.columns = ['country_code','income_group']

country_data = country_data.merge(
    coords[["country_code", "lat", "lon"]],
    on="country_code",
    how="left"
)

country_data = country_data.merge(
    regions,
    on="country_code",
    how="left"
)

country_data = country_data.merge(
    income,
    on="country_code",
    how="left"
)

country_data.loc[
    country_data['country_code'] == 'VEN',
    'income_group'
] = 'Lower-middle-income countries'

country_data.to_csv("../data/mock_country_data_new.csv",     index=False)