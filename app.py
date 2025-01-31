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
import seaborn as sns
from datetime import datetime
from datetime import time
import time
from courtCoordinates import CourtCoordinates
from random import randint
theme = """[theme]
backgroundColor="#000000"
secondaryBackgroundColor="#262631"
textColor="#ffffff"
font="monospace"
"""


st.set_page_config(page_title="NBA Shot Visualizer", page_icon='https://i.imgur.com/ljWwIOF.png?1', initial_sidebar_state="expanded")

currentyear = datetime.now().year

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
def draw_court2(ax=None, color='black', lw=2, outer_lines=False):
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
    ax.set_facecolor('white')
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
        plot_bgcolor="#D2B48C",
        yaxis=dict(
            scaleanchor="x",
            scaleratio=1,
            showgrid=False,
            zeroline=False,
            showline=False,
            ticks='',
            showticklabels=False,
            fixedrange=True
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
                # fillcolor='#333333',
                layer='below'
            ),
            dict(
                type="rect", x0=-80, y0=-52.5, x1=80, y1=137.5,
                line=dict(color=main_line_col, width=2),
                # fillcolor='#333333',
                layer='below'
            ),
            dict(
                type="rect", x0=-60, y0=-52.5, x1=60, y1=137.5,
                line=dict(color=main_line_col, width=2),
                # fillcolor='#333333',
                layer='below'
            ),
            dict(
                type="circle", x0=-60, y0=77.5, x1=60, y1=197.5, xref="x", yref="y",
                line=dict(color=main_line_col, width=2),
                # fillcolor='#dddddd',
                layer='below'
            ),
            dict(
                type="line", x0=-60, y0=137.5, x1=60, y1=137.5,
                line=dict(color=main_line_col, width=2),
                layer='below'
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
                 line=dict(color=main_line_col, width=2), layer='below'),
            dict(type="path",
                 path=ellipse_arc(a=237.5, b=237.5, start_angle=0.386283101, end_angle=np.pi - 0.386283101),
                 line=dict(color=main_line_col, width=2), layer='below'),
            dict(
                type="line", x0=-220, y0=-52.5, x1=-220, y1=threept_break_y,
                line=dict(color=three_line_col, width=2), layer='below'
            ),
            dict(
                type="line", x0=-220, y0=-52.5, x1=-220, y1=threept_break_y,
                line=dict(color=three_line_col, width=2), layer='below'
            ),
            dict(
                type="line", x0=220, y0=-52.5, x1=220, y1=threept_break_y,
                line=dict(color=three_line_col, width=2), layer='below'
            ),

            dict(
                type="line", x0=-250, y0=227.5, x1=-220, y1=227.5,
                line=dict(color=main_line_col, width=2), layer='below'
            ),
            dict(
                type="line", x0=250, y0=227.5, x1=220, y1=227.5,
                line=dict(color=main_line_col, width=2), layer='below'
            ),
            dict(
                type="line", x0=-90, y0=17.5, x1=-80, y1=17.5,
                line=dict(color=main_line_col, width=2), layer='below'
            ),
            dict(
                type="line", x0=-90, y0=27.5, x1=-80, y1=27.5,
                line=dict(color=main_line_col, width=2), layer='below'
            ),
            dict(
                type="line", x0=-90, y0=57.5, x1=-80, y1=57.5,
                line=dict(color=main_line_col, width=2), layer='below'
            ),
            dict(
                type="line", x0=-90, y0=87.5, x1=-80, y1=87.5,
                line=dict(color=main_line_col, width=2), layer='below'
            ),
            dict(
                type="line", x0=90, y0=17.5, x1=80, y1=17.5,
                line=dict(color=main_line_col, width=2), layer='below'
            ),
            dict(
                type="line", x0=90, y0=27.5, x1=80, y1=27.5,
                line=dict(color=main_line_col, width=2), layer='below'
            ),
            dict(
                type="line", x0=90, y0=57.5, x1=80, y1=57.5,
                line=dict(color=main_line_col, width=2), layer='below'
            ),
            dict(
                type="line", x0=90, y0=87.5, x1=80, y1=87.5,
                line=dict(color=main_line_col, width=2), layer='below'
            ),

            dict(type="path",
                 path=ellipse_arc(y_center=417.5, a=60, b=60, start_angle=-0, end_angle=-np.pi),
                 line=dict(color=main_line_col, width=2), layer='below'),

        ]
    )
    return True

