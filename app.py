import streamlit as st

# Import packages
from nba_api.stats.endpoints import shotchartdetail
import json
import requests
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt



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
SEASONS = [f'{i}-{str(i+1)[2:]}' for i in range(1999, 2024)]
SEASON = st.multiselect('Select a season', SEASONS)

Clutch_Time = st.checkbox('Clutch Time')
if Clutch_Time == 1:
    typeclutch = st.selectbox('Time Remaining', ['Last 5 Minutes', 'Last 4 Minutes','Last 3 Minutes','Last 2 Minutes','Last 1 Minute','Last 30 Seconds', 'Last 10 Seconds'])
Playoffs = st.checkbox('Playoffs')
Stat = st.selectbox('Select Stat',['PTS', 'FGA','FGM','FG3A','FG3M'])

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
  
def make_shot_chart(TEAM_ID, PLAYER_ID, SEASON):
    clutch_time = typeclutch if Clutch_Time == 1 else None
    seasontype = 'Playoffs' if Playoffs == 1 else 'Regular Season'
    stattype = Stat
    # GET THE DATA
    shot_json = shotchartdetail.ShotChartDetail(
                team_id = TEAM_ID, # team parameter
                player_id = PLAYER_ID, # player parameter
                context_measure_simple = stattype,
                season_nullable = SEASON, # season parameter
                season_type_all_star = seasontype,
                clutch_time_nullable = clutch_time
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
        st.error('Sorry... this player has no data for the given season')
    else:
        shot_data.columns = headers

        # General plot parameters
        mpl.rcParams['font.family'] = 'Avenir'
        mpl.rcParams['font.size'] = 14
        mpl.rcParams['axes.linewidth'] = 2

        # Draw basketball court
        fig = plt.figure(figsize=(4, 3.76))
        ax = fig.add_axes([0, 0, 1, 1])

        ax.hexbin(shot_data['LOC_X'], shot_data['LOC_Y'] + 60, gridsize=(30, 30), extent=(-300, 300, 0, 940), bins='log', cmap='Blues')

        ax = create_court(ax, 'black')

        ax.text(0, 1.05, f'{PLAYER} Shot Chart', transform=ax.transAxes, ha='left', va='baseline')

        st.pyplot(fig)





make_shot_chart(0,PLAYER_ID, SEASON)