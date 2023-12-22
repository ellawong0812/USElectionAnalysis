#!/usr/bin/env python
# coding: utf-8

# In[7]:


import selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import pandas as pd

# Function to initialize the Selenium driver
def initialize_driver():
    s = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=s)
    return driver

# Function to scrape the state names from the given URL
def scrape_state_names(url):
    response = requests.get(url, timeout=3)
    soup = BeautifulSoup(response.content, 'html.parser')
    item_list = soup.find_all('a', {'class': "styles_is-mobile__c1oGv"})
    states_name = [item.text.replace(' ', '-') for item in item_list]
    return states_name

# Function to generate the list of URLs
def generate_url_list(link_prefix, states_name):
    url_list = [link_prefix + state.lower() + '/house/' for state in states_name]
    return url_list  

# Function to get candidate data from a given URL
def get_candidate_data(driver, url):
    driver.get(url)
    
    #click the two kinds of buttons
    races_button_by_text_xpath = '//button[starts-with(.//span[text()],"See ") and contains(.//span[text()], " more races")]'
    candidates_button_by_text_xpath = '//button[.//span[text()="Other candidates"]]'
    
    
    try:
        print("getting races_button")
        races_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, races_button_by_text_xpath)))
        races_button.click()
        print("clicked races button")
        
        candidates_buttons = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, candidates_button_by_text_xpath)))
        
        for candidates_button in candidates_buttons:
            candidates_button.click()
            
        print("clicked candidates_button button")
    except Exception as e:
        print("Unable to click race/ candidates button: ")
        pass

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    #total number of candidates in the state
    number = len(soup.find_all('tr', class_='styles_container__sXqdi'))
    box = soup.find_all('tr', class_='styles_container__sXqdi')
    
    #scraping the state name
    state=soup.find('p',class_='styles_nav-title__fbC7_').a.text.split('Election')[0]
    state_list = [state] * number

    party_list = extract_party_list(box)
    candidate_list = extract_candidate_list(soup)
    incumbent_list = extract_incumbent_list(soup)
    pct_list = extract_percentage_list(box)
    state_code_list = extract_state_code_list(soup, number)
    district_list = extract_district_list(soup, number)
    vote_list = extract_vote_list(box)
    
    return state_list, party_list, candidate_list, incumbent_list, pct_list, state_code_list, district_list, vote_list


# Function to extract the party list
def extract_party_list(box):
    party_list = []

    for i in range(len(box)):
        party = box[i].find('span', {'class': "styles_tag__5jkDh"})

        if party:
            party_text = party.text
            party_text = party_text.replace('(', '').replace(')', '')  # Remove brackets

            if party_text == 'R':
                party_list.append('Republican')
            elif party_text == 'D':
                party_list.append('Democratic')
            else:
                party_list.append(party_text)
        else:
            party_list.append('/')

    return party_list

# Function to extract the candidate list
def extract_candidate_list(soup):
    candidate = soup.find_all('tbody', class_="styles_container__rgbfN")
    candidate_list = []
    for i in range(len(candidate)):
        if len(candidate[i].find_all('tr')[-1].find_all('span')) == 1:
            for j in range(len(candidate[i].find_all('tr')) - 1):
                name = candidate[i].find_all('tr')[j].find_all('span')[2].text
                candidate_list.append(name.replace('*', ''))
        else:
            for j in range(len(candidate[i].find_all('tr'))):
                name = candidate[i].find_all('tr')[j].find_all('span')[2].text
                candidate_list.append(name.replace('*', ''))
    
    return candidate_list

