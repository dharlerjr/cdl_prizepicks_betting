

# Dictionary of color scales by gamemode ---------------------------------------

gamemode_color_scales <- list(
  "Hardpoint" = c("red", "orange", "green", "blue", "purple"),
  "Search & Destroy" = c("red", "orange", "green", "blue", "purple"),
  "Control" = c("red", "green", "blue")
)

# Dictionary of colors by map & mode -------------------------------------------

map_and_mode_colors <- list(
  "Hardpoint" = list(
    "Invasion" = "red", 
    "Karachi" = "orange",
    "Rio" = "green",
    "Skidrow" = "blue",
    "Sub Base" = "purple"
  ), 
  "Search & Destroy" = list(
    "Highrise" = "red", 
    "Invasion" = "orange",
    "Karachi" = "green", 
    "Rio" = "blue",
    "Terminal" = "purple"
  ), 
  "Control" = list(
    "Highrise" = "red", 
    "Invasion" = "green", 
    "Karachi" = "blue"
  )
)

# Dictionary of viridis color scales by gamemode -------------------------------

viridis_gamemode_color_scales <- list(
  "Hardpoint" = 
    c("#FDE725FF", "#56c667ff", "#21908CFF", "#3B528BFF", "#440154FF"), 
  "Search & Destroy" = 
    c("#FDE725FF", "#56c667ff", "#21908CFF", "#3B528BFF", "#440154FF"), 
  "Control" = c("#FDE725FF", "#56c667ff", "#21908CFF")
)

# Dictionary of viridis colors by map & mode -----------------------------------

viridis_map_and_mode_colors <- list(
  "Hardpoint" = list(
    "Invasion" = "#FDE725FF", 
    "Karachi" = "#56c667ff",
    "Rio" = "#21908CFF",
    "Skidrow" = "#3B528BFF",
    "Sub Base" = "#440154FF"
  ), 
  "Search & Destroy" = list(
    "Highrise" = "#FDE725FF", 
    "Invasion" = "#56c667ff",
    "Karachi" = "#21908CFF", 
    "Rio" = "#3B528BFF",
    "Terminal" = "#440154FF"
  ), 
  "Control" = list(
    "Highrise" = "#FDE725FF", 
    "Invasion" = "#56c667ff", 
    "Karachi" = "#21908CFF"
  )
)

# Dictionary of binwidths by gamemode ------------------------------------------

gamemode_bins <- list(
  "Hardpoint" = 50, 
  "Search & Destroy" = 1, 
  "Control" = 1
)

# Dictionary of ylims by gamemode ----------------------------------------------

gamemode_kill_lims <- list(
  "Hardpoint" = c(0, 45), 
  "Search & Destroy" = c(0, 16), 
  "Control" = c(0, 45)
)

# Team Summary DF --------------------------------------------------------------

team_summaries <- 
  bind_rows(
    cdlDF %>%
      select(match_id, team, map_name, gamemode, map_result) %>%
      distinct() %>% 
      group_by(team, gamemode, map_name) %>%
      summarise(wins = sum(map_result), 
                losses = n() - sum(map_result), 
                win_percentage = round(sum(map_result) / n(), 2)) %>%
      filter(!(gamemode == "Hardpoint" & map_name == "Terminal") &
               !(gamemode == "Search & Destroy" & map_name == "Skidrow")), 
    cdlDF %>%
      filter(!(gamemode == "Hardpoint" & map_name == "Terminal") &
               !(gamemode == "Search & Destroy" & map_name == "Skidrow")) %>%
      select(match_id, team, map_name, gamemode, map_result) %>%
      distinct() %>%
      group_by(team, gamemode) %>%
      summarise(wins = sum(map_result), 
                losses = n() - sum(map_result), 
                win_percentage = round(sum(map_result) / n(), 2))
  ) %>%
  replace_na(list(map_name = "Overall"))

team_summaries$gamemode <- factor(
  team_summaries$gamemode, levels = c("Hardpoint", "Search & Destroy", "Control")
)

team_summaries$map_name <- factor(
  team_summaries$map_name, 
  levels = c("Highrise", "Invasion", "Karachi", "Rio", "Skidrow", 
             "Sub Base", "Terminal", "Overall")
)

# Score Differentials by Map & Mode --------------------------------------------

