import streamlit as st
import pandas as pd
from nbapy import constants
from nbapy.nba_api import NbaAPI
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd
from nbapy import constants
import datetime
from nba_api.stats.static import players
import requests
from nba_api.stats.endpoints import LeagueDashPlayerStats
st.set_page_config(page_title="NBA Shot Visualizer", page_icon='https://juststickers.in/wp-content/uploads/2015/05/basket-ball-player-1-decal.png', initial_sidebar_state="expanded")

currentyear = datetime.datetime.now().year

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


class PlayerNotFoundException(Exception):
    pass

class PlayerList:
    """Contains a list of players and their teams.

    Args:
        league_id: ID for the league to look in
        season: Season given to look up. This affects whether or not the player
            is active and on what team.
        active_only: (1 or 0 for true or false respectively).
            Only return active players for the given season.
            If season is set prior to the current season, and active_only is 1,
            then only players who's career ended in the specified season will
            be listed.
    """

    _endpoint = "commonallplayers"

    def __init__(
        self,
        league_id=constants.League.NBA,
        season=constants.CURRENT_SEASON,
        active_only=1,
    ):
        self._params = {
            "LeagueID": league_id,
            "Season": season,
            "IsOnlyCurrentSeason": active_only,
        }
        self.api = NbaAPI(self._endpoint, self._params)

    def players(self):
        return self.api.get_result()

def get_id(
    name, season=constants.CURRENT_SEASON, active_only=0,
):
    """Get a player_id for any specified player.

    Calls PlayerList, then matches name to return the id. Player id is needed
    for most of our player functions.

    Args:
        name: name of the player to lookup. This must match the name
            as presented on nba.com (case insensitive)
        season: season to lookup
        active_only: only match active players

    Returns:
        Nba.com player_id

    Raises:
        PlayerNotFoundException
    """
    name = name.lower()

    players = pd.DataFrame(PlayerList(season=season, active_only=active_only).players())

    player = players.loc[players["DISPLAY_FIRST_LAST"].str.lower() == name, "PERSON_ID"]
    try:
        player_id = player.iat[0]
    except IndexError:
        raise PlayerNotFoundException(
            f'The player "{name}" could not be found. Please double check the '
            "name against nba.com"
        )

    return player_id

def get_player_season_range(player_id):
    player_stats = PlayerList().players()
    if not player_stats.empty:
        player_stats = player_stats[player_stats["PERSON_ID"] == player_id]
        if not player_stats.empty:
            first_season = player_stats['FROM_YEAR'].tolist()[0] if player_stats['FROM_YEAR'].tolist() else '1996'
            last_season = player_stats['TO_YEAR'].tolist()[0] if player_stats['TO_YEAR'].tolist() else str(currentyear-1)
        else:
            first_season = '1996'
            last_season = str(currentyear-1)
    else:
        first_season = '1996'
        last_season = str(currentyear-1)
    return first_season, last_season



# Define Streamlit app

st.title('NBA Shot Visualizer')
    # User input for player name
