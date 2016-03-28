# -*- coding: utf-8 -*-
'''
Copyright (c) 2016, Virginia Tech
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
 following conditions are met:
1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those of the authors and should not be
interpreted as representing official policies, either expressed or implied, of the FreeBSD Project.

This material was prepared as an account of work sponsored by an agency of the United States Government. Neither the
United States Government nor the United States Department of Energy, nor Virginia Tech, nor any of their employees,
nor any jurisdiction or organization that has cooperated in the development of these materials, makes any warranty,
express or implied, or assumes any legal liability or responsibility for the accuracy, completeness, or usefulness or
any information, apparatus, product, software, or process disclosed, or represents that its use would not infringe
privately owned rights.

Reference herein to any specific commercial product, process, or service by trade name, trademark, manufacturer, or
otherwise does not necessarily constitute or imply its endorsement, recommendation, favoring by the United States
Government or any agency thereof, or Virginia Tech - Advanced Research Institute. The views and opinions of authors
expressed herein do not necessarily state or reflect those of the United States Government or any agency thereof.

VIRGINIA TECH – ADVANCED RESEARCH INSTITUTE
under Contract DE-EE0006352

#__author__ = "BEMOSS Team"
#__credits__ = ""
#__version__ = "2.0"
#__maintainer__ = "BEMOSS Team"
#__email__ = "aribemoss@gmail.com"
#__website__ = "www.bemoss.org"
#__created__ = "2014-09-12 12:04:50"
#__lastUpdated__ = "2016-03-14 11:23:33"
'''

from _utils.page_load_utils import get_device_list_side_navigation

from apps.alerts.views import get_notifications, general_notifications
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.http import HttpResponse
from apps.dashboard.models import DeviceMetadata
from _utils import config_helper
from _utils import page_load_utils as _helper
from agents.ZMQHelper.zmq_pub import ZMQ_PUB as zmqPub
from apps.thermostat.models import Thermostat
import httplib
import os
import json
import urllib2
import logging
import settings
import settings_tornado
import _utils.defaults as __

logger = logging.getLogger("views")

kwargs = {'subscribe_address': __.SUB_SOCKET,
                    'publish_address': __.PUSH_SOCKET}
             
zmq_pub = zmqPub(**kwargs)

def get_zip_code():
    try:
        location_info = urllib2.urlopen('http://ipinfo.io/json').read()
        location_info_json = json.loads(location_info)
        zipcode = location_info_json['postal'].encode('ascii', 'ignore')
        return zipcode
    except urllib2.HTTPError, e:
        logger.error('HTTPError = ' + str(e.code))
    except urllib2.URLError, e:
        logger.error('URLError = ' + str(e.reason))
    except httplib.HTTPException, e:
        logger.error('HTTPException = ' + str(e.message))
    except Exception:
        import traceback
        logger.error('generic exception: ' + traceback.format_exc())

def get_weather_info():
    #Get current weather data from wunderground
    json_file = open(os.path.join(settings_tornado.PROJECT_DIR, 'resources/metadata/bemoss_metadata.json'), "r+")
    _json_data = json.load(json_file)
    zipcode = _json_data['building_location_zipcode']
    json_file.close()

    # Get the zip according to your IP, if available:
    ip_zipcode = get_zip_code()
    # our default zip code is 22203, if we can obtain your location based on your IP, we will update it below.
    if zipcode == '22203' and ip_zipcode is not None:
        zipcode = ip_zipcode

    rs = {}
    try:
        # Get weather underground service key
        wu_key = settings.WUNDERGROUND_KEY
        rs = urllib2.urlopen("http://api.wunderground.com/api/" + wu_key + "/conditions/q/" + zipcode + ".json")
    except urllib2.HTTPError, e:
        logger.error('HTTPError = ' + str(e.code))
    except urllib2.URLError, e:
        logger.error('URLError = ' + str(e.reason))
    except httplib.HTTPException, e:
        logger.error('HTTPException = ' + str(e.message))
    except Exception:
        import traceback
        logger.error('generic exception: ' + traceback.format_exc())
    print rs
    print zipcode

    json_string = rs.read() if rs != {} else {}
    try:
        parsed_json = json.loads(json_string)
        location = parsed_json['current_observation']['display_location']['full']
        temp_f = parsed_json['current_observation']['temp_f']
        humidity = parsed_json['current_observation']['relative_humidity']
        precip = parsed_json['current_observation']['precip_1hr_in']
        precip = precip if float(precip)>0 else '0.0'
        winds = parsed_json['current_observation']['wind_mph']
        icon = str(parsed_json['current_observation']['icon'])
        weather = parsed_json['current_observation']['weather']
    except Exception:
        location = 'Arlington, VA (Default, please update settings)'
        temp_f = '77'
        humidity = '10%'
        precip = '0.0'
        winds = '1.0'
        icon = 'mostlysunny'
        weather = 'Sunny'

    weather_icon = config_helper.get_weather_icon(icon)

    weather_info = [location, temp_f, humidity, precip, winds, weather, weather_icon]

    return weather_info

