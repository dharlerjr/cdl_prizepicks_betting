
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
    "Search & Destroy": (-9, 6), 
    "Control": (-5, 3)
}

# Dictionary of min_x values for score diff ridgeline plot
min_x_values_by_gamemode = {
    "Hardpoint": -345, 
    "Search & Destroy": -10.75, 
    "Control": -6
}

# Dictionary of xticks for ridgeline plot by gamemode
gamemode_xticks = {
    "Hardpoint": [-200, -100, 0, 100, 200], 
    "Search & Destroy": [-6, -3, 0, 3, 6], 
    "Control": [-3, 0, 3]
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


# Team Distribution of Score Differentials by Map & Mode
def team_score_diffs(
        cdlDF_input: pd.DataFrame, team_input: str, team_color: str,
        gamemode_input: str, map_input = "All"
):
    
    # If user selected all maps    
    if map_input == "All":
    
        # Filter data based on user inputs
        queried_df = cdlDF_input[
            (cdlDF_input['gamemode'] == gamemode_input) &
            (cdlDF_input['team'] == team_input)
            ][['match_id', 'map_name', 'score_diff']].drop_duplicates()
    
    # User selected only one map 
    else:

        # Filter data based on user inputs, including map
        queried_df = cdlDF_input[
            (cdlDF_input['gamemode'] == gamemode_input) &
            (cdlDF_input['team'] == team_input) &
            (cdlDF_input["map_name"] == map_input)
            ][['match_id', 'map_name', 'score_diff']].drop_duplicates()
        

    # Create the figure
    fig, ax = plt.subplots()

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
    ax.set_xlabel("")
    ax.set_ylabel("")

    # Set ticks for Search & Destroy
    if gamemode_input == "Search & Destroy":
        plt.xticks([-6, -3, 0, 3, 6])


# Team % of Maps Played by Mode
def team_percent_maps_played(
        team_summaries_input: pd.DataFrame, team_input: str,
        gamemode_input: str
):

    # Filter team_summaries_input by team & mode
    queried_df = team_summaries_input[
        (team_summaries_input["team"] == team_input) &
        (team_summaries_input["gamemode"] == gamemode_input) &
        (team_summaries_input["map_name"] != "Overall") & 
        (team_summaries_input["total"] != 0)
    ]

    # Create figure
    fig, ax = plt.subplots()

    # Create chart labels
    total = queried_df['total'].sum()
    chart_labels = []
    for index, row in queried_df.iterrows():
        chart_labels.append(
            f"{row['map_name']}\n{row['total'] * 100 / total:.0f}%"
        )

    # Pie Chart
    ax.pie(queried_df["total"], labels = chart_labels,
           labeldistance = 1.25, colors = palettes[gamemode_input], 
           textprops = dict(family = "Segoe UI"))
    
    # Create donut by adding white inner circle with smaller radius
    my_circle = plt.Circle( (0,0), 0.65, color = 'white')
    ax.add_artist(my_circle)
    
    # Margins
    plt.margins(0.05)


# Team Distribution of Series Differentials
def team_series_diffs(series_score_diffs_input: pd.DataFrame, 
                      team_input: str, team_color: str):
    
    # Filter series_score_diffs by team
    queried_df = series_score_diffs_input[
        series_score_diffs_input["team"] == team_input
    ]

    # Create figure
    fig, ax = plt.subplots()

    # Bar chart
    sns.histplot(data = queried_df, x = "series_score_diff", 
                 discrete = True, color = team_color)

    # Styling
    ax.set_xlabel("")
    ax.set_ylabel("")

    # Set margins
    plt.margins(0.05)


# Player Kills vs Time by Map & Mode
def player_kills_vs_time(        
        cdlDF_input: pd.DataFrame, player_input: str, team_color: str,
        gamemode_input: str, cur_line: float, map_input = "All"
):
    
    # Set seaborn theme
    sns.set_theme(style = "darkgrid")

    # If user selected all maps
    if map_input == "All":
        
        # Filter data based on user inputs
        queried_df = cdlDF_input[
            (cdlDF_input["player"] == player_input) &
            (cdlDF_input["gamemode"] == gamemode_input)
            ]

    # If user selected only one map
    else:
        
        # Filter data based on user inputs, including map
        queried_df = cdlDF_input[
            (cdlDF_input["player"] == player_input) &
            (cdlDF_input["gamemode"] == gamemode_input) & 
            (cdlDF_input["map_name"] == map_input)
            ]
    
    # Create figure with gridspec
    f, axs = plt.subplots(1, 2, sharey = True, gridspec_kw = 
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

    # X- & Y-Axis Labels
    axs[0].set_ylabel("Kills", family = "Segoe UI")
    axs[1].set_ylabel("")
    axs[1].set_xticks([])

    # Date Ticks
    formatter = mdates.DateFormatter('%b %d')
    axs[0].xaxis.set_major_formatter(formatter)

    # Scale and style
    min_x = scale_time_axis(queried_df, axs[0])
    y_pad = scale_kills_axis(queried_df, axs[0], cur_line)
    style_player_plot(axs[0], min_x, y_pad, player_input, cur_line)
    

# Player Kills vs Score Differential by Map & Mode
def player_kills_vs_score_diff(
        cdlDF_input: pd.DataFrame, player_input: str, team_color: str,
        gamemode_input: str, cur_line: float, map_input = "All"
):
    
    # Set seaborn theme
    sns.set_theme(style = "darkgrid")

    # If user selected all maps
    if map_input == "All":
        
        # Filter data based on user inputs
        queried_df = cdlDF_input[
            (cdlDF_input["player"] == player_input) &
            (cdlDF_input["gamemode"] == gamemode_input)
            ]

    # If user selected only one map
    else:
        
        # Filter data based on user inputs, including map
        queried_df = cdlDF_input[
            (cdlDF_input["player"] == player_input) &
            (cdlDF_input["gamemode"] == gamemode_input) & 
            (cdlDF_input["map_name"] == map_input)
            ]
        
    # Create figure with gridspec
    f, axs = plt.subplots(1, 2, gridspec_kw = dict(width_ratios=[2, 0.4], wspace = 0.05), sharey = True)

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

    # X- & Y-Axis Label
    axs[0].set_ylabel("Kills", family = "Segoe UI")
    axs[1].set_ylabel("")
    axs[1].set_xticks([])

    # Scale and style
    min_x = scale_score_diff_axis(queried_df, axs[0], gamemode_input)
    y_pad = scale_kills_axis(queried_df, axs[0], cur_line)
    style_player_plot(axs[0], min_x, y_pad, player_input, cur_line)


# Player Maps 1 - 3 Kills vs Time
def player_1_thru_3_kills_vs_time(
        map_1_thru_3_totals_df_input: pd.DataFrame, player_input: str, 
        team_color: str, cur_line: float
):
    
    # Set seaborn theme
    sns.set_theme(style = "darkgrid")
    
    # Filter data for selected player
    queried_df = map_1_thru_3_totals_df_input[(map_1_thru_3_totals_df_input["player"] == player_input)]

    # Convert match_date column to dt.datetime

    # Create figure with gridspec
    f, axs = plt.subplots(1, 2, sharey = True, gridspec_kw = 
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

    # X- & Y-Axis Labels
    axs[1].set_ylabel("Maps 1 - 3 Kills", labelpad = 6, family = "Segoe UI")
    axs[1].set_xticks([])
    axs[1].set_ylabel("")

    # Date Ticks
    formatter = mdates.DateFormatter('%b %d')
    axs[0].xaxis.set_major_formatter(formatter)

    # Scale and style
    min_x = scale_time_axis(queried_df, axs[0])
    y_pad = scale_kills_axis(queried_df, axs[0], cur_line)
    style_player_plot(axs[0], min_x, y_pad, player_input, cur_line)


# Player Kills by Map & Mode
def player_kills_by_map(
        cdlDF_input: pd.DataFrame, player_input: str, 
        gamemode_input: str, cur_line: float):
    
    # Set seaborn theme
    sns.set_theme(style = "darkgrid")
    
    # Filter data & sort by map name
    queried_df = cdlDF_input[
        (cdlDF_input["player"] == player_input) &
        (cdlDF_input["gamemode"] == gamemode_input)] \
        .sort_values("map_name")

    # Create figure with gridspec
    f, ax = plt.subplots()

    # Boxplots
    sns.boxplot(queried_df, x = "map_name", y =  "kills", 
                hue = "map_name", showfliers = False, fill = False,
                palette = palettes[gamemode_input])
    sns.stripplot(queried_df, x = "map_name", y =  "kills", 
                  hue = "map_name", jitter = 0.05, 
                  palette = palettes[gamemode_input])
    ax.axhline(y = cur_line, color = prizepicks_color, linestyle = '--')

    # Y-Axis Label
    ax.set_ylabel("Kills", family = "Segoe UI")

    # Scale and style
    min_x = ax.get_xlim()[0] + ((ax.get_xlim()[1] - ax.get_xlim()[0]) * 0.02)
    y_pad = scale_kills_axis(queried_df, ax, cur_line)
    style_player_plot(ax, min_x, y_pad, player_input, cur_line)
    
    
# Player Kills by Mapset
def player_kills_by_mapset(
        cdlDF_input: pd.DataFrame, player_input: str, 
        map_1_input = "All", map_2_input = "All", map_3_input = "All"):
    
    # Set seaborn theme
    sns.set_theme(style = "darkgrid")

    # Get map lists for filtering
    if map_1_input == "All":
        hp_maps = ["All", "6 Star", "Highrise", "Invasion", "Karachi", "Rio"]
    else:
        hp_maps = [map_1_input]

    if map_2_input == "All":
        snd_maps = ["6 Star", "Highrise", "Invasion", "Karachi", "Rio"]
    else:
        snd_maps = [map_2_input]

    if map_3_input == "All":
        ctrl_maps = ["Highrise", "Invasion", "Karachi"]
    else:
        ctrl_maps = [map_3_input]

    
    # Query cdlDF_input
    queried_df = cdlDF_input[
        (((cdlDF_input['gamemode'] == 'Hardpoint') &  (cdlDF_input['map_name'].isin(hp_maps))) |
        ((cdlDF_input['gamemode'] == 'Search & Destroy') &  (cdlDF_input['map_name'].isin(snd_maps))) |
        ((cdlDF_input['gamemode'] == 'Control') &  (cdlDF_input['map_name'].isin(ctrl_maps)))) &
        (cdlDF_input['player'] == player_input)
    ].sort_values('map_name', ignore_index = True)

    # Create figure
    fig, ax = plt.subplots()

    # Boxplots
    sns.boxplot(queried_df, x = 'gamemode', y = 'kills', showfliers = False,
                fill = False, hue = 'gamemode',
                palette = palettes["Control"])
    sns.stripplot(queried_df, x = "gamemode", y =  "kills", 
                  hue = "gamemode", jitter = 0.05, 
                  palette = palettes["Control"])
    
    # Get X Tick Labels
    label_1 = f'{map_1_input} HP' if map_1_input != "All" else "Hardpoint"
    label_2 = f'{map_2_input} SnD' if map_2_input != "All" else "Search & Destroy"
    label_3 = f'{map_3_input} Ctrl' if map_3_input != "All" else "Control"

    # X Ticks & Y-Axis Label
    ax.set_xticks(ticks = ['Hardpoint', 'Search & Destroy', 'Control'],
                  labels = [label_1, label_2, label_3])
    ax.set_ylabel("Kills", family = "Segoe UI")

    # Scale and style
    y_pad = scale_kills_axis(queried_df, ax, 0)
    style_player_plot(ax, 0, y_pad, player_input, 0)
    
    
# Ridgeline Plot of Team Score Diffs
def score_diffs_ridge(        
        cdlDF_input: pd.DataFrame, team_icon_x: str, team_icon_y: str,
        x_color: str, y_color: str, gamemode_input: str, map_input = "All"
):
    
    # Set seaborn theme
    sns.set_theme(style="white", rc={"axes.facecolor": (0, 0, 0, 0)})

    # If user selected all maps    
    if map_input == "All":

        # Query data
        queried_df = cdlDF_input[
            ((cdlDF_input['team_icon'] == team_icon_x) | (cdlDF_input['team_icon'] == team_icon_y)) &
            (cdlDF_input['gamemode'] == gamemode_input)
        ][['match_id', 'team_icon', 'map_name', 'score_diff']].drop_duplicates()


    # User selected only one map
    else:

        # Query data
        queried_df = cdlDF_input[
            ((cdlDF_input['team_icon'] == team_icon_x) | (cdlDF_input['team_icon'] == team_icon_y)) &
            (cdlDF_input['gamemode'] == gamemode_input) &
            (cdlDF_input['map_name'] == map_input)
        ][['match_id', 'team_icon', 'map_name', 'score_diff']].drop_duplicates()

    # Reorder team factor levels for graphing
    queried_df['team_icon'] = pd.Categorical(
        queried_df['team_icon'], 
        categories = [team_icon_x, team_icon_y]
        )

    # Initialize the FacetGrid object
    g = sns.FacetGrid(queried_df, row = "team_icon", hue = "team_icon", 
                      aspect = 3.4, height = 2.2, palette = [x_color, y_color])
    
    # Histogram for Hardpoint
    if gamemode_input == "Hardpoint":

        # Plot the histogram
        g.map_dataframe(sns.histplot, x = "score_diff", binwidth = 50, 
                        binrange = (-300, 250), alpha = 0.9)
        
        # Get max y
        queried_df['bin'] = pd.cut(queried_df['score_diff'], bins = range(-250, 300, 50))
        max_y = max(queried_df[['bin', "team_icon"]].value_counts())
        
    # Bar chart for SnD & Control
    else:

        # Plot the bar chart
        g.map_dataframe(sns.histplot, x = "score_diff", discrete = True, 
                        binrange = gamemode_bin_ranges[gamemode_input], 
                        alpha = 0.9)
        
        # Get max y
        max_y = 0 if queried_df.empty else max(queried_df[["score_diff", "team_icon"]].value_counts())
        
    # Add a horizontal line to the bottom of each plot
    g.map(plt.axhline, y = 0, lw = 2, clip_on = False)

    # Get teams for labeling
    teams = [team_icon_x, team_icon_y]

    # Use min_x value for labels
    min_x = min_x_values_by_gamemode[gamemode_input]

    # Add team name to each axs and change font
    for i, ax in enumerate(g.axes.flat):
        ax.text(min_x, max_y * 0.05, teams[i], family = "Segoe UI", 
                fontweight ='bold', fontsize = 15, 
                color = ax.lines[-1].get_color())
        
    # Overlap subplots
    g.figure.subplots_adjust(hspace = -0.4)

    # Styling
    g.set_titles("")
    g.set(yticks = [], ylabel = "", xlabel = "", 
          xticks = gamemode_xticks[gamemode_input])
    g.despine(bottom = True, left = True)
    g.tick_params(labelfontfamily = "Segoe UI")


# Ridgeline Plot of Team Series Diffs
def series_diff_ridge(
        series_score_diffs_input: pd.DataFrame, 
        team_icon_x: str, team_icon_y: str,
        x_color: str, y_color: str
):

    # Filter series_score_diffs by team
    queried_df = series_score_diffs_input[
        (series_score_diffs_input["team_icon"] == team_icon_x) |
        (series_score_diffs_input["team_icon"] == team_icon_y)
    ].copy()

    # Reorder team factor levels for graphing
    queried_df['team_icon'] = pd.Categorical(
        queried_df['team_icon'], 
        categories = [team_icon_x, team_icon_y]
        )
    
    # Set seaborn theme
    sns.set_theme(style="white", rc={"axes.facecolor": (0, 0, 0, 0)})

    # Initialize the FacetGrid object
    g = sns.FacetGrid(queried_df, row = "team_icon", hue = "team_icon", 
                      aspect = 3.4, height = 2.2, palette = [x_color, y_color])
    
    # Plot the bar chart
    g.map_dataframe(sns.histplot, x = "series_score_diff", discrete = True, 
                    binrange = (-5, 3), alpha = 0.9)
    
    # Add a horizontal line to the bottom of each plot
    g.map(plt.axhline, y = 0, lw = 2, clip_on = False)

    # Get teams for labeling
    teams = [team_icon_x, team_icon_y]

    # Get min_x
    if team_icon_x == "TOR" or team_icon_y == "TOR":
        min_x = -6.75
    else:
        min_x = -6

    # Add team name to each axs
    for i, ax in enumerate(g.axes.flat):
        ax.text(min_x, 0.45, teams[i], family = "Segoe UI", 
                fontweight ='bold', fontsize = 15,
                color = ax.lines[-1].get_color())
        
    # Overlap subplots
    g.figure.subplots_adjust(hspace = -0.4)

    # Styling
    g.set_titles("")
    g.set(xticks = [-3, 0, 3], yticks = [], ylabel = "", xlabel = "")
    g.despine(bottom = True, left = True)
    g.tick_params(labelfontfamily = "Segoe UI")


# Helper function to scale time axis of player plots
def scale_time_axis(queried_df: pd.DataFrame, ax: plt.axes):
        
    # Set & Scale X-Axis, if necessary
    match_dates = queried_df["match_date"].to_list()
    if match_dates:
        min_x = min(match_dates)
        max_x = max(match_dates)
    else:
        min_x = dt.date.today()
        max_x = dt.date.today()
    x_range = max_x - min_x

    # Case 1: x_range < 6 days
    if max_x - min_x < dt.timedelta(days = 6):
        min_x = min_x - dt.timedelta(days = math.ceil((6 - x_range.days) / 2))
        max_x = max_x + dt.timedelta(days = math.floor((6 - x_range.days) / 2))
        ax.set_xlim(min_x, max_x)
        # Add 6 hours to min_x for labeling purposes
        min_x += dt.timedelta(hours = 6)

    # Case 2: x_range <= 2 weeks
    elif x_range <= dt.timedelta(days = 14):
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday = (mdates.TU, mdates.SA)))
    
    # Case 3: x_range <= 1 month
    elif x_range <= dt.timedelta(days = 31):
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday = mdates.SA))

    # Case 4: x_range <= 2 months
    elif x_range <= dt.timedelta(days = 64):
        ax.xaxis.set_major_locator(mdates.DayLocator(bymonthday = [1, 15]))

    # Return min_x for PrizePicks line label
    return min_x