player_name = st.text_input("Enter player name (not case sensitive)")
if player_name:
    try:
            # Call get_id function to retrieve player ID
        PLAYER_ID = get_id(player_name)
        st.success(f"Successfully found {player_name}")
        display_player_image(PLAYER_ID,300,'')
            
            # Get the range of seasons the selected player has played in
        first_season, last_season = get_player_season_range(PLAYER_ID)
            # Generate the list of seasons within the range
        SEASONS = [f'{season}-{str(int(season)+1)[2:]}' for season in range(int(first_season), int(last_season)+1)]
            
        SEASON = st.sidebar.selectbox('Select a season', reversed(SEASONS))
        player_stats = LeagueDashPlayerStats(season=SEASON,per_mode_detailed='PerGame')
        player_stats_df = player_stats.get_data_frames()[0]
        specificstats = player_stats_df[player_stats_df['PLAYER_ID'] == PLAYER_ID]

        Stat = st.sidebar.selectbox('Select Stat',['MAKES', 'MISSES','FGA','3PA','FB PTS','PTS OFF TOV','2ND CHANCE PTS','PF'])
        if Stat == 'MAKES':
            Stat2 = 'PTS'
        elif Stat == 'MISSES':
            Stat2 = 'FGA'
        elif Stat == 'FGA':
            Stat2 = 'FGA'
        elif Stat == '3PA':
            Stat2 = 'FG3A'
        elif Stat == 'FB PTS':
            Stat2 = 'PTS_FB'
        elif Stat == 'PTS OFF TOV':
            Stat2 = 'PTS_OFF_TOV'
        elif Stat == '2ND CHANCE PTS':
            Stat2 = 'PTS_2ND_CHANCE'
        elif Stat == 'PF':
            Stat2 = 'PF'
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
        AheadBehind = st.sidebar.checkbox('Ahead/Behind')
        if AheadBehind == 1:
            typeaheadbehind = st.sidebar.selectbox('Ahead/Behind',['Behind or Tied','Ahead or Tied'])
        else:
            typeaheadbehind = None

        col1, col2 = st.columns(2)
            # Create ShotChart object
        shot_chart = ShotChart(PLAYER_ID, season=SEASON,game_segment=typeseg,clutch_time=typeclutch,season_type=typeseason,vs_conf=typeconf,location=typeloc,outcome=typeout,context_measure=Stat2,ahead_behind=typeaheadbehind)

            # Fetch shot chart data
        shot_data = shot_chart.shot_chart()

            # Visualize shot chart
        if not shot_data.empty:
            if Stat != 'MISSES':
                # Plot shot chart on basketball court
                plt.figure(figsize=(10, 5))
                ax = plt.gca()
                # Plot makes in green
                total_makes = len(shot_data[shot_data["SHOT_MADE_FLAG"] == 1])
                total_misses = len(shot_data[shot_data["SHOT_MADE_FLAG"] == 0])
                total_shots = total_makes + total_misses
                shooting_percentage = round((total_makes / total_shots) * 100, 1)
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
                ax.legend(loc='upper right')
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
                st.write(specificstats[['PLAYER_NAME', 'TEAM_ABBREVIATION',
       'AGE', 'GP', 'PTS','OREB', 'DREB', 'REB', 'AST',
        'STL', 'BLK', 'TOV', 'BLKA', 'PF', 'PFD', 'W', 'L', 'W_PCT', 'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M',
       'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT',  'PLUS_MINUS']])
                st.sidebar.header(f'{total_makes}/{total_shots} - {shooting_percentage}%')
            else:
                # Plot shot chart on basketball court
                plt.figure(figsize=(10, 5))
                ax = plt.gca()
                # Plot makes in green
                total_misses = len(shot_data[shot_data["SHOT_MADE_FLAG"] == 0])
                shooting_percentage = 0
                # Plot misses in red
                ax.scatter(shot_data[shot_data["SHOT_MADE_FLAG"] == 0]["LOC_X"], 
                        shot_data[shot_data["SHOT_MADE_FLAG"] == 0]["LOC_Y"] + 60, 
                        color="red", alpha=0.6, label="Misses",marker='x')
                create_court(ax, 'black')
                ax.set_xlim(-250, 250)
                ax.set_ylim(0, 470)
                ax.set_aspect('equal')
                ax.legend(loc='upper right')
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
                st.write(specificstats[['PLAYER_NAME', 'TEAM_ABBREVIATION',
       'AGE', 'GP', 'PTS','OREB', 'DREB', 'REB', 'AST',
        'STL', 'BLK', 'TOV', 'BLKA', 'PF', 'PFD', 'W', 'L', 'W_PCT', 'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M',
       'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT',  'PLUS_MINUS']])
                st.sidebar.header(f'0/{total_misses} - {shooting_percentage}%')
    except PlayerNotFoundException as e:
        st.error(str(e))
else:
    st.write("")
