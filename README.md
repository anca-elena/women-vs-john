# Women vs John 
Data visualisation project, using dash, numpy, pandas and plotly, which won the Hack4Her 2023 hackathon. \
Made with [Elena Stroiu](https://github.com/EStroiu) within a weekend, reusing some code from Hack4Her 2022 (kudos to [Red](https://github.com/RedKinda)).

## Usage
There are two separate files. To see a map of countries, run `python3 world_view.py`. To see a scatterplot, run `python3 john-salary.py`. 

## Dataset 
We were given a [dataset](https://www.levels.fyi/js/salaryData.json) from [levels.fyi](https://www.levels.fyi/?compare=Adobe,Amazon,IBM&track=Software%20Engineer). 
This data contains information about gender, years of experience, years within a company, and compensation given (in stocks, salary, bonuses etc.). \
Unfortunately, data about age, level of education, ethnicity etc. was not available to us.

### ! Fair warning !
This data is self-reported, often incomplete and sometimes plain wrong. We tried to clean up the data and fix discrepancies (e.g.: some reported salary as "100k", others as "100000"). \
However, the data provided is not enough for us to draw informed conclusions from, though it is an interesting exercise in visualisation.

## Visualisation 
The data can be viewed both in a scatterplot and as a choropleth map (both of the world and of the US, since most of the data came from North America). It can be filtered via position and company.

## Presentation
You can find our PP presentation for the project in [this file](./Hack4Her%202023.pptx). It is mostly just the main points with little context, but you can enjoy the dinosaurs.
