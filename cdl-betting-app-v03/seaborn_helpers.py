
# Imports
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import matplotlib.dates as mdates
import math
import datetime as dt

# Dictionary of color palettes by gamemode
palettes = {
  "Hardpoint":
    ["#033c73", "#105490", "#1b6ead", "#2588ca", "#2fa4e7"],
  "Search & Destroy":
    ["#033c73", "#105490", "#1b6ead", "#2588ca", "#2fa4e7"],
  "Control": ["#033c73", "#1b6ead", "#2fa4e7"]
}

# Dictionary of bin ranges by gamemode
gamemode_bin_ranges = {
    "Search & Destroy": (-6, 6), 
    "Control": (-3, 3)
}

# Dictionary of team colors for plotting
team_colors = {
    "Atlanta FaZe": "#e43d30", 
    "Boston Breach": "#02ff5b",
    "Carolina Royal Ravens": "#0083c1",
    "Los Angeles Guerrillas": "#60269e",
    "Los Angeles Thieves": "#ff0000",
    "Las Vegas Legion": "#ee7623",
    "Miami Heretics": "#216d6b",
    "Minnesota ROKKR": "#351f65",
    "New York Subliners": "#fff000", #"#171C38", 
    "Seattle Surge": "#00ffcc", 
    "Toronto Ultra": "#780df2",
    "OpTic Texas": "#92c951" # "#000000"

}

# PrizePicks Color Variable
prizepicks_color = "purple"

# Helper function to round HP score differential to nearest ten
def truncate(n, decimals = -1):
    multiplier = 10 ** decimals
    return int(int(n * multiplier) / multiplier)

# Function to map y-axis range to padding for y-axis limits
def map_range(min: int, max:int):
    if max - min <= 1:
        return 2.5
    elif max - min < 4:
        return 1.5
    elif max - min == 4:
        return 0.5
    else:
        return 0
    
# Function to adjust score diff ticks based on gamemode and current range
def adjust_score_diff_ticks(gamemode: str, min_x: int, max_x: int):
    if gamemode == "Control":
        while max_x - min_x < 4:
            if min_x != -3:
                min_x -= 1
            if max_x - min_x < 4 and max_x != 3:
                max_x += 1
    elif gamemode == "Search & Destroy":
        while max_x - min_x < 4:
            if min_x != -6:
                min_x -= 1
            if max_x - min_x < 4 and max_x != 6:
                max_x += 1
    else:
        while max_x - min_x < 50:
            if min_x != -250:
                min_x -= 10
            if max_x - min_x < 50 and max_x != 250:
                max_x += 10
    return min_x, max_x

# Function to adjust time ticks based on current range
def adjust_time_ticks(min_x, max_x):
    while max_x - min_x < dt.timedelta(days = 6):
        min_x -= dt.timedelta(days = 1)
        if max_x - min_x < dt.timedelta(days = 6):
            max_x += dt.timedelta(days = 1)
    return min_x, max_x

