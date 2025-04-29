#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 25 17:06:38 2025

@author: jackhiggins
"""
#this script prepares geopackage to be imported into Tableau

import pandas as pd
import geopandas as gpd
import zipfile

#reading in data
arms_data = pd.read_csv('trimmed_trade.csv')

#aggregating by country and year
annual_tiv = arms_data.groupby(['Recipient', 'Delivery year'])['Total TIV'].sum().reset_index()
#pivoting to create columns for each year
wide_annual_tiv = annual_tiv.pivot(index='Recipient', 
                                   columns='Delivery year', 
                                   values='Total TIV')
#renaming columns for clarity
wide_annual_tiv.columns = [f'TIV_{year}' for year in wide_annual_tiv.columns]

# %%


#resetting index and replacing nan values 
wide_annual_tiv = wide_annual_tiv.reset_index()
wide_annual_tiv = wide_annual_tiv.fillna(0)

#creating dataframe with year/type columns
annual_tiv_type = arms_data.groupby(['Recipient', 'Delivery year', 
                                     'Armament category'])['Total TIV'].sum().reset_index()

#pivoting to wide
wide_type = annual_tiv_type.pivot_table(
    index='Recipient',
    columns=['Delivery year', 'Armament category'],
    values='Total TIV',
    aggfunc='sum',
    fill_value=0)

#flattening multi level columns and resetting index
wide_type.columns = [f"{year}_{category}" for year, category in wide_type.columns]
wide_type = wide_type.reset_index()

#merging to make master wide
complete_wide_data = pd.merge(wide_annual_tiv, wide_type, on='Recipient')

# %%

#reading in shapefile to merge with
#creating path to zipped shapefile
zip_shapefile_path = 'ne_10m_admin_0_countries.zip'

#checking shapefiles in the zip
with zipfile.ZipFile(zip_shapefile_path, 'r') as zipf:
    shp_files = [f for f in zipf.namelist() if f.endswith('.shp')]
    print(f"Shapefile(s) found in the zip: {shp_files}")

#loading shapefile from the zip
shapefile_name = shp_files[0]
world = gpd.read_file(f"zip://{zip_shapefile_path}!{shapefile_name}")

# %%

#simple merge
merged_data = world.merge(
    complete_wide_data,
    left_on='NAME',
    right_on='Recipient',
    how='left')

#setting nan's to 0 for countries which haven't recieved weapons
numeric_columns = merged_data.select_dtypes(include=['float64', 'int64']).columns
merged_data[numeric_columns] = merged_data[numeric_columns].fillna(0)

# %%

#saving as GeoPackage
merged_data.to_file("arms_transfers_map.gpkg", driver='GPKG', layer='arms_transfers')