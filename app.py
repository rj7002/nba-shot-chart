import requests
import streamlit as st
from nba_api.stats.endpoints import shotchartdetail
import json
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import datetime 
from nba_api.stats.static import players
import plotly.graph_objects as go
import numpy as np

currentyear = datetime.datetime.now().year
def scrape_player_ids():

    # Load the CSV file into a DataFrame
    nba_data_all = pd.read_csv('matched_data.csv')

    # Get the unique player names
    player_names = nba_data_all['Player'].unique()

    # List to store player names and their corresponding IDs
    player_info = []

    # Iterate over each player name
    for player_name in player_names:
    # Find the player by full name
        player = players.find_players_by_full_name(player_name)
    # Check if player found
        if player:
        # Get the player ID
            player_id = player[0]['id']
        # Append player name and ID to the list
            player_info.append({'Player': player_name, 'Player ID': player_id})
        else:
            print(f"No player found for {player_name}")

# Create a DataFrame from the player info list
    player_info_df = pd.DataFrame(player_info)

# Save the DataFrame to a CSV file
    player_info_df.to_csv('playerids.csv', index=False)

    print("Player IDs saved to player_ids2.csv")

# Function to draw basketball court
def create_court(ax, color):
    # Short corner 3PT lines
    ax.plot([-220, -220], [0, 140], linewidth=2, color=color)
    ax.plot([220, 220], [0, 140], linewidth=2, color=color)

    # 3PT Arc
    ax.add_artist(mpl.patches.Arc((0, 140), 440, 315, theta1=0, theta2=180, facecolor='none', edgecolor=color, lw=2))

    # Lane and Key
    ax.plot([-80, -80], [0, 190], linewidth=2, color=color)
    ax.plot([80, 80], [0, 190], linewidth=2, color=color)
    ax.plot([-60, -60], [0, 190], linewidth=2, color=color)
    ax.plot([60, 60], [0, 190], linewidth=2, color=color)
    ax.plot([-80, 80], [190, 190], linewidth=2, color=color)
    ax.add_artist(mpl.patches.Circle((0, 190), 60, facecolor='none', edgecolor=color, lw=2))

    # Rim
    ax.add_artist(mpl.patches.Circle((0, 60), 15, facecolor='none', edgecolor=color, lw=2))

    # Backboard
    ax.plot([-30, 30], [40, 40], linewidth=2, color=color)

    # Remove ticks
    ax.set_xticks([])
    ax.set_yticks([])

    # Set axis limits
    ax.set_xlim(-250, 250)
    ax.set_ylim(0, 470)
    
    return ax

# Modified make_shot_chart function with longer timeout