# Function to extract the incumbent list
def extract_incumbent_list(soup):
    incumbent_list = []
 
    # if more than 1 distrcits
    if soup.find_all('h5', {"class": "styles_is-table__D_lzx"}):
        district_grids = soup.find('div', {"class": "styles_table-container__vTHda"}).find_all("div", {"class": "styles_left-title__rNUfI"})

        for i in range(len(district_grids)):
            # for each candidate
            candidates_in_district = district_grids[i].find_all('tr', {'class': 'styles_container__sXqdi'})
            incumbent_list.extend(["incumbent"])
            incumbent_list.extend(["/"] * (len(candidates_in_district) - 1))
    else:
        incumbent=soup.find('tbody',class_="styles_container__rgbfN").find_all('tr', {"class": "styles_container__sXqdi"})
        for i in range(len(incumbent)):
            if incumbent[i].find('path',{'class':"styles_fill-white__eraEk styles_stroke-white__tmKE_"}):
                incumbent_list.append("incumbent")
            else:
                incumbent_list.append("/")

    return incumbent_list


# Function to extract the percentage list
def extract_percentage_list(box):
    pct_list = []
    for i in range(len(box)):
        if box[i].find('td', {'class': "styles_container__vzwvV"}):
            pct_list.append(box[i].find('td', {'class': "styles_container__vzwvV"}).text)
        else:
            pct_list.append(0)
    
    return pct_list

# Function to extract the state code list
def extract_state_code_list(soup, number):
    state_code = soup.find_all('p', "styles_district-number__5i_rg")
    state_code_list = []
    if state_code:
        for i in range(number):
            state_code_list.append(state_code[0].text.split('-')[0])
    else:
        state_code_list = ['/'] * number
    
    return state_code_list

# Function to extract the district list
def extract_district_list(soup, number):
    district_list = []

    # if more than one district
    if soup.find_all('h5', {"class": "styles_is-table__D_lzx"}):
        district_grids = soup.find('div', {"class": "styles_table-container__vTHda"}).find_all("div", {"class": "styles_left-title__rNUfI"})
        
        # for each district
        #    get the district index
        #    count number of candidate
        #    append district index * number of candidate
        for i in range(len(district_grids)):
            district_index = district_grids[i].find('h5', {"class": "styles_is-table__D_lzx"}).text
            number_of_candidate_within_dist=len(district_grids[i].find_all("tr", {"class": "styles_container__sXqdi"}))
            district_list.extend([district_index]*number_of_candidate_within_dist)
            
    else:
        district_list = ['/'] * number
    
    return district_list
            
# Function to extract the vote list
def extract_vote_list(box):
    vote_list = []
    for i in range(len(box)):
        if box[i].find('td', class_='styles_container__MY5SI'):
            vote_list.append(box[i].find('td', class_='styles_container__MY5SI').text)
        else:
            vote_list.append(0)
    
    return vote_list

# Main function
link_prefix = "https://www.politico.com/2022-election/results/"
driver = initialize_driver()
driver.set_page_load_timeout(5)
try:
    driver.get(url)
except Exception as e:
    print("Load page timeout")
        
states_name = scrape_state_names(link_prefix)
url_list = generate_url_list(link_prefix, states_name)

incumbent_list = []
party_list = []
candidate_list = []
pct_list = []
state_code_list = []
district_list = []
vote_list = []
state_list = []

#check whether the length of each lists are equal or not
def validate_list_lengths():
    lists = [incumbent_list, party_list, candidate_list, pct_list, state_code_list, district_list, vote_list, state_list]
    length = len(lists[0])
    for lst in lists[1:]:
        if len(lst) != length:
            return False
    return True

#print out the length of each lists
def print_list_length():
    print(len(incumbent_list),
    len(party_list),
    len(candidate_list),
    len(pct_list),
    len(state_code_list),
    len(district_list),
    len(vote_list),
    len(state_list))


i = 0
for link in url_list:
    print("Procssing url index: ", i)
    print("Processing url: ", link)
    state, party, candidate, incumbent, pct, state_code, district, vote = get_candidate_data(driver, link)
    state_list.extend(state)
    party_list.extend(party)
    candidate_list.extend(candidate)
    incumbent_list.extend(incumbent)
    pct_list.extend(pct)
    state_code_list.extend(state_code)
    district_list.extend(district)
    vote_list.extend(vote)
    print('finish')
    i = i+1
    
    #if the length of each lists are not equal, break the loop and tell me
    if (validate_list_lengths() == False):
        print("ERROR!!!!!")
        print("Length not equal")
        #print out the length of each lists
        print_list_length()
        break
    

