from gpx import GPX, Waypoint
import re

gpx = GPX.from_file("invader.gpx")
wpt=gpx.waypoints

INVADER_ID_PATTERN = r'([A-Z]+_[0-9]{2,4})'

for i in range(0,len(wpt)):
      
    if  gpx.waypoints[i].name == None : gpx.waypoints[i].name = "ERR_404" #change empty names to ERR_404
    else:
        gpx.waypoints[i].name=gpx.waypoints[i].name.split(' ')[0]
        match = re.search(INVADER_ID_PATTERN, gpx.waypoints[i].name)
        gpx.waypoints[i].name = match.group(1) if match else "ERR_404" #change random incorrect names to ERR_404
      
        #change padding (PA_0012 / LDN_02) to match pattern from invader spotter website (PA_12 / LDN_12)
        avant=gpx.waypoints[i].name     
        if int(gpx.waypoints[i].name.split('_')[1])<10:
            gpx.waypoints[i].name=gpx.waypoints[i].name.split('_')[0]+'_0'+str(int(gpx.waypoints[i].name.split('_')[1]))
        else:
            gpx.waypoints[i].name=gpx.waypoints[i].name.split('_')[0]+'_'+str(int(gpx.waypoints[i].name.split('_')[1]))
        apres=gpx.waypoints[i].name
        print(avant+' -> '+apres) #check modification

gpx.to_file("invader-clean.gpx")