def make_shot_chart(TEAM_ID, PLAYER_ID, SEASON, SEGMENT, CONF, LOC, OUTCOME):
    clutch_time = typeclutch if Clutch_Time == 1 else None
    seasontype = 'Playoffs' if Playoffs == 1 else 'Regular Season'
    stattype = Stat
    try:
        # Headers with additional fields
        headers = {
            'Host': 'stats.nba.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://stats.nba.com/',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'x-nba-stats-origin': 'stats',
            'x-nba-stats-token': 'true'
        }

        # GET THE DATA with longer timeout and additional headers
        shot_json = shotchartdetail.ShotChartDetail(
            team_id=TEAM_ID, # team parameter
            player_id=PLAYER_ID, # player parameter
            context_measure_simple=stattype,
            season_nullable=SEASON, # season parameter
            season_type_all_star=seasontype,
            clutch_time_nullable=clutch_time,
            game_segment_nullable=SEGMENT,
            vs_conference_nullable=CONF,
            location_nullable=LOC,
            outcome_nullable=OUTCOME,
            timeout=60, # Longer timeout period in seconds
            headers=headers  # Additional headers
        )

        # Load data into a Python dictionary
        shot_data = json.loads(shot_json.get_json())
        # Get the relevant data from our dictionary
        relevant_data = shot_data['resultSets'][0]
        # Get the headers and row data
        headers = relevant_data['headers']
        rows = relevant_data['rowSet']
        # Create pandas DataFrame
        shot_data = pd.DataFrame(rows)
        if shot_data.shape[0] == 0:
            st.error('No data available')
        else:
            shot_data.columns = headers

            # General plot parameters
            # mpl.rcParams['font.family'] = 'Avenir'
            plt.rcParams['font.family'] = 'Avenir'

            mpl.rcParams['font.size'] = 14
            mpl.rcParams['axes.linewidth'] = 2

            # Draw basketball court
            fig = plt.figure(figsize=(4, 3.76))
            ax = fig.add_axes([0, 0, 1, 1])

            # Plot hexbin with custom colormap
            hb = ax.hexbin(shot_data['LOC_X'], shot_data['LOC_Y'] + 60, gridsize=(30, 30), extent=(-300, 300, 0, 940), bins='log', cmap='inferno')
            legend_elements = [plt.Line2D([0], [0], marker='H', color='w', label='Less Shots', markerfacecolor='black', markersize=10),
            plt.Line2D([0], [0], marker='H', color='w', label='More Shots', markerfacecolor='yellow', markersize=10)]
            plt.legend(handles=legend_elements, loc='upper right')  
            # Customize color bar legend


            ax = create_court(ax, 'black')


            st.pyplot(fig)

    except requests.exceptions.ReadTimeout:
        st.error('Timeout error: The request took too long to complete. Please try again later.')

def make_shot_chart2(TEAM_ID, PLAYER_ID, SEASON,SEGMENT, CONF,LOC,OUTCOME):
    clutch_time = typeclutch if Clutch_Time == 1 else None
    seasontype = 'Playoffs' if Playoffs == 1 else 'Regular Season'
    stattype = Stat
    try:
        # GET THE DATA with longer timeout
        shot_json = shotchartdetail.ShotChartDetail(
            team_id=TEAM_ID, # team parameter
            player_id=PLAYER_ID, # player parameter
            context_measure_simple=stattype,
            season_nullable=SEASON, # season parameter
            season_type_all_star=seasontype,
            clutch_time_nullable=clutch_time,
            game_segment_nullable=SEGMENT,
            vs_conference_nullable=CONF,
            location_nullable=LOC,
            outcome_nullable=OUTCOME,
            timeout=60 # Longer timeout period in seconds
        )

        # Load data into a Python dictionary
        shot_data = json.loads(shot_json.get_json())
        # Get the relevant data from our dictionary
        relevant_data = shot_data['resultSets'][0]
        # Get the headers and row data
        headers = relevant_data['headers']
        rows = relevant_data['rowSet']
        # Create pandas DataFrame
        shot_data = pd.DataFrame(rows)
        if shot_data.shape[0] == 0:
            st.error('No data available')
        else:
            shot_data.columns = headers

            # General plot parameters
            mpl.rcParams['font.family'] = 'Avenir'
            mpl.rcParams['font.size'] = 14
            mpl.rcParams['axes.linewidth'] = 2

            # Draw basketball court
            fig = plt.figure(figsize=(4, 3.76))
            ax = fig.add_axes([0, 0, 1, 1])

            # Plot makes and misses
            makes = shot_data[shot_data['SHOT_MADE_FLAG'] == 1]
            misses = shot_data[shot_data['SHOT_MADE_FLAG'] == 0]

            ax.scatter(makes['LOC_X'], makes['LOC_Y'] + 60, color='green', label='Makes', marker='o')
            ax.scatter(misses['LOC_X'], misses['LOC_Y'] + 60, color='red', label='Misses', marker='x')

            ax = create_court(ax, 'black')

            ax.legend(loc='upper right')

            st.pyplot(fig)

    except requests.exceptions.ReadTimeout:
        st.error('Timeout error: The request took too long to complete. Please try again later.')