print('end all')



# In[8]:


print(len(incumbent_list),
len(party_list),
len(candidate_list),
len(pct_list),
len(state_code_list),
len(district_list),
len(vote_list),
len(state_list))


# In[9]:


#making dataframe using the scrapped data
df=pd.DataFrame({'Incumbent':incumbent_list,
'Party':party_list,
'Candidate Name':candidate_list,
'Percentage':pct_list,
'State Code':state_code_list,
'District':district_list,
'Vote':vote_list,
'State':state_list})
df


# In[ ]:





# In[10]:


#Download csv file
df.to_csv("/Users/ellawong/Desktop/election_results.csv", index=False)


# In[6]:


#This is the newest one

from dash import html, dcc, Dash
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import json

with open('cd118.json') as f:
    cds = json.load(f) 

with open('statecode.json') as f:
    statecode = json.load(f) 

with open('cdname.json') as f:
    cdname = json.load(f) 
    
election_df = pd.read_csv('election_results.csv')

# Get the list of unique states for the dropdown menu options
dropdown_choices = election_df['State'].unique().tolist()
# Add 'All states' as the first choice of the dropdown list
dropdown_choices.insert(0, 'All states')

# Convert the vote values from strings to numeric values
election_df['Vote'] = election_df['Vote'].str.replace(',', '').astype(int)

# Calculate the total vote count for each district within same state
election_df['Total Votes'] = election_df.groupby(['State','District'])['Vote'].transform('sum')

# Create a new column for the vote percentage of each candidate
election_df['Vote Percentage'] = election_df['Vote'] / election_df['Total Votes']
# if that row belongs to democratic, make the vote percentage be negative
election_df["Vote Percentage"] = election_df.apply(lambda row: float(row["Vote Percentage"]) if row["Party"] == "Republican" else -float(row["Vote Percentage"]), axis=1)

#grouping all vote of same party within one state
df_grouped = election_df.groupby(['State', 'Party'])['Vote'].sum().reset_index()

#e.g. Alabama 01
election_df['State District'] = election_df['State'] + ' ' + election_df['District'].str.replace('st', '').str.replace('nd', '').str.replace('rd', '').str.replace('th', '').str.replace('/','0').str.zfill(2)

#fill all the empty boxes with 0
election_df=election_df.fillna(0)

# This is for the id for the choropleth map e.g. 0101, 0102
election_df['District Number'] = election_df['State District'].str.extract('(\d+)')    
# Create the 'id' column
election_df['id'] = election_df['State'].str.strip().map(statecode)+election_df['District Number']

election_df_incumbent=election_df[election_df['Incumbent'].isin(['incumbent'])]


#change the District column from 1st into 01
def convert_district(district):
    #if district = '/'-->convert it to 01
    #else directly change from 1st to 01
    if district=='/':
        return '01'
    num = int(district[:-2])
    return f'{num:02d}'

election_df['District'] = election_df['District'].apply(convert_district)

app = Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.H1(children='2022 U.S. House Election Results',
                style={'display': 'flex', 'justify-content': 'center'})
    ]),
    html.Hr(),
    html.Div([
        
        # Button for Introduction
        html.Button('Introduction', id='intro_button', n_clicks=0,
                    style={'background-color': '#e9967a','font-size': '16px','cursor': 'pointer','color': 'white','border-radius': '50px'}),
        
        # Message pop out after clicking button
        html.Div(id='alert-output'), 
        
        # Choropleth Map
        html.Div([
            html.H3(
                id='description_map'
            ),
            dcc.Dropdown(
                id='select_state',
                placeholder='Zoom in on a state:',
                options=[{'label': value, 'value': value} for value in dropdown_choices],
                value='All states',
                style={'border-radius': '15px', 'background-color': '#AFEEEE','border-radius': '5px'}
            ),
            dcc.Graph(id='choropleth_map')
        ],
        style={'width': '50%', 'height': '600px', 'float': 'left', 'display': 'inline'
              }),
      
  html.Div([
    # Dropdown for selecting the state
    dcc.Dropdown(
        id='state-dropdown',
        options=[{'label': state, 'value': state} for state in election_df['State'].unique()],
        value=election_df['State'].unique()[0],
        clearable=False,
        style={'border-radius': '15px', 'background-color': '#E0FFFF','border-radius': '5px'}
    ),
      html.H3('Select one district below:'),
    # Radio buttons for selecting the district
    dcc.RadioItems(
        id='district-radio',
        options=[],
        value='',
        labelStyle={'display': 'inline-block', 'margin': '10px'}
    ),
      html.H3(children='Here is the distribution of votes for each candidates within same district:',style={'color': 'purple', 'font-size': '20px'}),
      html.H3(id='description_pie'),
    # Pie chart
    dcc.Graph(id='pie-chart')
],
  style={'width': '50%', 'height': '600px', 'float': 'left', 'display': 'inline'}
         ),      
        
        # Bar chart
        html.Div([
            
            #different hover text mode
            html.P("Select the hover mode you want for the two bar charts below:",
                  style={
                      'color':'#8b4513',
                      "text-decoration":"underline"
                  }),
            dcc.RadioItems(
                id='hover_mode',
                inline=True,
                options=['x', 'closest'],
                value='closest'
            ),
            #first bar chart that shows
            html.Div([
                html.H3(id='description_bar1', children='Total votes received in All states'),
                dcc.Graph(id='bar1')
            ]),
            html.Div([
                html.H3(id='description_bar2', children='Votes received across states'),
                dcc.Graph(id='bar2')
            ])
        ],
        style={'width': '50%', 
               #'float': 'right',
               'display': 'inline-block'})
    ]),
    html.Div([
        html.H3('Please select a state from the dropdown list at the top of this page in order to view the data visualization in a scatter plot and a 3D axes diagram.')
    ]),
    
    
    #scatter plot
    html.Div([
    html.H1("Voter Turnout vs Party",style={'color':'#6495ed','font-size': '20px'}),
    dcc.Graph(id='scatter-plot')
]),
        #3D axes
    html.Div([
        dcc.Graph(id='3d-axes')
    ]),  
    
    #choropleth map: display the party of each incumbent
    html.Div([
        dcc.Graph(
        figure=px.choropleth(
            election_df_incumbent,
            geojson=cds, 
            featureidkey='properties.id',
            locations=election_df_incumbent['id'],
            color='Party',
            color_discrete_map={'Republican': 'red', 'Democratic': 'blue'},
            scope='usa',
            hover_data=['Candidate Name', 'Party','State District'],
            title='The Party Distribution of Incumbents in Each Districts'
        ))
    ]),
    
    #a slider to switch between Republican and Democratic parties and display bar charts showing the top ten percentages of votes received by incumbents from each party.
    html.Div([
    html.H1("Select one party:"),
    dcc.Slider(
        id='party-slider',
        marks={0: 'Republican', 1: 'Democratic'},
        min=0,
        max=1,
        step=1,
        value=0
    ),
    dcc.Graph(id='vote-chart')
]),
    # a tree map
    html.Div([
    dcc.Graph(
    figure=px.treemap(election_df, path=['Party', 'State', 'Candidate Name'], values='Vote',
                     color='Percentage', hover_data=['Vote Percentage'],
                     color_continuous_scale='RdBu', 
                      title='Election Results Treemap',
                     ), style={'height': '800px'}
             
             ),
]),
    
])

#clicking the button
@app.callback(Output('alert-output', 'children'),
              Input('intro_button', 'n_clicks'))
def show_alert(n_clicks):
    if n_clicks is None:
        return ''
    else:
        return dcc.ConfirmDialog(
        id='intro',
        message='The data in this app is scraped from the 2022 U.S. House Election results',
        displayed=True
    ),

