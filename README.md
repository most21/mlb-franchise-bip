# mlb-franchise-bip
A quantitative replication/exploration of Tim Britton's article in The Athletic called "What’s the best starting rotation built from pitchers who didn’t play together?" using binary integer programming

Article: https://theathletic.com/1816605/2020/12/28/best-pitchers-best-rotations-mlb/

### Data

The data are stored in two folders: `franchise` and `player`. The `franchise` folder contains 1 file per team where each file contains a list of the top pitchers in franchise history (by fWAR). The `player` folder contains 1 file per player where each file contains the team history for that player (which team he was on and during which seasons).

The `data` directory also contains a file called `players.csv`. This file contains the name and Fangraphs ID of every player that appears in the franchise data. These are the players whose individual data must be scraped from Fangraphs.

The `franchise` data was downloaded manually from Fangraphs for each team using the link below. Using the leaderboard functionality, select the team and adjust the year range to encompass all the years that franchise has been in existence.

https://www.fangraphs.com/leaders.aspx?pos=all&stats=sta&lg=all&qual=y&type=6&season=2020&month=0&season1=1901&ind=0&team=9&rost=0&age=0&filter=&players=0&startdate=&enddate=


### Files & Other Notes

The `scrape_player_data.py` file contains code to scrape individual player data from Fangraphs.com. When run, this file will scrape data for each player in the `players.csv` data file with a 3 second delay between each player. As there are ~5000 players in the dataset, this can take approximately 4-5 hours to run.

The `teammate_matrix.py` file contains code to construct a binary adjacency matrix for each franchise, representing the teammate relationship between all players in the dataset. Teammates are calculated based on overlapping seasons spent with the same franchise, including partial seasons resulting from trade acquisitions. However, the data lack sufficient granularity to account for the edge case where Player A is traded from Team C prior to Player B being acquired by Team C in the same season. Technically, Players A & B should not be considered teammates in this (presumably rare) case.

The `bip.py` is the main driver file and contains the code that sets up and solves the optimization problem, using the teammate adjacency matrix to build the constraints. When this file is run, the optimal all-time rotation will be computed for each of the 30 active franchises. Note that integer programming is NP-Complete, so the solver may take a long time to run, especially for older franchises that have larger data. To reduce the size of the data, we might only consider the players in franchise history that have positive WAR.

The `testing.py` file contains code to validate the results for each team by comparing them to the "ground truth" in Britton's article. Discrepancies are possible and not necessarily caused by a bug in the code.