def frequency_chart(df: pd.DataFrame, extent=(-300, 300,-50,422.5,),
                                gridsize=25, cmap="inferno"):
                """ Create a shot chart of a player's shot frequency and accuracy
                """ 
                # create frequency of shots per hexbin zone
                shots_hex = plt.hexbin(
                df.LOC_X, df.LOC_Y,
                extent=extent, cmap=cmap, gridsize=gridsize)
                plt.close()
                shots_hex_array = shots_hex.get_array()
                freq_by_hex = shots_hex_array / sum(shots_hex_array)
                
                # create field goal % per hexbin zone
                makes_df = df[df.SHOT_MADE_FLAG == 1] # filter dataframe for made shots
                makes_hex = plt.hexbin(makes_df.LOC_X, makes_df.LOC_Y, cmap=cmap,
                                gridsize=gridsize, extent=extent) # create hexbins
                plt.close()
                pcts_by_hex = makes_hex.get_array() / shots_hex.get_array()
                pcts_by_hex[np.isnan(pcts_by_hex)] = 0  # convert NAN values to 0
                
                # filter data for zone with at least 5 shots made
                sample_sizes = shots_hex.get_array()
                filter_threshold = 5
                for i in range(len(pcts_by_hex)):
                        if sample_sizes[i] < filter_threshold:
                                pcts_by_hex[i] = 0
                x = [i[0] for i in shots_hex.get_offsets()]
                y = [i[1] for i in shots_hex.get_offsets()]
                z = pcts_by_hex
                sizes = freq_by_hex * 1000
                
                # Create figure and axes
                fig = plt.figure(figsize=(3.6, 3.6), facecolor='black', edgecolor='black', dpi=100)
                ax = fig.add_axes([0, 0, 1, 1], facecolor='black')
                plt.xlim(275, -275)
                plt.ylim(-55, 430)
                # Plot hexbins
                scatter = ax.scatter(x, y, c=z, cmap=cmap, marker='h', s=sizes)
                # Draw court
                ax = draw_court(ax,outer_lines=True)
                # Add legends
                max_freq = max(freq_by_hex)
                max_size = max(sizes)
                legend_acc = plt.legend(
                *scatter.legend_elements(num=5, fmt="{x:.0f}%",
                                        func=lambda x: x * 100),
                loc=[0.84,0.75], title='Shot %', fontsize=6)
                legend_freq = plt.legend(
                *scatter.legend_elements(
                        'sizes', num=5, alpha=0.8, fmt="{x:.1f}%"
                        , func=lambda s: s / max_size * max_freq * 100
                ),
                loc=[0.68,0.785], title='Freq %', fontsize=6)
                plt.gca().add_artist(legend_acc)
                # Add title
                
                # add headshot

                return fig




# Define Streamlit app

st.sidebar.markdown('<div style="text-align: center;"><span style="font-size:30px;">NBA Shot Visualizer</span></div>', unsafe_allow_html=True)
st.sidebar.image("https://i.imgur.com/ljWwIOF.png?1")
animated = st.sidebar.toggle('Animated Shot Charts')

