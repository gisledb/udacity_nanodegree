Pre-feedback version: https://public.tableau.com/profile/gisle.gaasemyr#!/vizhome/airbnb_in_san_francisco/Story
Final version: https://public.tableau.com/profile/gisle.gaasemyr#!/vizhome/AirbnbinSanFrancisco_0/Story

#### **Summary**
With this project I aim to display the distribution of different types of rooms and hosts who  used Airbnb in San Francisco, during the years 2014 to mid-2017. The perception amongst many San Franciscians is that Airbnb is being utilized by landlords, who take rentable rooms off the permanent rental market in order to rent them to tourists on Airbnb, thereby contributing to the current housing crisis and soaring rental prices in the City. One goal with this project was to explore the Airbnb data and try to see if there is any merit to these accusations by examining how many of Airbnb's hosts own multiple properties.

My project will also explore Airbnb trends over time, including median prices for Airbnb room rentals in San Francisco's various neighborhoods, the neighborhood pricing trends over time, the types of rentals available on Airbnb (entire home, private rooms, and shared rooms) and the number of rooms or homes that hosts manage through the site.

#### **Design**

After deciding on the data source I wanted to use, I downloaded 32 individual files which I merged into one larger file via an R script (union_script.R) to make it easier to work with the data in Tableau. While doing the initial data exploration in Tableau I quickly noticed that something was off with one the dates: all of the records from 2015-06-05 had price set to 0. Due to this I rewrote the R script to exclude the 2015-06-05 data file.

In my story, I use variations of six different visualization types: table, bar chart, choropleth map, time series line chart, bubble chart and pie chart. I chose these types to best represent my findings because they made the results the easiest to understand visually. I spent extra time creating the interactive neighborhood map of San Francisco to allow the viewer to easier dig deeper into the data without resorting to including text. 

I went through several iterations before ending up with my final story. The majority of the visualizations I made were eventually abandoned. At one point I tried to include demographics data for the different San Francisco neighborhoods for deeper analysis. After a while I realized that this made the scope of the project way too large, so I dropped pursuing it further. In my final version, to keep my story focused, I removed worksheets showing the following: price compared to size, dates with lowest and highest prices, neighborhood counts, satisfaction/rating (map and time series), rating compared to price, price compared to vacancy per neighborhood, and various other descriptive statistics over time.

For a while I struggled making Tableau shape the data the way I wanted. Eventually I realized I had to reshape the dataset outside of Tableau to achieve the desired groupings, which you can see the result of in number_of_units.csv (generated with create_datasets.ipynb). When the new data file was ready it became much easier to continue the project.

The main change I made after receiving feedback was to remove the introduction page, and instead include a short introduction on the metadata page. I also removed a table from that story point which had aggregated data collection counts per quarter, as it didn't add any value to the story. In the second story point, I moved the line showing median price closer to the map to make it clearer it uses the same years. I also included more information in the title of that chart to make it more clear that it's showing median price per bedroom for all of San Francisco (per year). In the last story point, I changed the text in the point box from "Conclusion" to "Rental units taken off the traditional markets", as that is both more descriptive and more accurate. To make it more consistent with the three previous story points I added 3 sub-charts showing the distribution of "2&3 units" and "4% units" for "Units owned by multi-unit owners".

#### **Feedback**
Feedback from Slack user Iulia in the Udacity Data Science Slack channel \#P6-data-visualization received December 29, 2017:
"Here are few points that came to my mind while viewing your story :

1. Introduction (dashboard1 and 2): maybe it will be more viewer-friendly to make it more concise ? Just highlight the main points ?  Or even combine it with the second dashboard The dataset (metadata), which essentially is sort of introduction too?  Also if you state your goal as analysing the distribution of different types of rooms and hosts who  used Airbnb in San Francisco, during the years 2014 to mid-2017 and trends over time, I do not quite understand how does the graphs about records distribution per month and per quarter contribute to the goal ?
2. Median price per bedroom (dashboard 3):  It took me some time to understand the meaning of your graph “Median for all of SanFrancisco” . I think it would be better to add axes (or at least x-axis) to show that it is median pricing change over the years and maybe specify it in the header of the graph to make it more obvious t
3. Dashboards 4-5 : Loved the price ranking graph very much ! I think those graphs are very clear and viewer-friendly. 
4. Dashboards 6-9: I think there is a bit of inconsistency : in dashboards 6-8 you divide homeowners into 3 groups: 1 unit owners , 2&3 unit owners and 4+ unit owners but at the conclusion part you discuss only two groups : multi-unit owners and single unit owners."

Feedback from my Udacity mentor Rodrigo received December 29, 2017:
"I saw your story and looks great! You could use many types of graphics e visualizations. Good job! I liked the way you did the graphic for the 3 types of rooms along the years. Hopefully, you will receive many feedbacks to finish your project. Can you check something? Trying to save the file on your pc with the story page on the first one. Then when the people you sent the link open it the Introduction page will pop-up."

Feedback from my Udacity mentor Rodrigo on the version of the project I am submitting for review, received January 1, 2018:
"Your graphics are more readable and clear. I liked the highlight you gave in the last graphic."


#### **Resources**
**Primary Data Source**
http://tomslee.net/airbnb-data-collection-get-the-data (the San Francisco section)
**Data source for neighborhood map**
http://data.insideairbnb.com/united-states/ca/san-francisco/2017-10-02/visualisations/neighbourhoods.geojson

**Books**
*The Visual Display of Quantitative Information (2nd edition)* by Edward Tufte, 2001
*Storytelling with Data* by Cole Nussbaumer Knaflic, 2015

While working on the project, I consulted the following sources for visualization and Tableau knowledge:

 - Udacity courses Data Visualization Fundamentals, Design Principles, Creating Visualizations in Tableau and Telling stories with Tableau. 
 - Various forum threads at https://community.tableau.com
 - Various tutorial videos at https://www.tableau.com/learn/training
 - Various documentation from https://onlinehelp.tableau.com 
  - Including [Overview: Level of Details Expressions](https://onlinehelp.tableau.com/current/pro/desktop/en-us/calculations_calculatedfields_lod_overview.html)
