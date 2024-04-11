
# Import ggplot
from plotnine import ggplot, aes, geom_histogram, geom_point, geom_jitter, geom_boxplot, geom_hline, geom_vline, \
    geom_smooth, facet_wrap, scale_color_manual, scale_fill_manual, scale_x_date, labs, xlab, ylab, element_text, \
     element_blank, theme

# Import setup
from setup.setup import load_and_clean_cdl_data

# Dictionary of color scales by gamemode 
gamemode_color_scales = {
  "Hardpoint": ["red", "orange", "green", "blue", "purple"],
  "Search & Destroy": ["red", "orange", "green", "blue", "purple"],
  "Control": ["red", "green", "blue"]
}

# Dictionary of colors by map & mode 
map_and_mode_colors = {
  "Hardpoint" : {
    "6 Star" : "red", 
    "Karachi" : "orange",
    "Rio" : "green",
    "Sub Base" : "blue",
    "Vista" : "purple"
  } ,
  "Search & Destroy" : {
    "6 Star" : "red", 
    "Highrise" : "orange",
    "Invasion" : "green", 
    "Karachi" : "blue",
    "Rio" : "purple"
  },
  "Control" : {
    "Highrise" : "red", 
    "Invasion" : "green", 
    "Karachi" : "blue"
  }
}

# Dictionary of viridis color scales by gamemode
viridis_gamemode_color_scales = {
  "Hardpoint":
    ["#FDE725FF", "#56c667ff", "#21908CFF", "#3B528BFF", "#440154FF"],
  "Search & Destroy":
    ["#FDE725FF", "#56c667ff", "#21908CFF", "#3B528BFF", "#440154FF"], 
  "Control": ["#FDE725FF", "#56c667ff", "#21908CFF"]
}

# Dictionary of viridis colors by map & mode
viridis_map_and_mode_colors = {
  "Hardpoint": {
    "6 Star" : "#FDE725FF", 
    "Karachi" : "#56c667ff",
    "Rio" : "#21908CFF",
    "Sub Base" : "#3B528BFF",
    "Vista" : "#440154FF"
  }, 
  "Search & Destroy": {
    "6 Star" : "#FDE725FF", 
    "Highrise" : "#56c667ff",
    "Invasion" : "#21908CFF", 
    "Karachi" : "#3B528BFF",
    "Rio" : "#440154FF"
  }, 
  "Control": {
    "Highrise" : "#FDE725FF", 
    "Invasion" : "#56c667ff", 
    "Karachi" : "#21908CFF"
  }
}

# Dictionary of binwidths by gamemode
gamemode_bins = {
  "Hardpoint": 50, 
  "Search & Destroy": 1, 
  "Control": 1
}

# Dictionary of ylims by gamemode 
gamemode_kill_lims = {
  "Hardpoint": [0, 45],
  "Search & Destroy": [0, 16],
  "Control": [0, 45]
}

# Dictionary of maps to filter out by gamemode 
maps_to_filter = {
    "Hardpoint": ["Invasion", "Skidrow", "Terminal"],
    "Search & Destroy": ["Skidrow", "Terminal"], 
    "Control": []
}

# Load in data
cdlDF = load_and_clean_cdl_data()
cdlDF

