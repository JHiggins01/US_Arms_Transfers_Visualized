#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 20 15:39:46 2025

@author: jackhiggins
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
import zipfile

#setting figure dpi
plt.rcParams['figure.dpi'] = 300

#reading in trade data
arms_data = pd.read_csv('trimmed_trade.csv')

#filtering to 1990 and after
arms_data = arms_data[arms_data['Delivery year'] >= 1990]

#aggregating by recipient country
country_totals = arms_data.groupby(['Recipient'])['Total TIV'].sum().reset_index()
print(f"Total countries with arms sales data: {len(country_totals)}")

#creating path to zipped shapefile
zip_shapefile_path = 'ne_10m_admin_0_countries.zip'

#checking shapefiles files in the zip
with zipfile.ZipFile(zip_shapefile_path, 'r') as zipf:
    shp_files = [f for f in zipf.namelist() if f.endswith('.shp')]
    print(f"Shapefile(s) found in the zip: {shp_files}")

#loading shapefile from the zip
shapefile_name = shp_files[0]
world = gpd.read_file(f"zip://{zip_shapefile_path}!{shapefile_name}")

# %%

#listing country names not matched by shape file
missing_values = country_totals[~country_totals['Recipient'].isin(world['NAME'])]
print(missing_values)

#dictionary to fix mismatched names 
name_mapping = {
    "Bosnia-Herzegovina":"Bosnia and Herz.",
    "Central African Republic":"Central African Rep.",
    "Cote d'Ivoire":"Côte d'Ivoire",
    "DR Congo":"Dem. Rep. Congo",
    "Dominican Republic":"Dominican Rep.",
    "Equatorial Guinea":"Eq. Guinea",
    "Saint Vincent":"St. Vin. and Gren.",
    "Turkiye":"Turkey",
    "UAE":"United Arab Emirates",
    "Viet Nam":"Vietnam",}

#dropping 2 small deliveries of vehicle engines to South Sudan - Not included in shapefile
country_totals = country_totals[~country_totals['Recipient'].str.contains('South Sudan', na=False)]

#creating standard column of country names to match shape file 
country_totals['Recipient_std'] = country_totals['Recipient'].replace(name_mapping)

#checking to make sure country data names match shapefile names
all_present = country_totals['Recipient_std'].isin(world['NAME']).all()
print("All values present?" , all_present)
# %%

#merging datasets
merged_data = world.merge(country_totals, how='left', left_on='NAME', right_on='Recipient_std')

#filling NaN's with 0 values
merged_data['Total TIV'] = merged_data['Total TIV'].fillna(0)
# %%
#plotting

#setting color scheme using a log scale due to wide range
#filtering for only positive values
positive_values = merged_data['Total TIV'][merged_data['Total TIV'] > 0]
if len(positive_values) > 0:
#setting min and max values
    vmin = positive_values.min()
    vmax = merged_data['Total TIV'].max()
#creating log scale for colors
    norm = colors.LogNorm(vmin=max(vmin, 0.1), vmax=vmax)
else:
# Fallback if there are no positive values
    norm = None

#creating the plot
fig, ax = plt.subplots(figsize=(15, 10))
merged_data.plot(
    column='Total TIV',
    ax=ax,
    legend=True,
    cmap='YlOrRd',  # Yellow-Orange-Red color scheme
    norm=norm,
    legend_kwds={'label': 'Total Arms Exports (TIV)'},
    missing_kwds={'color': 'lightgrey'},
    edgecolor='black',
    linewidth=0.1 )

#titling
ax.set_title('US Arms Exports by Country (1990-2024)', fontsize=15)
#removing axis lines
ax.set_axis_off()

#adding source
plt.figtext(0.1, 0.01, 'Data Source: SIPRI Arms Transfer Databse', fontsize=10)
# %%

#saving
fig.tight_layout()
fig.savefig('us_arms_exports_heatmap.png', bbox_inches='tight')