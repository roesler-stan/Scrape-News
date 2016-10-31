library(stm)

setwd("/Users/katharina/Dropbox/Projects/Scrape News/Output")

# Only include words occuring at least MIN_WORDS times
MIN_WORDS = 1
NUM_TOPICS = 5

cols <- names(df)[names(df) != "text"]
# Creates 528 documents, despite original 675
processed <- textProcessor(df$text, meta = df[, cols], striphtml = T)
out <- prepDocuments(processed$documents, processed$vocab, processed$meta,
                     lower.thresh = MIN_WORDS)

prevFit <- stm(out$documents, out$vocab, K = NUM_TOPICS,
               prevalence =~ site, max.em.its = 75,
               data = out$meta, init.type = "Spectral")

# Top words for each topic
labelTopics(prevFit)
# Word cloud for topic 1
cloud(prevFit, topic = 1, scale = c(3, .25))
png('cloud3.png')
cloud(prevFit, topic = 3, scale = c(4, 0.5))
title("Topic 3")
dev.off()
png('cloud5.png')
cloud(prevFit, topic = 5, scale = c(4, 0.5))
title('Topic 5')
dev.off()


# A sentence for topic 3 - doesn't work
thoughts1 <- findThoughts(prevFit, texts = out$documents, n = 1, topics = 3)
plot(thoughts1)

thoughts1 <- findThoughts(prevFit, texts = out$documents, n = 1, topics = 1)$docs[[1]]
png("topic1.png")
plotQuote(thoughts1, main = "Topic 1", width = 100)
dev.off()

# Topic proportions by site and associated words
plot.STM(prevFit, text.cex = 0.6, n = 4, xlim = c(0, 0.7))
plot.STM(prevFit, text.cex = 0.6, n = 4, xlim = c(0, 0.7), labeltype = "score")
plot.STM(prevFit, type = "labels", text.cex = 0.6, n = 5)
plot.STM(prevFit, type = "labels", text.cex = 0.6, labeltype = "score", n = 5)

# Estimate site likelihood by topic
prep <- estimateEffect(1:NUM_TOPICS ~ site, prevFit, meta = out$meta, uncertainty = "Global")
png('topic_bysite.png')
plot.estimateEffect(prep, covariate = "site", topics = seq(1, NUM_TOPICS),
                    model = prevFit, method = "difference",
                    cov.value1 = "CNN", cov.value2 = "Fox", xlab = "CNN ... Fox",
                    labeltype = "custom", custom.labels = paste(seq(NUM_TOPICS)),
                    main = "Topic Prevalence by Site")
dev.off()


# Consider the words in each site - takes a long time (EM iteration)
content <- stm(out$documents, out$vocab, K = NUM_TOPICS,
               prevalence =~ site, content =~ site,
               max.em.its = 75, data = out$meta, init.type = "Spectral")

png("topic3_sites.png")
plot.STM(content, type = "perspectives", topics = 3)
title("Topic 3 by New Source")
dev.off()
plot.STM(content, type = "perspectives", topics = c(3,5))
