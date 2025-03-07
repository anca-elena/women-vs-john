import requests
import pandas as pd
import json
from math import floor

import plotly.express as px

from dash import Dash, dcc, html, Output, Input

# Provided data
with open('salaryData.json') as f:
    data = json.load(f)
job_data = pd.DataFrame(data)

# clean data
job_data["yearsofexperience"] = pd.to_numeric(job_data["yearsofexperience"])
job_data["yearsatcompany"] = pd.to_numeric(job_data["yearsatcompany"])

for i, row in job_data.iterrows():
    if floor(float(row["totalyearlycompensation"])) < 10000:
        job_data.at[i, 'totalyearlycompensation'] = floor(float(row["totalyearlycompensation"])) * 1000
    if str(row["gender"]) == "":
        job_data.at[i, 'gender'] = "Other"

job_data = job_data.drop(job_data[job_data['totalyearlycompensation'] == 0].index)


def get_company_entries(search_company, df):
    result_df = df.loc[df['company'].str.lower() == search_company.lower()]
    return result_df


def get_position_entries(search_position, df):
    result_df = df.loc[df['title'].str.lower() == search_position.lower()]
    return result_df


def get_scores():
    women_count = {}
    men_count = {}
    women_total_compensation = {}
    men_total_compensation = {}

    for row in job_data.iterrows():
        company = row[1]["company"]
        compensation = row[1]["totalyearlycompensation"]
        content = row[1]["title"]
        gender = row[1]["gender"]

        men_count.setdefault(company, [0])
        women_count.setdefault(company, [0])
        women_total_compensation.setdefault(company, [0])
        men_total_compensation.setdefault(company, [0])

        if gender == "Female":
            women_count[company][0] += 1
            women_total_compensation[company][0] += int(compensation)
        elif gender == "Male":
            men_count[company][0] += 1
            men_total_compensation[company][0] += int(compensation)

    reindex = {"company": list(women_count.keys()),
               "Women Count": [wc[0] for wc in women_count.values()],
               "Men Count": [mc[0] for mc in men_count.values()],
               "Women total compensation": [wtc[0] for wtc in women_total_compensation.values()],
               "Men total compensation": [mtc[0] for mtc in men_total_compensation.values()],
               "Women avg compensation": [],
               "Men avg compensation": [],
               "wm-ratio": [],
               "wm-comp-ratio": [],
               "comp-score": []
               }

    # Calculate the ratio per country and add it to the reindex dictionary
    for i, company in enumerate(reindex['company']):
        women_count = reindex['Women Count'][i]
        men_count = reindex['Men Count'][i]
        women_total = reindex['Women total compensation'][i]
        men_total = reindex['Men total compensation'][i]

        if women_count == 0 and men_count == 0:
            ratio = 0
        elif women_count != 0 and men_count == 0:
            ratio = 1
        else:
            ratio = women_count / men_count  # Calculate the ratio, handle division by zero

        if women_count != 0:
            women_avg = women_total / women_count
            reindex['Women avg compensation'].append(women_avg)
        else:
            women_avg = 0
            reindex['Women avg compensation'].append(0)
        if men_count != 0:
            men_avg = men_total / men_count
            reindex['Men avg compensation'].append(men_avg)
        else:
            men_avg = 0
            reindex['Men avg compensation'].append(0)

        if men_avg != 0:
            wm_comp_r = women_avg / men_avg
            reindex['wm-comp-ratio'].append(wm_comp_r)
        else:
            # future TODO: maybe change the ratio?
            wm_comp_r = 1
            reindex['wm-comp-ratio'].append(1)

        reindex['comp-score'].append(ratio + wm_comp_r)
        reindex['wm-ratio'].append(ratio)

    d = pd.DataFrame(reindex)
    d = d.drop(d[d['Women Count'] + d['Men Count'] < 20].index)

    return d

    # maybe an idea for later
    # 0.6 (0.6 > 0.5) - meh (1 - 0.6 = 0.4)
    # 0.5 - ideal
    # 0.4 - meh


