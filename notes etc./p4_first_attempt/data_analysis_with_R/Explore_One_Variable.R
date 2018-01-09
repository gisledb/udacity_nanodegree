#Limiting the axes
#Adjusting the bin width
qplot(x = friend_count, data = pf, binwidth = 25) + 
  scale_x_continuous(limits = c(0, 1000), breaks = seq(0, 1000, 50))


#Equivalent ggplot syntax: 
  ggplot(aes(x = friend_count), data = pf) + 
  geom_histogram(binwidth = 25) + 
  scale_x_continuous(limits = c(0, 1000), breaks = seq(0, 1000, 50))


