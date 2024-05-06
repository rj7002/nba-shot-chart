import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd
from nbapy import constants
from nbapy.nba_api import NbaAPI
import datetime
currentyear = datetime.datetime.now().year

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


# Streamlit UI
st.title("NBA Shot Chart Visualization")

# Get player ID from user input
player_id = st.text_input("Enter player ID:")

# Get season range from user input
SEASONS = [f'{i}-{str(i+1)[2:]}' for i in range(1996, currentyear)]
SEASON = st.selectbox('Select a season', SEASONS)
GameSegment = st.checkbox('Game Segment')
if GameSegment == 1:
    typeseg = st.selectbox('Game Segment',['First Half', 'Second Half', 'Overtime'])
else:
    typeseg = None



if player_id:
    # Create ShotChart object
    shot_chart = ShotChart(player_id, season=SEASON,game_segment=typeseg)

    # Fetch shot chart data
    shot_data = shot_chart.shot_chart()

    # Visualize shot chart
    if not shot_data.empty:
        # Plot shot chart on basketball court
        plt.figure(figsize=(10, 9))
        ax = plt.gca()
        # Plot makes in green
        ax.scatter(shot_data[shot_data["SHOT_MADE_FLAG"] == 1]["LOC_X"], 
                   shot_data[shot_data["SHOT_MADE_FLAG"] == 1]["LOC_Y"], 
                   color="green", alpha=0.6, label="Made",marker='o')
        # Plot misses in red
        ax.scatter(shot_data[shot_data["SHOT_MADE_FLAG"] == 0]["LOC_X"], 
                   shot_data[shot_data["SHOT_MADE_FLAG"] == 0]["LOC_Y"], 
                   color="red", alpha=0.6, label="Missed",marker='x')
        create_court(ax, 'black')
        ax.set_xlim(-250, 250)
        ax.set_ylim(0, 470)
        ax.set_aspect('equal')
        ax.set_title(f"NBA Shot Chart")
        ax.legend()
        st.pyplot(plt)
    else:
        st.error("Failed to fetch shot chart data. Please check the player ID and season range.")