# Function to scale X & Y axes of player kills plots & return axes ranges
def scale_fig(queried_df: pd.DataFrame, ax: plt.axes, x_axis: str, 
              gamemode_input: str, cur_line: int):

    # Time
    if x_axis == "time":

        # Set & Scale X-Axis, if necessary
        match_dates = queried_df["match_date"].to_list()
        if match_dates:
            min_x = min(match_dates)
            max_x = max(match_dates)
        else:
            min_x = dt.date.today()
            max_x = dt.date.today()

        # Case 1: max_x - min_x < 6 days
        if max_x - min_x < dt.timedelta(days = 6):
            min_x, max_x = adjust_time_ticks(min_x, max_x)
            ax.set_xlim(min_x, max_x)

        # Case 2: max_x - min_x <= 2 weeks
        elif max_x - min_x <= dt.timedelta(days = 14):
            ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday = (mdates.TU, mdates.SA)))
        
        # Case 3: max_x - min_x <= 1 month
        elif max_x - min_x <= dt.timedelta(days = 31):
            ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday = mdates.SA))

        # Case 4: max_x - min_x <= 2 months
        elif max_x - min_x <= dt.timedelta(days = 64):
            ax.xaxis.set_major_locator(mdates.DayLocator(bymonthday = [1, 15]))
    
    # Score Diffs
    if x_axis == "score_diff":

        # Set & Scale X-Axis, if necessary
        score_diffs = queried_df["score_diff"].to_list()
        if score_diffs:
            min_x = min(score_diffs)
            max_x = max(score_diffs)
        else:
            min_x = 0
            max_x = 0

        # Case 1: Hardpoint
        if gamemode_input == "Hardpoint" and max_x - min_x < 50:
            ax.xaxis.set_major_locator(MultipleLocator(base = 10))
            if min_x == max_x:
                min_x = math.floor(min_x / 10) * 10
                max_x = math.ceil(max_x / 10) * 10
            else:
                min_x = truncate(min_x)
                max_x = truncate(max_x)
            min_x, max_x = adjust_score_diff_ticks(gamemode_input, min_x, max_x)
            ax.set_xlim(min_x - 5, max_x + 5)

        # Case 2: Search & Destroy & Control
        elif max_x - min_x < 4:
            ax.xaxis.set_major_locator(MultipleLocator(base = 1))
            min_x, max_x = adjust_score_diff_ticks(gamemode_input, min_x, max_x)
            ax.set_xlim(min_x - 0.25, max_x + 0.25)

    # Set & Scale Y-Axis, if necessary
    kills = queried_df["kills"].to_list()
    kills.append(cur_line)
    min_y = min(kills)
    max_y = max(kills)

    # Case 1: Y-Axis Range <= 4
    if max_y - min_y <= 4:
        ax.yaxis.set_major_locator(MultipleLocator(base = 1))
        pad = map_range(min_y, max_y)
        min_y = min_y - pad
        max_y = max_y + pad
        ax.set_ylim(min_y, max_y)
        
    # Case 2: Y-Axis Range <= 15
    elif max_y - min_y > 12 and max_y - min_y <= 18:
        ax.yaxis.set_major_locator(MultipleLocator(base = 4))

    return min_x, min_y, max_x, max_y

# Set seaborn theme
sns.set_theme(style = "darkgrid")

# Team Distribution of Score Differentials by Map & Mode
def team_score_diffs(
        cdlDF_input: pd.DataFrame, team_input: str, team_color: str,
        gamemode_input: str, map_input = "All"
):
    
    # Create a copy of cdlDF_input
    queried_df = cdlDF_input.copy()

    # If user selected all maps    
    if map_input == "All":
    
        # Filter data based on user inputs
        queried_df = \
        queried_df[(queried_df['gamemode'] == gamemode_input) & \
                (queried_df['team'] == team_input)] \
                [['match_id', 'map_name', 'score_diff']].drop_duplicates()
    
    # User selected only one map 
    else:

        # Filter data based on user inputs, including map
        queried_df = \
        queried_df[(queried_df['gamemode'] == gamemode_input) & \
                (queried_df['team'] == team_input) & \
                (queried_df["map_name"] == map_input)] \
                [['match_id', 'map_name', 'score_diff']].drop_duplicates()
        

    # Create the figure
    fig, ax = plt.subplots(figsize = (4, 2))

    # Histogram for Hardpoint
    if gamemode_input == "Hardpoint":
          
        # Plot the histogram
        sns.histplot(data = queried_df, x = "score_diff", binwidth = 50, 
                     binrange = (-250, 250), color = team_color)

        # Get max y
        queried_df['bin'] = pd.cut(queried_df['score_diff'], bins = range(-250, 300, 50))
        max_y = max(queried_df['bin'].value_counts())

    # Bar chart for SnD & Control
    else:
        
        # Plot the bar chart
        sns.histplot(data = queried_df, x = "score_diff", discrete = True, 
             binrange = gamemode_bin_ranges[gamemode_input], 
             color = team_color)
        
        # Get max y
        max_y = 0 if queried_df.empty else max(queried_df["score_diff"].value_counts())
        
    # Set y-axis to integer values only
    step_y = 1 if max_y < 6 else 2
    y_axis_ticks = range(0, max_y + 1, step_y)
    plt.yticks(y_axis_ticks)
        
    # Styling
    ax.set_xlabel("Map Result")


