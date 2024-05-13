import io
import json
import numpy as np
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
from abc import ABC, abstractmethod
import plotly.express as px
from matplotlib.patches import Circle, Rectangle, Arc


st.set_page_config(page_title="NBA Shot Visualizer", page_icon='https://juststickers.in/wp-content/uploads/2015/05/basket-ball-player-1-decal.png', initial_sidebar_state="expanded")

currentyear = datetime.datetime.now().year

class Summary:
    """Contains common player information like headline stats, weight, etc.

    Args:
        player_id: ID of the player to look up
    """

    _endpoint = "commonplayerinfo"

    def __init__(self, player_id: str):
        self._params = {"PlayerID": player_id}

        self.api = NbaAPI(self._endpoint, self._params)

    def info(self):
        return self.api.get_result("CommonPlayerInfo")

    def headline_stats(self):
        return self.api.get_result("PlayerHeadlineStats")

class GameLogs:
    """Contains a full log of all the games for a player for a given season.

    Args:
        player_id: ID of the player to look up
        league_id: ID for the league to look in
        season: Season given to look up
        season_type: Season type to consider (Regular / Playoffs)
    """

    _endpoint = "playergamelog"

    def __init__(
        self,
        player_id: str,
        league_id=constants.League.NBA,
        season=constants.CURRENT_SEASON,
        season_type=constants.SeasonType.Regular,
    ):
        self._params = {
            "PlayerID": player_id,
            "LeagueID": league_id,
            "Season": season,
            "SeasonType": season_type,
        }
        self.api = NbaAPI(self._endpoint, self._params)

    def logs(self):
        return self.api.get_result("PlayerGameLog")



