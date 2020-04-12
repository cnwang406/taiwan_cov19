import ui
#from __future__ import division
import clipboard

from urllib3 import PoolManager, request,disable_warnings,exceptions
disable_warnings(exceptions.InsecureRequestWarning)
import json
import math
import sys
import location
from time import sleep

MASK_CHILD_MAX=500
MASK_CHILD_MIN=0
MASK_ADULT_MAX=500
MASK_ADULT_MIN=0
DISTANCE_MAX=10
DISTANCE_MIN=0
MAX_COUNT_MAX=10
VERSION=1.0
TITLE=(f'''
**********************************
Search Children Masks UI
	v.{VERSION}
based on Pythonista IOS
source : gov.tw

	by cnwang, 2020/04
**********************************
''')


def slider_action(sender):
	v=sender.superview

	maskChild=int(v['sChild'].value*MASK_CHILD_MAX)
	maskAdult=int(v['sAdult'].value*MASK_ADULT_MAX)
	distance=round(v['sDistance'].value*DISTANCE_MAX,2)
	maxCount=int(v['sMaxCount'].value*MAX_COUNT_MAX)
	#v['txtResult'].text=f'Search {maskChild}/{maskAdult} within {distance}km, search nearest {maxCount} pharmacies'


	v['txtChild'].text=str(maskChild)
	v['txtAdult'].text=str(maskAdult)
	v['txtDistance'].text=str(distance)
	v['txtMaxCount'].text=str(maxCount)

	
def btm_Go(sender):

	v=sender.superview	
	sender.alpha=0.1
	if location.is_authorized():
		location.start_updates()
		loc=location.get_location()
		homeGPS=[loc['longitude'], loc['latitude']]
	else:
		homeGPS=[float(v['txtHomeLon'].text),float(v['txtHomeLat'].text)]
	#print(f'\n\nSearch Child:{v["txtChild"].text} Adult:{v["txtAdult"].text} within {v["txtDistance"].text}km, search nearest {v["txtMaxCount"].text} pharmacies from [{homeGPS[0]}, {homeGPS[1]}]')
	v['txtResult'].text =TITLE
	v['txtResult'].text+=f'\n\nSearch Child:{v["txtChild"].text} Adult:{v["txtAdult"].text} within {v["txtDistance"].text}km, search nearest {v["txtMaxCount"].text} pharmacies from [{round(homeGPS[0],3)}, {round(homeGPS[1],3)}]'
	sleep(3)
	allData=getPharmaciesData()

	hits=filterOut(allData,homeGPS, distance=float(v['txtDistance'].text), mask_child=int(v['txtChild'].text), mask_adult=int(v['txtAdult'].text), maxCount=int(v['txtMaxCount'].text))

	v['txtResult'].text +=resultText(hits,allData)
	sleep(1)
	sender.alpha=1.0

def getPharmaciesData():
	pharmaciesUrl=r'https://raw.githubusercontent.com/kiang/pharmacies/master/json/points.json'
	http=PoolManager()

	r=http.request('GET',pharmaciesUrl)
	pharmaciesData=json.loads(r.data)['features']


	allData=[]
	for phd in pharmaciesData:
		data={}
		geo=phd['geometry']['coordinates']
		name = phd['properties']['name']
		address=phd['properties']['address']
		mask_adult=phd['properties']['mask_adult']
		mask_child=phd['properties']['mask_child']
		available = phd['properties']['available']
		note = phd['properties']['note']
		data={'name':name, 'address':address, 'mask_adult':mask_adult,'mask_child':mask_child, 'available':available, 'note':note,'geometry':geo}
		allData.append(data)
	return allData

def geoDistance(loc1,loc2):
    import math

    R = 6373.0
    #radius of the Earth

    lat1 = math.radians(loc1[1])
    #coordinates
    lon1 = math.radians(loc1[0])
    lat2 = math.radians(loc2[1])
    lon2 = math.radians(loc2[0])

    dlon = lon2 - lon1
    #change in coordinates
    dlat = lat2 - lat1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    #Haversine formula
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c

    return distance

def calcDistances(loc):
	for phd in allData:

		distance=geoDistance(loc,phd['geometry'])
		print (distance)
def filterOut(allData,loc, distance=3, mask_child=100, mask_adult=200, maxCount=5):
	hits=[]
	hitsCount=0
	for phd in allData:
		phdDistance=geoDistance(loc, phd['geometry'])
		if phdDistance<=distance:
			if (phd['mask_adult']>=mask_adult and phd['mask_child']>=mask_child):
				phd['distance']=phdDistance
				hits.append(phd)
				hitsCount+=1
				#print (phd)
		#if hitsCount>=maxCount:
		#	break
	hits=sorted(hits, key=lambda i: (i['distance']))

	return hits
def resultText(hits,allData):
	output=''
	output+=f'meet criteria {len(hits)} out of {len(allData)} pharmacies \n' 
	if len(hits)==0:
		output+='\n 🈚️🈚️🈚️ NO FOUND 🈚️🈚️🈚️'
	for hit in hits:
		if hit["mask_child"]>200:
			headings='‼️'
		else:
			headings=''
		output+=f'{headings}💊{hit["name"]} 童🧒🏻 {hit["mask_child"]}/ 大👩🏻 {hit["mask_adult"]} ({hit["distance"]:.2f}km) {headings}\n'
		output+=f'{hit["address"]} {hit["note"]}\n'
		output+='\n'
	output+='---[FINISHED]---'
	return output


if __name__ == '__main__':
	if location.is_authorized():
		location.start_updates()	

	v = ui.load_view()
	v.present('sheet')

	v['txtResult'].text=TITLE
