# Google Trends Script

### The purpose of this script is to collect disease data from a specific country, and it's subregions. It was made to automate the work for Sanofi's Data Engineer team.

### How does it work?

To use the script, you need to pass some arguments at execution, with the first argument being the Geo Code for the region, and the other arguments being the Keywords, or diseases you wish to search.
<br>
For example: `python app.py MX Allergy Flu`. In that case, the script is going to search for the diseases Allergy and Flu in Mexico (MX).

### How to install the dependencies: (pytrends and pandas)

To install the dependencies just use `pip install -r requirements.txt`.