if animated == 1:
    player_list = PlayerList()
    players_df = player_list.players()
    
    # Create a multiselect widget with player options
    player_name = st.selectbox("Select player:", options=players_df["DISPLAY_FIRST_LAST"].tolist(), index=None)
    
    if player_name:
    
        PLAYER_ID = get_id(player_name)
    
        first_season, last_season = get_player_season_range(PLAYER_ID)
                    # Generate the list of seasons within the range
        SEASONS = [f'{season}-{str(int(season)+1)[2:]}' for season in range(int(first_season), int(last_season)+1)]
                    
        SEASON = st.selectbox(f'Select season', reversed(SEASONS))
    
        shotchart = ShotChart(player_id=PLAYER_ID,season=SEASON).shot_chart()
        games = []
        games = []
        added_game_ids = set()
    
    # Iterate through each row of the DataFrame
        for index, row in shotchart.iterrows():
            game_id = row['GAME_ID']
            hometeam = row['HTM']
            awayteam = row['VTM']
            datestr = row['GAME_DATE']
            date = datetime.strptime(datestr, '%Y%m%d').strftime('%m/%d/%Y')
            
            # Check if game_id has already been added
            if game_id not in added_game_ids:
                desc = f"{hometeam} vs {awayteam} | {date} | {game_id}"
                games.append(desc)
                added_game_ids.add(game_id)
        datetype = st.selectbox('Select game', [''] + games)
        speed = st.slider('Speed',-1,5)
        if speed == 5:
            sp = 0
        elif speed == 4:
            sp = 1
        elif speed == 3:
            sp = 2
        elif speed == 2:
            sp = 3
        elif speed == 1:
            sp = 4
        elif speed == 0:
            sp = 5
        if speed >=0 and datetype:
            parts = datetype.split(' | ')
            id = parts[-1]
            shotchart = shotchart[shotchart['GAME_ID'] == id]
    
      
            display_player_image(PLAYER_ID,300,player_name)
            # date = {shotchart["GAME_DATE"].apply(lambda date_str: '-'.join([date_str[4:6], date_str[6:], date_str[:4]]))}
            st.subheader(f"{shotchart['HTM'].iloc[0]} vs {shotchart['VTM'].iloc[0]} - {shotchart['PLAYER_NAME'].iloc[0]} Shot Chart")
    
            fig = go.Figure()
    
            # Draw the court
            draw_plotly_court(fig)
    
    
            hover_template = (
                        "<b>Date</b>: %{customdata[0]}<br>" +
                        "<b>Game</b>: %{customdata[1]}<br>" +
                        "<b>Shot</b>: %{customdata[2]}<br>" +
                        "<b>Shot Zone</b>: %{customdata[6]}<br>" +
                        "<b>Distance</b>: %{customdata[5]}<br>"+
                        "<b>Period</b>: %{customdata[3]}<br>" +
                        "<b>Time</b>: %{customdata[4]}" 
                        
                    )
    
                    # Assuming shot_data is already defined as per your provided data
                    # Extracting individual components from text_all and assigning them to customdata
            shotchart['GAME_DATE_NEW'] = shotchart["GAME_DATE"].apply(lambda date_str: '-'.join([date_str[4:6], date_str[6:], date_str[:4]]))
            shotchart['MATCH'] = shotchart["HTM"] + ' VS ' + shotchart["VTM"]
            shotchart['SHOT'] = shotchart['SHOT_TYPE'].str.replace(' Field Goal', '') + ' - ' + shotchart["ACTION_TYPE"]
            shotchart['PERIOD_TIME'] = shotchart["PERIOD"].astype(str) + 'Q'
            shotchart['TIME'] = shotchart["MINUTES_REMAINING"].astype(str) + ':' + shotchart["SECONDS_REMAINING"].astype(str)
            shotchart['DISTANCE'] = shotchart['SHOT_DISTANCE'].astype(str) + 'ft'
            shotchart['SHOT_ZONE'] = shotchart['SHOT_ZONE_AREA'] + ' - ' + shotchart['SHOT_ZONE_BASIC']
            # Create trace for makes
            make_trace = go.Scatter(
                x=[],
                y=[],
                mode='markers',
                marker=dict(color='rgba(0, 128, 0, 0.6)', size=15),
                name='Made Shot ✅',
                customdata=shotchart[shotchart["SHOT_MADE_FLAG"] == 1][['GAME_DATE_NEW', 'MATCH', 'SHOT', 'PERIOD_TIME','TIME','DISTANCE','SHOT_ZONE']],  # Use customdata for makes only
                hoverinfo='text',  # Set hoverinfo to text
                hovertemplate=hover_template
            )
    
            # Create trace for misses
            miss_trace = go.Scatter(
                x=[],
                y=[],
                mode='markers',
                marker=dict(symbol='x', color='rgba(255, 0, 0, 0.6)', size=15),
                name='Missed Shot ❌',
                customdata=shotchart[shotchart["SHOT_MADE_FLAG"] == 0][['GAME_DATE_NEW', 'MATCH', 'SHOT', 'PERIOD_TIME','TIME','DISTANCE','SHOT_ZONE']],  # Use customdata for misses only
                hoverinfo='text',  # Set hoverinfo to text
                hovertemplate=hover_template
            )
    
    
    
            # Initialize the plot with empty traces for 'make' and 'miss' shots
            fig.add_trace(make_trace)
            fig.add_trace(miss_trace)
    
            fig.update_layout(
                xaxis=dict(range=[-250, 250], showgrid=False, zeroline=False),
                yaxis=dict(range=[-50, 400], showgrid=False, zeroline=False),
                height=600,  # Adjust the height of the plot
                width=600,
                showlegend=False
                # Adjust the width of the plot
            )
            fig.update_yaxes(scaleanchor='x', scaleratio=1)
    
            headers = {
                'Host': 'stats.nba.com',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'x-nba-stats-origin': 'stats',
                'x-nba-stats-token': 'true',
                'Connection': 'keep-alive',
                'Referer': 'https://stats.nba.com/',
                'Pragma': 'no-cache',
                'Cache-Control': 'no-cache'
            }
    
    
            plot_placeholder = st.empty()
    
            # Create a placeholder for the message
            message_placeholder = st.empty()
            message2 = st.empty()
            message3 = st.empty()
            messages = []
            videos = []
    
            if 'paused' not in st.session_state:
                st.session_state.paused = False
            if 'current_index' not in st.session_state:
                st.session_state.current_index = 0
    
            # Define play and pause buttons
            
            if st.button("Replay"):
                st.session_state.paused = False
        
    
            # Loop through each shot and update the plot
            total_makes = 0
            total_misses = 0
            totalpoints = 0
            if datetype:
                for i, shot in shotchart.iterrows():
                    event_id = shot['GAME_EVENT_ID']
                    game_id = shot['GAME_ID']
                    url = 'https://stats.nba.com/stats/videoeventsasset?GameEventID={}&GameID={}'.format(
                            event_id, game_id)
                    r = requests.get(url, headers=headers)
                    if r.status_code == 200:
                        json = r.json()
                        video_urls = json['resultSets']['Meta']['videoUrls']
                        playlist = json['resultSets']['playlist']
                        video_event = {'video': video_urls[0]['lurl'], 'desc': playlist[0]['dsc']}
                        video = video_urls[0]['lurl']
                    
                    if shot['SHOT_MADE_FLAG'] == 1:
                        if shot['SHOT_TYPE'] == '3PT Field Goal':
                            totalpoints = totalpoints+3
                        else:
                            totalpoints = totalpoints+2
                        total_makes = total_makes+1
                        fig.data[0].x += (shot['LOC_X'],)
                        fig.data[0].y += (shot['LOC_Y'],)
                        message = f"✅ {shot['EVENT_TYPE']} - {shot['SHOT_TYPE']}: {shot['ACTION_TYPE']} ({shot['SHOT_DISTANCE']} ft) {shot['PERIOD']}Q - {shot['MINUTES_REMAINING']}:{shot['SECONDS_REMAINING']}"
                    else:
                        total_misses = total_misses+1
                        fig.data[1].x += (shot['LOC_X'],)
                        fig.data[1].y += (shot['LOC_Y'],)
                        message = f"❌ {shot['EVENT_TYPE']} - {shot['SHOT_TYPE']}: {shot['ACTION_TYPE']} ({shot['SHOT_DISTANCE']} ft) {shot['PERIOD']}Q - {shot['MINUTES_REMAINING']}:{shot['SECONDS_REMAINING']}"
                    messages.append(message) 
                    videos.append(video)
                    videos.append(message) # Insert the new message at the beginning of the list
    
    
    
                    # Update the plot in the placeholder
                    plot_placeholder.plotly_chart(fig, use_container_width=True)
                    
                    # Display the message
                    message_placeholder.text(message)
                    if message == None:
                        st.text('')
                    else:
                        message_placeholder.text(f'Latest shot: {message}')
                        message2.text(f'{total_makes}/{total_misses+total_makes} - {round((total_makes / (int(total_makes+total_misses))) * 100, 1)}% Points (Without FTs): {totalpoints}')
                    # Pause for a brief moment to create the animation effect
                    time.sleep(sp)  # Adjust the sleep time for your preferred speed
                
                with st.expander('All Shots'):
                    for i, vid in enumerate(videos):
                        if i % 2 == 0:  # Check if index i is even
                            st.video(vid)
                        else:
                            st.text(vid)
        else:
            if speed < 0 and datetype != '':
                st.error('Please pick a positive speed')
            elif datetype == '' and speed != -1:
                st.error('Please select a game')
            else:
                st.error('Please select a game and pick a positive speed')
