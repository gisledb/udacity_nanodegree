ff <- factor(substring("statistics", 1:10, 1:10), levels = letters)
factor(ff)

factor(letters[1:20], labels = "cat")
LETTERS[3:1]
z <- factor(LETTERS[3:1], ordered = TRUE)
z
#we will set the seed to equal 124 in order to make the results reproducible.
set.seed(124)
schtyp <- sample(0:1, 20, replace = TRUE)
schtyp

is.factor(schtyp)
is.numeric((schtyp))
#creating factor variable
schtyp.f <- factor(schtyp, labels=c("private", "public"))
schtyp.f

is.factor(schtyp.f)

#Creating string variable for socio-economic status
ses <- c("low", "middle", "low", "low", "low", "low", "middle", "low", "middle",
         "middle", "middle", "middle", "middle", "high", "high", "low", "middle",
         "middle", "low", "high")
is.factor(ses)
is.character((ses))
#Creating factor variable based on ses
ses.f.bad.order <- factor(ses)
is.factor(ses.f.bad.order)
levels(ses.f.bad.order)
#problem: incorrect order of levels
#Fixing level order
ses.f <- factor(ses, levels = c("low", "middle", "high"))
ses.f
levels(ses.f)

#Creating ordered factor variables
ses.order <- ordered(ses, levels = c("low", "middle", "high"))
ses
ses.order
is.factor(ses.order)

ses.f <- ses.f.new
read <- c(34, 39, 63, 44, 47, 47, 57, 39, 48, 47, 34, 37, 47, 47, 39, 47,
          47, 50, 28, 60)

# combining all the variables in a data frame
combo <- data.frame(schtyp, schtyp.f, ses, ses.f, read)
combo

