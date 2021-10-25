import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
#from geopandas import GeoDataFrame


def plot_max_df_colors(df, col_label):
    fig, ax = plt.subplots(1)
    # remove the axis
    ax.axis('off')
    # add a title and annotation
    ax.set_title(f'Meistgewählte Partei nach Wahlkreisen', fontdict={'fontsize': '25', 'fontweight': '3'})
    ax.annotate('Source: Bundeswahlleiter - https://www.bundeswahlleiter.de/bundestagswahlen/2021/ergebnisse/opendata', xy=(.05, .05),
                xycoords='figure fraction', fontsize=8, color='#555555')
    df.plot(color=df[col_label], linewidth=0.8, ax=ax, edgecolor='0.8')
    plt.title(f'Meistgewählte Partei nach Wahlkreisen')
    plt.savefig(f"img/{col_label}.png")


def plot_df_distribution(df, to_drop, name, values, relative=True):
    df_dropped = df.drop(to_drop, axis=1, level=1)
    df_dropped.columns = df_dropped.columns.droplevel(1)
    for variable in values:
        if relative:
            df_dropped[variable] = df_dropped[variable] / df_dropped['Gültige Stimmen'] *100
        # set the range for the choropleth values
        vmax = df_dropped[variable].max()
        vmin = df_dropped[variable].min()

        # create figure and axes for Matplotlib
        fig, ax = plt.subplots(1)
        # remove the axis
        ax.axis('off')
        # add a title and annotation
        ax.set_title(f'{variable}', fontdict={'fontsize': '25', 'fontweight': '3'})
        ax.annotate('Source: Bundeswahlleiter - https://www.bundeswahlleiter.de/bundestagswahlen/2021/ergebnisse/opendata', xy=(.05, .05),
                    xycoords='figure fraction', fontsize=8, color='#555555')
        # Create colorbar legend
        sm = plt.cm.ScalarMappable(norm=plt.Normalize(vmin=vmin, vmax=vmax))
        # empty array for the data range
        sm.set_array([])  # or alternatively sm._A = []. Not sure why this step is necessary, but many recommends it
        # add the colorbar to the figure
        fig.colorbar(sm)
        # create map
        df_dropped.plot(column=variable, linewidth=0.8, ax=ax, edgecolor='0.8')
        savename_var = variable.replace(" ", "").replace("ü", "ue").replace("/", "_")
        if relative:
            plt.title(f'{variable}: Anteil Stimmen in %')
            plt.savefig(f"img/Stimmenanteil_{savename_var}_{name}.png")
        else:
            plt.title(f'{variable}: Anzahl der Stimmen')
            plt.savefig(f"img/Stimmenanzahl_{savename_var}_{name}.png")



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
# set the value column that will be visualised
parteien = ['Christlich Demokratische Union Deutschlands', 'Sozialdemokratische Partei Deutschlands', 'Alternative für Deutschland',
            'DIE LINKE', 'Freie Demokratische Partei', 'BÜNDNIS 90/DIE GRÜNEN', 'Christlich-Soziale Union in Bayern e.V.', 'Die Grauen – '
                                                                                                                           'Für alle '
                                                                                                                           'Generationen', 'Piratenpartei Deutschland', 'Ungültige Stimmen', 'Wählende']
parteien_new = ['Christlich Demokratische Union Deutschlands', 'Sozialdemokratische Partei Deutschlands', 'Alternative für Deutschland',
                'DIE LINKE', 'Freie Demokratische Partei', 'BÜNDNIS 90/DIE GRÜNEN', 'Christlich-Soziale Union in Bayern e.V.', np.nan]
colors_p = ['black', 'red', 'blue', 'purple', 'yellow', 'green', 'black', 'grey']
parteien_colors = zip(parteien_new, colors_p)
parteien_colors_dict = dict(parteien_colors)

df_zweitstimme = merged_df_2021.drop('Erststimmen', axis=1, level=1)
df_zweitstimme.columns = df_zweitstimme.columns.droplevel(1)
# idxmax only works for numeric data
idx_max = df_zweitstimme[parteien_new[:-1]].idxmax(axis=1)
colors_df = [parteien_colors_dict[id_max] for id_max in idx_max]
# append new column to old df which contains the geodata
merged_df_2021_augmented = merged_df_2021.copy()
merged_df_2021_augmented['maxPartei'] = idx_max
merged_df_2021_augmented['maxParteiColor'] = colors_df
plot_max_df_colors(merged_df_2021_augmented, 'maxParteiColor')
plot_df_distribution(df=merged_df_2021, to_drop='Zweitstimmen', name='Erststimme', values=parteien, relative=False)
plot_df_distribution(df=merged_df_2021, to_drop='Erststimmen', name='Zweitstimme', values=parteien, relative=False)

