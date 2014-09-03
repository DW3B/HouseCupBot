HouseCupBot
===========

Reddit bot that keeps a running score for Hogwarts houses.

- When the bot detects a string like "50 points for Gryffindor" it will add 50 points to Gryffindor's running total.
    - Limits are set to (max: 500 points) and (min: 1 point) to prevent ridiculous scores and removing points for a house. 
- A winner is decided quarterly and all points are reset to 0. Winners will be tracked in a SQL database.
- Commands available:
    - "HouseCupBot !help"   : Will reply with a helpful comment to show what HouseCupBot can do.
    - "HouseCupBot !scores" : Will reply with the current scores for all houses.
    - "HouseCupBot !winners": Will reply with the pas winners of the House Cup.
    - All responses have the option of being sent via PM if it detects the "-PM" switch.