team_score_diffs <- function(team_input, gamemode_input, map_input = "All"){
  
  if(map_input == "All"){
    cdlDF %>%
      filter(!(gamemode == "Hardpoint" & map_name == "Terminal") & 
               !(gamemode == "Search & Destroy" & map_name == "Skidrow") &
               gamemode == gamemode_input & team == team_input) %>%
      select(match_id, map_name, score_diff) %>%
      distinct() %>%
      ggplot(aes(score_diff, fill = map_name)) +
      geom_histogram(position = position_dodge(), 
                     binwidth = gamemode_bins[[gamemode_input]]) +
      facet_wrap(~map_name) +
      scale_fill_manual(values = viridis_gamemode_color_scales[[gamemode_input]]) +
      labs(title = paste(team_input, "Distribution of Score Differentials:", 
                         gamemode_input), 
           fill = "Map") +
      xlab("Score Differential") + ylab("Count") +
      theme(
        plot.title = element_text(size = 18),
        axis.text.x.bottom = element_text(size = 12, color = "#3b3b3b"), 
        axis.text.y.left = element_text(size = 12, color = "#3b3b3b"), 
        legend.position = "none", 
        axis.title = element_text(size = 14), 
        strip.text = element_text(size = 14)
      )
  }
  else{
    cdlDF %>%
      filter(!(gamemode == "Hardpoint" & map_name == "Terminal") & 
               !(gamemode == "Search & Destroy" & map_name == "Skidrow") &
               gamemode == gamemode_input & team == team_input & 
               map_name == map_input) %>%
      select(match_id, map_name, score_diff) %>%
      distinct() %>%
      ggplot(aes(score_diff, fill = map_name)) +
      geom_histogram(position = position_dodge(), 
                     binwidth = gamemode_bins[[gamemode_input]]) +
      scale_fill_manual(
        values = viridis_map_and_mode_colors[[gamemode_input]][[map_input]]
      ) +
      labs(title = paste(team_input, "Distribution of Score Differentials:", 
                         map_input, gamemode_input),
           fill = "Map") +
      xlab("Score Differential") + ylab("Count") +
      theme(
        plot.title = element_text(size = 18),
        axis.text.x.bottom = element_text(size = 12, color = "#3b3b3b"), 
        axis.text.y.left = element_text(size = 12, color = "#3b3b3b"), 
        legend.position = "none", 
        axis.title = element_text(size = 14)
      )
  }
  
}

# Team vs Team Summaries -------------------------------------------------------

team_summary_vs_fn <- function(team_x, team_y) {
  
  left_join(
    team_summaries %>% filter(team == team_x) %>% 
      ungroup(),
    team_summaries %>% filter(team == team_y) %>% 
      ungroup(),
    by = c("gamemode" = "gamemode", "map_name" = "map_name")
  ) %>%
    select(-c(team.x, team.y)) %>% arrange(gamemode, map_name) %>%
    gt() %>%
    opt_align_table_header("center") %>%
    cols_align("center") %>%
    opt_row_striping() %>%
    tab_header(title = paste(team_x, "&", team_y, "Summaries")) %>%
    gt_theme_espn() %>%
    tab_spanner(label = team_x, columns = ends_with("x")) %>%
    tab_spanner(label = team_y, columns = ends_with("y")) %>%
    tab_row_group(label = "Hardpoint", 
                  rows = gamemode == "Hardpoint") %>%
    tab_row_group(label = "Search & Destroy", 
                  rows = gamemode == "Search & Destroy") %>%
    tab_row_group(label = "Control", 
                  rows = gamemode == "Control") %>%
    row_group_order(c("Hardpoint", "Search & Destroy", "Control")) %>%
    cols_hide(columns = gamemode) %>%
    data_color(
      columns = starts_with("win_percentage"),
      fn = scales::col_numeric(
        palette =  c("#cb181d", "#cb181d", "#fcae91", "#ffffff", 
                     "#bdd7e7", "#2171b5", "#2171b5"),
        domain = c(0, 1))) %>%
    cols_width(map_name ~ px(100), starts_with("win_percentage") ~ px(60),
               starts_with("wins") ~ px(40), starts_with("losses") ~ px(40)) %>%
    cols_label(map_name = "Map", starts_with("win_percentage") ~ "Win %", 
               starts_with("wins") ~ "W", starts_with("losses") ~ "L") %>%
    fmt_percent(columns = starts_with("win_percentage"), 
                decimals = 0) %>%
    tab_options(table.font.size = px(12), 
                heading.title.font.size = px(18), 
                table.align = "center", 
                heading.align = "center")
  
}

