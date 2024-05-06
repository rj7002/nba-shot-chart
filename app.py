import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd
from nbapy import constants
from nbapy.nba_api import NbaAPI
import datetime
from nba_api.stats.static import players
import requests
currentyear = datetime.datetime.now().year

from nba_api.stats.static import players
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
            player_info.append({'Player': player_name, 'Player ID': 2})

# Create a DataFrame from the player info list
    player_info_df = pd.DataFrame(player_info)

# Save the DataFrame to a CSV file
    player_info_df.to_csv('playerids.csv', index=False)

    print("Player IDs saved to player_ids2.csv")

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

def create_court(ax, color):
    # Short corner 3PT lines
    ax.plot([-220, -220], [0, 140], linewidth=2, color=color)
    ax.plot([220, 220], [0, 140], linewidth=2, color=color)

    # 3PT Arc
    ax.add_artist(patches.Arc((0, 140), 440, 315, theta1=0, theta2=180, facecolor='none', edgecolor=color, lw=2))

    # Lane and Key
    ax.plot([-80, -80], [0, 190], linewidth=2, color=color)
    ax.plot([80, 80], [0, 190], linewidth=2, color=color)
    ax.plot([-60, -60], [0, 190], linewidth=2, color=color)
    ax.plot([60, 60], [0, 190], linewidth=2, color=color)
    ax.plot([-80, 80], [190, 190], linewidth=2, color=color)
    ax.add_artist(patches.Circle((0, 190), 60, facecolor='none', edgecolor=color, lw=2))

    # Rim
    ax.add_artist(patches.Circle((0, 60), 15, facecolor='none', edgecolor=color, lw=2))

    # Backboard
    ax.plot([-30, 30], [40, 40], linewidth=2, color=color)

    # Remove ticks
    ax.set_xticks([])
    ax.set_yticks([])

    # Set axis limits
    ax.set_xlim(-250, 250)
    ax.set_ylim(0, 470)
    
    return ax

class ShotChart:
    _endpoint = "shotchartdetail"

    def __init__(
        self,
        player_id: str,
        team_id=constants.TeamID.Default,
        game_id=constants.GameID.Default,
        league_id=constants.League.Default,
        season=constants.CURRENT_SEASON,
        season_type=constants.SeasonType.Default,
        outcome=constants.Outcome.Default,
        location=constants.Location.Default,
        month=constants.Month.Default,
        season_segment=constants.SeasonSegment.Default,
        date_from=constants.DateFrom.Default,
        date_to=constants.DateTo.Default,
        opponent_team_id=constants.OpponentTeamID.Default,
        vs_conf=constants.VsConference.Default,
        vs_div=constants.VsDivision.Default,
        position=constants.PlayerPosition.Default,
        game_segment=constants.GameSegment.Default,
        period=constants.Period.Default,
        last_n_games=constants.LastNGames.Default,
        ahead_behind=constants.AheadBehind.Default,
        context_measure=constants.ContextMeasure.Default,
        clutch_time=constants.ClutchTime.Default,
        rookie_year=constants.RookieYear.Default,
    ):

        self._params = {
            "PlayerID": player_id,
            "TeamID": team_id,
            "GameID": game_id,
            "LeagueID": league_id,
            "Season": season,
            "SeasonType": season_type,
            "Outcome": outcome,
            "Location": location,
            "Month": month,
            "SeasonSegment": season_segment,
            "DateFrom": date_from,
            "DateTo": date_to,
            "OpponentTeamID": opponent_team_id,
            "VsConference": vs_conf,
            "VsDivision": vs_div,
            "PlayerPosition": position,
            "GameSegment": game_segment,
            "Period": period,
            "LastNGames": last_n_games,
            "AheadBehind": ahead_behind,
            "ContextMeasure": context_measure,
            "ClutchTime": clutch_time,
            "RookieYear": rookie_year,
        }
        self.api = NbaAPI(self._endpoint, self._params)

    def shot_chart(self):
        return self.api.get_result("Shot_Chart_Detail")

    def league_average(self):
        return self.api.get_result("LeagueAverages")

page = st.sidebar.selectbox("", ('Home','Shot Chart Visualization'))
players = pd.read_csv('playerids.csv')
player_df = pd.DataFrame(players)

if page == 'Home':
    scrape_player_ids()
    st.title('NBA Shot Chart Visualizer')
    st.subheader('Plot Shot Charts For Any Player')

elif page == 'Shot Chart Visualization':
    st.title('Shot Chart Visualization')

# Streamlit UI

