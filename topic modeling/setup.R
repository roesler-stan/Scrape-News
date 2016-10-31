rm(list = ls())
options(scipen=999)

# set the working directory to the data folder
directory <- "/Users/katharina/Dropbox/Projects/Scrape News/Data/"
setwd(directory)
infile <- "data.csv"
image <- paste0(directory, "analysis.Rdata")

# Load the image, if it's present and up to date
load(image)

# Otherwise, read it and save the image
df <- read.csv(infile)
save.image(image)