# Score Differentials by Map & Mode
def team_score_diffs(
        team_input: str, gamemode_input: str, map_input = "All"
):
    if map_input == "All":
        return(
            ggplot(
                cdlDF[(cdlDF["gamemode"] == gamemode_input) & \
                    ~(cdlDF["map_name"].isin(maps_to_filter[gamemode_input])) & \
                    (cdlDF["team"] == team_input)] \
                    [["match_id", "map_name", "score_diff"]].drop_duplicates(),
                aes(x = "score_diff", fill = "map_name")
            ) + \
                geom_histogram(binwidth = gamemode_bins[gamemode_input]) + \
                facet_wrap("~map_name") + \
                scale_fill_manual(values = viridis_gamemode_color_scales[gamemode_input]) + \
                labs(title = f"{team_input} Distribution of Score Differentials: {gamemode_input}", 
                    fill = "Map") + \
                xlab("Score Differential") + ylab("Count") + \
                theme(
                    plot_title = element_text(size = 14),
                    strip_text = element_text(size = 10), 
                    axis_title = element_text(size = 10), 
                    axis_text_x = element_text(size = 8, color = "#3b3b3b"), 
                    axis_text_y = element_text(size = 8, color = "#3b3b3b"), 
                    legend_position = "none", 
                )
        )
    else:
        return(
            ggplot(
                cdlDF[(cdlDF["gamemode"] == gamemode_input) & \
                    ~(cdlDF["map_name"].isin(maps_to_filter[gamemode_input])) & \
                    (cdlDF["team"] == team_input) & \
                    (cdlDF["map_name"] == map_input)] \
                    [["match_id", "map_name", "score_diff"]].drop_duplicates(),
                aes(x = "score_diff", fill = "map_name")
            ) + \
                geom_histogram(binwidth = gamemode_bins[gamemode_input]) + \
                scale_fill_manual(values = viridis_map_and_mode_colors[gamemode_input][map_input]) + \
                labs(title = f"{team_input} Distribution of Score Differentials: {map_input} {gamemode_input}", 
                    fill = "Map") + \
                xlab("Score Differential") + ylab("Count") + \
                theme(
                    plot_title = element_text(size = 14),
                    strip_text = element_text(size = 10), 
                    axis_title = element_text(size = 10), 
                    axis_text_x = element_text(size = 8, color = "#3b3b3b"), 
                    axis_text_y = element_text(size = 8, color = "#3b3b3b"), 
                    legend_position = "none", 
                )
        )

# Player Kills Overview
def player_kills_overview(
        player_input: str, gamemode_input: str, cur_line: float, map_input = "All"
):
    if map_input == "All":
        return(
            ggplot(
                cdlDF[(cdlDF["gamemode"] == gamemode_input) & \
                    ~(cdlDF["map_name"].isin(maps_to_filter[gamemode_input])) & \
                    (cdlDF["player"] == player_input)],
                aes(y = "kills")
            ) + \
                geom_jitter(
                    aes(x = "dummy_x", color = "map_name"), size = 2, width = 0.05, height = 0.05, 
                ) + \
                geom_boxplot(alpha = 0.5, outlier_alpha = 0) + \
                geom_hline(yintercept = cur_line, linetype = "dashed", color = 'purple') + \
                scale_color_manual(values = gamemode_color_scales[gamemode_input]) + \
                labs(title = f"{player_input} {gamemode_input} Kills",
                    color = "Map") + \
                xlab("") + ylab("Kills") + \
                theme(
                    plot_title = element_text(size = 14),
                    axis_title = element_text(size = 10), 
                    axis_text_x = element_blank(), 
                    axis_ticks = element_blank(), 
                    axis_text_y = element_text(size = 8, color = "#3b3b3b"), 
                    legend_title = element_text(size = 10), 
                    legend_text = element_text(size = 8)
                )
        )
    else:
        return(
            ggplot(
                cdlDF[(cdlDF["gamemode"] == gamemode_input) & \
                    ~(cdlDF["map_name"].isin(maps_to_filter[gamemode_input])) & \
                    (cdlDF["player"] == player_input) & \
                    (cdlDF["map_name"] == map_input)],
                aes(y = "kills")
            ) + \
                geom_jitter(
                    aes(x = "dummy_x", color = "map_wl"), size = 2, width = 0.05, height = 0.05, 
                ) + \
                geom_boxplot(alpha = 0.5, outlier_alpha = 0) + \
                geom_hline(yintercept = cur_line, linetype = "dashed", color = 'purple') + \
                scale_color_manual(values = ["blue", "red"]) + \
                labs(title = f"{player_input} Kills on {map_input} {gamemode_input}",
                    color = "W/L") + \
                xlab("") + ylab("Kills") + \
                theme(
                    plot_title = element_text(size = 14),
                    axis_title = element_text(size = 10), 
                    axis_text_x = element_blank(), 
                    axis_ticks = element_blank(), 
                    axis_text_y = element_text(size = 8, color = "#3b3b3b"), 
                    legend_title = element_text(size = 10), 
                    legend_text = element_text(size = 8)
                )
        )

