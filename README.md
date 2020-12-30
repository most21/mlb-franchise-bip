# mlb-franchise-bip
A quantitative replication of Tim Britton's article in The Athletic called "What’s the best starting rotation built from pitchers who didn’t play together?" using binary integer programming

Article: https://theathletic.com/1816605/2020/12/28/best-pitchers-best-rotations-mlb/

### Data

The data are stored in two folders: `franchise` and `player`. The `franchise` folder contains 1 file per team where each file contains a list of the top pitchers in franchise history (by fWAR). The `player` folder contains 1 file per player where each file contains the team history for that player (which team he was on and during which seasons).