# Team H2H  --------------------------------------------------------------------

team_h2h_gt_fn <- function(team_a, team_b){
  
  tempDF <- cdlDF %>%
    select(match_id, team, map_name, gamemode, map_result, opp) %>%
    filter(!(gamemode == "Hardpoint" & map_name == "Terminal") &
             !(gamemode == "Search & Destroy" & map_name == "Skidrow") &
             team == team_a & opp == team_b) %>%
    distinct() %>%
    group_by(gamemode) %>%
    summarise(team_a_wins = sum(map_result),
              team_a_losses = n() - sum(map_result),
              team_a_win_percentage = round(sum(map_result) / n(), 2),
              team_b_wins = n() - sum(map_result), 
              team_b_losses = sum(map_result), 
              team_b_win_percentage = round((n() - sum(map_result)) / n(), 2))
  
  tempDF$map_name = c("Overall", "Overall", "Overall")
  
  tempDF <- tempDF %>%
    select(gamemode, map_name, 
           team_a_wins, team_a_losses, team_a_win_percentage, 
           team_b_wins, team_b_losses, team_b_win_percentage)
  
  tempDF <- bind_rows(
    tempDF, 
    cdlDF %>%
      select(match_id, team, map_name, gamemode, map_result, opp) %>%
      filter(!(gamemode == "Hardpoint" & map_name == "Terminal") &
               !(gamemode == "Search & Destroy" & map_name == "Skidrow") &
               team == team_a & opp == team_b) %>%
      distinct() %>%
      group_by(gamemode, map_name) %>%
      summarise(team_a_wins = sum(map_result),
                team_a_losses = n() - sum(map_result),
                team_a_win_percentage = round(sum(map_result) / n(), 2),
                team_b_wins = n() - sum(map_result), 
                team_b_losses = sum(map_result), 
                team_b_win_percentage = round((n() - sum(map_result)) / n(), 2))
  )
  
  tempDF$map_name <- factor(
    tempDF$map_name, 
    levels = c("Highrise", "Invasion", "Karachi", "Rio", "Skidrow", 
               "Sub Base", "Terminal", "Overall")
  )
  
  tempDF %>% ungroup() %>% arrange(map_name) %>% 
    gt() %>%
    opt_align_table_header("center") %>%
    cols_align("center") %>%
    opt_row_striping() %>%
    tab_header(title = paste0(team_a, " & ", team_b, " H2H Summary")) %>%
    gt_theme_espn() %>%
    tab_spanner(label = team_a, columns = starts_with("team_a")) %>%
    tab_spanner(label = team_b, columns = starts_with("team_b")) %>%
    tab_row_group(label = "Hardpoint", 
                  rows = gamemode == "Hardpoint") %>%
    tab_row_group(label = "Search & Destroy", 
                  rows = gamemode == "Search & Destroy") %>%
    tab_row_group(label = "Control", 
                  rows = gamemode == "Control") %>%
    row_group_order(c("Hardpoint", "Search & Destroy", "Control")) %>%
    cols_hide(columns = gamemode) %>%
    data_color(
      columns = ends_with("win_percentage"),
      fn = scales::col_numeric(
        palette =  c("#cb181d", "#cb181d", "#fcae91", "#ffffff", 
                     "#bdd7e7", "#2171b5", "#2171b5"),
        domain = c(0, 1))) %>%
    cols_width(map_name ~ px(100), ends_with("win_percentage") ~ px(60),
               ends_with("wins") ~ px(40), ends_with("losses") ~ px(40)) %>%
    cols_label(map_name = "Map", ends_with("win_percentage") ~ "Win %", 
               ends_with("wins") ~ "W", ends_with("losses") ~ "L") %>%
    fmt_percent(columns = ends_with("win_percentage"), 
                decimals = 0) %>%
    tab_options(table.font.size = px(12), 
                heading.title.font.size = px(18), 
                table.align = "center", 
                heading.align = "center")
  
}

# Player Kills vs Time ---------------------------------------------------------

