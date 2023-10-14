# invader-spotter-scraper
Space Invaders Spotter - Street Art website scraper

These scripts do not give you gps locations of invaders. If you have a gpx file with lat/lon of referenced invaders it will update the status of invaders and add points / image informations in your gpx.


3 scripts

Cleangpx.py
Needs to be run once to clean your gpx file before running the other scripts. Takes your invader.gpx file and creates and invader-clean.gpx file. Rename it to invader.gpx if all went ok.

Scraper.py
Gets points / status / most image urls for all invaders listed on invader-spotter website and puts them into an "invaders-updated.csv" file

Updategpx.py
Takes your (cleaned) invader.gpx file and your invaders-updated.csv file and creates and invader-updated.gpx file. 