# choropleth_map
@app.callback(
    [Output(component_id='description_map', component_property='children'),
     Output(component_id='choropleth_map', component_property='figure')],
    [Input(component_id='select_state', component_property='value')]
)
def plot_choropleth(state):
    if state != 'All states':
        filtered_df = election_df[election_df['State'] == state]
    else:
        filtered_df = election_df
    
    # Filter the dataframe for rows with 'Incumbent' in the incumbent column
    filtered_df_incumbent = filtered_df[filtered_df['Incumbent'].isin(['incumbent'])]
    
    fig = px.choropleth(
        filtered_df_incumbent,
        geojson=cds, 
        featureidkey='properties.id',
        locations=filtered_df_incumbent['id'],
        scope="usa",
        color='Vote Percentage',
        color_continuous_scale="RdBu_r",
        range_color=(-1, 1),
        hover_name=filtered_df_incumbent['State District'],
        hover_data={
        'Winner': filtered_df_incumbent['Candidate Name'],
        'Winning Party': filtered_df_incumbent['Party'],
        'Votes for Winner': filtered_df_incumbent['Vote']
    }
        
    )
    
    fig.update_geos(fitbounds="locations", visible=False)

    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        coloraxis_colorbar=dict(
            title=dict(text=None),
            x=0.95,
            tickvals=[-1, 0, 1],
            ticktext=["favor democratic", "neutral", "favor republican"],
            outlinecolor='black',
            outlinewidth=1,
            lenmode='fraction',
            len=0.3,
            thickness=15,
            tickfont=dict(size=14)
        )
    )
    
    # Count the total number of seats
    total_seats = filtered_df_incumbent.shape[0]
    
    # Count the number of seats won by Republicans
    republican_seats = filtered_df_incumbent[filtered_df_incumbent['Party'].str.lower() == 'republican'].shape[0]
    
    # Count the number of seats won by Democrats
    democratic_seats = filtered_df_incumbent[filtered_df_incumbent['Party'].str.lower() == 'democratic'].shape[0]

    text = f'Total seats: {total_seats} | Republican won: {republican_seats} seats | Democratic won: {democratic_seats} seats'

    return text, fig 

# Update the district radio buttons based on the selected state
@app.callback(
    Output('district-radio', 'options'),
    [Input('state-dropdown', 'value')]
)
def update_district_radio(state):
    districts = election_df[election_df['State'] == state]['District'].unique()
    return [{'label': district, 'value': district} for district in districts]

# Update the pie chart based on the selected state and district
@app.callback(
    [Output('description_pie','children'),
    Output('pie-chart', 'figure')],
    [Input('state-dropdown', 'value'),
     Input('district-radio', 'value')]
)
def update_pie_chart(state, district):
    filtered_df = election_df[(election_df['State'] == state) & (election_df['District'] == district)]
    fig = px.pie(filtered_df, values='Vote', names='Candidate Name',height=400,width=500,hole=.3, color='Party',color_discrete_map={'Republican': '#ED1C2E', 'Democratic': '#005BAC', 'Libertarian Party': '#FED105'})
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    incumbent = filtered_df[filtered_df['Incumbent'].str.lower() == 'incumbent']
    party = incumbent['Party'].values
    
    text= f'{incumbent["Candidate Name"].values} from the {party} gets the most votes'
    text = text.replace('[', '').replace(']', '').replace("'",'')
    
    return text, fig

# bar chart x 2
@app.callback(
    [Output(component_id='description_bar1', component_property='children'),
     Output(component_id='bar1', component_property='figure'),
     Output(component_id='description_bar2', component_property='children'),
     Output(component_id='bar2', component_property='figure')],
    [Input(component_id='select_state', component_property='value'),
     Input("hover_mode", "value")]
    )
