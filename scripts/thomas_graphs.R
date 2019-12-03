library(tidyverse)
library(parcoords)
path = 'Documents/Cours/Exploratory\ Data\ Analysis/Code/Final\ Project/datasets/raw/dataset1_4000.csv'
#load dataframe and rremove rows without genres
df <- filter(read.csv(path, sep =";"), genres != '')
#get first genre for every movie (most relevant)
single_genres <- do.call(rbind,strsplit(as.character(df$genres),'\\|'))[,1]
df1 <- data.frame(genres = single_genres, select(df, -genres))

#all genres
unique(df1$genres)

#plot (number of movies for each genre)
genres_info <- df1 %>% 
               count(genres) %>% 
               mutate(perc =  n / nrow(df1))

ggplot(genres_info, aes(x = reorder(genres,perc), y = perc)) + geom_bar(stat = "identity") + coord_flip()
ggplot(genres_info, aes(x=reorder(genres,n), y=n)) + geom_bar(stat = 'identity') + coord_flip()

#5 most present genres : Comedy, Action, Drama, Adventure, Horror
genres_under_study <- arrange(genres_info,-n)[1:5,'genres'][['genres']]
df2 <- filter(df1, genres %in% as.vector(genres_under_study))
df3 <- select(df2, genres, popularity, budget, revenue, vote_count, vote_average)
df3 %>% 
  group_by(genres) %>%
  summarise(popularity = mean(popularity), budget = mean(budget), revenue = mean(revenue), 
            mark = sum(vote_average*vote_count)/sum(vote_count)) -> results

parcoords(data = results, 
          rownames = FALSE, 
          brushMode = "1D-axes", 
          queue = T, 
          reorderable = T)

#group by genres for year t and year t+2
df4 <- select(df2, release_date, genres, popularity, budget, revenue, vote_count, vote_average)
years <- as.numeric(do.call(rbind,strsplit(as.character(df4$release_date), '-'))[,1])
df5 <- data.frame(years = years, select(df4, -release_date))

gap <- 3

df5 %>%
  group_by(genres,years) %>%
  summarize(revenue_generated_t1 = sum(revenue), n_movies_t1 = n()) %>%
  ungroup() -> results1
results1$n_movies_t2 <- NA

for (year in years){
    for (genre in genres_under_study){
       tmp <- results1[results1$years == year-gap & results1$genres == genre,]['n_movies_t1']
       results1[results1$years == year & results1$genres == genre,]['n_movies_t2'] <- as.numeric(tmp)
    }
}
results1 <- na.omit(results1)

ggplot(data = results1, aes(x = log(revenue_generated_t1), y = n_movies_t2, color = genres)) + geom_point()