# Team % of Maps Played by Mode
def team_percent_maps_played(
        team_summaries_input: pd.DataFrame, team_input: str,
        gamemode_input: str
):
    
    # Create a copy of cdlDF_input
    queried_df = team_summaries_input.copy()

    # Filter team_summaries_input by team & mode
    queried_df = queried_df[
        (queried_df["team"] == team_input) &
        (queried_df["gamemode"] == gamemode_input) &
        (queried_df["map_name"] != "Overall") & 
        (queried_df["total"] != 0)
    ]

    # Create figure
    fig, ax = plt.subplots(figsize = (4, 2))

    # Create chart labels
    chart_labels = []
    for index, row in queried_df.iterrows():
        chart_labels.append(
            f"{row['map_name']}\n{row['win_percentage'] * 100:.0f}%"
        )

    # Pie Chart
    ax.pie(queried_df["total"], labels = chart_labels,
           labeldistance = 1.2, 
           colors = palettes[gamemode_input])
    
    # Create donut by adding white inner circle with smaller radius
    my_circle = plt.Circle( (0,0), 0.65, color = 'white')
    ax.add_artist(my_circle)
    
    # Margins
    plt.margins(0.05)


# Team Distribution of Series Differentials
def team_series_diffs(series_score_diffs_input: pd.DataFrame, 
                      team_input: str, team_color: str,):
    
    # Filter series_score_diffs by team
    queried_df = series_score_diffs_input[
        series_score_diffs_input["team"] == team_input
        ].copy()

    # Create figure
    fig, ax = plt.subplots(figsize = (4, 2))

    # Histogram
    sns.histplot(data = queried_df, x = "series_score_diff", 
                 discrete = True, color = team_color)

    # Styling
    ax.set_xlabel("Series Result")

    # Set margins
    plt.margins(0.05)


# Player Kills vs Time by Map & Mode
def player_kills_vs_time(        
        cdlDF_input: pd.DataFrame, player_input: str, team_color: str,
        gamemode_input: str, cur_line: float, map_input = "All"
):
    
    # Create a copy of cdlDF_input
    queried_df = cdlDF_input.copy()

    # If user selected all maps
    if map_input == "All":
        
        # Filter data based on user inputs
        queried_df = queried_df[
            (queried_df["player"] == player_input) &
            (queried_df["gamemode"] == gamemode_input)
            ]

    # If user selected only one map
    else:
        
        # Filter data based on user inputs, including map
        queried_df = queried_df[
            (queried_df["player"] == player_input) &
            (queried_df["gamemode"] == gamemode_input) & 
            (queried_df["map_name"] == map_input)
            ]
        
    # Set match_date column to dt.date type
    queried_df.loc[:, 'match_date'] = pd.to_datetime(queried_df['match_date']).dt.date
    
    # Create figure with gridspec
    f, axs = plt.subplots(1, 2, figsize = (6, 3), sharey = True, gridspec_kw = 
                          dict(width_ratios=[2, 0.4], wspace = 0.05))

    # Scatterplot
    sns.scatterplot(queried_df, x = "match_date", y = "kills", ax=axs[0], 
                    color = team_color)
    axs[0].axhline(y = cur_line, color = prizepicks_color, linestyle = '--')

    # Boxplot
    sns.boxplot(queried_df, y =  "kills", fill = False, ax=axs[1], 
                color = team_color, showfliers = False)
    sns.stripplot(queried_df, y = "kills", jitter = 0.05, ax=axs[1], color = team_color)
    axs[1].axhline(y = cur_line, color = prizepicks_color, linestyle = '--')

    # Add title
    axs[0].set_title(player_input, fontsize = 20, loc = "left", 
                     family = "Segoe UI", fontweight = 400, 
                     color = "#495057", pad = 5)

    # X- & Y-Axis Labels
    axs[0].set_xlabel("")
    axs[0].set_ylabel("Kills")
    axs[1].set_xticks([])
    axs[1].set_ylabel("")

    # Date Ticks
    formatter = mdates.DateFormatter('%b %d')
    axs[0].xaxis.set_major_formatter(formatter)
    axs[0].tick_params(axis = 'x', rotation = 30)

    # Scale X & Y Axes & get ranges
    min_x, min_y, max_x, max_y = \
        scale_fig(queried_df, axs[0], "time", gamemode_input, cur_line)

    # Label current line from PrizePicks
    plt.sca(axs[0])
    bbox = {'facecolor': prizepicks_color, 'alpha': 0.5, 
            'pad': 0.4, 'boxstyle': 'round'}
    if max_y - min_y <= 5:
        y_pad = 0.25
    elif max_y - min_y < 8:
        y_pad = 0.5
    else:
        y_pad = 1
    if max_y - cur_line <= 0.5:
        y_pad = y_pad * -1
    if max_x - min_x == dt.timedelta(days = 6):
        min_x = min_x + dt.timedelta(days = 1)
    plt.text(min_x, cur_line + y_pad, "Line: " + str(cur_line), bbox = bbox, color = "white")

    # Set margins
    plt.margins(0.05)
    