def display_player_image(player_id, width2, caption2):
    # Construct the URL for the player image using the player ID
    image_url = f"https://cdn.nba.com/headshots/nba/latest/260x190/{player_id}.png"
    
    
    # Check if the image URL returns a successful response
    response = requests.head(image_url)
    
    if response.status_code == 200:
        # If image is available, display it
        st.markdown(
    f'<div style="display: flex; flex-direction: column; align-items: center;">'
    f'<img src="{image_url}" style="width: {width2}px;">'
    f'<p style="text-align: center; font-size: 20px;">{caption2}</p>'
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
def draw_court(ax=None, color='black', lw=2, outer_lines=False):
    # If an axes object isn't provided to plot onto, just get current one
    if ax is None:
        ax = plt.gca()

    # Create the various parts of an NBA basketball court

    # Create the basketball hoop
    # Diameter of a hoop is 18" so it has a radius of 9", which is a value
    # 7.5 in our coordinate system
    hoop = Circle((0, 0), radius=7.5, linewidth=lw, color=color, fill=False)

    # Create backboard
    backboard = Rectangle((-30, -7.5), 60, -1, linewidth=lw, color=color)

    # The paint
    # Create the outer box 0f the paint, width=16ft, height=19ft
    outer_box = Rectangle((-80, -47.5), 160, 190, linewidth=lw, color=color,
                          fill=False)
    # Create the inner box of the paint, widt=12ft, height=19ft
    inner_box = Rectangle((-60, -47.5), 120, 190, linewidth=lw, color=color,
                          fill=False)

    # Create free throw top arc
    top_free_throw = Arc((0, 142.5), 120, 120, theta1=0, theta2=180,
                         linewidth=lw, color=color, fill=False)
    # Create free throw bottom arc
    bottom_free_throw = Arc((0, 142.5), 120, 120, theta1=180, theta2=0,
                            linewidth=lw, color=color, linestyle='dashed')
    # Restricted Zone, it is an arc with 4ft radius from center of the hoop
    restricted = Arc((0, 0), 80, 80, theta1=0, theta2=180, linewidth=lw,
                     color=color)

    # Three point line
    # Create the side 3pt lines, they are 14ft long before they begin to arc
    corner_three_a = Rectangle((-220, -47.5), 0, 140, linewidth=lw,
                               color=color)
    corner_three_b = Rectangle((220, -47.5), 0, 140, linewidth=lw, color=color)
    # 3pt arc - center of arc will be the hoop, arc is 23'9" away from hoop
    # I just played around with the theta values until they lined up with the 
    # threes
    three_arc = Arc((0, 0), 475, 475, theta1=22, theta2=158, linewidth=lw,
                    color=color)

    # Center Court
    center_outer_arc = Arc((0, 422.5), 120, 120, theta1=180, theta2=0,
                           linewidth=lw, color=color)
    center_inner_arc = Arc((0, 422.5), 40, 40, theta1=180, theta2=0,
                           linewidth=lw, color=color)

    # List of the court elements to be plotted onto the axes
    court_elements = [hoop, backboard, outer_box, inner_box, top_free_throw,
                      bottom_free_throw, restricted, corner_three_a,
                      corner_three_b, three_arc, center_outer_arc,
                      center_inner_arc]

    if outer_lines:
        # Draw the half court line, baseline and side out bound lines
        outer_lines = Rectangle((-250, -47.5), 500, 470, linewidth=lw,
                                color=color, fill=False)
        court_elements.append(outer_lines)

    # Add the court elements onto the axes
    for element in court_elements:
        ax.add_patch(element)
    ax.set_facecolor('#D2B48C')
    return ax

def create_court(ax, color):
    # Short corner 3PT lines
    ax.set_facecolor('#D2B48C')

    ax.plot([-220, -220], [0, 140], linewidth=4, color=color)
    ax.plot([220, 220], [0, 140], linewidth=4, color=color)

    # 3PT Arc
    ax.add_artist(patches.Arc((0, 140), 440, 315, theta1=0, theta2=180, facecolor='none', edgecolor=color, lw=4))
    ax.add_artist(patches.Circle((0, 475), 60, facecolor='none', edgecolor=color, lw=4))

    # Lane and Key
    ax.plot([-255,255],[0,0],linewidth=4,color=color)
    ax.plot([-255,-255],[0,515],linewidth=4,color=color)
    ax.plot([255,255],[0,515],linewidth=4,color=color)
    ax.plot([-255,255],[468,468],linewidth=4,color=color)
    ax.plot([-80, -80], [3, 190], linewidth=4, color=color)
    ax.plot([80, 80], [3, 190], linewidth=4, color=color)
    ax.plot([-60, -60], [3, 190], linewidth=4, color=color)
    ax.plot([60, 60], [3, 190], linewidth=4, color=color)
    ax.plot([-80, 80], [190, 190], linewidth=4, color=color)
    ax.add_artist(patches.Circle((0, 190), 60, facecolor='none', edgecolor=color, lw=4))

    # Rim
    ax.add_artist(patches.Circle((0, 60), 15, facecolor='none', edgecolor=color, lw=4))

    # Backboard
    ax.plot([-30, 30], [40, 40], linewidth=4, color=color)

    # Remove ticks
    ax.set_xticks([])
    ax.set_yticks([])
    

    # Set axis limits
    ax.set_xlim(-262, 262)
    ax.set_ylim(-5, 472)
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

class ShotTracking(Splits):
    """Tracking data for shooting for a given player.

    Args:
        see Splits
    """

    _endpoint = "playerdashptshots"

    def overall(self):
        return self.api.get_result("Overall")

    def general(self):
        return self.api.get_result("GeneralShooting")

    def shot_clock(self):
        return self.api.get_result("ShotClockShooting")

    def dribbles(self):
        return self.api.get_result("DribbleShooting")

    def closest_defender(self):
        return self.api.get_result("ClosestDefenderShooting")

    def closest_defender_long(self):
        return self.api.get_result("ClosestDefender10ftPlusShooting")

    def touch_time(self):
        return self.api.get_result("TouchTimeShooting")


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
        active_only=0,
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

    players = pd.DataFrame(PlayerList(season=season, active_only=0).players())

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

def ellipse_arc(x_center=0.0, y_center=0.0, a=10.5, b=10.5, start_angle=0.0, end_angle=2 * np.pi, N=200, closed=False):
        t = np.linspace(start_angle, end_angle, N)
        x = x_center + a * np.cos(t)
        y = y_center + b * np.sin(t)
        path = f'M {x[0]}, {y[0]}'
        for k in range(1, len(t)):
            path += f'L{x[k]}, {y[k]}'
        if closed:
            path += ' Z'
        return path

def draw_plotly_court(fig, fig_width=600, margins=10):
        
    # From: https://community.plot.ly/t/arc-shape-with-path/7205/5
    

    fig_height = fig_width * (470 + 2 * margins) / (500 + 2 * margins)
    fig.update_layout(width=fig_width, height=fig_height)

    # Set axes ranges
    fig.update_xaxes(range=[-250 - margins, 250 + margins])
    fig.update_yaxes(range=[-52.5 - margins, 417.5 + margins])

    threept_break_y = 89.47765084
    three_line_col = "black"
    main_line_col = "black"

    fig.update_layout(
        # Line Horizontal
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="white",
        plot_bgcolor="white",
        yaxis=dict(
            scaleanchor="x",
            scaleratio=1,
            showgrid=False,
            zeroline=False,
            showline=False,
            ticks='',
            showticklabels=False,
            fixedrange=True,
        ),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showline=False,
            ticks='',
            showticklabels=False,
            fixedrange=True,
        ),
        shapes=[
            dict(
                type="rect", x0=-250, y0=-52.5, x1=250, y1=417.5,
                line=dict(color=main_line_col, width=2),
                # fillcolor='#333333'
                
            ),
            dict(
                type="rect", x0=-80, y0=-52.5, x1=80, y1=137.5,
                line=dict(color=main_line_col, width=2),
                # fillcolor='#333333'
                
            ),
            dict(
                type="rect", x0=-60, y0=-52.5, x1=60, y1=137.5,
                line=dict(color=main_line_col, width=2),
                # fillcolor='#333333'
                
            ),
            dict(
                type="circle", x0=-60, y0=77.5, x1=60, y1=197.5, xref="x", yref="y",
                line=dict(color=main_line_col, width=2),
                # fillcolor='#dddddd'
                
            ),
            dict(
                type="line", x0=-60, y0=137.5, x1=60, y1=137.5,
                line=dict(color=main_line_col, width=2)
                
            ),

            dict(
                type="rect", x0=-2, y0=-7.25, x1=2, y1=-12.5,
                line=dict(color="#ec7607", width=2),
                fillcolor='#ec7607',
            ),
            dict(
                type="circle", x0=-7.5, y0=-7.5, x1=7.5, y1=7.5, xref="x", yref="y",
                line=dict(color="#ec7607", width=2),
            ),
            dict(
                type="line", x0=-30, y0=-12.5, x1=30, y1=-12.5,
                line=dict(color="#ec7607", width=2),
            ),

            dict(type="path",
                 path=ellipse_arc(a=40, b=40, start_angle=0, end_angle=np.pi),
                 line=dict(color=main_line_col, width=2)),
            dict(type="path",
                 path=ellipse_arc(a=237.5, b=237.5, start_angle=0.386283101, end_angle=np.pi - 0.386283101),
                 line=dict(color=main_line_col, width=2)),
            dict(
                type="line", x0=-220, y0=-52.5, x1=-220, y1=threept_break_y,
                line=dict(color=three_line_col, width=2)
            ),
            dict(
                type="line", x0=-220, y0=-52.5, x1=-220, y1=threept_break_y,
                line=dict(color=three_line_col, width=2)
            ),
            dict(
                type="line", x0=220, y0=-52.5, x1=220, y1=threept_break_y,
                line=dict(color=three_line_col, width=2)
            ),

            dict(
                type="line", x0=-250, y0=227.5, x1=-220, y1=227.5,
                line=dict(color=main_line_col, width=2)
            ),
            dict(
                type="line", x0=250, y0=227.5, x1=220, y1=227.5,
                line=dict(color=main_line_col, width=2)
            ),
            dict(
                type="line", x0=-90, y0=17.5, x1=-80, y1=17.5,
                line=dict(color=main_line_col, width=2)
            ),
            dict(
                type="line", x0=-90, y0=27.5, x1=-80, y1=27.5,
                line=dict(color=main_line_col, width=2)
            ),
            dict(
                type="line", x0=-90, y0=57.5, x1=-80, y1=57.5,
                line=dict(color=main_line_col, width=2)
            ),
            dict(
                type="line", x0=-90, y0=87.5, x1=-80, y1=87.5,
                line=dict(color=main_line_col, width=2)
            ),
            dict(
                type="line", x0=90, y0=17.5, x1=80, y1=17.5,
                line=dict(color=main_line_col, width=2)
            ),
            dict(
                type="line", x0=90, y0=27.5, x1=80, y1=27.5,
                line=dict(color=main_line_col, width=2)
            ),
            dict(
                type="line", x0=90, y0=57.5, x1=80, y1=57.5,
                line=dict(color=main_line_col, width=2)
            ),
            dict(
                type="line", x0=90, y0=87.5, x1=80, y1=87.5,
                line=dict(color=main_line_col, width=2)
            ),

            dict(type="path",
                 path=ellipse_arc(y_center=417.5, a=60, b=60, start_angle=-0, end_angle=-np.pi),
                 line=dict(color=main_line_col, width=2)),

        ]
    )
    return True




