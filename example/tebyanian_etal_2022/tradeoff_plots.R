library(dplyr)
library(plotly)


#--------------------------------------read results

pareto_set_100000=read.csv("optimize-NSGAII-100000.csv")
all_results_100000= read.csv("all_results.csv")


#-------------------- 2d trade off--runoff vacant

fig <- plot_ly()


fig <- fig %>%
  add_markers(data=all_results_100000, name="All 100,000 runs", x = ~RunoffVolume, y = ~VacantPriority, marker=list(color="#c6dbef"))
fig <- fig %>%
  add_markers(data=pareto_set_100000, name="Pareto set", x = ~RunoffVolume, y = ~VacantPriority, marker=list(color='#FF00FF'), size=10)


fig <-fig %>%
  layout(plot_bgcolor='#F5F5F5',
         title = ' Pareto set of the 100000 NFE optimization ',
         xaxis = list(
           title = list(text='Peak Runoff Volume at the Outfall (CFS)', font = list(size = 30), standoff = 30),
           tickfont = list( size=20),
           ticklen=16,
           tickcolor="#ffff",
           zeroline= F,
           showline = T,
           zerolinecolor = '404040',
           zerolinewidth = 4,
           gridcolor = 'ffff'
         ), 
         yaxis = list(
           title = list(text='Vacant Percentage (%)', font = list(size = 30), standoff = 30),
           tickfont = list( size=20),
           ticklen=16,
           tickcolor="#ffff",
           zeroline= F,
           showline = T,
           zerolinecolor = '404040',
           zerolinewidth = 4,
           gridcolor = 'ffff'
         ))



fig <- fig %>% layout(legend = list(x = 0.1, y = 0.97))

fig <- fig %>% layout(legend = list(font = list(size = 20)))
fig
#-------------------- 2d trade off--cost vacant

fig <- plot_ly()


fig <- fig %>%
  add_markers(data=all_results_100000, name="All 100,000 runs", x = ~Cost, y = ~VacantPriority, marker=list(color="#c6dbef"))
fig <- fig %>%
  add_markers(data=pareto_set_100000, name="Pareto set", x = ~Cost, y = ~VacantPriority, marker=list(color='#FF00FF'), size=10)

fig <-fig %>%
  layout(plot_bgcolor='#F5F5F5',
         title = ' Pareto set of the 100000 NFE optimization ',
         xaxis = list(
           title = list(text='Cost ($)', font = list(size = 30), standoff = 30),
           tickfont = list( size=20),
           ticklen=16,
           tickcolor="#ffff",
           zeroline= F,
           showline = T,
           zerolinecolor = '404040',
           zerolinewidth = 4,
           gridcolor = 'ffff'
         ), 
         yaxis = list(
           title = list(text='Vacant Percentage (%)', font = list(size = 30), standoff = 30),
           tickfont = list( size=20),
           ticklen=16,
           tickcolor="#ffff",
           zeroline= F,
           showline = T,
           zerolinecolor = '404040',
           zerolinewidth = 4,
           gridcolor = 'ffff'
         ))



fig <- fig %>% layout(legend = list(x = 0.7, y = 0.97))

fig <- fig %>% layout(legend = list(font = list(size = 20)))
fig

#-------------------- 2d trade off--runoff cost 

fig <- plot_ly()


fig <- fig %>%
  add_markers(data=all_results_100000, name="All 100,000 runs", x = ~RunoffVolume, y = ~Cost, marker=list(color="#c6dbef"))
fig <- fig %>%
  add_markers(data=pareto_set_100000, name="Pareto set", x = ~RunoffVolume, y = ~Cost, marker=list(color='#FF00FF'), size=10)

fig <-fig %>%
  layout(plot_bgcolor='#F5F5F5',
         title = ' Pareto set of the 100000 NFE optimization ',
         xaxis = list(
           title = list(text='Peak Runoff Volume at the Outfall (CFS)', font = list(size = 30), standoff = 30),
           tickfont = list( size=20),
           ticklen=16,
           tickcolor="#ffff",
           zeroline= F,
           showline = T,
           zerolinecolor = '404040',
           zerolinewidth = 4,
           gridcolor = 'ffff'
         ), 
         yaxis = list(
           title = list(text='Cost ($)', font = list(size = 30), standoff = 30),
           tickfont = list( size=20),
           ticklen=16,
           tickcolor="#ffff",
           zeroline= F,
           showline = T,
           zerolinecolor = '404040',
           zerolinewidth = 4,
           gridcolor = 'ffff'
         ))



fig <- fig %>% layout(legend = list(x = 0.7, y = 0.97))

fig <- fig %>% layout(legend = list(font = list(size = 20)))
fig


#--------------------------------------- 3d plot

fig <- plot_ly(pareto_set_100000, x = ~RunoffVolume, y = ~Cost, z = ~VacantPriority, marker = list(color = ~VacantPriority, colorscale = c('#c6dbef', '#FF00FF'), showscale = TRUE))
fig <- fig %>% add_markers()
fig <- fig %>% layout(scene = list(xaxis = list(title = list(text='Average Runoff Volume (CFS)', font = list(size = 20))),
                                   yaxis = list(title = list(text='Cost ($)', font = list(size = 20))),
                                   zaxis = list(title = list(text='Vacant Score (%)', font = list(size = 20)))))

fig



fig <- plot_ly()
fig <- fig %>%
  add_markers(data=pareto_set_100000, x = ~RunoffVolume, y = ~Cost, z = ~VacantPriority, marker=list(color='#FF00FF', line=list(width=0), size=8))

fig <- fig %>%
  add_markers(data=all_results_100000,  x = ~RunoffVolume, y = ~Cost, z = ~VacantPriority, marker=list(color="#c6dbef", line=list(width=0)), size=10)



fig <- fig %>% layout(scene = list(xaxis = list(title = list(text='Peak Runoff Volume (CFS)', font = list(size = 20))),
                                   yaxis = list(title = list(text='Cost ($)', font = list(size = 20))),
                                   zaxis = list(title = list(text='Vacant Score (%)', font = list(size = 20)))))

fig

