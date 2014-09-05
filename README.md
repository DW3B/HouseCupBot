HouseCupBot
===========

Reddit bot that keeps a running score for Hogwarts houses.

- When the bot detects a string like "50 points for Gryffindor" it will add 50 points to Gryffindor's running total.
    - Limits are set to (max: 200 points/ min: 1 point) to prevent ridiculous scores and removing points for a house. 
    - Awarding of points is rate-limited per redditor. If you try to give a house points too fast your house (that you are trying to add points to) will have points removed.
- A winner is decided quarterly and all points are reset to 0. Winners will be tracked via SQL database.
- Commands available:
    - "HouseCupBot !winners": Will reply via PM with the past winners of the House Cup.
