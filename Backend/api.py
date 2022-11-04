'''
Written by Noe Soto, 11/4/2022 
'''
from flask import Flask, request, abort
from flask_cors import CORS
import requests
import geocoder
import math
import datetime
#By default, the carbon-aware-sdk webAPI will be hosted through this link, this link is to get the lowest carbon rate region:
URL = "http://localhost:5073/emissions/bylocations/best?location=francecentral&location=westus&location=eastus&location=australiaeast&location=uksouth&"
#the two following links are to get the information for all the regions.
ALL_REGION_URL = "http://localhost:5073/emissions/bylocations?location=francecentral&location=westus&location=eastus&location=australiaeast&location=uksouth&"
OFF_URL = "http://localhost:5073/emissions/bylocations/best?location="

#these are the latitudes and longitudes of the regions used in this demo
long_lat_list = [[48.8566, 2.3522], [37.7749, -122.4194], [36.6676, -78.3875], [-33.8688, 151.2093], [51.5072, 0.1276]]
region_list = ['francecentral', 'westus', 'eastus', 'australiaeast', 'uksouth']
region_names = ['FR', 'CAISO_NORTH', 'PJM_ROANOKE', 'NEM_NSW', 'UK']

#this is so we don't lose the counter for "impact" in case of a shutoff.
#we read the text file on start up.
file_read = open('info.txt')
user_requests = int(file_read.readline())
grams_total = float(file_read.readline())
grams_saved = float(file_read.readline())
file_read.close()

app = Flask(__name__)
cors = CORS(app)

#returns the region info for a single region
def region_single(region_name):
    now = datetime.datetime.now()
    dateStr = str(now)
    dateStr = dateStr[:dateStr.rindex(":")].replace(" ", "T").replace(":", "%3A")
    request_carbon = requests.get(url=OFF_URL+region_name+"&time="+str(dateStr))
    return request_carbon.json()

#degrees to radians
def deg_to_rad(deg):
    return deg * (math.pi/180)

