import io
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
import requests
import plotly.graph_objs as go

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
    f'<p style="text-align: center; font-size: 30px;">{caption2}</p>'
    f'</div>',
    unsafe_allow_html=True
)
    
    
        # st.image(image_url, width=width2, caption=caption2)
    else:
        image_url = "https://cdn.nba.com/headshots/nba/latest/1040x760/fallback.png"
        st.markdown(
        f'<div style="display: flex; flex-direction: column; align-items: center;">'
        f'<img src="{image_url}" style="width: {width2}px;">'
        f'<p style="text-align: center;font-size: larger;">{"Image Unavailable"}</p>'
        f'</div>',
        unsafe_allow_html=True
    )
def create_court(ax, color):
    # Short corner 3PT lines
    ax.set_facecolor('#D2B48C')

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
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    return ax

class Splits:
    """Player stats splits.

    Also a base class containing common arguments for different split type
    child classes.

    Args:
        player_id: ID of the player to look up
        team_id: ID of the team to look up
        measure_type: Specifies type of measure to use (Base, Advanced, etc.)
        per_mode: Mode to measure statistics (Totals, PerGame, Per36, etc.)
        plus_minus: Whether or not to consider plus minus (Y or N)
        pace_adjust: Whether or not to pace adjust stats (Y or N)
        rank: Whether or not to consider rank (Y or N)
        league_id: ID for the league to look in (Default is 00)
        season: Season given to look up
        season_type: Season type to consider (Regular / Playoffs)
        po_round: Playoff round
        outcome: Filter out by wins or losses
        location: Filter out by home or away
        month: Specify month to filter by
        season_segment: Filter by pre/post all star break
        date_from: Filter out games before a specific date
        date_to: Filter out games after a specific date
        opponent_team_id: Opponent team ID to look up
        vs_conference: Filter by conference
        vs_division: Filter by division
        game_segment: Filter by half / overtime
        period: Filter by quarter / specific overtime
        shot_clock_range: Filter statistics by range in shot clock
        last_n_games: Filter by number of games specified in N
    """

    _endpoint = "playerdashboardbygeneralsplits"  # this could be any split

    def __init__(
        self,
        player_id: str,
        team_id: str = "0",
        measure_type=constants.MeasureType.Default,
        per_mode=constants.PerMode.Default,
        plus_minus=constants.PlusMinus.Default,
        pace_adjust=constants.PaceAdjust.Default,
        rank=constants.PaceAdjust.Default,
        league_id=constants.League.Default,
        season=constants.CURRENT_SEASON,
        season_type=constants.SeasonType.Default,
        po_round=constants.PlayoffRound.Default,
        outcome=constants.Outcome.Default,
        location=constants.Location.Default,
        month=constants.Month.Default,
        season_segment=constants.SeasonSegment.Default,
        date_from=constants.DateFrom.Default,
        date_to=constants.DateTo.Default,
        opponent_team_id=constants.OpponentTeamID.Default,
        vs_conference=constants.VsConference.Default,
        vs_division=constants.VsDivision.Default,
        game_segment=constants.GameSegment.Default,
        period=constants.Period.Default,
        shot_clock_range=constants.ShotClockRange.Default,
        last_n_games=constants.LastNGames.Default,
    ):
        self._params = {
            "PlayerID": player_id,
            "TeamID": team_id,
            "MeasureType": measure_type,
            "PerMode": per_mode,
            "PlusMinus": plus_minus,
            "PaceAdjust": pace_adjust,
            "Rank": rank,
            "LeagueID": league_id,
            "Season": season,
            "SeasonType": season_type,
            "PORound": po_round,
            "Outcome": outcome,
            "Location": location,
            "Month": month,
            "SeasonSegment": season_segment,
            "DateFrom": date_from,
            "DateTo": date_to,
            "OpponentTeamID": opponent_team_id,
            "VsConference": vs_conference,
            "VsDivision": vs_division,
            "GameSegment": game_segment,
            "Period": period,
            "ShotClockRange": shot_clock_range,
            "LastNGames": last_n_games,
        }
        self.api = NbaAPI(self._endpoint, self._params)
    def overall(self):
        return self.api.get_result("OverallPlayerDashboard")
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
@st.cache_data(ttl = 11600)
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

st.sidebar.markdown('<div style="text-align: center;"><span style="font-size:30px;">NBA Shot Visualizer</span></div>', unsafe_allow_html=True)

    # User input for player name