# Define Streamlit app

st.sidebar.markdown('<div style="text-align: center;"><span style="font-size:30px;">NBA Shot Visualizer</span></div>', unsafe_allow_html=True)
type = st.sidebar.selectbox('Player Stats',['Per Game','Totals'])
shottrack = st.sidebar.selectbox('Shot Tracking Stats',['Overall','General','Shot Clock','Dribbles','Closest Defender','Closest Defender Long','Touch Time'])
Stat = st.sidebar.selectbox('',['FGA','MAKES', 'MISSES','3PA','FB PTS','PTS OFF TOV','2ND CHANCE PTS','PF'])
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
GameSegment = st.sidebar.toggle('Game Segment')
if GameSegment == 1:
    typeseg = st.sidebar.selectbox('',['First Half', 'Second Half', 'Overtime'])
else:
    typeseg = None
Quarters = st.sidebar.toggle('Quarters')
if Quarters:
    typequart = st.sidebar.selectbox('',['1','2','3','4'])
Clutch_Time = st.sidebar.toggle('Clutch Time')
if Clutch_Time == 1:
    typeclutch = st.sidebar.selectbox('', ['Last 5 Minutes', 'Last 4 Minutes','Last 3 Minutes','Last 2 Minutes','Last 1 Minute','Last 30 Seconds', 'Last 10 Seconds'])
else:
    typeclutch = None
Playoffs = st.sidebar.toggle('Playoffs')
if Playoffs == 1:
    typeseason = 'Playoffs'
else:
    typeseason = "Regular Season"
Conference = st.sidebar.toggle('Conference')
if Conference == 1:
    typeconf = st.sidebar.selectbox('',['East', 'West'])
else:
    typeconf = None
Location = st.sidebar.toggle('Location')
if Location == 1:
    typeloc = st.sidebar.selectbox('',['Home', 'Road'])
else:
    typeloc = None
Outcome = st.sidebar.toggle('Outcome')
if Outcome == 1:
    typeout = st.sidebar.selectbox('',['W', 'L'])
else:
    typeout = None
AheadBehind = st.sidebar.toggle('Ahead/Behind')
if AheadBehind == 1:
    typeaheadbehind = st.sidebar.selectbox('',['Behind or Tied','Ahead or Tied'])
else:
    typeaheadbehind = None
ShotDist = st.sidebar.toggle('Shot Distance')
if ShotDist == 1:
    shotdistbool = True
    # shotdistance = st.sidebar.slider("Shot Distance", 0, 40)
    shotdistance_min, shotdistance_max = st.sidebar.slider("Shot Distance", 0, 40, (0, 40))
