#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  2 12:08:44 2025

@author: jackhiggins
"""
#this script prepares data for Tableau mapping
import pandas as pd

#reading in trimmed data
arms_data = pd.read_csv("trimmed_trade.csv")

#aggregating data by year, country, and type for Tableau mapping
agg_arms_data = arms_data.groupby(['Recipient', 'Delivery year', 'Armament category']).agg({
    'Total TIV': 'sum'}).reset_index()

#renaming columns for Tableau Clarity
agg_arms_data = agg_arms_data.rename(columns={
    'recipient_country': 'Country',
    'year': 'Year',
    'category': 'Weapon_Category',})

#saving to a CSV that will be used for Tableau Mapping
agg_arms_data.to_csv('arms_transfers_aggregated.csv', index=False)