kills_vs_time <-
  function(player_input, gamemode_input, cur_line, map_input = "All"){
    if(map_input == "All"){
      cdlDF %>% 
        filter(!(gamemode == "Hardpoint" & map_name == "Terminal") & 
                 !(gamemode == "Search & Destroy" & map_name == "Skidrow") &
                 gamemode == gamemode_input & player == player_input) %>%
        ggplot(aes(x = match_date, y = kills, color = map_name)) + 
        geom_point(size = 2) +
        geom_hline(yintercept = cur_line, color = "purple", linetype = "dashed", 
                   linewidth = 0.75) +
        scale_color_manual(values = gamemode_color_scales[[gamemode_input]]) +
        labs(title = paste(player_input, gamemode_input, "Kills colored by Map"), 
             color = "Map") +
        xlab("Date") + ylab("Kills") +
        theme(
          plot.title = element_text(size = 18),
          axis.text.x.bottom = element_text(size = 12, color = "#3b3b3b"), 
          axis.text.y.left = element_text(size = 12, color = "#3b3b3b"), 
          axis.title = element_text(size = 14), 
          legend.title = element_text(size = 14), 
          legend.text = element_text(size = 10)
        )
    }
    
    else {
      cdlDF %>% 
        filter(!(gamemode == "Hardpoint" & map_name == "Terminal") & 
                 !(gamemode == "Search & Destroy" & map_name == "Skidrow") &
                 gamemode == gamemode_input & player == player_input &
                 map_name == map_input) %>%
        ggplot(aes(x = match_date, y = kills, color = map_wl)) + 
        geom_point(size = 2) +
        geom_hline(yintercept = cur_line, color = "purple", linetype = "dashed", 
                   linewidth = 0.75) +
        scale_color_manual(values = c("blue", "red")) +
        labs(title = paste(player_input, map_input, gamemode_input, "Kills"), 
             color = "W/L") +
        xlab("Date") + ylab("Kills") +
        theme(
          plot.title = element_text(size = 18),
          axis.text.x.bottom = element_text(size = 12, color = "#3b3b3b"), 
          axis.text.y.left = element_text(size = 12, color = "#3b3b3b"), 
          axis.title = element_text(size = 14), 
          legend.title = element_text(size = 14), 
          legend.text = element_text(size = 10)
        )
    }
  }

# Player Kills vs Total Score by WL --------------------------------------------

kills_vs_total <-
  function(player_input, gamemode_input, cur_line, map_input = "All"){
    if(map_input == "All"){
      cdlDF %>% 
        filter(!(gamemode == "Hardpoint" & map_name == "Terminal") & 
                 !(gamemode == "Search & Destroy" & map_name == "Skidrow") &
                 gamemode == gamemode_input & player == player_input) %>%
        ggplot(aes(x = total_score, y = kills, color = map_wl)) + 
        geom_point(size = 2) +
        geom_smooth(level = 0) +
        geom_hline(yintercept = cur_line, color = "purple", linetype = "dashed", 
                   linewidth = 0.75) +
        scale_color_manual(values = c("blue", "red")) +
        labs(title = paste(player_input, gamemode_input, "Kills colored by Map W/L"), 
             color = "W/L") +
        xlab("Total Score") + ylab("Kills") +
        theme(
          plot.title = element_text(size = 18),
          axis.text.x.bottom = element_text(size = 12, color = "#3b3b3b"), 
          axis.text.y.left = element_text(size = 12, color = "#3b3b3b"), 
          axis.title = element_text(size = 14), 
          legend.title = element_text(size = 14), 
          legend.text = element_text(size = 10)
        )
    }
    
    else {
      cdlDF %>% 
        filter(!(gamemode == "Hardpoint" & map_name == "Terminal") & 
                 !(gamemode == "Search & Destroy" & map_name == "Skidrow") &
                 gamemode == gamemode_input & player == player_input &
                 map_name == map_input) %>%
        ggplot(aes(x = total_score, y = kills, color = map_wl)) + 
        geom_point(size = 2) +
        geom_smooth(level = 0) +
        geom_hline(yintercept = cur_line, color = "purple", linetype = "dashed", 
                   linewidth = 0.75) +
        scale_color_manual(values = c("blue", "red")) +
        labs(title = paste(player_input, "Kills on", map_input, gamemode_input, 
                           "colored by Map W/L"), 
             color = "W/L") +
        xlab("Total Score") + ylab("Kills") +
        theme(
          plot.title = element_text(size = 18),
          axis.text.x.bottom = element_text(size = 12, color = "#3b3b3b"), 
          axis.text.y.left = element_text(size = 12, color = "#3b3b3b"), 
          axis.title = element_text(size = 14), 
          legend.title = element_text(size = 14), 
          legend.text = element_text(size = 10)
        )
    }
  }