ShotType = st.sidebar.toggle('Shot Type')
if ShotType == 1:
    shottypebool = True
    shottype = st.sidebar.selectbox('', ['Jump Shot', 'Layup','Dunk','Other'])
    if shottype == 'Jump Shot':
        jumpshottype = st.sidebar.multiselect('', ['Stepback Jump shot', 'Running Pull-Up Jump Shot','Turnaround Fadeaway shot','Fadeaway Jump Shot','Pullup Jump shot','Jump Bank Shot','Jump Shot'])
        finaltype = jumpshottype
    elif shottype == 'Layup':
        layuptype = st.sidebar.multiselect('', ['Layup Shot', 'Running Finger Roll Layup Shot','Cutting Layup Shot','Driving Layup Shot','Running Layup Shot','Alley Oop Layup shot','Tip Layup Shot','Reverse Layup Shot','Driving Reverse Layup Shot','Running Reverse Layup Shot'])
        finaltype = layuptype
    elif shottype == 'Dunk':
        dunktype = st.sidebar.multiselect('', ['Running Dunk Shot', 'Cutting Dunk Shot','Running Reverse Dunk Shot','Running Alley Oop Dunk Shot','Dunk Shot','Tip Dunk Shot'])    
        finaltype = dunktype
    elif shottype == 'Other':
        othertype = st.sidebar.multiselect('', ['Driving Floating Jump Shot', 'Floating Jump shot','Driving Floating Bank Jump Shot','Driving Bank Hook Shot','Driving Hook Shot','Turnaround Hook Shot','Hook Shot'])
        finaltype = othertype
