#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 14 12:51:21 2025

@author: jackhiggins
"""

import pandas as pd

#reading in data
trade = pd.read_csv("trade-register.csv")

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
                                              'Status'])
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

#renaming and creating standardized name column to use later
trimmed_trade['Recipient'] = trimmed_trade['Recipient'].replace(name_mapping)
#dropping 2 small deliveries to South Sudan - not included in Shape
trimmed_trade = trimmed_trade[~trimmed_trade['Recipient'].str.contains('South Sudan', na=False)]

#saving to a csv
trimmed_trade.to_csv('trimmed_trade.csv')