# Player Kills vs Score Diff ---------------------------------------------------

player_kills_vs_score_diff <- function(player_input, gamemode_input, cur_line, 
                                       map_input = "All"){
  
  if(map_input == "All"){
    cdlDF %>% 
      filter(!(gamemode == "Hardpoint" & map_name == "Terminal") & 
               !(gamemode == "Search & Destroy" & map_name == "Skidrow") &
               gamemode == gamemode_input & player == player_input) %>%
      ggplot(aes(x = score_diff, y = kills)) + 
      geom_point(aes(color = map_name), size = 2, alpha = 1) +
      geom_smooth() +
      geom_vline(xintercept = 0, color = "orange", linetype = "dashed", 
                 linewidth = 0.75) +
      geom_hline(yintercept = cur_line, color = "purple", linetype = "dashed", 
                 linewidth = 0.75) +
      scale_color_manual(values = gamemode_color_scales[[gamemode_input]]) +
      labs(title = paste(player_input, "Kills vs Score Differential:", gamemode_input), 
           color = "Map") +
      xlab("Score Differential") + ylab("Kills") +
      # ylim(gamemode_kill_lims[[gamemode_input]]) +
      theme(
        plot.title = element_text(size = 18),
        axis.text.x.bottom = element_text(size = 12, color = "#3b3b3b"), 
        axis.text.y.left = element_text(size = 12, color = "#3b3b3b"), 
        axis.title = element_text(size = 14), 
        legend.title = element_text(size = 14), 
        legend.text = element_text(size = 10)
      )
  }
  
  else{
    cdlDF %>% 
      filter(!(gamemode == "Hardpoint" & map_name == "Terminal") & 
               !(gamemode == "Search & Destroy" & map_name == "Skidrow") &
               gamemode == gamemode_input & player == player_input &
               map_name == map_input) %>%
      ggplot(aes(x = score_diff, y = kills, color = map_name)) + 
      geom_point(size = 2, alpha = 1) +
      geom_smooth(level = 0) +
      geom_vline(xintercept = 0, color = "orange", linetype = "dashed", 
                 linewidth = 0.75) +
      geom_hline(yintercept = cur_line, color = "purple", linetype = "dashed", 
                 linewidth = 0.75) +
      scale_color_manual(values = map_and_mode_colors[[gamemode_input]][[map_input]]) +
      labs(title = paste(player_input, "Kills vs Score Differential:", map_input, gamemode_input)) + 
      xlab("Score Differential") + ylab("Kills") +
      # ylim(gamemode_kill_lims[[gamemode_input]]) +
      theme(
        plot.title = element_text(size = 18),
        axis.text.x.bottom = element_text(size = 12, color = "#3b3b3b"), 
        axis.text.y.left = element_text(size = 12, color = "#3b3b3b"), 
        legend.position = "none", 
        axis.title = element_text(size = 14)
      )
  }
  
}

# Player Kills Overview --------------------------------------------------------

