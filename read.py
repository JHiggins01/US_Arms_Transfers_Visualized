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
                                              'Delivery year is estimate'])

#saving to a csv
trimmed_trade.to_csv('trimmed_trade.csv')

# %%