# Helper function to scale score_diff axis of player plots
def scale_score_diff_axis(queried_df: pd.DataFrame, ax: plt.axes, gamemode_input: str):
    
    # Get min_x and x_range
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
        min_x = math.floor(min_x / 10) * 10
        max_x = math.ceil(max_x / 10) * 10
        min_x, max_x = adjust_score_diff_ticks(gamemode_input, min_x, max_x)
        ax.set_xlim(min_x - 5, max_x + 5)

    # Case 2: Search & Destroy & Control: need to add more ticks
    elif gamemode_input != "Hardpoint" and max_x - min_x < 4:
        min_x, max_x = adjust_score_diff_ticks(gamemode_input, min_x, max_x)
        ax.set_xlim(min_x - 0.25, max_x + 0.25)
        ax.xaxis.set_major_locator(MultipleLocator(base = 1))

    # Case 3: Search & Destroy & Control, Set Major Locator only
    elif gamemode_input != "Hardpoint" and max_x - min_x == 4:
        ax.xaxis.set_major_locator(MultipleLocator(base = 1))

    # Return min_x to label PrizePicks line
    return min_x


# Helper function to scale kills axis of player plots
def scale_kills_axis(queried_df: pd.DataFrame, ax: plt.axes, cur_line: float):
    
    # Get y_range and y_pad for cur_line
    kills = queried_df["kills"].to_list()
    if cur_line != 0:
        kills.append(cur_line)
    min_y = min(kills) if kills else 5
    max_y = max(kills) if kills else 10
    y_range = max_y - min_y
        
    # Scaling
    if y_range <= 1:
        min_y -= 2.5
        max_y += 2.5
        ax.set_ylim(min_y, max_y)
        ax.yaxis.set_major_locator(MultipleLocator(base = 1))
    elif y_range < 4:
        min_y -= 1.5
        max_y += 1.5
        ax.set_ylim(min_y, max_y)
        ax.yaxis.set_major_locator(MultipleLocator(base = 1))
    elif y_range == 4:
        min_y -= 0.5
        max_y += 0.5
        ax.set_ylim(min_y, max_y)
        ax.yaxis.set_major_locator(MultipleLocator(base = 1))
    elif y_range < 16:
        ax.yaxis.set_major_locator(MultipleLocator(base = 2))
    elif y_range < 25:
        ax.yaxis.set_major_locator(MultipleLocator(base = 4))
    elif y_range < 32:
        ax.yaxis.set_major_locator(MultipleLocator(base = 5))
    else:
        ax.yaxis.set_major_locator(MultipleLocator(base = 10))

    # Get y_pad for style_player_plot
    y_pad = (max_y - min_y) * 0.05

    # Make y_pad negative if cur_line is close to the max y-limit
    if (max_y - (cur_line + y_pad)) / (max_y - min_y) < 0.15:
        y_pad = -1.2 * y_pad

    # Return y_pad
    return y_pad


