
# Set directory ----

setwd("C:/Users/David Harler Jr/OneDrive/Desktop/dataClass/06-cod-analysis/2024.03.12 CDL Stats Visualization/cdl_viz/player-viz-app-v01")

# Source setup & helpers ----

source("00_Setup/00_Setup.R")
source("helpers.R")

# Load Shiny ----

library(shiny)

# Define ui ----

ui <- fluidPage(

  # App title ----
  titlePanel(title = "CODLeague Visualizations"),
  
  # Navbar layout ----
  navbarPage(title = "", 
             
    # First page ----
    tabPanel(h5("Player Singe Map Kills"), 
             
      # First row ----
      fluidRow(
        
        # First column ----
        column(2,
               
               # Sidebar panel ----
               wellPanel(
               
                 # Team Select Box ----
                 selectInput(inputId = "TeamInput", 
                             label = h4("Team"), 
                             choices = unique((cdlDF %>% arrange(team))$team), 
                             selected = "OpTic Texas"),
                 
                 # Opponent Select Box ----
                 selectInput(inputId = "OppInput", 
                             label = h4("Opponent"), 
                             choices = unique((cdlDF %>% arrange(team))$team), 
                             selected = "Atlanta FaZe")
                 
               )
        ), 
        
        # Second column ----
        column(4, gt_output(outputId = "TeamvsSummaryTbl")), 
        
        # Third column ----
        column(4, gt_output(outputId = "TeamSummaryH2HTbl")), 
        
        # Fourth column ----
        column(2)
        
        
      ), 
      
      # Second row ----
      fluidRow(
          
        # First column ----
        column(2, 
               
               # Sidebar panel
               wellPanel(
                 
                 
                 # Gamemode Select Box ----
                 selectInput(inputId = "GamemodeInput", 
                             label = h4("Gamemode"), 
                             choices = c("Hardpoint", "Search & Destroy", "Control")),
                 
                 # Map Select Box ----
                 selectInput(inputId = "MapInput", 
                             label = h4("Map"), 
                             choices = 
                               unique((cdlDF %>% arrange(map_name))$map_name) %>%
                               append("All", after = 0), 
                             selected = "All"), 
                 
                 # Player 1 PrizePicks Kills Numeric Input ----
                 numericInput(inputId = "P1Kills", 
                              label = h4("Player 1 Line"), 
                              min = 5.5, max = 25.5, step = 0.5, value = 21),
                 
                 # Player 2 PrizePicks Kills Numeric Input ----
                 numericInput(inputId = "P2Kills", 
                              label = h4("Player 2 Line"), 
                              min = 5.5, max = 25.5, step = 0.5, value = 21),
                 
                 # Player 3 PrizePicks Kills Numeric Input ----
                 numericInput(inputId = "P3Kills", 
                              label = h4("Player 3 Line"), 
                              min = 5.5, max = 25.5, step = 0.5, value = 21),
                 
                 # Player 4 PrizePicks Kills Numeric Input ----
                 numericInput(inputId = "P4Kills", 
                              label = h4("Player 4 Line"), 
                              min = 5.5, max = 25.5, step = 0.5, value = 21),
                 
                 # X Axis Select Box ----
                 selectInput(inputId = "xAxisInput", 
                             label = h4("X-Axis"), 
                             choices = c("Time", "Total Score", 
                                         "Score Differential"), 
                             selected = "Time")
                 
               )
               
        ), 
        
        # Second column ----
        column(3, 
               plotOutput(outputId = "P1KillsBoxPlot"), 
               plotOutput(outputId = "P2KillsBoxPlot"), 
               plotOutput(outputId = "P3KillsBoxPlot"), 
               plotOutput(outputId = "P4KillsBoxPlot")
        ), 
        
        # Third column ----
        column(5, 
               plotOutput(outputId = "P1KillsPlot"), 
               plotOutput(outputId = "P2KillsPlot"), 
               plotOutput(outputId = "P3KillsPlot"), 
               plotOutput(outputId = "P4KillsPlot")
               
        )
        
      ), 
      
      # Third row ----
      fluidRow(
        
        # First column ----
        column(2),
        
        # Second column ----
        column(3), 
        
        # Third column ----
        column(5, plotOutput(outputId = "TeamScoreDiffs")),
        
        # Fourth column ----
        column(2)
        
      ), 
      
      # Fourth row ----
      fluidRow(
        
        # First column ----
        column(5), 
        
        # Second column ----
        column(5, gt_output(outputId = "TeamMapScores")), 
        
        # Third column ----
        column(2)
        
      ),
      
      # Fifth row ----
      fluidRow(
        
        # First column ----
        column(2, 
               
               # Sidebar panel
               wellPanel(
                 
                 # Opp 1 PrizePicks Kills Numeric Input ----
                 numericInput(inputId = "Opp1Kills", 
                              label = h4("Opp 1 Line"), 
                              min = 5.5, max = 25.5, step = 0.5, value = 21),
                 
                 # Opp 2 PrizePicks Kills Numeric Input ----
                 numericInput(inputId = "Opp2Kills", 
                              label = h4("Opp 2 Line"), 
                              min = 5.5, max = 25.5, step = 0.5, value = 21),
                 
                 # Opp 3 PrizePicks Kills Numeric Input ----
                 numericInput(inputId = "Opp3Kills", 
                              label = h4("Opp 3 Line"), 
                              min = 5.5, max = 25.5, step = 0.5, value = 21),
                 
                 # Opp 4 PrizePicks Kills Numeric Input ----
                 numericInput(inputId = "Opp4Kills", 
                              label = h4("Opp 4 Line"), 
                              min = 5.5, max = 25.5, step = 0.5, value = 21),
                 
                 # Opp X Axis Select Box ----
                 selectInput(inputId = "OppxAxisInput", 
                             label = h4("X-Axis"), 
                             choices = c("Time", "Total Score", 
                                         "Score Differential"), 
                             selected = "Time")
                 
               )
               
        ), 
        
        # Second column ----
        column(3, 
               plotOutput(outputId = "Opp1KillsBoxPlot"), 
               plotOutput(outputId = "Opp2KillsBoxPlot"), 
               plotOutput(outputId = "Opp3KillsBoxPlot"), 
               plotOutput(outputId = "Opp4KillsBoxPlot")
        ), 
        
        # Third column ----
        column(5, 
               plotOutput(outputId = "Opp1KillsPlot"), 
               plotOutput(outputId = "Opp2KillsPlot"), 
               plotOutput(outputId = "Opp3KillsPlot"), 
               plotOutput(outputId = "Opp4KillsPlot")
               
        )
        
      ), 
      
      # Sixth row ----
      fluidRow(
        
        # First column ----
        column(2),
        
        # Second column ----
        column(3), 
        
        # Third column ----
        column(5, plotOutput(outputId = "OppScoreDiffs")),
        
        # Fourth column ----
        column(2)
        
      ), 
      
      # Seventh row ----
      fluidRow(
        
        # First column ----
        column(5), 
        
        # Second column ----
        column(5, gt_output(outputId = "OppMapScores")), 
        
        # Third column ----
        column(2)
        
      )
             
    ), 
    
    # Second page ----
    tabPanel(h5("Player Maps 1 - 3 Kills")),
    
    # Third Page ----
    tabPanel(h5("About"))
  
  )

)

