import requests
import json
import geonamescache
import numpy as np
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Output, Input

# Provided data
data = requests.get('https://www.levels.fyi/js/salaryData.json').json()
job_data = pd.DataFrame(data)

job_data[['city', 'state', 'country']] = job_data['location'].str.split(', ', n=2, expand=True)
job_data['country'] = job_data['country'].fillna('United States')

# Preloading the maps + separate for states
gapminder = px.data.gapminder().query("year==2007")
gapminder.rename(columns={"country": "Country"}, inplace=True)
loaded = json.load(open("geojson-counties-fips.json", "r"))

# Caching states
gcache = geonamescache.GeonamesCache()
states = gcache.get_us_states_by_names()
reindex = {"code": [c['code'] for c in states.values()], "country_name": [c['name'] for c in states.values()]}

# Building a frame
state_frame = pd.DataFrame(reindex)


def get_frame(search=None, usa_only=False):

    final_df = job_data
    if search:
        final_df = job_data.loc[job_data['title'].str.lower() == search.lower()]

    location_count = {}
    ratio = 0
    women_count = {}
    men_count = {}

    for row in final_df.iterrows():
        city = row[1]["city"]
        state = row[1]["state"]
        country = row[1]["country"]
        content = row[1]["title"]  # Product Manager or Software Engineer
        gender = row[1]["gender"]

        # if search is not None:
        #     search_words = search.split()
        #     found = False
        #     for word in search_words:
        #         if word.lower() in content.lower():
        #             found = True
        #             break
        #     if not found:
        #         continue

        if usa_only:
            res = state
        else:
            res = country
        location_count.setdefault(res, [0])
        men_count.setdefault(res, [0])
        women_count.setdefault(res, [0])
        location_count[res][0] += 1

        if gender == "Female":
            women_count[res][0] += 1
        elif gender == "Male":
            men_count[res][0] += 1

    reindex = {"Country": list(location_count.keys()),
               "Women Count": [wc[0] for wc in women_count.values()],
               "Men Count": [mc[0] for mc in men_count.values()],
               "Count": [c[0] for c in location_count.values()],
               "log-count": [],
               "wm-ratio": []
               }

    # Calculate the ratio per country and add it to the reindex dictionary
    for i, country in enumerate(reindex['Country']):
        women_count = reindex['Women Count'][i]
        men_count = reindex['Men Count'][i]
        if women_count == 0 and men_count == 0:
            ratio = 0
        elif women_count != 0 and men_count == 0:
            ratio = 1
        else:
            ratio = women_count / men_count  # Calculate the ratio, handle division by zero
        reindex['wm-ratio'].append(ratio)
        reindex["log-count"].append(np.log(reindex['Count'])[i])

    d = pd.DataFrame(reindex)
    # d["log-count"] = np.log(d["Count"])

    if usa_only:
        d.rename(columns={"Country": "code"}, inplace=True)
        ret = d.merge(state_frame, on="code")
    else:
        ret = gapminder.merge(d, how='left', on='Country')
    return ret


app = Dash(__name__)

app.layout = html.Div([
    html.H4('Sorting by criteria'),
    html.P("Search by title:"),
    dcc.Textarea(id='search', value='', style={'width': '10%', 'height': '15px'}),
    dcc.RadioItems(
        id='category',
        options=[
            {"label": "Logarithmic employee count", "value": "log-count"},
            {"label": "Overall employee count", "value": "Count"},
            {"label": "Ratio of women to men", "value": "wm-ratio"},
        ],
        value="wm-ratio",
        inline=True
    ),
    dcc.RadioItems(
        id='usa_only',
        options=[
            {"label": "USA only", "value": True},
            {"label": "World", "value": False},
        ],
        value=False,
        inline=True
    ),
    dcc.Graph(id="graph"),
])


@app.callback(
    Output("graph", "figure"),
    Input("search", "value"),
    Input("category", "value"),
    Input("usa_only", "value")
)
def display(search, category, usa_only):
    df = get_frame(search=search if search != "" else None, usa_only=usa_only)

    # if category = log:
    #     # Apply log scale to count
    #     df["Count"] = np.log(df["Count"])

    fig = px.choropleth(df, locations='iso_alpha' if not usa_only else 'code',
                        color=category,
                        locationmode="USA-states" if usa_only else None,
                        color_continuous_scale="Plasma",
                        scope="usa" if usa_only else "world",
                        labels={'Logarithmic count': 'employee count'}
                        )

    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


app.run_server(debug=True)
print("done")