# Player Kills vs Score Differential by Map & Mode
def player_kills_vs_score_diff(
        cdlDF_input: pd.DataFrame, player_input: str, team_color: str,
        gamemode_input: str, cur_line: float, map_input = "All"
):
    
    # Create a copy of cdlDF_input
    queried_df = cdlDF_input.copy()

    # If user selected all maps
    if map_input == "All":
        
        # Filter data based on user inputs
        queried_df = queried_df[
            (queried_df["player"] == player_input) &
            (queried_df["gamemode"] == gamemode_input)
            ]

    # If user selected only one map
    else:
        
        # Filter data based on user inputs, including map
        queried_df = queried_df[
            (queried_df["player"] == player_input) &
            (queried_df["gamemode"] == gamemode_input) & 
            (queried_df["map_name"] == map_input)
            ]
        
    # Create figure with gridspec
    f, axs = plt.subplots(1, 2, figsize = (6, 3), gridspec_kw = dict(width_ratios=[2, 0.4], wspace = 0.05), sharey = True)

    # Scatterplot
    sns.scatterplot(queried_df, x = "score_diff", y = "kills", ax=axs[0], 
                    color = team_color)
    sns.regplot(queried_df, x = "score_diff", y = "kills", lowess = True, ax=axs[0], 
                color = team_color)
    axs[0].axhline(y = cur_line, color = prizepicks_color, linestyle = '--')
    # axs[0].axvline(x = 0, color = "orange", linestyle = '--')

    # Boxplot
    sns.boxplot(queried_df, y =  "kills", fill = False, ax=axs[1], 
                color = team_color, showfliers = False)
    sns.stripplot(queried_df, y = "kills", jitter = 0.05, ax=axs[1], 
                  color = team_color)
    axs[1].axhline(y = cur_line, color = prizepicks_color, linestyle = '--')

    # Add title
    axs[0].set_title(player_input, fontsize = 20, loc = "left", 
                    family = "Segoe UI", fontweight = 400, 
                    color = "#495057", pad = 5)

    # X- & Y-Axis Labels
    axs[0].set_xlabel("")
    axs[0].set_ylabel("Kills")
    axs[1].set_xticks([])
    axs[1].set_ylabel("")

    # Scale X & Y Axes & get ranges
    min_x, min_y, max_x, max_y = \
        scale_fig(queried_df, axs[0], "score_diff", gamemode_input, cur_line)

    # Label current line from PrizePicks if queried_df is not empty
    plt.sca(axs[0])
    bbox = {'facecolor': prizepicks_color, 'alpha': 0.5, 
            'pad': 0.4, 'boxstyle': 'round'}
    if max_y - min_y <= 5:
        y_pad = 0.25
    elif max_y - min_y < 8:
        y_pad = 0.5
    else:
        y_pad = 1
    if max_y - cur_line <= 0.5:
        y_pad = y_pad * -1
    plt.text(min_x, cur_line + y_pad, "Line: " + str(cur_line), bbox = bbox, color = "white")

    # Set margins
    plt.margins(0.05)