def get_top_best(sort_by_comp):
    d = get_scores()

    if (sort_by_comp):
        top_ten = d.sort_values(by=['comp-score'], ascending=False).head(20)
    else:
        top_ten = d.sort_values(by=['wm-ratio'], ascending=False).head(20)
    ret = []

    for row in top_ten.iterrows():
        ratio = round(row[1]["wm-ratio"], 3)
        score = round(row[1]['comp-score'], 3)
        cstr = str(row[1]["company"]) + " | " + str(ratio) + " | " + str(score)
        ret.append(cstr)

    return ret


def get_top_worst(sort_by_comp):
    d = get_scores()

    if (sort_by_comp):
        top_ten = d.sort_values(by=['comp-score'], ascending=False).tail(20)
    else:
        top_ten = d.sort_values(by=['wm-ratio'], ascending=False).tail(20)

    ret = []

    for row in top_ten.iterrows():
        ratio = round(row[1]["wm-ratio"], 3)
        score = round(row[1]['comp-score'], 3)
        cstr = str(row[1]["company"]) + " | " + str(ratio) + " | " + str(score)
        ret.append(cstr)

    return ret


def get_frame(search_company=None, search_position=None, years="years_of_experience"):
    # get_top_best()
    final_df = job_data
    if search_company:
        final_df = get_company_entries(search_company, final_df)
    if search_position:
        final_df = get_position_entries(search_position, final_df)

    return final_df


app = Dash(__name__)

app.layout = html.Div([
    html.H4('Summary of the data'),

    html.P("Search by company:"),
    dcc.Textarea(id='search_company', value='', style={'width': '20%', 'height': '15px'}),

    html.P("Search by position:"),
    dcc.Textarea(id='search_position', value='', style={'width': '20%', 'height': '15px'}),

    dcc.RadioItems(id='years', options=[
        {"label": "Years at the Company", "value": "years_at_company"},
        {"label": "Years of experience", "value": "years_of_experience"}
    ], value="years_of_experience", inline=True),

    dcc.Graph(id="graph"),

    html.Div([
        html.Div(
            className="trend",
            children=[
                html.H4("Top 20 best companies by total company score:"),
                html.Ul(id='my-list', children=[html.Li(i) for i in get_top_best(True)])
            ],
        ),
        html.Div(
            className="trend",
            children=[
                html.H4("Top 20 worst companies by total company score:"),
                html.Ul(id='my-list', children=[html.Li(i) for i in get_top_worst(True)])
            ],
        )
    ], style={'display': 'flex', 'justify-content': 'space-around'}),

    html.Div([
        html.Div(
            className="trend",
            children=[
                html.H4("Top 20 best companies by w/m ratio:"),
                html.Ul(id='my-list', children=[html.Li(i) for i in get_top_best(False)])
            ]
        ),
        html.Div(
            className="trend",
            children=[
                html.H4("Top 20 worst companies by w/m ratio:"),
                html.Ul(id='my-list', children=[html.Li(i) for i in get_top_worst(False)])
            ],
        )
    ], style={'display': 'flex', 'justify-content': 'space-around'}),
])


@app.callback(
    Output("graph", "figure"),
    Input("search_company", "value"),
    Input("search_position", "value"),
    Input("years", "value")
)
def display(search_company, search_position, years):
    df = get_frame(search_company=search_company if search_company != "" else None,
                   search_position=search_position if search_position != "" else None,
                   years=years)

    df["totalyearlycompensation"] = pd.to_numeric(df["totalyearlycompensation"])
    df = df.sort_values("totalyearlycompensation", ascending=True)

    df["yearsofexperience"] = pd.to_numeric(df["yearsofexperience"])
    df["yearsatcompany"] = pd.to_numeric(df["yearsatcompany"])

    df = df.sort_values("yearsofexperience", ascending=True)
    fig = px.scatter(df, y="totalyearlycompensation", x="yearsofexperience", color="gender")

    if years == "years_at_company":
        df = df.sort_values("yearsatcompany", ascending=True)
        fig = px.scatter(df, y="totalyearlycompensation", x="yearsatcompany", color="gender")

    return fig


app.run_server(debug=True)
print("done")