def plot_stat_data(state, mode):
    if state != 'All states':
        filtered_df = election_df[election_df['State'] == state]
        filtered_df2 = df_grouped[df_grouped['State'] == state]
        x_option='State District'
    else:
        filtered_df = df_grouped
        # Dataframe that contains the sum of votes grouped by party
        filtered_df2 = election_df.groupby('Party')['Vote'].sum().reset_index()
        x_option='State'

    fig1 = px.bar(
        filtered_df2, x='Vote', y='Party', color='Party',
        color_discrete_map={'Republican': '#ED1C2E', 'Democratic': '#005BAC', 'Libertarian Party': '#FED105'},
         width=800, height=700
    
    )
    fig1.update_layout(
        xaxis_title='Vote',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", title="Party", x=1)
    )
    fig1.update_layout(hovermode=mode)
    
    text1 = f'Total votes received in {state}'

    fig2 = px.bar(
        filtered_df, x= x_option, y='Vote', color='Party',
        color_discrete_map={'Republican': '#ED1C2E', 'Democratic': '#005BAC', 'Libertarian Party': '#FED105'},
        width=1000, height=600
    )
    
    fig2.update_layout(hovermode=mode)
    
    text2 = f'Votes received across {"congressional districts" if state != "All states" else "states"}'

    return text1, fig1, text2, fig2

#scatter plot
@app.callback(
    Output('scatter-plot', 'figure'),
    Input('select_state', 'value')
)
def update_scatter_plot(selected_state):
    filtered_df = election_df[election_df['State'] == selected_state]
    fig = px.scatter(filtered_df, x='Party', y='Vote',
                     color='Party',color_discrete_map={'Republican': '#ED1C2E', 'Democratic': '#005BAC', 'Libertarian Party': '#FED105'},
                     hover_data=['Candidate Name'], symbol='Party',
                    width=800, height=600)
    fig.update_traces(marker_size=10)
    return fig

#3D Axes diagram
@app.callback(
    Output('3d-axes', 'figure'),
    Input('select_state', 'value')
)
def update_plots(select_state):
    filtered_df = election_df[election_df['State'] == select_state]

    # Update the 3D Axes diagram
    fig = px.scatter_3d(filtered_df, x='Percentage', y='Vote Percentage', z='Total Votes', color='Party',
                           labels={'Percentage': 'Candidate Percentage', 'Vote Percentage': 'Vote Percentage',
                                   'Total Votes': 'Total Votes'},color_discrete_map={'Republican': '#ED1C2E', 'Democratic': '#005BAC', 'Libertarian Party': '#FED105'},)
    
    fig.update_layout(scene = dict(
                    xaxis = dict(
                         backgroundcolor="rgb(200, 200, 230)",
                         gridcolor="white",
                         showbackground=True,
                         zerolinecolor="white",),
                    yaxis = dict(
                        backgroundcolor="rgb(230, 200,230)",
                        gridcolor="white",
                        showbackground=True,
                        zerolinecolor="white"),
                    zaxis = dict(
                        backgroundcolor="rgb(230, 230,200)",
                        gridcolor="white",
                        showbackground=True,
                        zerolinecolor="white",),),
                    width=700,
                    margin=dict(
                    r=10, l=10,
                    b=10, t=10)
                  )
    return fig

#a slider to switch between Republican and Democratic parties and display bar charts showing the top ten percentages of votes received by incumbents from each party.
@app.callback(
    Output('vote-chart', 'figure'),
    [Input('party-slider', 'value')]
)
def update_chart(selected_party):
    # Filter the data for incumbents from Republican and Democratic parties
    republican_data = election_df[election_df['Party'] == 'Republican']
    democratic_data = election_df[election_df['Party'] == 'Democratic']

    # Sort the data by vote percentage in descending order
    republican_data = republican_data.sort_values(by='Vote', ascending=False)
    democratic_data = democratic_data.sort_values(by='Vote', ascending=False)

    if selected_party == 0:
        data = republican_data
        bar_color = 'red'
    else:
        data = democratic_data
        bar_color = 'blue'

    top_ten_data = data.head(10)

    fig = px.bar(
        top_ten_data,
        x='Candidate Name',
        y='Vote',
        color='Vote',
        color_continuous_scale=[(0, bar_color), (1, bar_color)],
        hover_data=['State District']
    )
    fig.update_layout(title='Top Ten Incumbent Vote by Party')
    return fig


#if __name__ == '__main__':
#    app.run_server(debug=True)

app.run(jupyter_mode="tab") 


# In[ ]:





# In[ ]:





# In[ ]:




