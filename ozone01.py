# Ozone at YVR and Abbotsford
# -*- coding: utf-8 -*-

# Run this app with `python app3.py` and
# visit http://127.0.0.1:8050/ in your web browser.
# documentation at https://dash.plotly.com/ 

# based on ideas at "Dash App With Multiple Inputs" in https://dash.plotly.com/basic-callbacks
# plotly express line parameters via https://plotly.com/python-api-reference/generated/plotly.express.line.html#plotly.express.line

import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
# plotly express could be used for simple applications
# but this app needs to build plotly graph components separately 
import plotly.graph_objects as go
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# read in the data from the prepared CSV file. 
# Data are assumed to be in the custom formatted CSV file `YVR and Abbotsford 2017.csv`, stored in the folder `data`. 

all_O3 = pd.read_csv("./YVR and Abbotsford 2017.csv",index_col=0, parse_dates=['date_pst'])

# rolling n-point moving average (hence the .mean()); data points are 1hr apart, hence 24/day or 168/wk.
days = 7
hrs = 24*days
YVR_smoothed = all_O3.YVR_ppb.rolling(hrs, center=True, min_periods=6).mean() 
Abb_smoothed = all_O3.Abbotsford_ppb.rolling(hrs, center=True, min_periods=6).mean() 

# add this as columns to the dataframe
all_O3['YVR_smoothed']=YVR_smoothed
all_O3['Abb_smoothed']=Abb_smoothed

# rolling 8hr moving "average" (hence the .mean()); points are 1hr apart
yvr_8hr_O3 = all_O3.YVR_ppb.rolling(8,min_periods=6).mean()
abb_8hr_O3 = all_O3.Abbotsford_ppb.rolling(8,min_periods=6).mean()

# resample result by "day" (the 'D'), choosing the max value. 
YVR_max8hrsavg=yvr_8hr_O3.resample('D').max()
Abb_max8hrsavg=abb_8hr_O3.resample('D').max()

# Dash starts by defining dashboard controls at the same time as 
# placing them on the page using layout functions.
# HTML can be used, but it's easier to just have Dash translate MarkDown.
# For more control over layout, HTML and a chosen CSS template will be needed.
# YVR = Vancouver airport
# Abb = Abbotsford
# MDA8 = maximum daily 8 hour average

app.layout = html.Div([
# Start the page with introductory text and instructions.
    dcc.Markdown('''
        ### Ozone at two locations for all of 2017

        #### Purpose: 

        Plot two data sets with any combination of raw data, 7-day avg, or maximum daily 8-hr avg.  
        
        #### Instructions

        * Select timeseries to display using checkboxes. Dropdown sets trace type for Abb's data only ("markers" type plots slowly). 
        * Zoom, pan, examine datapoint values, etc. using graph controls, upper right when your mouse is over the graph.
        * Zoom the time-window only using 'click-and-hold' then drag horizontally and release. 
        * Move the graphed window by clicking the "Pan" button. Reset using the the little **"home"** icon.
        * YVR = Vancouver airport, Abb = Abbotsford and MDA8 = maximum daily 8 hour average.

        ----------
        '''),
    html.Div([
# CheckList can define all checkboxes together but then the logic becomes 
# more awkward for this simple task. So each box is a separate CheckBox of this situation.

# Layout intention is to have 3 columns, 2 with checkboxes and a third with the dropdown.
# result is not ideal (dropdown is too low).
# The solution involves manipulating CSS but it is probably better to use BootStrap classes.
# That can be pursued later as it is "cosmetics" not functionality.
        dcc.Markdown('''
        **Select YVR components**
        '''),
        dcc.Checklist(
            id='yvrr_chkbox',
            options=[
                {'label': 'YVR raw', 'value': 'yvrr'}
            ],
            value=['yvrr']
        ),
        dcc.Checklist(
            id='yvrs_chkbox',
            options=[
                {'label': 'YVR smoothed', 'value': 'yvrs'}
            ],
            value=[]
        ),
        dcc.Checklist(
            id='yvrm_chkbox',
            options=[
                {'label': 'YVR MDA8', 'value': 'yvrm'}
            ],
            value=[]
        ),
    ], style={'width': '30%', 'display': 'inline-block'}),
    html.Div([
        dcc.Markdown('''
        **Select Abb. components**
        '''),
        dcc.Checklist(
            id='abbr_chkbox',
            options=[
                {'label': 'Abb raw', 'value': 'abbr'}
            ],
            value=[]
        ),
        dcc.Checklist(
            id='abbs_chkbox',
            options=[
                {'label': 'AbbR smoothed', 'value': 'abbs'}
            ],
            value=[]
        ),
        dcc.Checklist(
            id='abbm_chkbox',
            options=[
                {'label': 'Abb MDA8', 'value': 'abbm'}
            ],
            value=[]
        ),
    ], style={'width': '30%', 'display': 'inline-block'}),
    html.Div([
        dcc.Markdown('''
        Plot type for Abbotsford data only
        '''),
        dcc.Dropdown(
            id='linetype',
            options=[
                {'label': 'Lines', 'value': 'lines'},
                {'label': 'Markers', 'value': 'markers'},
                {'label': 'Lines & markers', 'value': 'lines+markers'}
            ],
            value='lines'
        ),
    ], style={'width': '30%', 'display': 'inline-block'}),

# after controls, place the figure
    dcc.Graph(id='indicator-graphic'),

# then the text for instruction or to define the assignment.
    dcc.Markdown('''
        ## Usage for teaching and learning

        Here are a few examples of questions that could be posed in class, on your own, or as an assignment. Choices will depend on whether this dashboard is being used to compare ozone levels at a coastal location to those further inland, or whether the purpose is to explore the challenges and potential for working with "messy" data sets. 

        1. Plot just one raw data set. How much variation is there over the whole year? 
        2. Use zoom and scrolling functionality to estimate daily variability of this parameter. 
        3. What times during the year seem to have lowest ozone levels? Highest Ozone levels? How difficult is it to make these judgements 
        4. Plot two raw data sets. Which site appears to experience higher ozone events? At what time of year? Why might that be? 
        5. Are ozone variations easier to "see" by processing data with a 7-day average or by calcuating the maximum daily 8-hr average? 
        6. Which of these two processing options makes it easier (or more effective) to compare these two stations stations? Why? 
        7. Look closely at a day or two of smoothed and mda8 data. You should see they appear to be not quite "lined up". Why is this? _{{Because smoothed values are hourly wherease mda8 is a daily value assigned to the date at "0" hours. So the mda8 peak may not match up with a smoothed hourly peak. Most daily peaks are in the afternoon, especially in the summer.}}_
        8. many other ideas ...

        ---

        ## Attribution
        * Data used here are hourly ozone (parts per billion) for 2017 only, from 2 of many monitoring stations. Full datasets can be found at the BC Data Catalogue, [Air Quality Monitoring: Verified Hourly Data](https://catalogue.data.gov.bc.ca/dataset/77eeadf4-0c19-48bf-a47a-fa9eef01f409), licensed under the [Open Government Licence – British Columbia](https://www2.gov.bc.ca/gov/content/data/open-data/open-government-licence-bc). For more information about these data and their source, see the [Status of Ground-Level Ozone in B.C. (2015-2017)](http://www.env.gov.bc.ca/soe/indicators/air/ozone.html) web page.
        * The idea is derived from a discussion between Tara Ivanochko and Rivkah Gardner-Frolick <rivkahgf@gmail.com> who uses the complete dataset as part of a [Python tutorial](https://colab.research.google.com/drive/1DO0ICvInsr74vnl3AcPBoGtJyNrV-J8F?usp=sharing#scrollTo=a5l7UD_njHPv) on importing modules, importing data, plotting timeseries and scatter plots.
        * Code by [Francis Jones](https://www.eoas.ubc.ca/people/francisjones).  
                ''')
], style={'width': '900px'}
)