st.markdown('<div style="text-align: center;"><span style="font-size:80px;">NBA Shot Visualizer</span></div>', unsafe_allow_html=True)

player_name = st.text_input("Enter player name (not case sensitive)")

if player_name:
    try:
            # Call get_id function to retrieve player ID
        PLAYER_ID = get_id(player_name)

        st.success(f"Successfully found {player_name.lower().title()}")
        
            
            # Get the range of seasons the selected player has played in
        first_season, last_season = get_player_season_range(PLAYER_ID)
            # Generate the list of seasons within the range
        SEASONS = [f'{season}-{str(int(season)+1)[2:]}' for season in range(int(first_season), int(last_season)+1)]
            
        SEASON = st.sidebar.selectbox('Select season', reversed(SEASONS))
        if SEASON:
            # Create an empty list to store shot data for all selected seasons
            all_shot_data = []
            type = st.radio('',['PerGame','Totals','Per36'])

            
            
            player_summarytotals = Splits(player_id=PLAYER_ID,season=SEASON,per_mode=type)
            if player_summarytotals is not None and player_summarytotals:
                player_headline_stats2 = player_summarytotals.overall()
                min = player_headline_stats2['MIN'].values[0]
                tov = player_headline_stats2['TOV'].values[0]
                pts = player_headline_stats2['PTS'].values[0]
                ast = player_headline_stats2['AST'].values[0]
                reb = player_headline_stats2['REB'].values[0]
                blk = player_headline_stats2['BLK'].values[0]
                stl = player_headline_stats2['STL'].values[0]
                season_val = player_headline_stats2['GROUP_VALUE'].values[0]
                fg_pct = player_headline_stats2['FG_PCT'].values[0]
                fg3_pct = player_headline_stats2['FG3_PCT'].values[0]
                ft_pct = player_headline_stats2['FT_PCT'].values[0]
                name = player_name.lower().title()


# Display the variables
                cl1,cl2 = st.columns(2)
                with cl1:
                    display_player_image(PLAYER_ID,350,name)
            
            
                with cl2:
                    st.header("Season: " + season_val)

# Define text colors
                    pts_color = "blue"
                    ast_color = "green"
                    reb_color = "red"
                    blk_color = "purple"
                    stl_color = "orange"
                    fg_pct_color = "yellow"
                    fg3_pct_color = "gray"
                    ft_pct_color = "gold"

# Display text with different colors
                    font_size_large = "28px"

