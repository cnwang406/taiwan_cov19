import ui
#from __future__ import division
import clipboard

from urllib3 import PoolManager, request,disable_warnings,exceptions
disable_warnings(exceptions.InsecureRequestWarning)
import json
import math
import sys
import location
import dialogs
from time import sleep

MASK_CHILD_MAX=500
MASK_CHILD_MIN=0
MASK_ADULT_MAX=500
MASK_ADULT_MIN=0
DISTANCE_MAX=10
DISTANCE_MIN=0
MAX_COUNT_MAX=10
VERSION=1.01
HOMEGPS=[121.0185,24.833318]
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

def getGPS():
	if location.is_authorized():
		location.start_updates()
		sleep(1)
		loc=location.get_location()
		dialogs.alert(title='Location updated', message=f'[{loc["longitude"]:.3f},{loc["latitude"]:.3f}]\n or enter manually',button1='Got It', hide_cancel_button=True)
		return [loc['longitude'], loc['latitude']]
	else:
		dialogs.alert(title='Cannot get GPS', message='You have to enable it from setting/privacy or enter manually',button1='Got It', hide_cancel_button=True)
		return HOMEGPS

def btmGetGPS(sender):
	loc=getGPS()
	v=sender.superview
	v['txtHomeLon'].text,v['txtHomeLat'].text=str(loc[0]),str(loc[1])

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
	v['txtResult'].text =''
	v['txtResult'].text+=f'\n\nSearch Child >{v["txtChild"].text} Adult >{v["txtAdult"].text} within {v["txtDistance"].text}km, search nearest {v["txtMaxCount"].text} pharmacies from [{round(homeGPS[0],3)}, {round(homeGPS[1],3)}]'
	sleep(1)
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
	output+=f'\nmeet criteria {len(hits)} out of {len(allData)} pharmacies \n\n' 
	if len(hits)==0:
		output+='\n 🈚️🈚️🈚️ NO FOUND 🈚️🈚️🈚️'
	for hit in hits:
		if hit["mask_child"]>200:
			headings='‼️'
		else:
			headings=''
		output+=f'{headings}💊{hit["name"]} 童🧒🏻 {numberToEmoji(hit["mask_child"])}/ 大👩🏻 {hit["mask_adult"]} ({hit["distance"]:.2f}km) {headings}\n'
		output+=f'{hit["address"]} {hit["note"]}\n'
		output+='\n'
	output+='---[FINISHED]---'
	return output

def numberToEmoji(n):
	emojis=['0️⃣','1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣']
	ss=str(n)
	ret=''
	for s in ss:
		ret+=emojis[int(s)]
	return ret



