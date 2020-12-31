# mlb-franchise-bip
A quantitative replication/exploration of Tim Britton's article in The Athletic called "What’s the best starting rotation built from pitchers who didn’t play together?" using binary integer programming

Article: https://theathletic.com/1816605/2020/12/28/best-pitchers-best-rotations-mlb/

### Data

The data are stored in two folders: `franchise` and `player`. The `franchise` folder contains 1 file per team where each file contains a list of the top pitchers in franchise history (by fWAR). The `player` folder contains 1 file per player where each file contains the team history for that player (which team he was on and during which seasons).

The `data` directory also contains a file called `players.csv`. This file contains the name and Fangraphs ID of every player that appears in the franchise data. These are the players whose individual data must be scraped from Fangraphs.

The `franchise` data was downloaded manually from Fangraphs for each team using the link below. Using the leaderboard functionality, select the team and adjust the year range to encompass all the years that franchise has been in existence.

https://www.fangraphs.com/leaders.aspx?pos=all&stats=sta&lg=all&qual=y&type=6&season=2020&month=0&season1=1901&ind=0&team=9&rost=0&age=0&filter=&players=0&startdate=&enddate=
