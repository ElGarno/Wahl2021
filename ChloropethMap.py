import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
#from geopandas import GeoDataFrame

fp = "non_general_shape/Geometrie_Wahlkreise_20DBT_VG250.shp"
map_df = gpd.read_file(fp)

df_election = pd.read_csv("election_data/kerg.csv", sep=";", skiprows=2, header=[0,1,2], skipinitialspace=True)
# drop last column as it is empty
df_election = df_election.drop(df_election.columns[-1][0], axis=1)
columns = pd.DataFrame(df_election.columns.tolist())
for i in range(3):
    columns.loc[columns[i].str.startswith('Unnamed:'), i] = np.nan
    columns[i] = columns[i].fillna(method='ffill')
    mask = pd.isnull(columns[i])
    columns[i] = columns[i].fillna('')
#columns.loc[mask, [0,2]] = columns.loc[mask, [2,0]].values
df_election.columns = pd.MultiIndex.from_tuples(columns.to_records(index=False).tolist())
print(df_election.head())
# create multiindex df in order to merge the map_df with df_election
map_df_multiindex = map_df.copy()
map_df_multiindex.columns = pd.MultiIndex.from_product([map_df_multiindex.columns, [''], ['']])
merged_df = map_df_multiindex.merge(df_election, how="left", left_on="WKR_NAME", right_on="Gebiet")
print(merged_df.head())
merged_df_2021 = merged_df.drop('Vorperiode', axis=1, level=2)
merged_df_2021.columns = merged_df_2021.columns.droplevel(2)
merged_df_2021_erststimmen = merged_df_2021.drop('Zweitstimmen', axis=1, level=1)
merged_df_2021_erststimmen.columns = merged_df_2021_erststimmen.columns.droplevel(1)
# set the value column that will be visualised
parteien = ['Christlich Demokratische Union Deutschlands', 'Sozialdemokratische Partei Deutschlands', 'Alternative für Deutschland', 'DIE LINKE', 'Freie Demokratische Partei', 'BÜNDNIS 90/DIE GRÜNEN', 'Christlich-Soziale Union in Bayern e.V.', 'Die Grauen – Für alle Generationen', 'Piratenpartei Deutschland', 'Ungültige Stimmen']

for variable in parteien:
    # set the range for the choropleth values
    vmax = merged_df_2021_erststimmen[variable].max()
    vmin = merged_df_2021_erststimmen[variable].min()

    # create figure and axes for Matplotlib
    fig, ax = plt.subplots(1, figsize=(30, 10))
    # remove the axis
    ax.axis('off')
    # add a title and annotation
    ax.set_title(f'{variable}', fontdict={'fontsize': '25', 'fontweight' : '3'})
    ax.annotate('Source: Bundeswahlleiter - https://www.bundeswahlleiter.de/bundestagswahlen/2021/ergebnisse/opendata', xy=(0.6, .05), xycoords='figure fraction', fontsize=12, color='#555555')
    # Create colorbar legend
    sm = plt.cm.ScalarMappable(norm=plt.Normalize(vmin=vmin, vmax=vmax))
    # empty array for the data range
    sm.set_array([]) # or alternatively sm._A = []. Not sure why this step is necessary, but many recommends it
    # add the colorbar to the figure
    fig.colorbar(sm)
    # create map
    merged_df_2021_erststimmen.plot(column=variable, linewidth=0.8, ax=ax, edgecolor='0.8')
    savename_var = variable.replace(" ", "").replace("ü", "ue").replace("/", "_")
    plt.savefig(f"img/Verteilung_{savename_var}.png")