# pyui
def uipage():
	return '''
[
  {
    "nodes" : [
      {
        "nodes" : [

        ],
        "frame" : "{{6, 20}, {114, 38}}",
        "class" : "Label",
        "attributes" : {
          "name" : "lChild",
          "frame" : "{{99, 314}, {150, 32}}",
          "uuid" : "AB3B4338-426C-4EF6-BD05-9168558A45A7",
          "class" : "Label",
          "alignment" : "left",
          "text" : "child",
          "font_size" : 18,
          "font_name" : "<System>"
        },
        "selected" : false
      },
      {
        "nodes" : [

        ],
        "frame" : "{{6, 63}, {114, 38}}",
        "class" : "Label",
        "attributes" : {
          "font_name" : "<System>",
          "frame" : "{{99, 314}, {150, 32}}",
          "uuid" : "AB3B4338-426C-4EF6-BD05-9168558A45A7",
          "class" : "Label",
          "alignment" : "left",
          "text" : "adult",
          "name" : "lAdult",
          "font_size" : 18
        },
        "selected" : false
      },
      {
        "nodes" : [

        ],
        "frame" : "{{214, 20}, {150, 34}}",
        "class" : "Slider",
        "attributes" : {
          "flex" : "W",
          "continuous" : true,
          "action" : "slider_action",
          "frame" : "{{74, 313}, {200, 34}}",
          "uuid" : "A5959A90-D808-4CDD-925D-A406BF55DBD9",
          "class" : "Slider",
          "value" : 0.5,
          "name" : "sChild"
        },
        "selected" : false
      },
      {
        "nodes" : [

        ],
        "frame" : "{{214, 62}, {150, 34}}",
        "class" : "Slider",
        "attributes" : {
          "flex" : "W",
          "continuous" : true,
          "action" : "slider_action",
          "frame" : "{{74, 313}, {200, 34}}",
          "class" : "Slider",
          "uuid" : "A5959A90-D808-4CDD-925D-A406BF55DBD9",
          "value" : 0.5,
          "name" : "sAdult"
        },
        "selected" : false
      },
      {
        "nodes" : [

        ],
        "frame" : "{{122, 20}, {84, 38}}",
        "class" : "TextField",
        "attributes" : {
          "name" : "txtChild",
          "autocorrection_type" : "default",
          "frame" : "{{74, 314}, {200, 32}}",
          "spellchecking_type" : "default",
          "class" : "TextField",
          "text" : "100",
          "background_color" : "RGBA(0.991597,1.000000,0.941176,1.000000)",
          "uuid" : "07B9B679-8049-45B6-82BF-3D44D5916A76",
          "alignment" : "left",
          "font_size" : 17,
          "font_name" : "<System>"
        },
        "selected" : false
      },
      {
        "nodes" : [

        ],
        "frame" : "{{122, 63}, {84, 38}}",
        "class" : "TextField",
        "attributes" : {
          "autocorrection_type" : "default",
          "font_name" : "<System>",
          "frame" : "{{74, 314}, {200, 32}}",
          "spellchecking_type" : "default",
          "class" : "TextField",
          "text" : "0",
          "background_color" : "RGBA(0.987395,1.000000,0.911765,1.000000)",
          "uuid" : "07B9B679-8049-45B6-82BF-3D44D5916A76",
          "alignment" : "left",
          "name" : "txtAdult",
          "font_size" : 17
        },
        "selected" : false
      },
      {
        "nodes" : [

        ],
        "frame" : "{{6, 109}, {114, 38}}",
        "class" : "Label",
        "attributes" : {
          "font_size" : 18,
          "frame" : "{{99, 314}, {150, 32}}",
          "uuid" : "AB3B4338-426C-4EF6-BD05-9168558A45A7",
          "class" : "Label",
          "alignment" : "left",
          "text" : "distance(km)",
          "name" : "lDistance",
          "font_name" : "<System>"
        },
        "selected" : false
      },
      {
        "nodes" : [

        ],
        "frame" : "{{122, 109}, {84, 38}}",
        "class" : "TextField",
        "attributes" : {
          "font_size" : 17,
          "autocorrection_type" : "default",
          "frame" : "{{74, 314}, {200, 32}}",
          "spellchecking_type" : "default",
          "class" : "TextField",
          "text" : "5",
          "background_color" : "RGBA(0.987395,1.000000,0.911765,1.000000)",
          "uuid" : "07B9B679-8049-45B6-82BF-3D44D5916A76",
          "alignment" : "left",
          "name" : "txtDistance",
          "font_name" : "<System>"
        },
        "selected" : false
      },
      {
        "nodes" : [

        ],
        "frame" : "{{212, 109}, {152, 34}}",
        "class" : "Slider",
        "attributes" : {
          "flex" : "W",
          "continuous" : true,
          "action" : "slider_action",
          "frame" : "{{74, 313}, {200, 34}}",
          "uuid" : "A5959A90-D808-4CDD-925D-A406BF55DBD9",
          "class" : "Slider",
          "value" : 0.5,
          "name" : "sDistance"
        },
        "selected" : false
      },
      {
        "nodes" : [

        ],
        "frame" : "{{6, 155}, {114, 38}}",
        "class" : "Label",
        "attributes" : {
          "font_name" : "<System>",
          "frame" : "{{99, 314}, {150, 32}}",
          "uuid" : "AB3B4338-426C-4EF6-BD05-9168558A45A7",
          "class" : "Label",
          "alignment" : "left",
          "text" : "max items",
          "font_size" : 18,
          "name" : "lMaxCount"
        },
        "selected" : false
      },
      {
        "nodes" : [

        ],
        "frame" : "{{122.00000000000001, 155}, {83.999999999999986, 38.000000000000028}}",
        "class" : "TextField",
        "attributes" : {
          "autocorrection_type" : "default",
          "font_name" : "<System>",
          "frame" : "{{74, 314}, {200, 32}}",
          "spellchecking_type" : "default",
          "class" : "TextField",
          "text" : "5",
          "background_color" : "RGBA(0.974790,1.000000,0.823529,1.000000)",
          "uuid" : "07B9B679-8049-45B6-82BF-3D44D5916A76",
          "alignment" : "left",
          "font_size" : 17,
          "name" : "txtMaxCount"
        },
        "selected" : false
      },
      {
        "nodes" : [

        ],
        "frame" : "{{212, 155}, {152, 34}}",
        "class" : "Slider",
        "attributes" : {
          "flex" : "W",
          "continuous" : true,
          "action" : "slider_action",
          "frame" : "{{74, 313}, {200, 34}}",
          "uuid" : "A5959A90-D808-4CDD-925D-A406BF55DBD9",
          "class" : "Slider",
          "value" : 0.5,
          "name" : "sMaxCount"
        },
        "selected" : false
      },
      {
        "nodes" : [

        ],
        "frame" : "{{14, 201}, {80, 32}}",
        "class" : "Button",
        "attributes" : {
          "uuid" : "9E014725-F5AC-49EE-9FAE-31FF3BDE95D4",
          "corner_radius" : 3,
          "background_color" : "RGBA(0.941176,0.957983,1.000000,1.000000)",
          "frame" : "{{134, 314}, {80, 32}}",
          "border_color" : "RGBA(0.823529,0.823529,1.000000,1.000000)",
          "border_width" : 2,
          "title" : "Go",
          "action" : "btm_Go",
          "alpha" : 1,
          "class" : "Button",
          "name" : "btmOk",
          "font_size" : 15
        },
        "selected" : false
      },
      {
        "nodes" : [

        ],
        "frame" : "{{6, 241}, {358, 419}}",
        "class" : "TextView",
        "attributes" : {
          "uuid" : "0584A3BA-03C7-49C9-A958-8643AE6AD2C9",
          "font_size" : 17,
          "frame" : "{{74, 230}, {200, 200}}",
          "border_color" : "RGBA(0.957983,1.000000,0.941176,1.000000)",
          "editable" : false,
          "alignment" : "left",
          "autocorrection_type" : "default",
          "text_color" : "RGBA(0.327731,0.058824,1.000000,1.000000)",
          "font_name" : "<System>",
          "spellchecking_type" : "default",
          "class" : "TextView",
          "name" : "txtResult",
          "flex" : "WH"
        },
        "selected" : false
      },
      {
        "nodes" : [

        ],
        "frame" : "{{104, 201}, {102, 32}}",
        "class" : "TextField",
        "attributes" : {
          "font_size" : 17,
          "frame" : "{{74, 314}, {200, 32}}",
          "spellchecking_type" : "default",
          "class" : "TextField",
          "uuid" : "957EB3C6-4E4E-4A46-96AB-8EB246B79247",
          "alignment" : "left",
          "text" : "0",
          "autocorrection_type" : "default",
          "name" : "txtHomeLon",
          "font_name" : "<System>"
        },
        "selected" : false
      },
      {
        "nodes" : [

        ],
        "frame" : "{{212, 201}, {102, 32}}",
        "class" : "TextField",
        "attributes" : {
          "font_name" : "<System>",
          "frame" : "{{74, 314}, {200, 32}}",
          "spellchecking_type" : "default",
          "class" : "TextField",
          "uuid" : "957EB3C6-4E4E-4A46-96AB-8EB246B79247",
          "alignment" : "left",
          "text" : "0",
          "autocorrection_type" : "default",
          "font_size" : 17,
          "name" : "txtHomeLat"
        },
        "selected" : false
      },
      {
        "nodes" : [

        ],
        "frame" : "{{322, 201}, {42, 32}}",
        "class" : "Button",
        "attributes" : {
          "action" : "btmGetGPS",
          "frame" : "{{145, 314}, {80, 32}}",
          "title" : "📡",
          "uuid" : "92AD293D-E7CC-4F62-996C-8B60D51B4D12",
          "class" : "Button",
          "name" : "btmGPS",
          "font_size" : 15
        },
        "selected" : true
      }
    ],
    "frame" : "{{0, 0}, {370, 660}}",
    "class" : "View",
    "attributes" : {
      "name" : "mask search",
      "enabled" : true,
      "background_color" : "RGBA(1.000000,1.000000,1.000000,1.000000)",
      "tint_color" : "RGBA(0.000000,0.478000,1.000000,1.000000)",
      "border_color" : "RGBA(0.000000,0.000000,0.000000,1.000000)",
      "flex" : ""
    },
    "selected" : false
  }
]

'''

if __name__ == '__main__':


	v = ui.load_view_str(uipage())
	v.name=f'MASK UI V{VERSION}'
	v.present('uipage')

	if location.is_authorized():
		location.start_updates()
		v['btmGPS'].alpha=1.0
		sleep(1)
		btmGetGPS(v['btmGPS'])
	
	else:
		v['btmGPS'].alpha=0.2



	v['txtResult'].text=TITLE



