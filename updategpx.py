import csv
from gpx import GPX, Waypoint

## in the gpx file, <sym> tag meaning : already flashed invaders are all "Dark_Green", unflashed invaders can be "None" (<50pts) or "Yellow" (50pts) or "Pink" (100pts) or "Dark_Red" (Destroyed) or "Brown" (Damaged)

#construct dicts from invaders-updated.csv (created by scraping script)
        
invadercsv = csv.DictReader(open('invaders-updated.csv'))
invaderstatus={}
invaderpoints={}
invaderurl={}

for row in invadercsv:
    invaderstatus[row['name']] = row['status_description']
    invaderpoints[row['name']] = row['points']
    invaderurl[row['name']] = row['picture_url']

#read invader.gpx map and update it
gpx = GPX.from_file("invader.gpx") 
wpt=gpx.waypoints

for key in invaderstatus:
    try:
        #add points and url to all entries in gpx for which there is info in the csv file
        for i in range(0,len(wpt)):
            if gpx.waypoints[i].name==key:
                gpx.waypoints[i].desc='points='+invaderpoints[key]+' image='+invaderurl[key] 

        #update invaders that have been restored and highlight all high points invaders that have not been flashed yet
        if (mapdict[key]=="Dark_Red" or mapdict[key]=="None") and invaderstatus[key]=="OK":
            for i in range(0,len(wpt)):
                if gpx.waypoints[i].name==key :
                    gpx.waypoints[i].sym="None"
                    if invaderpoints[key]=='100': gpx.waypoints[i].sym='Pink'
                    if invaderpoints[key]=='50': gpx.waypoints[i].sym='Yellow'

        #updated destroyed or not flashable invaders that have not been flashed yet
        if (mapdict[key]=="None" or mapdict[key]=="Yellow" or mapdict[key]=="Pink") and invaderstatus[key]!="OK":
            for i in range(0,len(wpt)):
                if gpx.waypoints[i].name==key:
                    if invaderstatus[key]=="Détruit !" : gpx.waypoints[i].sym="Dark_Red"
                    if invaderstatus[key]=='Dégradé' : gpx.waypoints[i].sym='Brown'
        
    except KeyError:
        pass