# The callback function with it's app.callback wrapper.
@app.callback(
    Output('indicator-graphic', 'figure'),
    Input('yvrr_chkbox', 'value'),
    Input('yvrs_chkbox', 'value'),
    Input('yvrm_chkbox', 'value'),
    Input('abbr_chkbox', 'value'),
    Input('abbs_chkbox', 'value'),
    Input('abbm_chkbox', 'value'),
    Input('linetype', 'value'),
    )
def update_graph(yvrr_chkbox, yvrs_chkbox, yvrm_chkbox, abbr_chkbox, abbs_chkbox, abbm_chkbox, linetype):
# constructing all the figure's components
    fig = go.Figure()
    if yvrr_chkbox == ['yvrr']:
        fig.add_trace(go.Scatter(x=all_O3.index, y=all_O3.YVR_ppb,
                    mode='lines', line=dict(color='MediumTurquoise'), name="YVR raw"))
        fig.layout.title = "Vancouver Airport"
    if abbr_chkbox == ['abbr']:
        fig.add_trace(go.Scatter(x=all_O3.index, y=all_O3.Abbotsford_ppb,
                    mode=linetype, line=dict(color='SandyBrown'), name="Abb raw"))
        fig.layout.title = "Abbotsford"
    if yvrs_chkbox == ['yvrs']:
        fig.add_trace(go.Scatter(x=all_O3.index, y=all_O3.YVR_smoothed, 
                    mode="lines", line=dict(color='green'), name="YVR 7-day average"))
        fig.layout.title = "Vancouver Airport"
    if abbs_chkbox == ['abbs']:
        fig.add_trace(go.Scatter(x=all_O3.index, y=all_O3.Abb_smoothed, 
                    mode=linetype, line=dict(color='red'), name="Abb 7-day average"))
        fig.layout.title = "Abbotsford"
# different "x" because mda8 has daily values, not hourly values. 
    if yvrm_chkbox == ['yvrm']:  
        fig.add_trace(go.Scatter(x=YVR_max8hrsavg.index, y=YVR_max8hrsavg, 
                    mode="lines", line=dict(color='blue', width=2), name="YVR max daily 8hr avg"))
        fig.layout.title = "Vancouver Airport"
    if abbm_chkbox == ['abbm']:
        fig.add_trace(go.Scatter(x=YVR_max8hrsavg.index, y=Abb_max8hrsavg, 
                    mode=linetype, line=dict(color='firebrick', width=2), name="Abb max daily 8hr avg"))
        fig.layout.title = "Abbotsford"
    
    if (yvrr_chkbox == ['yvrr'] or yvrs_chkbox == ['yvrs'] or yvrm_chkbox == ['yvrm']) and (abbr_chkbox == ['abbr']or abbs_chkbox == ['abbs'] or abbm_chkbox == ['abbm']):
        fig.layout.title = "Vancouver Airport and Abbotsford"
    fig.update_layout(xaxis_title='Time', yaxis_title='ppb')

    return fig    

# dubugging on causes the active page to refresh as soon as edits are saved. 
# Python will quite if there are syntax errors, but if not the app will 
# throw error messages directly into the running browser window. 
# This is a very efficient workflow.
if __name__ == '__main__':
    app.run_server(debug=True)

# I'm not sure if it's more efficient to turn off debug; needs researching. 
    #app.run_server(debug=False)