# Player Kills vs. Time
def player_kills_vs_time(
        player_input: str, gamemode_input: str, cur_line: float, map_input = "All"
):
    if map_input == "All":
        return(
            ggplot(
                cdlDF[(cdlDF["gamemode"] == gamemode_input) & \
                    ~(cdlDF["map_name"].isin(maps_to_filter[gamemode_input])) & \
                    (cdlDF["player"] == player_input)],
                aes(x = "match_date", y = "kills", color = "map_name")
            ) + \
                geom_point(size = 2) + \
                geom_hline(yintercept = cur_line, color = "purple", linetype = "dashed") + \
                scale_color_manual(values = gamemode_color_scales[gamemode_input]) + \
                scale_x_date(date_breaks = "1 month", date_labels = "%b %Y") + \
                labs(title = f"{player_input} {gamemode_input} Kills colored by Map",
                    color = "Map") + \
                xlab("Date") + ylab("Kills") + \
                theme(
                    plot_title = element_text(size = 14),
                    axis_title = element_text(size = 10), 
                    axis_text_x = element_text(size = 8, color = "#3b3b3b"), 
                    axis_text_y = element_text(size = 8, color = "#3b3b3b"), 
                    legend_title = element_text(size = 10), 
                    legend_text = element_text(size = 8)
                )
        )
    else:
        return(
            ggplot(
                cdlDF[(cdlDF["gamemode"] == gamemode_input) & \
                    ~(cdlDF["map_name"].isin(maps_to_filter[gamemode_input])) & \
                    (cdlDF["player"] == player_input) & \
                    (cdlDF["map_name"] == map_input)],
                aes(x = "match_date", y = "kills", color = "map_wl")
            ) + \
                geom_point(size = 2) + \
                geom_hline(yintercept = cur_line, color = "purple", linetype = "dashed") + \
                scale_color_manual(values = ["blue", "red"]) + \
                scale_x_date(date_breaks = "1 month", date_labels = "%b %Y") + \
                labs(title = f"{player_input} Kills on {map_input} {gamemode_input}",
                    color = "W/L") + \
                xlab("Date") + ylab("Kills") + \
                theme(
                    plot_title = element_text(size = 14),
                    axis_title = element_text(size = 10), 
                    axis_text_x = element_text(size = 8, color = "#3b3b3b"), 
                    axis_text_y = element_text(size = 8, color = "#3b3b3b"), 
                    legend_title = element_text(size = 10), 
                    legend_text = element_text(size = 8)
                )
        )