else:

    type = st.sidebar.selectbox('Player Stats',['Per Game','Totals'])
    # shottrack = st.sidebar.selectbox('Shot Tracking Stats',['Overall','General','Shot Clock','Dribbles','Closest Defender','Closest Defender Long','Touch Time'])
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
    # Month = st.sidebar.toggle('Month')
    # if Month == 1:
    #     typemonth = st.sidebar.selectbox('',['October','November','December','January','February','March','April','May','June','July'])
    #     if typemonth == 'October':
    #         typemonth = '1'
    #     elif typemonth == 'November':
    #         typemonth = '2'
    #     elif typemonth == 'December':
    #         typemonth = '3'
    #     elif typemonth == 'January':
    #         typemonth = '4'
    #     elif typemonth == 'February':
    #         typemonth = '5'
    #     elif typemonth == 'March':
    #         typemonth = '6'
    #     elif typemonth == 'April':
    #         typemonth = '7'
    #     elif typemonth == 'May':
    #         typemonth = '8'
    #     elif typemonth == 'June':
    #         typemonth = '9'
    #     elif typemonth == 'July':
    #         typemonth = '10'
    
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
        st.image("https://i.imgur.com/ljWwIOF.png?1",use_column_width=True)
    
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
                
            SEASONS = st.multiselect(f'Select season', reversed(SEASONS))
            if SEASONS:
                playerinfo = Summary(player_id=PLAYER_ID).info()
                playerheight = playerinfo.loc[playerinfo['DISPLAY_FIRST_LAST'] == player_name, 'HEIGHT'].values[0]
                playerweight = playerinfo.loc[playerinfo['DISPLAY_FIRST_LAST'] == player_name, 'WEIGHT'].values[0]
        
                display_player_image(PLAYER_ID,400,f"{player_name}")
                st.markdown(f'<div style="text-align: center;"><span style="font-size:20px;">Height: {playerheight} Weight: {playerweight}</span></div>', unsafe_allow_html=True)
        
                for SEASON in SEASONS:
                    if SEASON:
                        player_list = PlayerList(season=SEASON)
                        players_df2 = player_list.players()
        
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
                        player_summarytotals = Splits(player_id=PLAYER_ID,season=SEASON,per_mode=type2,season_type=typeseason,location=typeloc,vs_conference=typeconf,outcome=typeout,game_segment=typeseg)
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
        
        
        
            # Display the variables
                                
        
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
                            col1,col2 = st.columns(2)
                            with col1:
                                with st.expander('Player Stats'):
                                    st.markdown(f"<span style='font-size:{font_size_large}'>**Season:** <span style='color:{pts_color}'>{SEASON}</span>", unsafe_allow_html=True)
                                    st.markdown(f"<span style='font-size:{font_size_large}'>**Team:** <span style='color:{tov_color}'>{fullteam}</span>", unsafe_allow_html=True)
                                    st.markdown(f"<span style='font-size:{font_size_large}'>**Pts:** <span style='color:{pts_color}'>{pts}</span>   **Ast:** <span style='color:{ast_color}'>{ast}</span></span>", unsafe_allow_html=True)
                                    st.markdown(f"<span style='font-size:{font_size_large}'>**Reb:** <span style='color:{reb_color}'>{reb}</span>   **Blk:** <span style='color:{blk_color}'>{blk}</span></span>", unsafe_allow_html=True)
                                    st.markdown(f"<span style='font-size:{font_size_large}'>**Stl:** <span style='color:{stl_color}'>{stl}</span>   **<span style='color:{fg_pct_color}'>{round(fg_pct*100,1)}</span> FG%**</span>", unsafe_allow_html=True)
                                    st.markdown(f"<span style='font-size:{font_size_large}'><span style='color:{fg3_pct_color}'>{round(fg3_pct*100,1)} </span>3P%   **<span style='color:{ft_pct_color}'>{round(ft_pct*100,1)} </span>FT%**</span>", unsafe_allow_html=True)
                                    st.markdown(f"<span style='font-size:{font_size_large}'>**Tov:** <span style='color:{tov_color}'>{tov}</span>   **Min:** <span style='color:{min_color}'>{min}</span></span>", unsafe_allow_html=True)
        
                        else:
                            st.error(f'No data found for {player_name.lower().title()} in {SEASON}. Check season: shot chart data before 1996 is unavailable')
                        with col2:
                            with st.expander('Game Log'):
                                st.plotly_chart(plotgames)
        
        
                    col1, col,col2 = st.columns(3)
        
        
        
                    # Create ShotChart object
                
                all_shot_data = pd.DataFrame()
                for SEASON in SEASONS:
        
                    shot_chart = ShotChart(PLAYER_ID, season=SEASON,game_segment=typeseg,clutch_time=typeclutch,season_type=typeseason,vs_conf=typeconf,location=typeloc,outcome=typeout,context_measure=Stat2,ahead_behind=typeaheadbehind)
                        # Fetch shot chart data
                    shot_data = shot_chart.shot_chart()
                    all_shot_data = pd.concat([all_shot_data, shot_data], ignore_index=True)
        
        
                shootperc = 0
                        # Plot shot chart on basketball court
                plt.figure(figsize=(13, 8))
                ax = plt.gca()
                if Date == 1:
                        date = all_shot_data['GAME_DATE'].unique()
                        datetype = st.sidebar.multiselect('', all_shot_data['GAME_DATE'].unique())
                        all_shot_data = all_shot_data[all_shot_data['GAME_DATE'].isin(datetype)]
                if Stat == 'MISSES':
                        all_shot_data = all_shot_data[all_shot_data['SHOT_MADE_FLAG'] == 0]
                if Quarters:
                        all_shot_data = all_shot_data[all_shot_data['PERIOD'] == int(typequart)]
                if CourtLoc:
                        all_shot_data = all_shot_data[all_shot_data['SHOT_ZONE_AREA'].isin(courtloc)]
                if Teams:
                            all_shot_data = all_shot_data[(all_shot_data['VTM'].isin(teamtype)) | (all_shot_data['HTM'].isin(teamtype))]
                if ShotType:  # Check if ShotType checkbox is selected
                        all_shot_data = all_shot_data[all_shot_data['ACTION_TYPE'].isin(finaltype)]
                        # Plot makes in green
                if ShotDist == 1:
                        all_shot_data = all_shot_data[(all_shot_data['SHOT_DISTANCE'] >= shotdistance_min) & (all_shot_data['SHOT_DISTANCE'] <= shotdistance_max)]
                            
        
                
                total_makes = len(all_shot_data[all_shot_data["SHOT_MADE_FLAG"] == 1])
                total_misses = len(all_shot_data[all_shot_data["SHOT_MADE_FLAG"] == 0])
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
        all_shot_data["GAME_DATE"].apply(lambda date_str: '-'.join([date_str[4:6], date_str[6:], date_str[:4]])) + ': ' +
        all_shot_data["HTM"] + ' VS ' + all_shot_data["VTM"] + ' | ' +
        all_shot_data['SHOT_TYPE'].str.replace(' Field Goal', '') + ' - ' +  # Remove 'Field Goal'
        all_shot_data["ACTION_TYPE"] + ' (' +
        all_shot_data["SHOT_DISTANCE"].astype(str) + ' ft)' + ' | '  + all_shot_data["PERIOD"].astype(str) + 'Q' + ' - ' +
        all_shot_data["MINUTES_REMAINING"].astype(str) + ':' +
        all_shot_data["SECONDS_REMAINING"].astype(str)
        )
        
                hover_template = (
                    "<b>Date</b>: %{customdata[0]}<br>" +
                    "<b>Game</b>: %{customdata[1]}<br>" +
                    "<b>Shot</b>: %{customdata[2]}<br>" +
                    "<b>Shot Zone</b>: %{customdata[6]}<br>" +
                    "<b>Distance</b>: %{customdata[5]}<br>"+
                    "<b>Period</b>: %{customdata[3]}<br>" +
                    "<b>Time</b>: %{customdata[4]}" 
                    
                )
        
                # Assuming shot_data is already defined as per your provided data
                # Extracting individual components from text_all and assigning them to customdata
                all_shot_data['GAME_DATE_NEW'] = all_shot_data["GAME_DATE"].apply(lambda date_str: '-'.join([date_str[4:6], date_str[6:], date_str[:4]]))
                all_shot_data['MATCH'] = all_shot_data["HTM"] + ' VS ' + all_shot_data["VTM"]
                all_shot_data['SHOT'] = all_shot_data['SHOT_TYPE'].str.replace(' Field Goal', '') + ' - ' + all_shot_data["ACTION_TYPE"]
                all_shot_data['PERIOD_TIME'] = all_shot_data["PERIOD"].astype(str) + 'Q'
                all_shot_data['TIME'] = all_shot_data["MINUTES_REMAINING"].astype(str) + ':' + all_shot_data["SECONDS_REMAINING"].astype(str)
                all_shot_data['DISTANCE'] = all_shot_data['SHOT_DISTANCE'].astype(str) + 'ft'
                all_shot_data['SHOT_ZONE'] = all_shot_data['SHOT_ZONE_AREA'] + ' - ' + all_shot_data['SHOT_ZONE_BASIC']
                # Create trace for makes
                make_trace = go.Scatter(
                    x=-(all_shot_data[all_shot_data["SHOT_MADE_FLAG"] == 1]["LOC_X"]),
                    y=all_shot_data[all_shot_data["SHOT_MADE_FLAG"] == 1]["LOC_Y"],
                    mode='markers',
                    marker=dict(color='rgba(0, 128, 0, 0.6)', size=15),
                    name='Made Shot ✅',
                    customdata=all_shot_data[all_shot_data["SHOT_MADE_FLAG"] == 1][['GAME_DATE_NEW', 'MATCH', 'SHOT', 'PERIOD_TIME','TIME','DISTANCE','SHOT_ZONE']],  # Use customdata for makes only
                    hoverinfo='text',  # Set hoverinfo to text
                    hovertemplate=hover_template
                )
        
                # Create trace for misses
                miss_trace = go.Scatter(
                    x=-(all_shot_data[all_shot_data["SHOT_MADE_FLAG"] == 0]["LOC_X"]),
                    y=all_shot_data[all_shot_data["SHOT_MADE_FLAG"] == 0]["LOC_Y"],
                    mode='markers',
                    marker=dict(symbol='x', color='rgba(255, 0, 0, 0.6)', size=15),
                    name='Missed Shot ❌',
                    customdata=all_shot_data[all_shot_data["SHOT_MADE_FLAG"] == 0][['GAME_DATE_NEW', 'MATCH', 'SHOT', 'PERIOD_TIME','TIME','DISTANCE','SHOT_ZONE']],  # Use customdata for misses only
                    hoverinfo='text',  # Set hoverinfo to text
                    hovertemplate=hover_template
                )
                fig2trace = go.Scatter(
                        x=-(all_shot_data[all_shot_data["SHOT_MADE_FLAG"] == 0]["LOC_X"]),
            y=all_shot_data[all_shot_data["SHOT_MADE_FLAG"] == 0]["LOC_Y"],
            mode='markers',
            marker=dict(symbol='hexagon', color='rgba(255, 0, 0, 0.6)', size=15),
            name='Shots',
            text=text_all[all_shot_data["SHOT_MADE_FLAG"] == 0],  # Use concatenated text for misses only
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
                hb = ax.hexbin(-(all_shot_data['LOC_X']), all_shot_data['LOC_Y'], gridsize=(30, 30), extent=(-240, 240, -30, 370), bins='log', cmap='Blues',edgecolors='none')
                ax = draw_court(outer_lines=True)
                legend_elements = [
                    plt.Line2D([0.5], [0.5], marker='H', color='#D2B48C', label='Less Shots', markerfacecolor='white', markersize=20),
                    plt.Line2D([0.5], [0.5], marker='H', color='#D2B48C', label='More Shots', markerfacecolor='blue', markersize=20)
                ]
                plt.legend(handles=legend_elements, loc='upper right',framealpha=0) 
        
                # Create hexbin plot with Plotly
                
        
               
        
                # fig5.update_coloraxes(showscale=False)
        
        
                # fig5.update_coloraxes(showscale=False)
        
        
                # Show plot
        # Display the image in Streamlit
                            # Customize color bar legend
                plottype = st.selectbox('Plot Type',['Make/Miss','Hexbin Plot','Heat Map','KDE Plot','FG% and Frequency'])
                if plottype == '3D':
                    df = all_shot_data
                    court = CourtCoordinates(SEASON)
                    court_lines_df = court.get_coordinates()
                    fig = px.line_3d(
                        data_frame=court_lines_df,
                        x='x',
                        y='y',
                        z='z',
                        line_group='line_group_id',
                        color='line_group_id',
                        color_discrete_map={
                            'court': 'black',
                            'hoop': '#e47041',
                            'net': '#D3D3D3',
                            'backboard': 'gray',
                            'free_throw_line': 'black',
                            'hoop2':'white'
                        }
                    )
                    fig.update_traces(hovertemplate=None, hoverinfo='skip', showlegend=False)
                    fig.update_traces(line=dict(width=6))
                    fig.update_layout(    
                        margin=dict(l=20, r=20, t=20, b=20),
                        scene_aspectmode="data",
                        height=600,
                        scene_camera=dict(
                            eye=dict(x=1.3, y=0, z=0.7)
                        ),
                        scene=dict(
                            xaxis=dict(title='', showticklabels=False, showgrid=False),
                            yaxis=dict(title='', showticklabels=False, showgrid=False),
                            zaxis=dict(title='',  showticklabels=False, showgrid=False, showbackground=True, backgroundcolor='#d2a679'),
                        ),
                        showlegend=False,
                        legend=dict(
                            yanchor='top',
                            y=0.05,
                            x=0.2,
                            xanchor='left',
                            orientation='h',
                            font=dict(size=15, color='gray'),
                            bgcolor='rgba(0, 0, 0, 0)',
                            title='',
                            itemsizing='constant'
                        )
                    )
                    # df2 = shotchart(selected_player,realseason)
                    # shotchartdata = shotchartdetail.ShotChartDetail(player_id=id,season_nullable=realseason,team_id=0,context_measure_simple = 'FGA')
                    
                    # df = shotchartdata.get_data_frames()[0]
                    
                    x_values = []
                    y_values = []
                    z_values = []
                    
                    for index, row in df.iterrows():
                        
                        
                       
                        x_values.append(-row['LOC_X'])
                        # Append the value from column 'x' to the list
                        y_values.append(row['LOC_Y']+45)
                        z_values.append(0)
                    
                    
                    
                    x_values2 = []
                    y_values2 = []
                    z_values2 = []
                    for index, row in df.iterrows():
                        # Append the value from column 'x' to the list
                      
                    
                        x_values2.append(court.hoop_loc_x)
                    
                        y_values2.append(court.hoop_loc_y)
                        z_values2.append(100)
                    
                    import numpy as np
                    import plotly.graph_objects as go
                    import streamlit as st
                    import math
                    def calculate_distance(x1, y1, x2, y2):
                        """Calculate the distance between two points (x1, y1) and (x2, y2)."""
                        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                    
                    def generate_arc_points(p1, p2, apex, num_points=100):
                        """Generate points on a quadratic Bezier curve (arc) between p1 and p2 with an apex."""
                        t = np.linspace(0, 1, num_points)
                        x = (1 - t)**2 * p1[0] + 2 * (1 - t) * t * apex[0] + t**2 * p2[0]
                        y = (1 - t)**2 * p1[1] + 2 * (1 - t) * t * apex[1] + t**2 * p2[1]
                        z = (1 - t)**2 * p1[2] + 2 * (1 - t) * t * apex[2] + t**2 * p2[2]
                        return x, y, z
                    
                    # Example lists of x and y coordinates
                    x_coords = x_values
                    y_coords = y_values
                    z_value = 0  # Fixed z value
                    x_coords2 = x_values2
                    y_coords2 = y_values2
                    z_value2 = 100
                    for i in range(len(df)):
                        x1 = x_coords[i]
                        y1 = y_coords[i]
                        x2 = x_coords2[i]
                        y2 = y_coords2[i]
                        # Define the start and end points
                        p2 = np.array([x1, y1, z_value])
                        p1 = np.array([x2, y2, z_value2])
                        
                        # Apex will be above the line connecting p1 and p2
                        distance = calculate_distance(x1, y1, x2, y2)
                    
                        if df['SHOT_MADE_FLAG'].iloc[i] == 1:
                            s = 'circle-open'
                            s2 = 'circle'
                            size = 9
                            color = 'green'
                        else:
                            s = 'cross'
                            s2 = 'cross'
                            size = 10
                            color = 'red'
                        hovertemplate= f"Game: {df['HTM'].iloc[i]} vs {df['VTM'].iloc[i]}<br>Result: {df['EVENT_TYPE'].iloc[i]}<br>Shot Type: {df['ACTION_TYPE'].iloc[i]}<br>Distance: {df['SHOT_DISTANCE'].iloc[i]} ft {df['SHOT_TYPE'].iloc[i]}<br>Quarter: {df['PERIOD'].iloc[i]}<br>Time: {df['MINUTES_REMAINING'].iloc[i]}:{df['SECONDS_REMAINING'].iloc[i]}"
                    
                        if df['SHOT_DISTANCE'].iloc[i] > 3:
                            if df['SHOT_DISTANCE'].iloc[i] > 50:
                                h = randint(275,325)
                            elif df['SHOT_DISTANCE'].iloc[i] > 30:
                                h = randint(250,300)
                            elif df['SHOT_DISTANCE'].iloc[i] > 25:
                                h = randint(200,250)
                            elif df['SHOT_DISTANCE'].iloc[i] > 15:
                                h = randint(200,250)
                            else:
                                h = randint(150,200)
                        
                            apex = np.array([0.5 * (x1 + x2), 0.5 * (y1 + y2), h])  # Adjust apex height as needed
                            
                            # Generate arc points
                            x, y, z = generate_arc_points(p1, p2, apex)
                            fig.add_trace(go.Scatter3d(
                                        x=x, y=y, z=z,
                                        mode='lines',
                                        line=dict(width=8,color = color),
                                        opacity =0.5,
                                        name=f'Arc {i + 1}',
                                        # hoverinfo='text',
                                        hovertemplate=hovertemplate
                                    ))
                        # Add start and end points
                    
                        fig.add_trace(go.Scatter3d(
                            x=[p2[0], p2[0]],
                            y=[p2[1], p2[1]],
                            z=[p2[2], p2[2]],
                            mode='markers',
                            marker=dict(size=size, symbol=s,color=color),
                            name=f'Endpoints {i + 1}',
                            # hoverinfo='text',
                            hovertemplate=hovertemplate
                        ))
                        fig.add_trace(go.Scatter3d(
                            x=[p2[0], p2[0]],
                            y=[p2[1], p2[1]],
                            z=[p2[2], p2[2]],
                            mode='markers',
                            marker=dict(size=5, symbol=s2,color = color),
                            name=f'Endpoints {i + 1}',
                            # hoverinfo='text',
                            hovertemplate=hovertemplate
                    
                        ))
                    # st.subheader(f'{selected_player} Shot Chart in {realseason}')
                    st.plotly_chart(fig)

                    


                    
                if plottype == 'Make/Miss':
                    st.plotly_chart(fig,use_container_width=True)
                elif plottype == 'Hexbin Plot':
                    fig2.patch.set_visible(False)
                    st.pyplot(fig2)
                elif plottype =='Heat Map':
                    c1,c2 = st.columns(2)
                    with c1:
                        xbins = st.slider('Number of x bins',5,80,35)
                    with c2:
                        ybins = st.slider('Number of y bins',5,80,55)
                    fig5 = go.Figure()
                    fig5 = px.density_heatmap(all_shot_data, x=-(all_shot_data['LOC_X']), y=all_shot_data['LOC_Y'], nbinsx=xbins, nbinsy=ybins, color_continuous_scale='Hot')
        
        
        
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
                    st.plotly_chart(fig5,use_container_width=True)
                elif plottype =='FG% and Frequency':
                     st.pyplot(frequency_chart(shot_data))
                else:
                    if plottype != '3D':
                        plt.clf()
                        cmap = 'gist_heat_r'
                        fig6 = sns.kdeplot(x=-(shot_data['LOC_X']), y=shot_data['LOC_Y'], cmap=cmap, fill=True, n_levels=50)
                        draw_court2(fig6,outer_lines=True)
                        # Set the background color to white
                        fig6.set_facecolor('black')
                        fig6.set_xlim(250, -250)
                        fig6.set_ylim(-47.5, 422.5)
                        fig6.set_axis_off()
                        st.pyplot(fig6.figure)
                st.markdown(f'<div style="text-align: center;"><span style="font-size:25px;">{total_makes}/{total_shots} - {shootperc}%</span></div>', unsafe_allow_html=True)
        
                
                        # st.image(img_buffer, use_column_width=False, width=345)  
        
            
                # for SEASON in SEASONS:
                #     shotfull = ShotTracking(PLAYER_ID, season=SEASON, season_type=typeseason)
                #     if shottrack == 'Overall':
                #             shots = shotfull.overall()
                #     elif shottrack == 'General':
                #             shots = shotfull.general()
                #     elif shottrack == 'Shot Clock':
                #             shots = shotfull.shot_clock()
                #     elif shottrack == 'Dribbles':
                #             shots = shotfull.dribbles()
                #     elif shottrack == 'Closest Defender':
                #             shots = shotfull.closest_defender()
                #     elif shottrack == 'Closest Defender Long':
                #             shots = shotfull.closest_defender_long()
                #     elif shottrack == 'Touch Time':
                #             shots = shotfull.touch_time()
                #     shots.drop(columns=['PLAYER_ID','SORT_ORDER','PLAYER_NAME_LAST_FIRST','GP','G'], inplace=True)
                #     st.write(shots)
                #     st.write('')
        
                
                        # st.plotly_chart(fig3)
                        
                
        
                    
                    # st.sidebar.header(f'{season1}: 0/{total_misses} - {shooting_percentage}%')
        except PlayerNotFoundException as e:
            st.error(str(e))
        # else:
        #     st.image("https://static.vecteezy.com/system/resources/thumbnails/013/861/222/small/silhouette-of-basketball-player-with-ball-shooting-dunk-free-vector.jpg",use_column_width=True)
    
