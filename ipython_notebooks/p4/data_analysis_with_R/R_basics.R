getwd()
setwd("/Users/ggaasemyr/Documents/udacity/ipython_notebooks/p4/data_analysis_with_R/")

statesInfo <- read.csv('stateData.csv')

stateSubset <- subset(statesInfo, state.region == 1)
head(stateSubset,2)
dim(stateSubset)
#Alternative way to subset:
#dataset[ROWS,COLUMNS]
statesInfo[statesInfo$state.region == 1, ] #same as above
stateSubsetBracket <- statesInfo[statesInfo$state.region == 1, ]
head(stateSubsetBracket)
dim(stateSubsetBracket)

View(subset(statesInfo,illiteracy > 1.5))

#13. Factor Variables
reddit <- read.csv2('reddit.csv', sep=',')

str(reddit)
summary(reddit)

reddit_educated = subset(reddit, education == "Bachelor's degree" | education == "Graduate or professional degree")
reddit_some_college = subset(reddit,education == 'Some college')

prop.table(summary(reddit$marital.status))
prop.table(summary(reddit_some_college$marital.status))
summary(reddit_educated$marital.status)

?prop.table(table(reddit_educated$marital.status))

#14. Quiz: Ordered Factors

levels(reddit$age.range)

library(ggplot2)
qplot(data=reddit, x = age.range)
#Would be good to make the age range variables above displayed in correct order (ordered factor)

qplot(data=reddit, x=income.range)


#15. Quiz: Setting levels of ordered factors

levels(reddit$income.range)
ordered_levels <- factor(reddit$income.range, levels = c("Under $20,000", "$20,000 - $29,999", 
                         "$30,000 - $39,999", "$40,000 - $49,999", "$50,000 - $69,999", 
                         "$70,000 - $99,999", "$100,000 - $149,999", "$150,000 or more"))

reddit$age.range[1]
reddit$age.range <- factor(reddit$age.range, levels = c("Under 18", "18-24", "25-34", "35-44", 
                                    "45-54","55-64", "65 or Above"))
qplot(data=reddit, x=age.range)

#Also possible to use ordered()
reddit$age.range <- ordered(reddit$age.range, levels = c("Under 18", "18-24", "25-34", "35-44", 
                                                        "45-54","55-64", "65 or Above"))
qplot(data=reddit, x=age.range)

reddit$income.range <- ordered(reddit$income.range, levels = c("Under $20,000", "$20,000 - $29,999", 
                                                           "$30,000 - $39,999", "$40,000 - $49,999", 
                                                           "$50,000 - $69,999","$70,000 - $99,999", 
                                                           "$100,000 - $149,999", "$150,000 or more"))
qplot(data=reddit, x=income.range)