@login_required(login_url='/login/')
def thermostat(request, mac):
    print 'Thermostat pageload'
    context = RequestContext(request)
    mac = mac.encode('ascii', 'ignore')

    device_metadata = [ob.device_control_page_info() for ob in DeviceMetadata.objects.filter(mac_address=mac)]
    print device_metadata
    device_type = device_metadata[0]['device_type']
    device_id = device_metadata[0]['device_id']
    device_type_id = device_metadata[0]['device_model_id']
    device_type_id = device_type_id.device_model_id
    print device_type_id

    device_status = [ob.data_as_json() for ob in Thermostat.objects.filter(thermostat_id=device_id)]
    device_zone = device_status[0]['zone']['id']
    device_nickname = device_status[0]['nickname']
    zone_nickname = device_status[0]['zone']['zone_nickname']
    override = device_status[0]['override']
    hold = device_status[0]['hold']

    #Using page_load.json
    vals = _helper.get_page_load_data(device_id, device_type, device_type_id)
    print vals

    weather_info = get_weather_info()
    device_list_side_nav = get_device_list_side_navigation()
    context.update(device_list_side_nav)
    active_al = get_notifications()
    context.update({'active_al':active_al})
    bemoss_not = general_notifications()
    context.update({'b_al': bemoss_not})

    return render_to_response(
        'thermostat/thermostat.html',
        {'device_id': device_id, 'device_zone': device_zone, 'device_type_id': device_type_id,
         'zone_nickname': zone_nickname, 'mac_address': mac, 'device_nickname': device_nickname, 'device_data': vals,
         'location': weather_info[0], 'temp_f': weather_info[1], 'humidity': weather_info[2], 'precip': weather_info[3],
         'winds': weather_info[4], 'override': override, 'hold':hold, 'weather_icon': weather_info[6],
         'weather': weather_info[5], 'mac': mac},
        context)


@login_required(login_url='/login/')
def weather(request):
    print os.path.basename(__file__)+"in weather function"
    if request.method == 'GET':
        weather_info = get_weather_info()
        
        jsonresult = {
                          'locat':weather_info[0],
                          'temp_f':weather_info[1],
                          'humidity':weather_info[2],
                          'precip':weather_info[3],
                          'winds':weather_info[4],
                          'icon':weather_info[6],
                          'weather':weather_info[5]
                          }
        print json.dumps(jsonresult)
        if request.is_ajax():
            return HttpResponse(json.dumps(jsonresult), mimetype='application/json')


@login_required(login_url='/login/')
def submit_values(request):
    if request.POST:
        _data = request.body
        json_data = json.loads(_data)

        device_info = json_data['device_info']
        print device_info

        json_data.pop('device_info')
        print json_data

        device_id = device_info.split("/")
        device_id = device_id[2]

        #Let Agent handle override

        #override = json_data['override']
        #device_obj = Thermostat.objects.get(thermostat_id=device_id)
        #device_obj.override = override
        #device_obj.save()
        #json_data.pop('override')

        print json_data

        update_number = "wifi_3m50_01"

        device_info = device_info.split('/')  # e.g. 999/lighting/1NST18b43017e76a
        # TODO fix building name -> should be changeable from 'bemoss'
        ieb_topic = '/ui/agent/'+device_info[1]+'/update/bemoss/'+device_info[0]+'/'+device_info[2]
        print ieb_topic

        content_type = "application/json"
        fromUI = "UI"
        print "entering in sending message to agent"
        zmq_pub.sendToAgent(ieb_topic, json_data, content_type, fromUI)
        print json_data
        print "success in sending message to agent"

        a_dict = {'update_number': update_number}
        json_data.update(a_dict)
        print json_data

        if request.is_ajax():
            return HttpResponse(json.dumps(json_data), mimetype='application/json')


@login_required(login_url='/login/')
def get_thermostat_current_status(request):
    print "Getting current status of thermostat"
    if request.method == 'POST':
        data_recv = request.raw_post_data
        data_recv = json.loads(data_recv)
        device_info = data_recv['device_info']
        # same as the thermostat load method
        info_required = "current status"

        device_info = device_info.split('/')  # e.g. 999/lighting/1NST18b43017e76a
        # TODO fix building name -> should be changeable from 'bemoss'
        ieb_topic = '/ui/agent/'+device_info[1]+'/device_status/bemoss/'+device_info[0]+'/'+device_info[2]
        print ieb_topic

        zmq_pub.requestAgent(ieb_topic, info_required, "text/plain", "UI")

        jsonresult = {'status': 'sent'}

        if request.is_ajax():
            return HttpResponse(json.dumps(jsonresult), mimetype='application/json')