Teams = st.sidebar.toggle('Teams')
if Teams == 1:
    teamtype = st.sidebar.multiselect('', ['ATL', 'BOS', 'BKN', 'CHA', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GSW', 'HOU', 'IND', 'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN', 'NOP', 'NYK', 'OKC', 'ORL', 'PHI', 'PHX', 'POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS'])
CourtLoc = st.sidebar.toggle('Court Location')
if CourtLoc == 1:
    courtloc = st.sidebar.multiselect('',['Right Side(R)','Left Side(L)','Center(C)','Right Side Center(RC)','Left Side Center(LC)'])
Date = st.sidebar.toggle('Date (YearMonthDay)')

    # User input for player name
st.markdown('<div style="text-align: center;"><span style="font-size:80px;">NBA Shot Visualizer</span></div>', unsafe_allow_html=True)

# Text input for entering player names

# Fetch all players
player_list = PlayerList()
players_df = player_list.players()

# Create a multiselect widget with player options
player_name = st.selectbox("Select player:", options=players_df["DISPLAY_FIRST_LAST"].tolist(), index=None, help="Select a player to view shot data. Adjust filters on sidebar for specific data.")

# player_names_input = st.text_input("Enter player name (if multiple, separate by commas)")
if not player_name:
    st.image("https://static.vecteezy.com/system/resources/thumbnails/013/861/222/small/silhouette-of-basketball-player-with-ball-shooting-dunk-free-vector.jpg",use_column_width=True)

# Parse the input to extract individual player names
# player_names = [name.strip() for name in player_names_input.split(',') if name.strip()]
type2 = ''
if type == 'Per Game':
     type2 = 'PerGame'
elif type == 'Totals':
        type2 == 'Totals'
elif type == 'Per 36':
     type2 == 'Per36'

if player_name:
    
    try:
            # Call get_id function to retrieve player ID
        PLAYER_ID = get_id(player_name)
        
        
            
            # Get the range of seasons the selected player has played in
        first_season, last_season = get_player_season_range(PLAYER_ID)
            # Generate the list of seasons within the range
        SEASONS = [f'{season}-{str(int(season)+1)[2:]}' for season in range(int(first_season), int(last_season)+1)]
            
        SEASON = st.selectbox(f'Select season', reversed(SEASONS))
        if SEASON:
            playerinfo = Summary(player_id=PLAYER_ID).info()
            player_list = PlayerList(season=SEASON)
            players_df2 = player_list.players()
            playerheight = playerinfo.loc[playerinfo['DISPLAY_FIRST_LAST'] == player_name, 'HEIGHT'].values[0]
            playerweight = playerinfo.loc[playerinfo['DISPLAY_FIRST_LAST'] == player_name, 'WEIGHT'].values[0]

            team_name = players_df2.loc[players_df2["DISPLAY_FIRST_LAST"] == player_name, "TEAM_NAME"].values[0]
            team_city = players_df2.loc[players_df2["DISPLAY_FIRST_LAST"] == player_name, "TEAM_CITY"].values[0]
            fullteam = f"{team_city} {team_name}"

            game_logs = GameLogs(PLAYER_ID, season=SEASON, season_type=typeseason).logs()

    # Plot game log
            if game_logs is not None and not game_logs.empty:
                game_dates = game_logs['GAME_DATE'][::-1]
                pts = game_logs['PTS'][::-1]

            plotgames = px.bar(x=game_dates, y=pts, labels={"x": "Game Date", "y": "Points"},width=600, height=300)
            # st.success(f"Successfully found {player_name.lower().title()}")
            # Create an empty list to store shot data for all selected seasons
            all_shot_data = []

            
            
            player_summary = Splits(player_id=PLAYER_ID,season=SEASON)
            player_summarytotals = Splits(player_id=PLAYER_ID,season=SEASON,per_mode=type2)
            player_headline_stats2 = player_summarytotals.overall()

            # Check if player_summarytotals has data
            if player_headline_stats2 is not None and len(player_headline_stats2) > 0:
                min = round(player_headline_stats2['MIN'].values[0],1)
                tov = round(player_headline_stats2['TOV'].values[0],1)
                pts = round(player_headline_stats2['PTS'].values[0],1)
                ast = round(player_headline_stats2['AST'].values[0],1)
                reb = round(player_headline_stats2['REB'].values[0],1)
                blk = round(player_headline_stats2['BLK'].values[0],1)
                stl = round(player_headline_stats2['STL'].values[0],1)
                season_val = player_headline_stats2['GROUP_VALUE'].values[0]
                fg_pct = player_headline_stats2['FG_PCT'].values[0]
                fg3_pct = player_headline_stats2['FG3_PCT'].values[0]
                ft_pct = player_headline_stats2['FT_PCT'].values[0]
                name = player_name



# Display the variables
                cl1,cl2 = st.columns(2)
                with cl1:
                    display_player_image(PLAYER_ID,350,f"{name} - {fullteam}")
                    st.markdown(f'<div style="text-align: center;"><span style="font-size:20px;">Height: {playerheight} Weight: {playerweight}</span></div>', unsafe_allow_html=True)


                
                
                with cl2:
                    

    # Define text colors
                    pts_color = "blue"
                    ast_color = "green"
                    reb_color = "red"
                    blk_color = "purple"
                    stl_color = "orange"
                    fg_pct_color = "violet"
                    fg3_pct_color = "gray"
                    ft_pct_color = "gold"
                    min_color = "cyan"
                    tov_color = "magenta" 

    # Display text with different colors
                    font_size_large = "28px"

    # Display text with different colors and font sizes using markdown syntax

                    st.markdown(f"<span style='font-size:{font_size_large}'>**Pts:** <span style='color:{pts_color}'>{pts}</span>   **Ast:** <span style='color:{ast_color}'>{ast}</span></span>", unsafe_allow_html=True)
                    st.markdown(f"<span style='font-size:{font_size_large}'>**Reb:** <span style='color:{reb_color}'>{reb}</span>   **Blk:** <span style='color:{blk_color}'>{blk}</span></span>", unsafe_allow_html=True)
                    st.markdown(f"<span style='font-size:{font_size_large}'>**Stl:** <span style='color:{stl_color}'>{stl}</span>   **<span style='color:{fg_pct_color}'>{round(fg_pct*100,1)}</span> FG%**</span>", unsafe_allow_html=True)
                    st.markdown(f"<span style='font-size:{font_size_large}'><span style='color:{fg3_pct_color}'>{round(fg3_pct*100,1)} </span>3P%   **<span style='color:{ft_pct_color}'>{round(ft_pct*100,1)} </span>FT%**</span>", unsafe_allow_html=True)
                    st.markdown(f"<span style='font-size:{font_size_large}'>**Tov:** <span style='color:{tov_color}'>{tov}</span>   **Min:** <span style='color:{min_color}'>{min}</span></span>", unsafe_allow_html=True)

            else:
                st.error(f'No data found for {player_name.lower().title()} in {SEASON}. Check season: shot chart data before 1996 is unavailable')

            
        st.plotly_chart(plotgames)


        col1, col,col2 = st.columns(3)



            # Create ShotChart object


        shot_chart = ShotChart(PLAYER_ID, season=SEASON,game_segment=typeseg,clutch_time=typeclutch,season_type=typeseason,vs_conf=typeconf,location=typeloc,outcome=typeout,context_measure=Stat2,ahead_behind=typeaheadbehind)

            # Fetch shot chart data
        shot_data = shot_chart.shot_chart()

        shootperc = 0
                # Plot shot chart on basketball court
        plt.figure(figsize=(13, 8))
        ax = plt.gca()
        if Date == 1:
                date = shot_data['GAME_DATE'].unique()
                datetype = st.sidebar.multiselect('', shot_data['GAME_DATE'].unique())
                shot_data = shot_data[shot_data['GAME_DATE'].isin(datetype)]
        if Stat == 'MISSES':
                shot_data = shot_data[shot_data['SHOT_MADE_FLAG'] == 0]
        if Quarters:
                shot_data = shot_data[shot_data['PERIOD'] == int(typequart)]
        if CourtLoc:
                shot_data = shot_data[shot_data['SHOT_ZONE_AREA'].isin(courtloc)]
        if Teams:
                    shot_data = shot_data[(shot_data['VTM'].isin(teamtype)) | (shot_data['HTM'].isin(teamtype))]
        if ShotType:  # Check if ShotType checkbox is selected
                shot_data = shot_data[shot_data['ACTION_TYPE'].isin(finaltype)]
                # Plot makes in green
        if ShotDist == 1:
                shot_data = shot_data[(shot_data['SHOT_DISTANCE'] >= shotdistance_min) & (shot_data['SHOT_DISTANCE'] <= shotdistance_max)]
                    

        
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
        text_all = (
shot_data["GAME_DATE"].apply(lambda date_str: '-'.join([date_str[4:6], date_str[6:], date_str[:4]])) + ': ' +
shot_data["HTM"] + ' VS ' + shot_data["VTM"] + ' | ' +
shot_data['SHOT_TYPE'].str.replace(' Field Goal', '') + ' - ' +  # Remove 'Field Goal'
shot_data["ACTION_TYPE"] + ' (' +
shot_data["SHOT_DISTANCE"].astype(str) + ' ft)' + ' | '  + shot_data["PERIOD"].astype(str) + 'Q' + ' - ' +
shot_data["MINUTES_REMAINING"].astype(str) + ':' +
shot_data["SECONDS_REMAINING"].astype(str)
)

        hover_template = (
            "<b>Date</b>: %{customdata[0]}<br>" +
            "<b>Game</b>: %{customdata[1]}<br>" +
            "<b>Shot</b>: %{customdata[2]}<br>" +
            "<b>Distance</b>: %{customdata[5]}<br>"+
            "<b>Period</b>: %{customdata[3]}<br>" +
            "<b>Time</b>: %{customdata[4]}" 
            
        )

        # Assuming shot_data is already defined as per your provided data
        # Extracting individual components from text_all and assigning them to customdata
        shot_data['GAME_DATE_NEW'] = shot_data["GAME_DATE"].apply(lambda date_str: '-'.join([date_str[4:6], date_str[6:], date_str[:4]]))
        shot_data['MATCH'] = shot_data["HTM"] + ' VS ' + shot_data["VTM"]
        shot_data['SHOT'] = shot_data['SHOT_TYPE'].str.replace(' Field Goal', '') + ' - ' + shot_data["ACTION_TYPE"]
        shot_data['PERIOD_TIME'] = shot_data["PERIOD"].astype(str) + 'Q'
        shot_data['TIME'] = shot_data["MINUTES_REMAINING"].astype(str) + ':' + shot_data["SECONDS_REMAINING"].astype(str)
        shot_data['DISTANCE'] = shot_data['SHOT_DISTANCE'].astype(str) + ' ft'
        # Create trace for makes
        make_trace = go.Scatter(
            x=-(shot_data[shot_data["SHOT_MADE_FLAG"] == 1]["LOC_X"]),
            y=shot_data[shot_data["SHOT_MADE_FLAG"] == 1]["LOC_Y"],
            mode='markers',
            marker=dict(color='rgba(0, 128, 0, 0.6)', size=10),
            name='Made Shot ✅',
            customdata=shot_data[shot_data["SHOT_MADE_FLAG"] == 1][['GAME_DATE_NEW', 'MATCH', 'SHOT', 'PERIOD_TIME','TIME','DISTANCE']],  # Use customdata for makes only
            hoverinfo='text',  # Set hoverinfo to text
            hovertemplate=hover_template
        )

        # Create trace for misses
        miss_trace = go.Scatter(
            x=-(shot_data[shot_data["SHOT_MADE_FLAG"] == 0]["LOC_X"]),
            y=shot_data[shot_data["SHOT_MADE_FLAG"] == 0]["LOC_Y"],
            mode='markers',
            marker=dict(symbol='x', color='rgba(255, 0, 0, 0.6)', size=10),
            name='Missed Shot ❌',
            customdata=shot_data[shot_data["SHOT_MADE_FLAG"] == 0][['GAME_DATE_NEW', 'MATCH', 'SHOT', 'PERIOD_TIME','TIME','DISTANCE']],  # Use customdata for misses only
            hoverinfo='text',  # Set hoverinfo to text
            hovertemplate=hover_template
        )
        fig2trace = go.Scatter(
                x=-(shot_data[shot_data["SHOT_MADE_FLAG"] == 0]["LOC_X"]),
    y=shot_data[shot_data["SHOT_MADE_FLAG"] == 0]["LOC_Y"],
    mode='markers',
    marker=dict(symbol='hexagon', color='rgba(255, 0, 0, 0.6)', size=10),
    name='Shots',
    text=text_all[shot_data["SHOT_MADE_FLAG"] == 0],  # Use concatenated text for misses only
    hoverinfo='text'
        )

# Create layout
    
        layout = go.Layout(
    hovermode='closest',
    xaxis=dict(showline=False, showticklabels=False, showgrid=False, range=[-260, 260]),
    yaxis=dict(showline=False, showticklabels=False, showgrid=False, range=[-60, 474]),
    plot_bgcolor='#D2B48C',  # Set background color to the desired color
    
    width=650,  # Set the width of the background
    height=718,  # Set the height of the background
    autosize=False,
    legend=dict(x=0.98, y=1, xanchor='right', yanchor='top', bgcolor='rgba(0,0,0,0)',font=dict(color='black'), bordercolor='black', borderwidth=0),
    margin=dict(l=0, r=0, t=0, b=0)# Customize legend
)

# Create figure

        fig = go.Figure()
        draw_plotly_court(fig)
        fig.update_layout(layout)

        fig3 = go.Figure()

        
# Add basketball court lines as shapes
        court_shapes=[
            dict(
                type="rect", x0=-250, y0=-52.5, x1=250, y1=417.5,
                line=dict(color='white', width=2)
                # fillcolor='#333333',
                
            ),
            dict(
                type="rect", x0=-80, y0=-52.5, x1=80, y1=137.5,
                line=dict(color='white', width=2)
                # fillcolor='#333333',
                
            ),
            dict(
                type="rect", x0=-60, y0=-52.5, x1=60, y1=137.5,
                line=dict(color='white', width=2)
                # fillcolor='#333333',
                
            ),
            dict(
                type="circle", x0=-60, y0=77.5, x1=60, y1=197.5, xref="x", yref="y",
                line=dict(color='white', width=2)
                # fillcolor='#dddddd',
            ),
            dict(
                type="line", x0=-60, y0=137.5, x1=60, y1=137.5,
                line=dict(color='white', width=2)
            ),

            dict(
                type="rect", x0=-2, y0=-7.25, x1=2, y1=-12.5,
                line=dict(color="#ec7607", width=2),
                fillcolor='#ec7607',
            ),
            dict(
                type="circle", x0=-7.5, y0=-7.5, x1=7.5, y1=7.5, xref="x", yref="y",
                line=dict(color="#ec7607", width=2),
            ),
            dict(
                type="line", x0=-30, y0=-12.5, x1=30, y1=-12.5,
                line=dict(color="#ec7607", width=2),
            ),

            dict(type="path",
                 path=ellipse_arc(a=40, b=40, start_angle=0, end_angle=np.pi),
                 line=dict(color='white', width=2)),
            dict(type="path",
                 path=ellipse_arc(a=237.5, b=237.5, start_angle=0.386283101, end_angle=np.pi - 0.386283101),
                 line=dict(color='white', width=2)),
            dict(
                type="line", x0=-220, y0=-52.5, x1=-220, y1=89.47765084,
                line=dict(color='white', width=2)
            ),
            dict(
                type="line", x0=-220, y0=-52.5, x1=-220, y1=89.47765084,
                line=dict(color='white', width=2)
            ),
            dict(
                type="line", x0=220, y0=-52.5, x1=220, y1=89.47765084,
                line=dict(color='white', width=2)
            ),

            dict(
                type="line", x0=-250, y0=227.5, x1=-220, y1=227.5,
                line=dict(color='white', width=2)
            ),
            dict(
                type="line", x0=250, y0=227.5, x1=220, y1=227.5,
                line=dict(color='white', width=2)
            ),
            dict(
                type="line", x0=-90, y0=17.5, x1=-80, y1=17.5,
                line=dict(color='white', width=2)
            ),
            dict(
                type="line", x0=-90, y0=27.5, x1=-80, y1=27.5,
                line=dict(color='white', width=2)
            ),
            dict(
                type="line", x0=-90, y0=57.5, x1=-80, y1=57.5,
                line=dict(color='white', width=2)
            ),
            dict(
                type="line", x0=-90, y0=87.5, x1=-80, y1=87.5,
                line=dict(color='white', width=2)
            ),
            dict(
                type="line", x0=90, y0=17.5, x1=80, y1=17.5,
                line=dict(color='white', width=2)
            ),
            dict(
                type="line", x0=90, y0=27.5, x1=80, y1=27.5,
                line=dict(color='white', width=2)
            ),
            dict(
                type="line", x0=90, y0=57.5, x1=80, y1=57.5,
                line=dict(color='white', width=2)
            ),
            dict(
                type="line", x0=90, y0=87.5, x1=80, y1=87.5,
                line=dict(color='white', width=2)
            ),

            dict(type="path",
                 path=ellipse_arc(y_center=417.5, a=60, b=60, start_angle=-0, end_angle=-np.pi),
                 line=dict(color='white', width=2)),

        ]
        court_shapes2 = [
    dict(
            type = 'line',
            x0=256,
            x1=-256,
            y0=0,
            y1=0,
            line=dict(color='white', width=2.5)
    ),
        dict(
            type = 'line',
            x1=256,
            x0=256,
            y0=515,
            y1 = 0,
            line=dict(color='white', width=2.5)
    ),
    dict(
            type = 'line',
            x1=-256,
            x0=-256,
            y0=515,
            y1 = 0,
            line=dict(color='white', width=2.5)
    ),
    dict(
        type = 'circle',
        x1 = 60,
        x0 = -60,
        y0=410,
        y1 = 535,
        line=dict(color='white', width=2.5)
    ),
    dict(
            type = 'line',
            y0 = 469,
            y1 = 469,
            x1 = -255,
            x0 = 255,
            line=dict(color='white', width=2.5)
    ),

    
    dict(
        type='line',
        x0=-30,
        y0=40,
        y1=40,
        x1=30,
        line=dict(color='white', width=2.5)

    ),
    dict(
        type='line',
        x0=-223,
        y0=0,
        x1=-223,
        y1=140,
        line=dict(color='white', width=2.5)
    ),
    dict(
        type='line',
        x0=220,
        y0=0,
        x1=220,
        y1=140,
        line=dict(color='white', width=2.5)
    ),
    dict(
        type='path',
        path='M -225,132,100,150,160,170,180,190 C -200,320 150,375 219,140',
        line=dict(color='white', width=2.5)
    ),
    dict(
        type='line',
        x0=-80,
        y0=0,
        x1=-80,
        y1=190,
        line=dict(color='white', width=2.5)
    ),
    dict(
        type='line',
        x0=80,
        y0=0,
        x1=80,
        y1=190,
        line=dict(color='white', width=2.5)
    ),
    dict(
        type='line',
        x0=-60,
        y0=0,
        x1=-60,
        y1=190,
        line=dict(color='white', width=2.5)
    ),
    dict(
        type='line',
        x0=60,
        y0=0,
        x1=60,
        y1=190,
        line=dict(color='white', width=2.5)
    ),
    dict(
        type='line',
        x0=-80,
        y0=190,
        x1=80,
        y1=190,
        line=dict(color='white', width=2.5)
    ),
    dict(
        type='circle',
        xref='x',
        yref='y',
        x0=-60,
        y0=130,
        x1=60,
        y1=245,
        line=dict(color='white', width=2.5)
    ),
    dict(
        type='circle',
        xref='x',
        yref='y',
        x0=-15,
        y0=45,
        x1=15,
        y1=75,
        line=dict(color='white', width=2.5)
    )
]

# Set aspect ratio
        # fig.update_layout(shapes=court_shapes)
        fig.add_trace(make_trace)
        fig.add_trace(miss_trace)

        fig.update_yaxes(scaleanchor='x', scaleratio=1)

# Update hover labels
        fig.update_traces(hoverlabel=dict(bgcolor='black', font_size=12))
        
        fig3.update_layout(shapes=court_shapes)
        fig3.add_trace(fig2trace)
        fig3.update_traces(hoverlabel=dict(bgcolor='black', font_size=12))
        fig3.update_yaxes(scaleanchor='x', scaleratio=1)





# Display the plot
                    # Plot hexbin with custom colormap
        fig2 = plt.figure(figsize=(12,11))
        ax = fig2.add_axes([0, 0, 1, 1])
        hb = ax.hexbin(-(shot_data['LOC_X']), shot_data['LOC_Y'], gridsize=(50, 50), extent=(-300, 300, -150, 500), bins='log', cmap='Blues',edgecolors='none')
        ax = draw_court(outer_lines=True)
        legend_elements = [
            plt.Line2D([0.5], [0.5], marker='H', color='#D2B48C', label='Less Shots', markerfacecolor='white', markersize=20),
            plt.Line2D([0.5], [0.5], marker='H', color='#D2B48C', label='More Shots', markerfacecolor='blue', markersize=20)
        ]
        plt.legend(handles=legend_elements, loc='upper right',framealpha=0,fontsize=15) 

        # Create hexbin plot with Plotly
        fig5 = go.Figure()
        fig5 = px.density_heatmap(shot_data, x=-(shot_data['LOC_X']), y=shot_data['LOC_Y'], nbinsx=35, nbinsy=55, color_continuous_scale='Hot')



        # Add hover labels
        fig5.update_traces(hovertemplate='Shots: %{z}<extra></extra>',showscale=False)

        # Customize layout
        fig5.update_layout(
            title='Shot Density',
            xaxis_title='',
            yaxis_title='',
        xaxis=dict(showline=False, showticklabels=False, showgrid=False, range=[-252, 260]),
        yaxis=dict(showline=False, showticklabels=False, showgrid=False, range=[-70, 475]),
        plot_bgcolor='black',
        margin=dict(l=0, r=0, t=0, b=0),
            width=800,  # Set the width of the background
        height=765,  # Set the height of the background
        autosize=False,
        coloraxis=dict(
    showscale=False,
    cmin=1,
    cmax=25
)

        )
        fig5.update_layout(shapes=court_shapes)
        fig5.update_yaxes(scaleanchor='x', scaleratio=1)
        

        # fig5.update_coloraxes(showscale=False)


        # fig5.update_coloraxes(showscale=False)


        # Show plot
# Display the image in Streamlit
                    # Customize color bar legend
        plottype = st.selectbox('Plot Type',['Make/Miss','Hexbin Plot','Heat Map'])
        if plottype == 'Make/Miss':
            st.plotly_chart(fig,use_container_width=True)
        elif plottype == 'Hexbin Plot':
            fig2.patch.set_visible(False)
            st.pyplot(fig2)
        else:
            st.plotly_chart(fig5,use_container_width=True)
        st.markdown(f'<div style="text-align: center;"><span style="font-size:25px;">{SEASON}: {total_makes}/{total_shots} - {shootperc}%</span></div>', unsafe_allow_html=True)
                


        
        
                # st.image(img_buffer, use_column_width=False, width=345)  

    

        shotfull = ShotTracking(PLAYER_ID, season=SEASON, season_type=typeseason)
        if shottrack == 'Overall':
                shots = shotfull.overall()
        elif shottrack == 'General':
                shots = shotfull.general()
        elif shottrack == 'Shot Clock':
                shots = shotfull.shot_clock()
        elif shottrack == 'Dribbles':
                shots = shotfull.dribbles()
        elif shottrack == 'Closest Defender':
                shots = shotfull.closest_defender()
        elif shottrack == 'Closest Defender Long':
                shots = shotfull.closest_defender_long()
        elif shottrack == 'Touch Time':
                shots = shotfull.touch_time()
        shots.drop(columns=['PLAYER_ID','SORT_ORDER','PLAYER_NAME_LAST_FIRST','GP','G'], inplace=True)
        st.write(shots)

        
                # st.plotly_chart(fig3)
                
        

            
            # st.sidebar.header(f'{season1}: 0/{total_misses} - {shooting_percentage}%')
    except PlayerNotFoundException as e:
        st.error(str(e))
        st.write('')
    # else:
    #     st.image("https://static.vecteezy.com/system/resources/thumbnails/013/861/222/small/silhouette-of-basketball-player-with-ball-shooting-dunk-free-vector.jpg",use_column_width=True)

