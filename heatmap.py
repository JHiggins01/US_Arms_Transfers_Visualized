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

#filtering to 1990 and after
arms_data = arms_data[arms_data['Delivery year'] >= 1990]

#creating more eras
arms_90_00 = arms_data[arms_data['Delivery year'].between(1990, 2000)]
arms_00_10 = arms_data[arms_data['Delivery year'].between(2000, 2010)]
arms_10_20 = arms_data[arms_data['Delivery year'].between(2010, 2020)]
arms_20_24 = arms_data[arms_data['Delivery year'].between(2020, 2024)]


#aggregating by recipient country
def aggregate_country (decade):
    return decade.groupby(['Recipient'])['Total TIV'].sum().reset_index()

#agreggating, first total since 1990 and then by decade
country_totals = aggregate_country(arms_data)
a_90_00 = aggregate_country(arms_90_00)
a_00_10 = aggregate_country(arms_00_10)
a_10_20 = aggregate_country(arms_10_20)
a_20_24 = aggregate_country(arms_20_24)

# %%

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


#defining function to create standard column of country names matching shape file
def std_names (decade_in):
    decade_in['Recipient_std'] = decade_in['Recipient'].replace(name_mapping)
    #dropping 2 small deliveries to South Sudan - not included in Shape
    decade_in = decade_in[~decade_in['Recipient'].str.contains('South Sudan', na=False)]
    return(decade_in)

#calling function decades to match names to shape file
country_totals = std_names(country_totals)
a_90_00 = std_names(a_90_00)
a_00_10 = std_names(a_00_10)
a_10_20 = std_names(a_10_20)
a_20_24 = std_names(a_20_24)

#checking to make sure country data names match shapefile names
all_present = country_totals['Recipient_std'].isin(world['NAME']).all()
print("All values present?" , all_present)

# %%
#defining function to merge decades onto shape file and then plot 
def heat_map (decade_plt, years):
    #merging data
    merged_data = world.merge(decade_plt, how='left', left_on='NAME', right_on='Recipient_std')
    #filling nan's with 0 values
    merged_data['Total TIV'] = merged_data['Total TIV'].fillna(0)
    
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
        #fallback if there are no positive values
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
    ax.set_title(f"US Arms Exports by Country {(years)}", fontsize=20)
    #removing axis lines
    ax.set_axis_off()
    
    #adding source
    plt.figtext(0.1,0.01, 'Data Source: SIPRI Amrs Transfer Database', fontsize=10)
    
    #saving
    fig.tight_layout()
    fig.savefig(f"us_arms_exports_heatmapt_{years}.png",bbox_inches='tight')

#calling function on decades to map
heat_map(country_totals, "1990-2024")
heat_map(a_90_00, "1990-2000")
heat_map(a_00_10, "2000-2010")
heat_map(a_10_20, "2010-2020")
heat_map(a_20_24, "2020-2024")