# Helper function to style player plots
def style_player_plot(
        ax: plt.axes, min_x: float, y_pad: float,
        player_input: str, cur_line: float
        ):
    
    # Add title
    ax.set_title(player_input, fontsize = 20, loc = "left", 
                 family = "Segoe UI", fontweight = 400, 
                 color = "#495057", pad = 5)
    
    # Styling
    ax.set_xlabel("")
    ax.tick_params(labelfontfamily = "Segoe UI")

    # Label current line from PrizePicks
    if cur_line != 0:
        plt.sca(ax)
        bbox = {'facecolor': prizepicks_color, 'alpha': 0.5, 
                'pad': 0.4, 'boxstyle': 'round'}
        plt.text(min_x, cur_line + y_pad, "Line: " + str(cur_line), bbox = bbox, color = "white")

    # Set margins
    plt.margins(0.05)


# Function to create bar chart of vetoes based on user inputs
def chart_vetoes(vetoes_input: pd.DataFrame, team_input: str, select_input: str, gamemode_input: str, team_color: str, stage_min = 1, stage_max = 4):

    # Set seaborn theme
    sns.set_theme(style="white", rc={"axes.facecolor": (0, 0, 0, 0)})

    # Query vetoes
    queried_df = vetoes_input[
        (vetoes_input["team"] == team_input) &
        (vetoes_input["select"] == select_input) &
        (vetoes_input["gamemode"] == gamemode_input) &
        ((vetoes_input["stage"] >= stage_min) &
        (vetoes_input["stage"] <= stage_max))
    ]

    # Create the figure
    fig, ax = plt.subplots()

    # Get order
    bar_order = queried_df.map_name.value_counts().to_frame() \
        .reset_index().sort_values(["count", "map_name"], ascending = [False, True]).map_name

    # Plot the bar chart
    sns.countplot(data = queried_df, y = "map_name", color = team_color, 
                    order = bar_order)

    # Add counts
    ax.bar_label(ax.containers[0], padding = 4, family = "Segoe UI")

    # Color bars
    total = queried_df["map_name"].value_counts().sum()
    threshold = 1 / len(queried_df["map_name"].value_counts())
    for i in range(len(ax.containers[0])):
        if ax.containers[0].datavalues[i] / total < threshold:
            ax.containers[0][i].set_color("#ced4da")
        
    # Styling
    plt.xticks([])
    plt.xlabel("")
    plt.ylabel("")
    plt.yticks(family = "Segoe UI")
    sns.despine(bottom = True, left = True)
    plt.margins(0.05)