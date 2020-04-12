TITLE="""
*************************
Search Children Masks 

based on Pythonista IOS
source : gov.tw

	by cnwang, 2020/04
************************
"""

from urllib3 import PoolManager, request,disable_warnings,exceptions
disable_warnings(exceptions.InsecureRequestWarning)
import json
import math
import sys
if sys.platform=='ios':
	import location
	location.start_updates()
	loc=location.get_location()
	homeGPS=[loc['longitude'], loc['latitude']]
else:
	homeGPS=[121.018530,24.833318]

url=r'https://quality.data.gov.tw/dq_download_json.php?nid=116285&md5_url=2150b333756e64325bdbc4a5fd45fad1'


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
def filterOut(loc, distance=3, mask_child=100, mask_adult=200, maxCount=5):
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


if __name__=='__main__':

	DISTANCE=5.0
	MASK_CHILD=100
	MASK_ADULT=0
	MAXCOUNT=5

	print (TITLE)

	print ('Start querying...')
	print (f'here is [{homeGPS[0]:.4f} ,{homeGPS[1]:.4f}] , platfrom is {sys.platform}')
	print (f'with criteria : distance <={DISTANCE:.2f}km, CHILDREN >={MASK_CHILD}, ADULT>={MASK_ADULT}, max {MAXCOUNT} pharmacies')
	allData=getPharmaciesData()
	if sys.platform=='ios':
		loc=location.get_location()
		homeGPS=[loc['longitude'], loc['latitude']]
	else:
		homeGPS=[121.018530,24.833318]

	print('-'*30)
	hits=filterOut(loc=homeGPS, distance=DISTANCE, mask_child=MASK_CHILD, mask_adult=MASK_ADULT,maxCount=MAXCOUNT)
	print(f'meet criteria {len(hits)} out of {len(allData)} pharmacies \n' )
	for hit in hits:
		if hit["mask_child"]>200:
			headings='!!! '
		else:
			headings=''
		print (f'{headings}{hit["name"]} 童 {hit["mask_child"]}/ 大 {hit["mask_adult"]} ({hit["distance"]:.2f}km) {headings}')
		print (f'{hit["address"]} {hit["note"]}')
		print ('\n')
	print ('---[FINISHED]---')
