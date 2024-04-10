

# Load packages ----------------------------------------------------------------

library(tidyverse)
library(lubridate)
library(ggimage)
library(scales)
library(DBI)
library(RPostgres)
library(gt)
library(gtExtras)
library(RColorBrewer)
library(viridis)

# Source config ----------------------------------------------------------------
source("setup/config.R")

# Check if a connection exists to database -------------------------------------

conTest <- dbCanConnect(RPostgres::Postgres(),
                        dbname = "cdl_db", 
                        port = 5432, 
                        user = "postgres", 
                        password = db_password)

conTest

# Connect to cdl_db ------------------------------------------------------------

con <- dbConnect(RPostgres::Postgres(),
                 dbname = "cdl_db", 
                 port = 5432, 
                 user = "postgres", 
                 password = db_password)

con

# Load cdl_data into R dataframe -----------------------------------------------

cdlDF <- dbGetQuery(con, "SELECT * FROM cdl_data")

# Close the connection ---------------------------------------------------------

dbDisconnect(con)

# Show datatypes ---------------------------------------------------------------

str(cdlDF)

# Correct Minnesota ROKKR team name --------------------------------------------

cdlDF$team <- chartr("Minnesota RØKKR", "Minnesota ROKKR", cdlDF$team)

# Add W/L columns ---------------------------------------------------------------


cdlDF <- cdlDF %>% mutate(map_wl = if_else(map_result == 1, "W", "L"), 
                          series_wl = if_else(series_result == 1, "W", "L"))

# Get Team Logos & Colors ------------------------------------------------------

# team_logo <- c(
#   "https://dfpiiufxcciujugzjvgx.supabase.co/storage/v1/object/public/teams/ATL-FaZe-color-darkmode.png?t=2022-12-30T15%3A46%3A15.277Z", 
#   "https://static.wikia.nocookie.net/cod_esports_gamepedia_en/images/0/05/Boston_Breachlogo_square.png/revision/latest?cb=20220114204228",
#   "https://dfpiiufxcciujugzjvgx.supabase.co/storage/v1/object/public/teams/CAR_ROYAL_RAVENS_ALLMODE.webp",
#   "https://dfpiiufxcciujugzjvgx.supabase.co/storage/v1/object/public/teams/LV-Legion-color-allmode.png",
#   "https://static.wikia.nocookie.net/cod_esports_gamepedia_en/images/6/60/Los_Angeles_Guerrillaslogo_square.png/revision/latest?cb=20200612154050",
#   "https://dfpiiufxcciujugzjvgx.supabase.co/storage/v1/object/public/teams/LA-Thieves-color-allmode.png",
#   "https://dfpiiufxcciujugzjvgx.supabase.co/storage/v1/object/public/teams/MIA_HERETICS_ALLMODE.webp",
#   "https://dfpiiufxcciujugzjvgx.supabase.co/storage/v1/object/public/teams/MN-ROKKR-color-allmode.png",
#   "https://dfpiiufxcciujugzjvgx.supabase.co/storage/v1/object/public/teams/NY-Subliners-color-darkmode.png",
#   "https://static.wikia.nocookie.net/cod_esports_gamepedia_en/images/9/99/OpTic_Texaslogo_square.png/revision/latest?cb=20211114210508",
#   "https://dfpiiufxcciujugzjvgx.supabase.co/storage/v1/object/public/teams/SEA-Surge-color-allmode.png",
#   "https://static.wikia.nocookie.net/cod_esports_gamepedia_en/images/4/4f/Toronto_Ultralogo_square.png/revision/latest?cb=20191026213249"
# )

team_color <- c(
  "#e43d30", "#02ff5b", "#0083c1", "#ee7623", "#60269e", "#ff0000", 
  "#216d6b", "#351f65", "#fff000", "#92c951", "#00ffcc", "#780df2"
)

team <- unique((cdlDF %>% arrange(team))$team)


team_icon <- team %>%
  str_split_i(" ", -1)

team_icon[10] <- "OpTic"

team_abbr <- c("ATL", "BOS", "CAR", "LV", "LAG", "LAT",
               "MIA", "MIN", "NYSL", "TX", "SEA", "TOR")

team_logos_colors_df <- data.frame(
  team, 
  team_abbr, 
  team_icon, 
  # team_logo, 
  team_color
)

cdlDF <- cdlDF %>% left_join(team_logos_colors_df, by = c("team" = "team"))

# Get Opponents, Match Scores, and Score Differentials -------------------------

cdlDF <- cdlDF %>%
  mutate(player_lower = tolower(player))

cdlDF <- cdlDF %>%
  arrange(match_date, match_id, map_num, team, player_lower)

opps <- cdlDF %>%
  arrange(match_date, match_id, map_num, desc(team), player_lower) %>%
  select(
    team, 
    team_abbr,
    team_score, 
    # team_logo
    ) %>%
  rename("opp" = "team", 
         "opp_abbr" = "team_abbr",
         "opp_score" = "team_score", 
         # "opp_logo" = "team_logo"
         )

cdlDF <- bind_cols(cdlDF, opps) %>%
  mutate(total_score = team_score + opp_score, 
         score_diff = team_score - opp_score) %>%
  select(-player_lower)

# Get rosters & dropped players ------------------------------------------------

rostersDF <- cdlDF %>% select(player, team) %>% distinct() %>% arrange(team)

dropped_players <- c("GodRx", "ReeaL", "Afro", "Cammy", 
                     "JurNii", "Standy", "iLLeY", "Capsidal")

# Add Major, Week, and online/LAN columns using case_when statements -----------

cdlDF <- cdlDF %>%
  mutate(
    major = case_when(
      match_date <= ymd("2024-01-28")                                      ~ 1, 
      (match_date >= ymd("2024-02-16") & match_date <= ymd("2024-03-24"))  ~ 2 
    ), 
    week = case_when(
      match_date <= ymd("2023-12-10")                                      ~ 1,
      (match_date >= ymd("2023-12-15") & match_date <= ymd("2023-12-17"))  ~ 2,
      (match_date >= ymd("2024-01-12") & match_date <= ymd("2024-01-14"))  ~ 3,
      (match_date >= ymd("2024-01-19") & match_date <= ymd("2024-01-21"))  ~ 4,
      (match_date >= ymd("2024-02-16") & match_date <= ymd("2024-02-18"))  ~ 1,
      (match_date >= ymd("2024-02-23") & match_date <= ymd("2024-02-25"))  ~ 2,
      (match_date >= ymd("2024-03-01") & match_date <= ymd("2024-03-03"))  ~ 3,
      (match_date >= ymd("2024-03-08") & match_date <= ymd("2024-03-10"))  ~ 4,
      (match_date >= ymd("2024-03-15") & match_date <= ymd("2024-03-17"))  ~ 5
    ), 
    LAN = if_else(is.na(week), 1, 0)
  )

# Reorder W/L Levels for Graphing ----------------------------------------------

cdlDF$map_wl <- factor(cdlDF$map_wl, levels = c("W", "L"))