# Display text with different colors and font sizes using markdown syntax
                    st.markdown(f"<span style='font-size:{font_size_large}'>**Pts:** <span style='color:{pts_color}'>{pts}</span>   **Ast:** <span style='color:{ast_color}'>{ast}</span></span>", unsafe_allow_html=True)
                    st.markdown(f"<span style='font-size:{font_size_large}'>**Reb:** <span style='color:{reb_color}'>{reb}</span>   **Blk:** <span style='color:{blk_color}'>{blk}</span></span>", unsafe_allow_html=True)
                    st.markdown(f"<span style='font-size:{font_size_large}'>**Stl:** <span style='color:{stl_color}'>{stl}</span>   **<span style='color:{fg_pct_color}'>{round(fg_pct*100,1)}</span> FG%**</span>", unsafe_allow_html=True)
                    st.markdown(f"<span style='font-size:{font_size_large}'><span style='color:{fg3_pct_color}'>{round(fg3_pct*100,1)} </span>3P%   **<span style='color:{ft_pct_color}'>{round(ft_pct*100,1)} </span>FT%**</span>", unsafe_allow_html=True)
            else:
                st.error('No data found for this season')


           
            

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
        Quarters = st.sidebar.checkbox('Quarters')
        if Quarters:
            typequart = st.sidebar.selectbox('Quarters',['1','2','3','4'])
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
        ShotDist = st.sidebar.checkbox('Shot Distance')
        if ShotDist == 1:
            shotdistbool = True
            shotdistance = st.sidebar.slider("Shot Distance", 0, 40)
        ShotType = st.sidebar.checkbox('Shot Type')
        if ShotType == 1:
            shottypebool = True
            shottype = st.sidebar.selectbox('Shot Type', ['Jump Shot', 'Layup','Dunk','Other'])
            if shottype == 'Jump Shot':
                jumpshottype = st.sidebar.selectbox('Jump Shot Type', ['Stepback Jump shot', 'Running Pull-Up Jump Shot','Turnaround Fadeaway shot','Fadeaway Jump Shot','Pullup Jump shot','Jump Bank Shot','Jump Shot'])
                finaltype = jumpshottype
            elif shottype == 'Layup':
                layuptype = st.sidebar.selectbox('Layup Type', ['Layup Shot', 'Running Finger Roll Layup Shot','Cutting Layup Shot','Driving Layup Shot','Running Layup Shot','Alley Oop Layup shot','Tip Layup Shot','Reverse Layup Shot','Driving Reverse Layup Shot','Running Reverse Layup Shot'])
                finaltype = layuptype
            elif shottype == 'Dunk':
                dunktype = st.sidebar.selectbox('Dunk Type', ['Running Dunk Shot', 'Cutting Dunk Shot','Running Reverse Dunk Shot','Running Alley Oop Dunk Shot','Dunk Shot','Tip Dunk Shot'])    
                finaltype = dunktype
            elif shottype == 'Other':
                othertype = st.sidebar.selectbox('Other Type', ['Driving Floating Jump Shot', 'Floating Jump shot','Driving Floating Bank Jump Shot','Driving Bank Hook Shot','Driving Hook Shot','Turnaround Hook Shot','Hook Shot'])
                finaltype = othertype
        Teams = st.sidebar.checkbox('Teams')
        if Teams == 1:
            teamtype = st.sidebar.selectbox('Teams', ['ATL', 'BOS', 'BKN', 'CHA', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GSW', 'HOU', 'IND', 'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN', 'NOP', 'NYK', 'OKC', 'ORL', 'PHI', 'PHX', 'POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS'])
        CourtLoc = st.sidebar.checkbox('Court Location')
        if CourtLoc == 1:
            courtloc = st.sidebar.selectbox('Court Location',['Right Side(R)','Left Side(L)','Center(C)','Right Side Center(RC)','Left Side Center(LC)'])
        Date = st.sidebar.checkbox('Date')
        

        col1, col2 = st.columns(2)
            # Create ShotChart object
 

        shot_chart = ShotChart(PLAYER_ID, season=SEASON,game_segment=typeseg,clutch_time=typeclutch,season_type=typeseason,vs_conf=typeconf,location=typeloc,outcome=typeout,context_measure=Stat2,ahead_behind=typeaheadbehind)

            # Fetch shot chart data
        shot_data = shot_chart.shot_chart()
   
        shootperc = 0
                # Plot shot chart on basketball court
        plt.figure(figsize=(12, 7))
        ax = plt.gca()
        if Date == 1:
                date = shot_data['GAME_DATE'].unique()
                datetype = st.sidebar.selectbox('Date (YearMonthDay)', shot_data['GAME_DATE'].unique())
                shot_data = shot_data[shot_data['GAME_DATE'] == datetype]
        if Stat == 'MISSES':
                shot_data = shot_data[shot_data['SHOT_MADE_FLAG'] == 0]
        if Quarters:
                shot_data = shot_data[shot_data['PERIOD'] == int(typequart)]
        if CourtLoc:
                shot_data = shot_data[shot_data['SHOT_ZONE_AREA'] == courtloc]
        if Teams:
                    shot_data = shot_data[(shot_data['VTM'] == teamtype) | (shot_data['HTM'] == teamtype)]
        if ShotType:  # Check if ShotType checkbox is selected
                shot_data = shot_data[shot_data['ACTION_TYPE'] == finaltype]
                # Plot makes in green
        if ShotDist == 1:
                shot_data = shot_data[shot_data['SHOT_DISTANCE'] >= shotdistance]
                    

           
        total_makes = len(shot_data[shot_data["SHOT_MADE_FLAG"] == 1])
        total_misses = len(shot_data[shot_data["SHOT_MADE_FLAG"] == 0])
        total_shots = total_makes + total_misses
        if total_shots != 0:
                shooting_percentage = round((total_makes / total_shots) * 100, 1)
        else: 
                shooting_percentage = 0
        shootperc = shooting_percentage
        #20211019

# Create trace for makes
# Concatenate text labels for makes and misses
        text_all = shot_data["GAME_DATE"].apply(lambda date_str: '-'.join([date_str[4:6], date_str[6:], date_str[:4]])) + ': ' + \
           shot_data["HTM"] + ' VS ' + shot_data["VTM"] + ' | ' + \
           shot_data["ACTION_TYPE"] + ' (' + shot_data["SHOT_DISTANCE"].astype(str) + ' ft)' + ' | ' + \
           shot_data["PERIOD"].astype(str) + 'Q' + ' - ' + \
           shot_data["MINUTES_REMAINING"].astype(str) + ':' + \
           shot_data["SECONDS_REMAINING"].astype(str)

# Create trace for makes
        make_trace = go.Scatter(
    x=shot_data[shot_data["SHOT_MADE_FLAG"] == 1]["LOC_X"],
    y=shot_data[shot_data["SHOT_MADE_FLAG"] == 1]["LOC_Y"] + 60,
    mode='markers',
    marker=dict(color='rgba(0, 128, 0, 0.6)', size=6),
    name='Makes',
    text=text_all[shot_data["SHOT_MADE_FLAG"] == 1],  # Use concatenated text for makes only
    hoverinfo='text'
)

# Create trace for misses
        miss_trace = go.Scatter(
    x=shot_data[shot_data["SHOT_MADE_FLAG"] == 0]["LOC_X"],
    y=shot_data[shot_data["SHOT_MADE_FLAG"] == 0]["LOC_Y"] + 60,
    mode='markers',
    marker=dict(symbol='x', color='rgba(255, 0, 0, 0.6)', size=6),
    name='Misses',
    text=text_all[shot_data["SHOT_MADE_FLAG"] == 0],  # Use concatenated text for misses only
    hoverinfo='text'
)

# Create layout
        layout = go.Layout(
    hovermode='closest',
    xaxis=dict(showline=False, showticklabels=False, showgrid=False, range=[-230, 230]),
    yaxis=dict(showline=False, showticklabels=False, showgrid=False, range=[0, 470]),
    plot_bgcolor='#D2B48C',  # Set background color to the desired color
    width=345,  # Set the width of the background
    height=485,  # Set the height of the background
    autosize=False,
    legend=dict(x=1, y=1, xanchor='right', yanchor='top', bgcolor='white',font=dict(color='black'), bordercolor='gray', borderwidth=1)  # Customize legend
)

# Create figure
        fig = go.Figure(data=[make_trace, miss_trace], layout=layout)

# Add basketball court lines as shapes
        court_shapes = [

    dict(
         type = 'rect',
         x0=-253,
         x1 = -253,
         y1=465,
         y0=0,
         fillcolor="white",
         line=dict(color='black', width=2)
    ),
     dict(
         type = 'line',
         x0=253,
         x1 = 253,
         y1=465,
         y0=0,
         line=dict(color='black', width=2)
    ),
    dict(
         type = 'line',
         x0=-254,
         x1 = 254,
         y1=467,
         y0=467,
         line=dict(color='black', width=2)
    ),
    dict(
         type='line',
         x0=-30,
         y0=40,
         y1=40,
         x1=30,
         line=dict(color='black', width=2)
    ),
    dict(
        type='line',
        x0=-223,
        y0=0,
        x1=-223,
        y1=140,
        line=dict(color='black', width=2)
    ),
    dict(
        type='line',
        x0=220,
        y0=0,
        x1=220,
        y1=140,
        line=dict(color='black', width=2)
    ),
    dict(
        type='path',
        path='M -225,132,100,150,160,170,180,190 C -200,320 150,375 219,140',
        line=dict(color='black', width=2)
    ),
    dict(
        type='line',
        x0=-80,
        y0=0,
        x1=-80,
        y1=190,
        line=dict(color='black', width=2)
    ),
    dict(
        type='line',
        x0=80,
        y0=0,
        x1=80,
        y1=190,
        line=dict(color='black', width=2)
    ),
    dict(
        type='line',
        x0=-60,
        y0=0,
        x1=-60,
        y1=190,
        line=dict(color='black', width=2)
    ),
    dict(
        type='line',
        x0=60,
        y0=0,
        x1=60,
        y1=190,
        line=dict(color='black', width=2)
    ),
    dict(
        type='line',
        x0=-80,
        y0=190,
        x1=80,
        y1=190,
        line=dict(color='black', width=2)
    ),
    dict(
        type='circle',
        xref='x',
        yref='y',
        x0=-60,
        y0=130,
        x1=60,
        y1=245,
        line=dict(color='black', width=2)
    ),
    dict(
        type='circle',
        xref='x',
        yref='y',
        x0=-15,
        y0=45,
        x1=15,
        y1=75,
        line=dict(color='black', width=2)
    )
]
        fig.update_layout(shapes=court_shapes)

# Set aspect ratio
        fig.update_yaxes(scaleanchor='x', scaleratio=1)

# Update hover labels
        fig.update_traces(hoverlabel=dict(bgcolor='black', font_size=12))
        

    # Create a 2D histogram of shot locations
        histogram_trace = go.Histogram2d(
    x=shot_data[shot_data["SHOT_MADE_FLAG"] == 1]["LOC_X"],
    y=shot_data[shot_data["SHOT_MADE_FLAG"] == 1]["LOC_Y"] + 60,
    autobinx=False,
    xbins=dict(
        start=-300,
        end=300,
        size=10  # Adjust the size based on your preference
    ),
    autobiny=False,
    ybins=dict(
        start=0,
        end=940,
        size=10  # Adjust the size based on your preference
    ),
    colorscale='magma',
    showscale=False,
     # Hide the color scale legend
)
    # Create a 2D histogram of shot locations
        histogram_trace2 = go.Histogram2d(
    x=shot_data[shot_data["SHOT_MADE_FLAG"] == 0]["LOC_X"],
    y=shot_data[shot_data["SHOT_MADE_FLAG"] == 0]["LOC_Y"] + 60,
    autobinx=True,
    xbins=dict(
        start=-300,
        end=300,
        size=10  # Adjust the size based on your preference
    ),
    autobiny=True,
    ybins=dict(
        start=0,
        end=940,
        size=10,
          # Adjust the size based on your preference
    ),
    colorscale='magma',
    showscale=False  # Hide the color scale legend
)

# Add the histogram trace to the plot

# Add the histogram trace to the plot

        fig3 = go.Figure(data=[histogram_trace, histogram_trace2], layout=layout)
        fig3.update_layout(shapes=court_shapes)

# Set aspect ratio
        fig3.update_yaxes(scaleanchor='x', scaleratio=1)

# Update hover labels
        fig3.update_traces(hoverlabel=dict(bgcolor='black', font_size=12))
        

# Set axis titles

# Display the plot
        st.markdown(f'<div style="text-align: center;"><span style="font-size:30px;">{total_makes}/{total_shots} - {shootperc}%</span></div>', unsafe_allow_html=True)
        # st.header(f'{total_makes}/{total_shots} - {shootperc}%')
        with col2:
            st.markdown(f'<div style="text-align: center;"><span style="font-size:25px;">Makes and Misses</span></div>', unsafe_allow_html=True)
            st.plotly_chart(fig)
                    # Plot hexbin with custom colormap
        fig2 = plt.figure(figsize=(4, 3.76))
        ax = fig2.add_axes([0, 0, 1, 1])
        
        hb = ax.hexbin(shot_data['LOC_X'], shot_data['LOC_Y'] + 60, gridsize=(48, 48), extent=(-300, 300, 0, 940), bins='log', cmap='magma')
        ax = create_court(ax, 'black')
        legend_elements = [
            plt.Line2D([0], [0], marker='H', color='w', label='Less Shots', markerfacecolor='black', markersize=10),
            plt.Line2D([0], [0], marker='H', color='w', label='More Shots', markerfacecolor='yellow', markersize=10)
        ]
        plt.legend(handles=legend_elements, loc='upper right') 

# Save the figure as an image
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png')
        img_buffer.seek(0)

# Display the image in Streamlit
                    # Customize color bar legend

        
        with col1:
                st.markdown(f'<div style="text-align: center;"><span style="font-size:25px;">Shot Frequency</span></div>', unsafe_allow_html=True)
                st.header('')
                st.header('')
                st.header('')
                st.image(img_buffer, use_column_width=False, width=345)  

                # st.plotly_chart(fig3)
                
        

            
            # st.sidebar.header(f'{season1}: 0/{total_misses} - {shooting_percentage}%')
    except PlayerNotFoundException as e:
        st.error(str(e))
else:
    st.image("https://static.vecteezy.com/system/resources/thumbnails/013/861/222/small/silhouette-of-basketball-player-with-ball-shooting-dunk-free-vector.jpg",use_column_width=True)
