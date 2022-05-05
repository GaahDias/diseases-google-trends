# Google trends script
# The purpose of this script is to get data from Google Trends about diseases
# from a specific country, and it's subregions. 
# Written by Gabriel Dias


# Imports
import sys
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
pytrends = TrendReq(hl='en-US', tz=360)
keywords = []
suggestions = []
geo_code = ''
geo_codes = []

# Constant variables:
# today_date - just a var to hold today's date, which will be used later on Google Trends search.
# year_month - year and month from today_date's.
# year - in how many years the search is going to be made
# search_type - the type of search that will be done in Google Trends.
TODAY_DATE = date.today()
YEAR_MONTH = TODAY_DATE.strftime('%Y-%m')
YEAR = 1
SEARCH_TYPE = 'Disease'

# User input
keywords = sys.argv[2:]
geo_code = sys.argv[1]

# Getting suggestion code based on keyword
def get_suggestion_codes(keywords, search_type):
    suggestion_codes = []
    for x in range(len(keywords)):
        tmp_suggestion = pytrends.suggestions(keywords[x])
        for y in range(len(tmp_suggestion)):
            if tmp_suggestion[y]['type'] == search_type:
                tmp_suggestion = tmp_suggestion[y]
                break
        suggestion_codes.append(tmp_suggestion)
    return suggestion_codes


# Getting all subregions with a simple 3 months search
def get_subregions(suggestions, geo_code):
    geo_codes = []
    for x in range(len(suggestions)):
        pytrends.build_payload([suggestions[x]['mid']],
        cat=0,
        timeframe=str((TODAY_DATE - relativedelta(months=3))) + ' ' + str(TODAY_DATE),
        geo=geo_code)

        # Getting all subregions (inc_low_vol) with it's geo codes (inc_geo_code)
        tmp_gcs = pytrends.interest_by_region(resolution='COUNTRY', inc_low_vol=True, inc_geo_code=True)

        # Adding all geo codes into our var geo_codes for later usage
        for y in range(len(tmp_gcs['geoCode'])):
            if tmp_gcs['geoCode'][y] not in geo_codes:
                geo_codes.append(tmp_gcs['geoCode'][y])
    return geo_codes

# Searching all suggestions (disease) and subregions on Google Trends
def perform_search(suggestions, geo_codes):
    for x in range(len(suggestions)):
        for y in range(len(geo_codes)):
            print(f'Searching {suggestions[x]["title"]} in {geo_codes[y]}')
            # Search by "suggestion" - Allergy of type Disease for eg.
            # In case you want to search in general, and not by any specific term,
            # replace suggestions[x]['mid'] with keywords[x]
            pytrends.build_payload([suggestions[x]['mid']], 
            cat=0, 
            # Collecting data from one year ago - 2022-03-29 2021-03-29 for eg.
            timeframe=str((TODAY_DATE - relativedelta(years=YEAR))) + ' ' + str(TODAY_DATE),
            # Search by geo codes
            geo=geo_codes[y])

            data = pytrends.interest_over_time()

            if not data.empty:
                # Data cleansing
                data = data.drop(labels=['isPartial'],axis='columns')
                data = data.rename(columns={suggestions[x]['mid']: suggestions[x]['title'].lower()})
                data['region_id'] = geo_codes[y]

            dir_name = f"./Google-Trends_{geo_code}_{str(TODAY_DATE)}"
            file_path = f"{dir_name}/{geo_codes[y]}_{suggestions[x]['title']}_{YEAR_MONTH}_Google-Trends.csv"
            df_save_csv(data, dir_name, file_path)

# Saving final data to csv
def df_save_csv(df, dir_name, file_path):
    try:
        # Creating folder to store the csvs
        if not os.path.isdir(dir_name):
            os.mkdir(os.path.join(Path().absolute(), dir_name))
    except OSError as err:
        print('Something went wrong...\nERROR: ' + err)

    final_data = pd.concat([df], axis=1)
    # Creating final csv file into the created folder
    final_data.to_csv(file_path)
    df.to_csv()

suggestions = get_suggestion_codes(keywords, SEARCH_TYPE)

geo_codes = get_subregions(suggestions, geo_code)
geo_codes.insert(0, geo_code)

perform_search(suggestions, geo_codes)