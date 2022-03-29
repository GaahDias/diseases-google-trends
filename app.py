# Google trends script
# The purpose of this script is to get data from Google Trends, and compile that into a csv file
# Written by Gabriel Dias

# Imports
import os
from pathlib import Path
from time import strftime
from pytrends.request import TrendReq
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta

# Defining main variables:
# pytrends - Google Trends API.
# keywords - it's going to store all keywords provided by the user for the search.
# suggestions - it's going to store the suggestions codes based on the keywords.
# geo_code - just a var to store the main geo code (MX, US, ...).
# geo_codes - list to store all geo codes (subregions) for a specific region.
# inc_sub_region - bool flag to include or not subregions in search.
# today_date - just a var to hold today's date, which will be used later on Google Trends search.
# year_month - year and month from today_date's.
# search_type - the type of search that will be done in Google Trends.
pytrends = TrendReq(hl='en-US', tz=360)
keywords = []
suggestions = []
geo_code = ''
geo_codes = []
inc_sub_reg = False
today_date = date.today()
year_month = today_date.strftime('%Y-%m')
search_type = 'Disease'

# Welcome msg
print("============================\n" +
      "|   GOOGLE TRENDS SCRIPT   |\n" +
      "============================\n")

# Getting user input
while True:
    tmp_kw = input("What keywords you wish to search? (Eg.: Allergy, Influenza, ...)\nIf you are done, just press enter.\n")
    if tmp_kw == "":
        geo_code = input("What geo code you wish to search? (Eg.: MX, US, JP, ...)\n")
        geo_codes.append(geo_code)

        while True:
            tmp_sub_reg = input("\nDo you wish to search in all subregions? (y/n).\n")
            if tmp_sub_reg.lower() == 'y':
                inc_sub_reg = True
                break
            elif tmp_sub_reg.lower() == 'n':
                inc_sub_reg = False
                break
            else:
                print("\nPlease, insert y or n.")
        break
    keywords.append(tmp_kw)

# Getting suggestion code based on keyword
for x in range(len(keywords)):
    tmp_suggestion = pytrends.suggestions(keywords[x])
    for x in range(len(tmp_suggestion)):
        if tmp_suggestion[x]['type'] == search_type:
            tmp_suggestion = tmp_suggestion[x]
            break
    suggestions.append(tmp_suggestion)

# Getting all subregions
if inc_sub_reg == True:
    # Simple 3 months search just to get the subregions
    for x in range(len(suggestions)):
        pytrends.build_payload([suggestions[x]['mid']],
        cat=0,
        timeframe=str((today_date - relativedelta(months=3))) + ' ' + str(today_date),
        geo=geo_code)

        # Getting all subregions (inc_low_vol) with it's geo codes (inc_geo_code)
        tmp_gcs = pytrends.interest_by_region(resolution='COUNTRY', inc_low_vol=True, inc_geo_code=True)

        # Adding all geo codes into our var geo_codes for later usage
        for y in range(len(tmp_gcs['geoCode'])):
            if tmp_gcs['geoCode'][y] not in geo_codes:
                geo_codes.append(tmp_gcs['geoCode'][y])

# Searching all suggestions (disease) and subregions on Google Trends
for x in range(len(suggestions)):
    for y in range(len(geo_codes)):
        print(f'Searching {suggestions[x]["title"]} in {geo_codes[y]}')
        # Search by "suggestion" - Allergy of type Disease for eg.
        # In case you want to search in general, and not by any specific term,
        # replace suggestions[x]['mid'] with keywords[x]
        pytrends.build_payload([suggestions[x]['mid']], 
        cat=0, 
        # Collecting data from one year ago - 2022-03-29 2021-03-29 for eg.
        timeframe=str((today_date - relativedelta(years=1))) + ' ' + str(today_date),
        # Search by geo codes
        geo=geo_codes[y])

        tmp_data = pytrends.interest_over_time()

        if not tmp_data.empty:
            # Data cleansing
            tmp_data = tmp_data.drop(labels=['isPartial'],axis='columns')
            tmp_data = tmp_data.rename(columns={suggestions[x]['mid']: suggestions[x]['title']})

        try:
            # Creating folder to store the csvs
            if not os.path.isdir('./Google-Trends_' + geo_code + '_' + str(today_date)):
                os.mkdir(os.path.join(Path().absolute(), 'Google-Trends_' + geo_code + '_' + str(today_date)))
        except OSError as err:
            print('Something went wrong...\nERROR: ' + str(err))

        final_data = pd.concat([tmp_data], axis=1)
        # Creating final csv file into the created folder
        final_data.to_csv('./Google-Trends_' + geo_code + '_' + str(today_date) + '/' + geo_codes[y] + '_' + suggestions[x]['title'] + '_' + year_month + '_Google-Trends.csv')