# Get player ID from user input
    PLAYER = st.sidebar.selectbox('Select a player', player_df['Player'].to_list())
    PLAYER_ID = player_df.loc[(player_df['Player'] == PLAYER), 'Player ID'].iloc[0]

    player_row = player_df.loc[player_df['Player'] == PLAYER]

    if not player_row.empty:
    # If the player row exists, get the player ID
        playerid = player_row['Player ID'].values[0]
    else:
    # If the player row does not exist, provide a default player ID
        playerid = 436
    display_player_image(playerid,300,PLAYER)
    col1, col2= st.columns(2)

# Get season range from user input
    SEASONS = [f'{i}-{str(i+1)[2:]}' for i in range(1996, currentyear)]
    SEASON = st.sidebar.selectbox('Select a season', SEASONS)
    Stat = st.sidebar.selectbox('Select Stat',['PTS', 'FGA','FG3A'])
    GameSegment = st.sidebar.checkbox('Game Segment')
    if GameSegment == 1:
        typeseg = st.sidebar.selectbox('Game Segment',['First Half', 'Second Half', 'Overtime'])
    else:
        typeseg = None
    Clutch_Time = st.sidebar.checkbox('Clutch Time')
    if Clutch_Time == 1:
        typeclutch = st.sidebar.selectbox('Time Remaining', ['Last 5 Minutes', 'Last 4 Minutes','Last 3 Minutes','Last 2 Minutes','Last 1 Minute','Last 30 Seconds', 'Last 10 Seconds'])
    else:
        typeclutch = None
    Playoffs = st.sidebar.checkbox('Playoffs')
    if Playoffs == 1:
        typeseason = 'Playoffs'
    else:
        typeseason = "Regular Season"
    Conference = st.sidebar.checkbox('Conference')
    if Conference == 1:
        typeconf = st.sidebar.selectbox('Select a conference',['East', 'West'])
    else:
        typeconf = None
    Location = st.sidebar.checkbox('Location')
    if Location == 1:
        typeloc = st.sidebar.selectbox('Location',['Home', 'Road'])
    else:
        typeloc = None
    Outcome = st.sidebar.checkbox('Outcome')
    if Outcome == 1:
        typeout = st.sidebar.selectbox('Outcome',['W', 'L'])
    else:
        typeout = None



    if PLAYER_ID:
    # Create ShotChart object
        shot_chart = ShotChart(PLAYER_ID, season=SEASON,game_segment=typeseg,clutch_time=typeclutch,season_type=typeseason,vs_conf=typeconf,location=typeloc,outcome=typeout,context_measure=Stat)

    # Fetch shot chart data
        shot_data = shot_chart.shot_chart()

    # Visualize shot chart
        if not shot_data.empty:
        # Plot shot chart on basketball court
            plt.figure(figsize=(10, 5))
            ax = plt.gca()
        # Plot makes in green
            ax.scatter(shot_data[shot_data["SHOT_MADE_FLAG"] == 1]["LOC_X"], 
                    shot_data[shot_data["SHOT_MADE_FLAG"] == 1]["LOC_Y"] + 60, 
                    color="green", alpha=0.6, label="Makes",marker='o')
        # Plot misses in red
            ax.scatter(shot_data[shot_data["SHOT_MADE_FLAG"] == 0]["LOC_X"], 
                    shot_data[shot_data["SHOT_MADE_FLAG"] == 0]["LOC_Y"] + 60, 
                    color="red", alpha=0.6, label="Misses",marker='x')
            create_court(ax, 'black')
            ax.set_xlim(-250, 250)
            ax.set_ylim(0, 470)
            ax.set_aspect('equal')
            ax.legend()
            with col2:
                st.subheader('Makes and Misses Plot')
                st.pyplot(plt)

            fig = plt.figure(figsize=(4, 3.76))
            ax = fig.add_axes([0, 0, 1, 1])

            # Plot hexbin with custom colormap
            hb = ax.hexbin(shot_data['LOC_X'], shot_data['LOC_Y'] + 60, gridsize=(30, 30), extent=(-300, 300, 0, 940), bins='log', cmap='inferno')
            legend_elements = [plt.Line2D([0], [0], marker='H', color='w', label='Less Shots', markerfacecolor='black', markersize=10),
            plt.Line2D([0], [0], marker='H', color='w', label='More Shots', markerfacecolor='yellow', markersize=10)]
            plt.legend(handles=legend_elements, loc='upper right')  
            # Customize color bar legend


            ax = create_court(ax, 'black')


            with col1:
                st.subheader('Shot Frequency Plot')
                st.pyplot(fig)
    
        



    else:
        st.error("Failed to fetch shot chart data. Please check the player ID and season range.")
