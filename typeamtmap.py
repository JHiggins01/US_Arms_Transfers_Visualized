#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 24 09:13:30 2025

@author: jackhiggins
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import zipfile

#setting figure dpi
plt.rcParams['figure.dpi'] = 300

#reading in shape file for world map
#creating path to zipped shapefile
zip_shapefile_path = 'ne_10m_admin_0_countries.zip'

#checking shapefiles files in the zip
with zipfile.ZipFile(zip_shapefile_path, 'r') as zipf:
    shp_files = [f for f in zipf.namelist() if f.endswith('.shp')]
    print(f"Shapefile(s) found in the zip: {shp_files}")

#loading shapefile from the zip
shapefile_name = shp_files[0]
world = gpd.read_file(f"zip://{zip_shapefile_path}!{shapefile_name}")

#keeping only necessary name and geomoetry columns
world = world[['NAME', 'geometry']]

# %%

#defining function to create type map for desired date range, using SIPRI data and shape file
def create_arms_export_map(arms_data_path, output_path=None, 
                           start_year=None, end_year=None, country_col='Recipient',
                           year_col='Delivery year', type_col='Armament category', 
                           value_col='Total TIV'):
#reading in arms data
    arms_df = pd.read_csv(arms_data_path)
    
#filtering by desired year range
    if start_year is not None and end_year is not None:
        arms_df = arms_df[(arms_df[year_col] >= start_year) & (arms_df[year_col] <= end_year)]

#aggregating data by weapon type exported to each country
    country_type = arms_df.groupby([country_col, type_col])[value_col].sum().reset_index()
    #getting highest value of export by country
    top_exports = country_type.loc[country_type.groupby(country_col)[value_col].idxmax()]

#creating dictionary connecting country names and export types
    export_type_dict = dict(zip(top_exports[country_col], top_exports[type_col]))

#adding export type to geodata frame
    world['export_type'] = world['NAME'].map(export_type_dict)
    
#getting unique types for the color map
    unique_types = top_exports[type_col].unique()

#creating color map - assigning color value to each armament type
    cmap = plt.cm.get_cmap('tab20', len(unique_types))
    colors = {export_type: cmap(i) for i, export_type in enumerate(unique_types)}
    
#adding color coumn to geodata frame
    world['color'] = world['export_type'].map(colors)
    
#creating the map
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    
    #plotting countries with no data
    world[world['export_type'].isna()].plot(ax=ax, color='lightgray')
    #plotting countries with  data
    for export_type in unique_types:
        world[world['export_type'] == export_type].plot(
            ax=ax, 
            color=colors[export_type],
            label=export_type)
    #adding borders to each country
    world.boundary.plot(ax=ax, linewidth=0.2, edgecolor='black')
    
    #adding legend
    from matplotlib.patches import Patch #importing patch from matplotlib which 
    legend_elements = [Patch(facecolor=colors[etype], edgecolor='black', label=etype) for etype in unique_types]
    ax.legend(handles=legend_elements, title='Export Type', loc='lower left', fontsize='medium', 
              title_fontsize='large', bbox_to_anchor=(0.05, 0.15))
    
    #creating time range to append to title based
    if start_year is not None and end_year is not None:
        time_range = f"{start_year}-{end_year}"
    else:
        time_range = "1990-2024"
    
    #setting title and removing axis
    ax.set_title(f'Most Common US Arms Export Type by Country ({time_range})', fontsize=16)
    ax.set_axis_off()
    
    #ensuring equal aspect ratio for all date ranges
    ax.set_aspect('equal')

    #saving figure to outpath if provided
    if output_path:
        fig.tight_layout()
        fig.savefig(output_path, bbox_inches='tight')
        print(f"Map saved to {output_path}")
    
    
#returning 
    return fig, ax

# %%
#calling the function to create a map for the total time period
fig, ax = create_arms_export_map(
    arms_data_path='trimmed_trade.csv',  #Path to data file
    output_path='Images/us_arms_exports_typemap_1990-2024.png')  # Where to save the map

#calling the function for 2022-2024
fig, ax = create_arms_export_map(
    arms_data_path='trimmed_trade.csv',
    output_path='Images/us_arms_exports_typemap_2022-2024.png', 
    start_year=2022, end_year=2024)

fig, ax = create_arms_export_map(
    arms_data_path='trimmed_trade.csv',
    output_path='Images/us_arms_exports_typemap_2003-2016.png', 
    start_year=2003, end_year=2011)