#helper function that uses the "Haversine" formula to calculate the distance bettween two points on a sphere (i.e., two locations on Earth)
#it will be used to get find the nearest location relative to where the user is located at.
def get_distance(lat1, lon1, lat2, lon2):
    R = 6371 #radius of Earth (in km)
    dLat = deg_to_rad(lat2 - lat1)
    dLon = deg_to_rad(lon2 - lon1)
    a = math.sin(dLat/2) * math.sin(dLat/2) + math.cos(deg_to_rad(lat1)) * math.cos(deg_to_rad(lat2)) * math.sin(dLon/2) * math.sin(dLon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

#checking to see if everything was passed, if not then abort to 404
def parameters(args):
    if 'ip' not in args:
        return False
    if 'eco_toggle' not in args:
        return False
    if 'text' not in args:
        return False
    if 'src_lang' not in args:
        return False
    if 'tgt_lang' not in args:
        return False
    return True

#this route is to be used on startup to get the current number of requests
@app.route('/counter', methods = ['GET'])
def getCounters():
    return {'total_requests': user_requests, 'total_grams': grams_total, 'saved_grams': grams_saved}

#this route is when a user actually submits a request to be translated.
@app.route('/translation', methods = ['GET'])
def translate():
    args = request.args
    args = args.to_dict()

    #checking to see if all the proper parameters were received.
    if not(parameters(args)):
        abort(404)
    
    '''
    from here, I will depending on if they have eco_toggle or not:
    NO ECO: find the nearest server location based on their ip and send the information there.

    ECO: find the lowest carbon intensity by calling the web API and sending the request there.
    '''
    global user_requests
    global grams_total
    global grams_saved
    json_return = dict()
    #Getting the current time and date to call what the lowest carbon rating region is at the current time.
    now = datetime.datetime.now()
    dateStr = str(now)
    dateStr = dateStr[:dateStr.rindex(":")].replace(" ", "T").replace(":", "%3A")

    geo_ip = geocoder.ip(args.get('ip'))
    geo_ip = geo_ip.latlng
    smallest = float('inf')
    smallest_ind = 0
    #getting nearest location, this is used for the bar chart, and for finding how many grams of carbon was saved.
    for i in range(len(long_lat_list)):
        temp = get_distance(geo_ip[0], geo_ip[1], long_lat_list[i][0], long_lat_list[i][1])
        if temp < smallest:
            smallest = temp
            smallest_ind = i
    closest = {'closest_region': region_names[smallest_ind]}

    if args.get('eco_toggle') == 'true':
        request_carbon = requests.get(url = (URL + "time="+dateStr)).json() #calling the carbon-aware-sdk by sending the request.

        json_return = {'data': [args.get('text'), args.get('src_lang'), args.get('tgt_lang'), request_carbon[0]['rating']]} #what will be sent to VM
        if request_carbon[0]['location'] == 'FR':
            #France
            request_france = requests.post('https://8498c208d14fafeb.gradio.app/api/predict', json=json_return).json()
            json_return = request_france['data'][0] | {'region': 'FR'}

        elif request_carbon[0]['location'] == 'CAISO_NORTH':
            #West US
            request_caiso = requests.post('https://665fd2541ffc38a4.gradio.app/api/predict', json=json_return).json()
            json_return = request_caiso['data'][0] | {'region': 'CAISO_NORTH'}

        elif request_carbon[0]['location'] == 'PJM_DC':
            #East US
            request_dc = requests.post('https://9691c098558aaa98.gradio.app/api/predict', json=json_return).json()
            json_return = request_dc['data'][0] | {'region': 'PJM_ROANOKE'}

        elif request_carbon[0]['location'] == 'NEM_NSW':
            #Australia, NSW
            request_aus = requests.post('https://ba6858ad805d56a4.gradio.app/api/predict', json=json_return).json()
            json_return = request_aus['data'][0] | {'region': 'NEM_NSW'}

        elif request_carbon[0]['location'] == 'UK':
            #London
            request_london = requests.post('https://7829c30c5c41724f.gradio.app/api/predict', json=json_return).json()
            json_return = request_london['data'][0] | {'region': 'UK'}
    else:
        #even though eco_toggle is off, we still query the SDK in order to get the rating of the nearest location.
        rating_num = region_single(region_list[smallest_ind])
        json_return = {'data': [args.get('text'), args.get('src_lang'), args.get('tgt_lang'), rating_num[0]['rating']]} #what will be sent to VM
        if smallest_ind == 0:
            #France
            request_france = requests.post('https://8498c208d14fafeb.gradio.app/api/predict', json=json_return).json()
            json_return = request_france['data'][0] | {'region': 'FR'}
        elif smallest_ind == 1:
            #West US
            request_caiso = requests.post('https://665fd2541ffc38a4.gradio.app/api/predict', json=json_return).json()
            json_return = request_caiso['data'][0] | {'region': 'CAISO_NORTH'}
        elif smallest_ind == 2:
            #East US
            request_dc = requests.post('https://9691c098558aaa98.gradio.app/api/predict', json=json_return).json()
            json_return = request_dc['data'][0] | {'region': 'PJM_ROANOKE'}
        elif smallest_ind == 3:
            #Australia, NSW
            request_aus = requests.post('https://ba6858ad805d56a4.gradio.app/api/predict', json=json_return).json()
            json_return = request_aus['data'][0] | {'region': 'NEM_NSW'}
        elif smallest_ind == 4:
            #London
            request_london = requests.post('https://7829c30c5c41724f.gradio.app/api/predict', json=json_return).json()
            json_return = request_london['data'][0] | {'region': 'UK'}

    '''
    Now that we got the information for the region that was chosen, the code below will call the sdk again
    in order to get information for all regions in order to change the bar chart on the website.
    '''
    #calling to sdk again to get all region info for the bar chart
    request_all_regions = requests.get(url=(ALL_REGION_URL+"time="+dateStr)).json()
    location_info = dict()
    lowest_region = {'lowest_region' : 'temp', 'lowest_carbon_rate': float('inf')}
    for j in request_all_regions:
        location_info = location_info | {j['location']: j['rating']}
        if j['rating'] < lowest_region['lowest_carbon_rate']:
            lowest_region['lowest_region'] = j['location']

            lowest_region['lowest_carbon_rate'] = j['rating']
    #incrementing the user, and total/saved grams to be current.
    user_requests += 1
    grams_total += float(json_return['carbon'])
    temp_saved = 0
    #this if statement is to confirm that the user actually saved grams of CO2
    if args.get('eco_toggle') == 'true' and closest['closest_region'] != lowest_region['lowest_region']:
        temp_saved = abs(location_info[lowest_region['lowest_region']] - location_info[closest['closest_region']]) * float(json_return['energy'])
    grams_saved += temp_saved

    #we write to file to save the current amount of user + total/saved grams (in case of shutoff)
    file_write = open('info.txt', 'w')
    file_write.write(str(user_requests) + '\n' + str(grams_total) + '\n' + str(grams_saved))
    file_write.close()
    #we include all of these dictionaries to be sent as a json to be used in the front end side of things.
    return json_return | location_info | closest | {'amount_saved': temp_saved}

app.run() #you can add 'debug=true' in the params to edit the code more easily.