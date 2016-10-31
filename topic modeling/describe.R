table(df$datetime_scraped, df$site)

df$batch <- df$datetime_scraped
df$datetime_scraped <- as.POSIXlt(df$datetime_scraped, "GMT")
table(df$datetime_scraped$hour)