# Player Kills vs Total Score
def player_kills_vs_total(
        player_input: str, gamemode_input: str, cur_line: float, map_input = "All"
):
    if map_input == "All":
        return(
            ggplot(
                cdlDF[(cdlDF["gamemode"] == gamemode_input) & \
                    ~(cdlDF["map_name"].isin(maps_to_filter[gamemode_input])) & \
                    (cdlDF["player"] == player_input)],
                aes(x = "total_score", y = "kills", color = "map_wl")
            ) + \
                geom_point(size = 2) + \
                geom_smooth(method = "lowess") + \
                geom_hline(yintercept = cur_line, color = "purple", linetype = "dashed") + \
                scale_color_manual(values = ["blue", "red"]) + \
                labs(title = f"{player_input} Kills vs Total Score: {gamemode_input}", 
                    color = "W/L") + \
                xlab("Total Score") + ylab("Kills") + \
                theme(
                    plot_title = element_text(size = 14),
                    axis_title = element_text(size = 10), 
                    axis_text_x = element_text(size = 8, color = "#3b3b3b"), 
                    axis_text_y = element_text(size = 8, color = "#3b3b3b"), 
                    legend_title = element_text(size = 10), 
                    legend_text = element_text(size = 8)
                )
        )
    else:
        return(
            ggplot(
                cdlDF[(cdlDF["gamemode"] == gamemode_input) & \
                    ~(cdlDF["map_name"].isin(maps_to_filter[gamemode_input])) & \
                    (cdlDF["player"] == player_input) & 
                    (cdlDF["map_name"] == map_input)],
                aes(x = "total_score", y = "kills", color = "map_wl")
            ) + \
                geom_point(size = 2) + \
                geom_smooth(method = "lowess") + \
                geom_hline(yintercept = cur_line, color = "purple", linetype = "dashed") + \
                scale_color_manual(values = ["blue", "red"]) + \
                labs(title = f"{player_input} Kills vs Total Score: {map_input} {gamemode_input}", 
                    color = "W/L") + \
                xlab("Total Score") + ylab("Kills") + \
                theme(
                    plot_title = element_text(size = 14),
                    axis_title = element_text(size = 10), 
                    axis_text_x = element_text(size = 8, color = "#3b3b3b"), 
                    axis_text_y = element_text(size = 8, color = "#3b3b3b"), 
                    legend_title = element_text(size = 10), 
                    legend_text = element_text(size = 8)
                )
        )

# Player Kills vs Score Diff
def player_kills_vs_score_diff(
        player_input: str, gamemode_input: str, cur_line: float, map_input = "All"
):
    if map_input == "All":
        return(
            ggplot(
                cdlDF[(cdlDF["gamemode"] == gamemode_input) & \
                    ~(cdlDF["map_name"].isin(maps_to_filter[gamemode_input])) & \
                    (cdlDF["player"] == player_input)],
                aes(x = "score_diff", y = "kills")
            ) + \
                geom_point(aes(color = "map_name"), size = 2, alpha = 1) + \
                geom_smooth(method = "lowess", color = "dodgerblue") + \
                geom_vline(xintercept = 0, color = "orange", linetype = "dashed") + \
                geom_hline(yintercept = cur_line, color = "purple", linetype = "dashed") + \
                scale_color_manual(values = gamemode_color_scales[gamemode_input]) + \
                labs(title = f"{player_input} Kills vs Score Differential: {gamemode_input}", 
                    color = "Map") + \
                xlab("Score Differential") + ylab("Kills") + \
                theme(
                    plot_title = element_text(size = 14),
                    axis_title = element_text(size = 10), 
                    axis_text_x = element_text(size = 8, color = "#3b3b3b"), 
                    axis_text_y = element_text(size = 8, color = "#3b3b3b"), 
                    legend_title = element_text(size = 10), 
                    legend_text = element_text(size = 8)
                )
        )
    else:
        return(
            ggplot(
                cdlDF[(cdlDF["gamemode"] == gamemode_input) & \
                    ~(cdlDF["map_name"].isin(maps_to_filter[gamemode_input])) & \
                    (cdlDF["player"] == player_input) & \
                    (cdlDF["map_name"] == map_input)],
                aes(x = "score_diff", y = "kills", color = "map_name")
            ) + \
                geom_point(size = 2, alpha = 1) + \
                geom_smooth(method = "lowess", color = "dodgerblue") + \
                geom_vline(xintercept = 0, color = "orange", linetype = "dashed") + \
                geom_hline(yintercept = cur_line, color = "purple", linetype = "dashed") + \
                scale_color_manual(values = map_and_mode_colors[gamemode_input][map_input]) + \
                labs(title = f"{player_input} Kills vs Score Differential: {map_input} {gamemode_input}", 
                    color = "Map") + \
                xlab("Score Differential") + ylab("Kills") + \
                theme(
                    plot_title = element_text(size = 14),
                    axis_title = element_text(size = 10), 
                    axis_text_x = element_text(size = 8, color = "#3b3b3b"), 
                    axis_text_y = element_text(size = 8, color = "#3b3b3b"), 
                    legend_title = element_text(size = 10), 
                    legend_text = element_text(size = 8)
                )
        )