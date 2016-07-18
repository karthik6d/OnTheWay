"""
    This program is designed to navigate from Point A to Point B through any type of
    shop (using the yelp API). This program utilizes the Google Maps API and the Yelp
    API to find local shops on the way to the destination that are least intrusive to
    the transportation trip.

    Creators: Karthik Rao, Summer 2016
"""
import googlemaps
from datetime import datetime
import polyline
from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator

#Initialzing googlemaps API and yelp API
gmaps = googlemaps.Client(key = 'AIzaSyCGB_J21e7QLfqLUNg6mDnvrgaiaGSMSV0') #maps
auth = Oauth1Authenticator(
            consumer_key = 'MSgcEGxUl045m2C50DnnOA',
            consumer_secret = 'vaDcn9GHrbrlJFhkQWxYqfv_nUc',
            token = 'NnF6UpfSYniZxUki_Ql4Xcl8AX727ZxU',
            token_secret = 'zoP_pK1LMNxs2dM1apRwRxlGomk'
            )
client = Client(auth) #yelp

def main():
    """
    Function: main
    -----------------------
    main method that prints possible stores along the path from origin to destination
        first line: duration of straight trip
        following lines: name of store, address, new adjusted duration of trip

    returns: null
    """
    now = datetime.now()
    point1 = input('Entering starting point: ')
    point2 = input('Enter ending point: ')
    directions = gmaps.directions(point1, point2, departure_time = now, mode = 'driving')

    o = point1
    d = point2
    k = input('What are you looking for?: ')
    num = 2
    l = break_polyline(directions)

    print 'Total straight trip time: ', get_duration(directions), ' min'
    for i in range(len(l)):
        response = locations(k, num, l[i])
        if response[0].location.address != [] and response[1].location.address != []:
            print (response[0].name, response[0].location.address[0],
	    response[0].location.city, response[0].location.state_code,
	    check_duration_times(response, o,d, num)[0], ' min')
            print (response[1].name, response[1].location.address[0],
	    response[1].location.city, response[1].location.state_code,
	    check_duration_times(response, o,d, num)[1], ' min')


def print_directions(directions):
    """
    Function: print_directions
    ------------------------------
    prints the directions through all the legs

    directions: gmaps.directions object with origin and destination

    returns: Null (but prints the directions)
    """
    for i in range(len(directions[0]['legs'])):
        for j in range(len(directions[0]['legs'][i]['steps'])):
            print remove_html(directions[0]['legs'][i]['steps'][j]['html_instructions'])

def locations(keyword, num, location):
    """
    Function: location
    ----------------------
    returns top yelp options for the keyword given

    keyword: search term
    num: number of options you want to see
    location: location of where the shops will be

    return: list of yelp business objects
    """
    params = {'term':keyword}
    response = client.search_by_coordinates(location[0], location[1], sort = 1, **params)
    #print response.businesses

    if(num > len(response.businesses)):
        return response.businesses
    else:
        return response.businesses[:num]

def check_duration_times(response, origin, destination, num):
    """
    Function: check_duration_times
    ----------------------------------
    returns the duration times for each of the specified locations from the yelp search

    response: yelp object with businesses
    origin: origin location
    destination: destination location
    num: number of possible locations (same from locations function)

    return: list of duration times for each
    """
    times = []

    for i in range(num):
        lat = response[i].location.coordinate.latitude
        lon = response[i].location.coordinate.longitude
        times.append(get_duration(directions = gmaps.directions(origin, destination, waypoints = (lat,lon),
                                                               mode = 'driving')))
    return times

def new_directions(response, origin, destination, num):
    """
    Function: check_duration_times
    ----------------------------------
    prints the directions for each of the specified locations from the yelp search

    response: yelp object with businesses
    origin: origin location
    destination: destination location
    num: number of possible locations (same from locations function)

    return: null
    """
    for i in range(num):
        lat = response[i].location.coordinate.latitude
        lon = response[i].location.coordinate.longitude
        print_directions(gmaps.directions(origin, destination, waypoints = (lat,lon), mode = 'driving'))
        print "----------------------"

def break_polyline(directions):
    """
    Function: break_polyline
    ----------------------------
    takes an overview polyline of a navigation path and breaks it up into
        smaller intervals

    directions: gmaps.directions object with origin and destination

    returns: a list of latitude and longitude points at the polyline intervals
    """
    latlon = []
    length =  len(polyline.decode(directions[0]['overview_polyline']['points']))
    path = polyline.decode(directions[0]['overview_polyline']['points'])

    #print length
    #print float(directions[0]['legs'][0]['distance']['text'][:3])

    for i in range(0, length, 20): #finds every 20th polyline coordinate
        latlon.append((path[i][0],path[i][1]))

    return latlon

def get_duration(directions):
    """
    Function: get_duration
    -------------------------
    gets the duration of a specified path

    directions: gmaps.directions object with origin and destination

    returns: duration time of the trip
    """
    time = 0

    for i in range(len(directions[0]['legs'])): #adds the duration for all legs of trip
        time += convert_to_mins(directions[0]['legs'][i]['duration']['text'])

    return time

def remove_html(text):
    """
    Function: remove_html
    -----------------------
    takes html parses lines of text and converts to english

    text: text with <> inserted throughout the line

    returns: line of text without <>
    """
    ret = '' #empty string
    count =  0

    for i in text:
        if i == '<':
            count += 1
        elif i == '>' and count > 0:
            count -= 1
        elif count == 0:
            ret += i

    return ret

def convert_to_mins(time):
    """
    Function: convert_to_mins
    -----------------------------------
    returns an int of the time in mins of a string with hours and minutes

    time: string containing hours and minutes

    returns: int of time in min
    """
    length = len(time)
    min = 0

    if(length > 7):
        hour = time[:8]
        minutes = time[8:]
        if(minutes[0] == ' '):
            minutes = minutes[1:]
        if(hour[0] == '1' and hour[1] == ' '):
            min += 60
            minutes = time[7:]
        elif(hour[1] != ' '):
            min += 60*int(hour[:2])
        elif(hour[0] != '1'):
            min += 60 * int(hour[0])
        if(minutes[1] != ' '):
            min += int(minutes[:2])
        if(minutes[1] == ' '):
            min += int(minutes[0])
    elif(length <= 7):
        if(time[1] != ' '):
            min += int(time[:2])
        if(time[1] == ' '):
            min += int(time[0])

    return min

        