kills_overview <-
  function(player_input, gamemode_input, cur_line, map_input = "All"){
    if(map_input == "All"){
      cdlDF %>%
        filter(!(gamemode == "Hardpoint" & map_name == "Terminal") & 
                 !(gamemode == "Search & Destroy" & map_name == "Skidrow") &
                 player == player_input & gamemode == gamemode_input) %>%
        ggplot(aes(x = "", y = kills)) +
        geom_jitter(aes(color = map_name), 
                    width = 0.05, height = 0.05, size = 2) +
        geom_boxplot(alpha = 0.5, outlier.alpha = 0) +
        geom_hline(yintercept = cur_line, lty = 'dashed', color = 'purple') +
        labs(title = paste(player_input, gamemode_input, "Kills"),
             color = "Map") +
        xlab("") + ylab("Kills") + 
        theme(plot.title = element_text(size = 18), 
              plot.margin = margin(8, 12, 12, 12, "pt"), 
              axis.title = element_text(size = 14), 
              axis.text.y.left = element_text(size = 12, color = "#3b3b3b"), 
              axis.text.x = element_blank(),
              axis.ticks.x = element_blank(), 
              legend.title = element_text(size = 14), 
              legend.text = element_text(size = 10)
              ) +
        scale_color_manual(values = gamemode_color_scales[[gamemode_input]])
    }
    else {
      cdlDF %>%
        filter(!(gamemode == "Hardpoint" & map_name == "Terminal") & 
                 !(gamemode == "Search & Destroy" & map_name == "Skidrow") & 
                 player == player_input & gamemode == gamemode_input 
               & map_name == map_input) %>%
        ggplot(mapping = aes(x = map_name, y = kills)) +
        geom_jitter(mapping = aes(color = map_wl), 
                    width = 0.05, height = 0.05, size = 2) +
        geom_boxplot(alpha = 0.5, outlier.alpha = 0) +
        geom_hline(yintercept = cur_line, lty = 'dashed', color = 'purple') +
        labs(title = paste(player_input, "Kills on", map_input, gamemode_input), 
             color = "W/L") +
        xlab("") + ylab("Kills") + 
        theme(plot.title = element_text(size = 18), 
              plot.margin = margin(8, 12, 12, 12, "pt"), 
              axis.title = element_text(size = 14),
              axis.text.y.left = element_text(size = 12, color = "#3b3b3b"),
              axis.text.x = element_blank(),
              axis.ticks.x = element_blank(), 
              legend.title = element_text(size = 14), 
              legend.text = element_text(size = 10)
              ) +
        scale_color_manual(values = c("blue", "red"))
    }
  }

# Map Scores gt Table (Interactive) --------------------------------------------

match_scores_gt_fn <- function(team_input, gamemode_input, map_input = "All"){
  if(map_input == "All"){
    cdlDF %>%
      filter(!(gamemode == "Hardpoint" & map_name == "Terminal") & 
               !(gamemode == "Search & Destroy" & map_name == "Skidrow") &
               gamemode == gamemode_input & team == team_input) %>%
      select(match_date, map_name, team_score, opp_score, opp_abbr) %>% 
      distinct() %>%
      arrange(desc(match_date)) %>%
      gt() %>%
      opt_align_table_header("center") %>%
      cols_align("center") %>%
      opt_row_striping() %>%
      tab_header(title = paste(team_input, gamemode_input)) %>%
      gt_theme_espn() %>%
      cols_width(match_date ~ px(90), map_name ~ px(120), 
                 ends_with("score") ~ px(60), opp_abbr ~ px(90)) %>%
      cols_label(match_date = "Date", map_name = "Map", 
                 team_score = "", opp_score = "",
                 opp_abbr = "Opponent") %>%
      tab_options(table.font.size = px(8), 
                  column_labels.font.size = px(8),
                  heading.title.font.size = px(18), 
                  table.align = "center", 
                  heading.align = "center") %>%
      opt_interactive(use_compact_mode = TRUE, 
                      use_filters = TRUE)
  }
  else{
    cdlDF %>%
      filter(!(gamemode == "Hardpoint" & map_name == "Terminal") & 
               !(gamemode == "Search & Destroy" & map_name == "Skidrow") &
               gamemode == gamemode_input & team == team_input & 
               map_name == map_input) %>%
      select(match_date, team_score, opp_score, opp_abbr) %>% 
      distinct() %>%
      arrange(desc(match_date)) %>%
      gt() %>%
      opt_align_table_header("center") %>%
      cols_align("center") %>%
      opt_row_striping() %>%
      tab_header(title = paste(team_input, map_input, gamemode_input)) %>%
      gt_theme_espn() %>%
      cols_width(match_date ~ px(130), 
                 ends_with("score") ~ px(80), opp_abbr ~ px(130)) %>%
      cols_label(match_date = "Date", 
                 team_score = "", opp_score = "",
                 opp_abbr = "Opponent") %>%
      tab_options(table.font.size = px(8), 
                  column_labels.font.size = px(8),
                  heading.title.font.size = px(18), 
                  table.align = "center", 
                  heading.align = "center") %>%
      opt_interactive(use_compact_mode = TRUE, 
                      use_filters = FALSE)
  }
}
