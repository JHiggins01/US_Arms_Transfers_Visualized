#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 14 12:51:21 2025

@author: jackhiggins
"""

import pandas as pd

# opening data to find true header
file_path = 'trade-register.csv'

# finding line number where true header starts
header_line_idx = None
with open(file_path, 'r', encoding='latin1') as f:  # <--- changed encoding
    for idx, line in enumerate(f):
        if line.startswith('SIPRI AT'):
            header_line_idx = idx
            break
if header_line_idx is None:
    raise ValueError("Header line starting with 'Recipient' not found.")

# reading in data
trade = pd.read_csv(file_path, skiprows=header_line_idx, header=0, encoding='latin1')

# %%

#checking list of unique recipients to remove non-state entries
unique_values = trade['Recipient'].unique().tolist()

#removing non-country records
trimmed_trade = trade[~trade['Recipient'].str.endswith('*')]
trimmed_trade = trimmed_trade[~trade['Recipient'].str.endswith(')')]

#checking
unique_values = trimmed_trade['Recipient'].unique().tolist()

#dropping unneeded columns
trimmed_trade = trimmed_trade.drop(columns = ['Order date is estimate',
                                              'Numbers delivered is estimate',
                                              'Delivery year is estimate',
                                              'Supplier', 'Local production',
                                              'Status',
                                              'SIPRI AT Database ID'])
#renaming columns for ease
trimmed_trade = trimmed_trade.rename(columns = {'TIV delivery values':'Total TIV'})

#trimming to data from 1990 through present - helps with post Soviet States
trimmed_trade = trimmed_trade[trimmed_trade['Delivery year'] >= 1990]

#dictionary for standardizing country names to match shape file
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

#standardizing names to match shape file
trimmed_trade['Recipient'] = trimmed_trade['Recipient'].replace(name_mapping)
#dropping 2 small deliveries to South Sudan - not included in Shape
trimmed_trade = trimmed_trade[~trimmed_trade['Recipient'].str.contains('South Sudan', na=False)]

#saving to a csv
trimmed_trade.to_csv('trimmed_trade.csv')