# Define server logic ----
server <- function(input, output) {
  
  # 01 Team vs Summary Tbl Output ----
  output$TeamvsSummaryTbl <- render_gt(
    
    expr = team_summary_vs_fn(input$TeamInput, input$OppInput), 
    width = px(400), height = px(720), align = "center"
    
  )
  
  # 02 Team H2H Summary Tbl Output ----
  output$TeamSummaryH2HTbl <- render_gt(
    
    expr = team_h2h_gt_fn(input$TeamInput, input$OppInput), 
    width = px(400), height = px(720), align = "center"
    
  )
  
  # 03 Player 1 Plot Output ----
  output$P1KillsPlot <- renderPlot({
    
    player1 <- (rostersDF %>% 
                  filter(!(player %in% dropped_players) &
                    team == input$TeamInput))$player[1]
    
    if (input$xAxisInput == "Time"){
      p1Plot <- kills_vs_time(player1, input$GamemodeInput, 
                              input$P1Kills, input$MapInput)
      }
    if (input$xAxisInput == "Total Score"){
      p1Plot <- kills_vs_total(player1, input$GamemodeInput, 
                               input$P1Kills, input$MapInput)
      }
    if (input$xAxisInput == "Score Differential"){
      p1Plot <- player_kills_vs_score_diff(player1, input$GamemodeInput, 
                                           input$P1Kills, input$MapInput)
    }
    
    p1Plot
    
  })
  
  # 04 Player 2 Plot Output ----
  output$P2KillsPlot <- renderPlot({
    
    player2 <- (rostersDF %>% 
                  filter(!(player %in% dropped_players) &
                    team == input$TeamInput))$player[2]
    
    if (input$xAxisInput == "Time"){
      p2Plot <- kills_vs_time(player2, input$GamemodeInput, 
                              input$P2Kills, input$MapInput)
    }
    if (input$xAxisInput == "Total Score"){
      p2Plot <- kills_vs_total(player2, input$GamemodeInput, 
                               input$P2Kills, input$MapInput)
    }
    if (input$xAxisInput == "Score Differential"){
      p2Plot <- player_kills_vs_score_diff(player2, input$GamemodeInput, 
                                           input$P2Kills, input$MapInput)
    }
    
    p2Plot
    
  })
  
  
  # 05 Player 3 Plot Output ----
  output$P3KillsPlot <- renderPlot({
    
    player3 <- (rostersDF
                %>% filter(!(player %in% dropped_players) &
                  team == input$TeamInput))$player[3]
    
    if (input$xAxisInput == "Time"){
      p3Plot <- kills_vs_time(player3, input$GamemodeInput, 
                              input$P3Kills, input$MapInput)
    }
    if (input$xAxisInput == "Total Score"){
      p3Plot <- kills_vs_total(player3, input$GamemodeInput, 
                               input$P3Kills, input$MapInput)
    }
    if (input$xAxisInput == "Score Differential"){
      p3Plot <- player_kills_vs_score_diff(player3, input$GamemodeInput, 
                                           input$P3Kills, input$MapInput)
    }
    
    p3Plot
    
  })
  
  
  # 06 Player 4 Plot Output ----
  output$P4KillsPlot <- renderPlot({
    
    player4 <- (rostersDF %>% 
                  filter(!(player %in% dropped_players) &
                    team == input$TeamInput))$player[4]
    
    if (input$xAxisInput == "Time"){
      p4Plot <- kills_vs_time(player4, input$GamemodeInput, 
                              input$P4Kills, input$MapInput)
    }
    if (input$xAxisInput == "Total Score"){
      p4Plot <- kills_vs_total(player4, input$GamemodeInput, 
                               input$P4Kills, input$MapInput)
    }
    if (input$xAxisInput == "Score Differential"){
      p4Plot <- player_kills_vs_score_diff(player4, input$GamemodeInput, 
                                           input$P4Kills, input$MapInput)
    }
    
    p4Plot
    
  })
  
  # 07 Player 1 BoxPlot Output ----
  output$P1KillsBoxPlot <- renderPlot({
    
    player1 <- (rostersDF %>% 
                  filter(!(player %in% dropped_players) &
                    team == input$TeamInput))$player[1]
    
    p1BoxPlot <- kills_overview(player1, input$GamemodeInput, 
                                input$P1Kills, input$MapInput)
    
    p1BoxPlot
    
  })
  
  # 08 Player 2 BoxPlot Output ----
  output$P2KillsBoxPlot <- renderPlot({
    
    player2 <- (rostersDF %>% 
                  filter(!(player %in% dropped_players) &
                    team == input$TeamInput))$player[2]
    
    p2BoxPlot <- kills_overview(player2, input$GamemodeInput, 
                                input$P2Kills, input$MapInput)
    
    p2BoxPlot
    
  })
  
  # 09 Player 3 BoxPlot Output ----
  output$P3KillsBoxPlot <- renderPlot({
    
    player3 <- (rostersDF %>% 
                  filter(!(player %in% dropped_players) &
                    team == input$TeamInput))$player[3]
    
    p3BoxPlot <- kills_overview(player3, input$GamemodeInput, 
                                input$P3Kills, input$MapInput)
    
    p3BoxPlot
    
  })
  
  # 10 Player 4 BoxPlot Output ----
  output$P4KillsBoxPlot <- renderPlot({
    
    player4 <- (rostersDF %>% 
                  filter(!(player %in% dropped_players) &
                    team == input$TeamInput))$player[4]
    
    p4BoxPlot <- kills_overview(player4, input$GamemodeInput, 
                                input$P4Kills, input$MapInput)
    
    p4BoxPlot
    
  })
  
  # 11 Team Score Diffs Plot Output ----
  output$TeamScoreDiffs <- renderPlot({
    
    team_score_diffs(input$TeamInput, input$GamemodeInput, input$MapInput)
    
  })
  
  # 12 Opp 1 Plot Output ----
  output$Opp1KillsPlot <- renderPlot({
    
    opp1 <- (rostersDF %>% 
                  filter(!(player %in% dropped_players) &
                           team == input$OppInput))$player[1]
    
    if (input$OppxAxisInput == "Time"){
      opp1Plot <- kills_vs_time(opp1, input$GamemodeInput, 
                              input$Opp1Kills, input$MapInput)
    }
    if (input$OppxAxisInput == "Total Score"){
      opp1Plot <- kills_vs_total(opp1, input$GamemodeInput, 
                               input$Opp1Kills, input$MapInput)
    }
    if (input$OppxAxisInput == "Score Differential"){
      opp1Plot <- player_kills_vs_score_diff(opp1, input$GamemodeInput, 
                                           input$Opp1Kills, input$MapInput)
    }
    
    opp1Plot
    
  })
  
  
  # 13 Opp 2 Plot Output ----
  output$Opp2KillsPlot <- renderPlot({
    
    opp2 <- (rostersDF %>% 
                  filter(!(player %in% dropped_players) &
                           team == input$OppInput))$player[2]
    
    if (input$OppxAxisInput == "Time"){
      opp2Plot <- kills_vs_time(opp2, input$GamemodeInput, 
                              input$Opp2Kills, input$MapInput)
    }
    if (input$OppxAxisInput == "Total Score"){
      opp2Plot <- kills_vs_total(opp2, input$GamemodeInput, 
                               input$Opp2Kills, input$MapInput)
    }
    if (input$OppxAxisInput == "Score Differential"){
      opp2Plot <- player_kills_vs_score_diff(opp2, input$GamemodeInput, 
                                           input$Opp2Kills, input$MapInput)
    }
    
    opp2Plot
    
  })
  
  
  # 14 Opp 3 Plot Output ----
  output$Opp3KillsPlot <- renderPlot({
    
    opp3 <- (rostersDF
                %>% filter(!(player %in% dropped_players) &
                             team == input$OppInput))$player[3]
    
    if (input$OppxAxisInput == "Time"){
      opp3Plot <- kills_vs_time(opp3, input$GamemodeInput, 
                              input$Opp3Kills, input$MapInput)
    }
    if (input$OppxAxisInput == "Total Score"){
      opp3Plot <- kills_vs_total(opp3, input$GamemodeInput, 
                               input$Opp3Kills, input$MapInput)
    }
    if (input$OppxAxisInput == "Score Differential"){
      opp3Plot <- player_kills_vs_score_diff(opp3, input$GamemodeInput, 
                                           input$Opp3Kills, input$MapInput)
    }
    
    opp3Plot
    
  })
  
  
  # 15 Opp 4 Plot Output ----
  output$Opp4KillsPlot <- renderPlot({
    
    opp4 <- (rostersDF %>% 
                  filter(!(player %in% dropped_players) &
                           team == input$OppInput))$player[4]
    
    if (input$OppxAxisInput == "Time"){
      opp4Plot <- kills_vs_time(opp4, input$GamemodeInput, 
                              input$Opp4Kills, input$MapInput)
    }
    if (input$OppxAxisInput == "Total Score"){
      opp4Plot <- kills_vs_total(opp4, input$GamemodeInput, 
                               input$Opp4Kills, input$MapInput)
    }
    if (input$OppxAxisInput == "Score Differential"){
      opp4Plot <- player_kills_vs_score_diff(opp4, input$GamemodeInput, 
                                           input$Opp4Kills, input$MapInput)
    }
    
    opp4Plot
    
  })
  
  # 16 Opp 1 BoxPlot Output ----
  output$Opp1KillsBoxPlot <- renderPlot({
    
    opp1 <- (rostersDF %>% 
                  filter(!(player %in% dropped_players) &
                           team == input$OppInput))$player[1]
    
    opp1BoxPlot <- kills_overview(opp1, input$GamemodeInput, 
                                input$Opp1Kills, input$MapInput)
    
    opp1BoxPlot
    
  })
  
  # 17 Opp 2 BoxPlot Output ----
  output$Opp2KillsBoxPlot <- renderPlot({
    
    opp2 <- (rostersDF %>% 
                  filter(!(player %in% dropped_players) &
                           team == input$OppInput))$player[2]
    
    opp2BoxPlot <- kills_overview(opp2, input$GamemodeInput, 
                                input$Opp2Kills, input$MapInput)
    
    opp2BoxPlot
    
  })
  
  # 18 Opp 3 BoxPlot Output ----
  output$Opp3KillsBoxPlot <- renderPlot({
    
    opp3 <- (rostersDF %>% 
                  filter(!(player %in% dropped_players) &
                           team == input$OppInput))$player[3]
    
    opp3BoxPlot <- kills_overview(opp3, input$GamemodeInput, 
                                input$Opp3Kills, input$MapInput)
    
    opp3BoxPlot
    
  })
  
  # 19 Opp 4 BoxPlot Output ----
  output$Opp4KillsBoxPlot <- renderPlot({
    
    opp4 <- (rostersDF %>% 
                  filter(!(player %in% dropped_players) &
                           team == input$OppInput))$player[4]
    
    opp4BoxPlot <- kills_overview(opp4, input$GamemodeInput, 
                                input$Opp4Kills, input$MapInput)
    
    opp4BoxPlot
    
  })
  
  # 20 Team Score Diffs Plot Output ----
  output$OppScoreDiffs <- renderPlot({
    
    team_score_diffs(input$OppInput, input$GamemodeInput, input$MapInput)
    
  })
  
  # 21 Map Scores gt Table (Interactive) ----
  output$TeamMapScores <- render_gt(
    
    expr = match_scores_gt_fn(input$TeamInput, 
                              input$GamemodeInput, input$MapInput), 
    width = px(420), height = px(480), align = "center"
    
  )
  
  # 22 Opp Map Scores gt Table (Interactive) ----
  output$OppMapScores <- render_gt(
    
    expr = match_scores_gt_fn(input$OppInput, 
                              input$GamemodeInput, input$MapInput), 
    width = px(420), height = px(480), align = "center"
    
  )
  
}

# Create Shiny app ----
shinyApp(ui, server)