def display_player_image(player_id, width2, caption2):
    # Construct the URL for the player image using the player ID
    image_url = f"https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/latest/260x190/{player_id}.png"
    
    # Check if the image URL returns a successful response
    response = requests.head(image_url)
    
    if response.status_code == 200:
        # If image is available, display it
        st.markdown(
        f'<div style="display: flex; flex-direction: column; align-items: center;">'
        f'<img src="{image_url}" style="width: {width2}px;">'
        f'<p style="text-align: center;">{caption2}</p>'
        f'</div>',
        unsafe_allow_html=True
    )
    
        # st.image(image_url, width=width2, caption=caption2)
    else:
        image_url = "https://cdn.nba.com/headshots/nba/latest/1040x760/fallback.png"
        st.markdown(
        f'<div style="display: flex; flex-direction: column; align-items: center;">'
        f'<img src="{image_url}" style="width: {width2}px;">'
        f'<p style="text-align: center;">{"Image Unavailable"}</p>'
        f'</div>',
        unsafe_allow_html=True
    )
page = st.sidebar.selectbox("", ('Home','Shot Chart Visualization'))

if page == 'Home':
    scrape_player_ids()
    st.title('NBA Shot Chart Visualizer')
    st.subheader('Plot Shot Charts For Any Player')

elif page == 'Shot Chart Visualization':
    st.title('Shot Chart Visualization')

# Load teams file
    teams = pd.read_csv('teamids.csv')
# Load players file
    players = pd.read_csv('playerids.csv')

    teams_df = pd.DataFrame(teams)
    player_df = pd.DataFrame(players)

    team_list = teams_df['Team'].tolist()

# Allow user to select player
    PLAYER = st.selectbox('Select a player', player_df['Player'].to_list())
    PLAYER_ID = player_df.loc[(player_df['Player'] == PLAYER), 'Player ID'].iloc[0]

# Allow user to select season
    SEASONS = [f'{i}-{str(i+1)[2:]}' for i in range(1996, currentyear)]
    SEASON = st.selectbox('Select a season', SEASONS)
    GameSegment = st.checkbox('Game Segment')
    if GameSegment == 1:
        typeseg = st.selectbox('Game Segment',['First Half', 'Second Half', 'Overtime'])
    else:
        typeseg = None
    Clutch_Time = st.checkbox('Clutch Time')
    if Clutch_Time == 1:
        typeclutch = st.selectbox('Time Remaining', ['Last 5 Minutes', 'Last 4 Minutes','Last 3 Minutes','Last 2 Minutes','Last 1 Minute','Last 30 Seconds', 'Last 10 Seconds'])
    Playoffs = st.checkbox('Playoffs')
    Conference = st.checkbox('Conference')
    if Conference == 1:
        typeconf = st.selectbox('Select a conference',['East', 'West'])
    else:
        typeconf = None
    Location = st.checkbox('Location')
    if Location == 1:
        typeloc = st.selectbox('Location',['Home', 'Road'])
    else:
        typeloc = None
    Outcome = st.checkbox('Outcome')
    if Outcome == 1:
        typeout = st.selectbox('Outcome',['W', 'L'])
    else:
        typeout = None
    Stat = st.selectbox('Select Stat',['PTS', 'FGA','FG3A'])
    player_row = player_df.loc[player_df['Player'] == PLAYER]

    if not player_row.empty:
    # If the player row exists, get the player ID
        playerid = player_row['Player ID'].values[0]
    else:
    # If the player row does not exist, provide a default player ID
        playerid = 436
    display_player_image(playerid,300,PLAYER)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader('Shot Frequency Plot')
        make_shot_chart(0,PLAYER_ID,SEASON,typeseg,typeconf,typeloc,typeout)
    
    with col2:
        st.subheader('Makes and Misses Plot')
        make_shot_chart2(0, PLAYER_ID, SEASON,typeseg,typeconf,typeloc,typeout)

