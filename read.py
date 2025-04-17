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

#saving to a csv
trimmed_trade.to_csv('trimmed_trade.csv')

# %%
#grouping by different values
################################
#group by country by year
by_year = trimmed_trade.groupby(['Recipient', 'Delivery year'])['Total TIV'].sum().reset_index()
#group by country only
by_country = by_year.groupby(['Recipient'])['Total TIV'].sum().reset_index()

#grouping by weapon category
#checking types
types = trimmed_trade['Armament category'].unique().tolist()
by_cat_tot = trimmed_trade.groupby('Armament category')['Total TIV'].sum().reset_index()
by_cat_year = trimmed_trade.groupby(['Armament category','Delivery year'])['Total TIV'].sum().reset_index()
by_cat_country = trimmed_trade.groupby()