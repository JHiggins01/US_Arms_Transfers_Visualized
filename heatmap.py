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
import zipfile

#setting figure dpi
plt.rcParams['figure.dpi'] = 300

#reading in trade data
arms_data = pd.read_csv('trimmed_trade.csv')


# %%

#creating path to zipped shapefile
zip_shapefile_path = 'ne_10m_admin_0_countries.zip'

#checking shapefiles in the zip
with zipfile.ZipFile(zip_shapefile_path, 'r') as zipf:
    shp_files = [f for f in zipf.namelist() if f.endswith('.shp')]
    print(f"Shapefile(s) found in the zip: {shp_files}")

#loading shapefile from the zip
shapefile_name = shp_files[0]
world = gpd.read_file(f"zip://{zip_shapefile_path}!{shapefile_name}")

#keeping only necessary name and geomoetry columns
world = world[['NAME', 'geometry']]


# %%

#aggregating by recipient country
def aggregate_country (data_frame):
    return data_frame.groupby(['Recipient'])['Total TIV'].sum().reset_index()

# %%
#defining function to create heat maps, with option to specify year range
def heat_map (data, start_year = None, end_year = None):
    #if no range provided use all data
    if start_year is None or end_year is None:
        filtered_data = data
        years_label = f"{data['Delivery year'].min()}-{data['Delivery year'].max()}"
    else:
        filtered_data = data[data['Delivery year'].between(start_year, end_year)]
        years_label = f"{start_year}-{end_year}"
        
    #aggregate data by country
    aggregated_data = aggregate_country(filtered_data)
    
    #mergin data
    merged_data = world.merge(aggregated_data, how='left', left_on='NAME', 
                              right_on='Recipient')
    #filling nan's with 0 values
    merged_data['Total TIV'] = merged_data['Total TIV'].fillna(0)
    
    #plotting
    #setting color scheme using a log scale due to wide range
    #filtering for only positive values
    positive_values = merged_data['Total TIV'][merged_data['Total TIV']>0]
    if len(positive_values) > 0:
        #setting min and max values
        vmin = positive_values.min()
        vmax = merged_data['Total TIV'].max()
        #creating log scale for colors
        norm = colors.LogNorm(vmin=max(vmin,0.1), vmax=vmax)
    else:
        #fallback if there are no positive values
        norm = None
    
    #creating the plot
    fig, ax = plt.subplots(figsize=(15,10))
    merged_data.plot(
        column='Total TIV',
        ax=ax,
        legend=True,
        cmap='YlOrRd',
        norm=norm,
        legend_kwds={'label':'Total Arms Exports (TIV)'},
        missing_kwds={'color':'lightgrey'},
        edgecolor='black',
        linewidth=0.1)
    
    #Titling
    ax.set_title(f"US Arms Exports by Country {years_label}", fontsize=20)
    #removing axis lines
    ax.set_axis_off()
    
    #adding source
    plt.figtext(0.1, 0.01, 'Data Source: SIPRI Arms Transfer Database', fontsize=10)
    
    #saving
    fig.tight_layout()
    fig.savefig(f"us_arms_exports_heatmap_{years_label}.png", bbox_inches='tight')
    
    return fig, ax
# %%

#examples of calling the function
#for all data
heat_map(arms_data)
#for specific periods
heat_map(arms_data, 1990, 2000)
heat_map(arms_data, 2000, 2010)
heat_map(arms_data, 2010, 2020)
heat_map(arms_data, 2020, 2024)

