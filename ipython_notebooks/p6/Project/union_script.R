#install.packages('stringr')
library(stringr)

getwd()
setwd(paste0('/Users/ggaasemyr/Documents/udacity/ipython_notebooks/',
'p6/project/data_files/san_francisco'))

file_list <- list.files()
#removing folder
file_list <- file_list[file_list != "unedited_files"]
#removing file with corrupt data (0 as price for >99% of records)
file_list <- file_list[file_list != 
                         "tomslee_airbnb_san_francisco_0115_2015-06-05.csv"]

test_list = character()

rm(dataset)

for (file in file_list){
  
  test_list <- c(test_list,file)
  date = str_sub(file,-14,-5)
  # if the merged dataset doesn't exist, create it
  if (!exists("dataset")){

    dataset <- read.table(file, 
                          header=TRUE, sep=",")
    dataset$date_collected <- date
  } else  {
  # if the merged dataset does exist, append to it
    temp_dataset <-read.table(file, header=TRUE, sep=",")
    temp_dataset$date_collected <- date
    dataset<-rbind(dataset, temp_dataset)
    rm(temp_dataset)
  }
  
}

tail(test_list)
length(file_list) == length(test_list)
file_list %in% test_list

tail(dataset)

nrow(dataset)

#Taking a look at the count per file
View(table(dataset$date_collected))

write.csv(dataset, file = 'airbnb_union.csv', row.names = FALSE)

subset(dataset, date_collected == '2017-07-10')$price

seq(0,1,0.1)



quantile(subset(dataset, date_collected == '2015-08-21')$price, 
         seq(0,1,0.01))
quantile(subset(dataset, date_collected != '2015-08-21')$price, 
         seq(0,1,0.01))

