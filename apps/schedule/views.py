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


import os
from django.template import RequestContext

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from _utils.page_load_utils import get_device_list_side_navigation
from apps.alerts.views import get_notifications, general_notifications
from apps.dashboard.models import DeviceMetadata
from apps.discovery.models import SupportedDevices
from apps.thermostat.models import Thermostat
from apps.lighting.models import Lighting
from apps.smartplug.models import Plugload
import json
from _utils import config_helper

from agents.ZMQHelper.zmq_pub import ZMQ_PUB
import settings_tornado
from _utils import defaults as __


kwargs = {'subscribe_address': __.SUB_SOCKET,
                    'publish_address': __.PUSH_SOCKET}

zmq_pub = ZMQ_PUB(**kwargs)

device_id = ''

disabled_values_thermostat = {"everyday": {
            'monday': [],
            'tuesday': [],
            'wednesday': [],
            'thursday': [],
            'friday': [],
            'saturday': [],
            'sunday': []},
        "weekdayweekend": {
            'weekday': [],
            'weekend': []},
        "holiday": {
            'holiday': []}}

disabled_values_lighting = {"everyday": {
            'monday': [],
            'tuesday': [],
            'wednesday': [],
            'thursday': [],
            'friday': [],
            'saturday': [],
            'sunday': []},
        "weekdayweekend": {
            'weekday': [],
            'weekend': []},
        "holiday": {
            'holiday': []}}

disabled_values_plugload = {"everyday": {
            'monday': [],
            'tuesday': [],
            'wednesday': [],
            'thursday': [],
            'friday': [],
            'saturday': [],
            'sunday': []},
        "weekdayweekend": {
            'weekday': [],
            'weekend': []},
        "holiday": {
            'holiday': []}}


@login_required(login_url='/login/')
def thermostat_schedule(request, mac):
    print 'Inside Set Schedule method in Schedule app'
    context = RequestContext(request)
    username = request.user
    if request.user.get_profile().group.name.lower() == 'admin' or \
       request.user.get_profile().group.name.lower() == 'zone manager':
        print username
        print type(mac)
        mac = mac.encode('ascii', 'ignore')
        print type(mac)

        device_metadata = [ob.device_control_page_info() for ob in DeviceMetadata.objects.filter(mac_address=mac)]
        print device_metadata
        device_id = device_metadata[0]['device_id']
        device_type_id = device_metadata[0]['device_model_id']
        device_type_id = device_type_id.device_model_id
        device_model = device_metadata[0]['device_model']

        device_status = [ob.data_as_json() for ob in Thermostat.objects.filter(thermostat_id=device_id)]
        device_zone = device_status[0]['zone']['id']
        device_nickname = device_status[0]['nickname']
        zone_nickname = device_status[0]['zone']['zone_nickname']


        #Send message to OS to launch application
        app_launcher_topic = '/ui/appLauncher/thermostat_scheduler/' + device_id + '/launch'
        token = {"auth_token": "bemoss"}
        zmq_pub.requestAgent(app_launcher_topic, json.dumps(token), "application/json", "UI")

        device_list_side_nav = get_device_list_side_navigation()
        context.update(device_list_side_nav)
        active_al = get_notifications()
        context.update({'active_al':active_al})
        bemoss_not = general_notifications()
        context.update({'b_al': bemoss_not})
        _data = {}
        active_schedule = []
        disabled_range = __.DISABLED_VALUES_THERMOSTAT_NEW

        #Check if schedule file for this device exists
        _file_name = os.path.join(settings_tornado.PROJECT_DIR, 'resources/scheduler_data/thermostat/' + device_id
                                  + '_schedule.json')
        if os.path.isfile(_file_name):
            json_file = open(_file_name, 'r+')
            _json_data = json.load(json_file)
            if device_id in _json_data['thermostat']:
                print 'device id present'
                _data = _json_data['thermostat'][device_id]['schedulers']

                active_schedule = _json_data['thermostat'][device_id]['active']
                active_schedule = [str(x) for x in active_schedule]
                disabled_range = get_disabled_date_ranges_thermostat(_data)
                #disabled_range = get_disabled_date_ranges(_data, disabled_values_plugload)
                _data = json.dumps(_data)
                _data = json.loads(_data, object_hook=_decode_dict)
            json_file.close()
        else:
            #json_file = open(_file_name, 'w+')
            _json_data = {"thermostat": {
                device_id: {
                    "active": ['everyday', 'holiday'],
                    "inactive": [],
                    "schedulers": __.THERMOSTAT_DEFAULT_SCHEDULE_NEW
                }}}

            with open(_file_name, 'w') as _new_file:
                json.dump(_json_data, _new_file, sort_keys=True, indent=4, ensure_ascii=False)
            _new_file.close()
            if type(_json_data) is dict:
                _data = _json_data['thermostat'][device_id]['schedulers']
            else:
                _json_data = json.loads(_json_data)
                _data = _json_data['thermostat'][device_id]['schedulers']
            active_schedule = ['everyday', 'holiday']
            disabled_range = get_disabled_date_ranges_thermostat(_data)

        schedule_meta = [ob.get_schedule_info() for ob in SupportedDevices.objects.filter(device_model=device_model)]
        schedule_meta = json.dumps(schedule_meta[0])
        print schedule_meta

        return render_to_response(
            'schedule/th_sch_new.html',
            {'device_id': device_id, 'device_zone': device_zone, 'zone_nickname': zone_nickname, 'mac_address': mac,
             'device_nickname': device_nickname, 'schedule': _data,
             'disabled_ranges': disabled_range, 'active_schedule': active_schedule, 'schedule_meta': schedule_meta},
            context)
    else:
        return HttpResponseRedirect('/home')


def get_disabled_date_ranges_thermostat(_data):

    disabled_values = __.DISABLED_VALUES_THERMOSTAT_NEW
    for sch_type in _data:
        if sch_type == 'holiday':
            for item in _data[sch_type]:
                value = []
                for _item in _data[sch_type]:
                    value.append(int(_item['at']))
                disabled_values[sch_type]['holiday'] = value
        else:
            for day in _data[sch_type]:
                for item in _data[sch_type][day]:
                    value = []
                    for _item in _data[sch_type][day]:
                        value.append(int(_item['at']))
                    disabled_values[sch_type][day] = value
    print disabled_values
    return disabled_values


@login_required(login_url='/login/')
def update_thermostat_schedule(request):
    if request.POST:
        _data = json.loads(request.body)
        print _data
        device_info = _data['device_info']
        device_info = device_info.split('/')
        device_id = device_info[2]
        device_type = device_info[1]
        device_zone = device_info[0]
        schedule_type = ''
        if 'everyday' in str(_data):
            schedule_type = 'everyday'
        elif 'weekdayweekend' in str(_data):
            schedule_type = 'weekdayweekend'
        elif 'holiday' in str(_data):
            schedule_type = 'holiday'
        content = save_schedule(device_id, device_type, _data['schedule'], schedule_type)

        message_to_agent = {
            "path": os.path.join(settings_tornado.PROJECT_DIR, 'resources/scheduler_data/' + device_type + '/' + device_id
                              + '_schedule.json'),"content": content,
            "auth_token": "bemoss"
        }
        ieb_topic = '/ui/app/' + device_type + '_scheduler/' + device_id + '/update'
        print ieb_topic
        zmq_pub.requestAgent(ieb_topic, json.dumps(message_to_agent), "application/json", "UI")

        _data_to_send = {"update_number": "to_be_added"}

        if request.is_ajax():
            return HttpResponse(json.dumps(_data_to_send), mimetype='application/json')


def save_schedule(device_id, device_type, _data, schedule_type):
    #json_file = open(os.path.join(settings_tornado.PROJECT_DIR, 'resources/scheduler_data/' + device_type + '_schedule.json'), "r+")
    _file_name = os.path.join(settings_tornado.PROJECT_DIR, 'resources/scheduler_data/' + device_type + '/' + device_id
                              + '_schedule.json')
    json_file = open(_file_name, "r+")
    _json_data = json.load(json_file)
    print _json_data
    if device_id not in _json_data[device_type]:
        _json_data[device_type][device_id] = {'active': [], 'inactive': [], 'schedulers': {}}
    _json_data[device_type][device_id]['schedulers'][schedule_type] = _data[schedule_type]
    print _json_data
    json_file.seek(0)
    schedule_file_content = json.dumps(_json_data, indent=4, sort_keys=True)
    json_file.write(schedule_file_content)
    json_file.truncate()
    json_file.close()
    return schedule_file_content



def activate_schedule(request):
    if request.POST:
        _data = json.loads(request.body)
        device_info = _data['device_info']
        device_info = device_info.split('/')
        device_type = device_info[1]
        device_id = device_info[2]
        _file_name = os.path.join(settings_tornado.PROJECT_DIR, 'resources/scheduler_data/' + device_type + '/' + device_id
                              + '_schedule.json')
        json_file = open(_file_name, "r+")
        _json_data = json.load(json_file)
        _json_data[device_type][device_id]['active'] = _data['active']
        _json_data[device_type][device_id]['inactive'] = _data['inactive']
        json_file.seek(0)
        content = json.dumps(_json_data, indent=4, sort_keys=True)
        json_file.write(content)
        json_file.truncate()
        json_file.close()

        message_to_agent = {
            "path": _file_name,
            "auth_token": "bemoss",
            "content": content
        }
        ieb_topic = '/ui/app/' + device_type + '_scheduler/' + device_id + '/update'
        print ieb_topic
        zmq_pub.requestAgent(ieb_topic, json.dumps(message_to_agent), "application/json", "UI")

        _data_to_send = {"status": "success"}

        if request.is_ajax():
            return HttpResponse(json.dumps(_data_to_send), mimetype='application/json')

@login_required(login_url='/login/')
def update_schedule_status_to_browser(request):
    print "device_schedule_update_message_to_browser"
    if request.method == 'POST':
        _data = request.raw_post_data
        device_info = _data
        device_info = device_info.split('/')
        device_type = device_info[1]
        device_id = device_info[2]
        topic = 'schedule_update_status'
        thermostat_update_schedule_status = config_helper.get_update_message(topic)
        print type(thermostat_update_schedule_status)
        data_split = str(thermostat_update_schedule_status).split("/")
        if data_split[0] == device_id:
            result = data_split[1]
        else:
            result = 'failure'
        json_result = {'status': result}
        #zmq_topics.reset_update_topic()
        print json.dumps(json_result)
        if request.is_ajax():
            return HttpResponse(json.dumps(json_result), mimetype='application/json')


@login_required(login_url='/login/')
def plugload_schedule(request, mac):
    print 'Inside Set Schedule method in Schedule app'
    context = RequestContext(request)
    username = request.user
    if request.user.get_profile().group.name.lower() == 'admin' or \
       request.user.get_profile().group.name.lower() == 'zone manager':
        print username
        print type(mac)
        mac = mac.encode('ascii', 'ignore')
        print type(mac)

        device_metadata = [ob.device_control_page_info() for ob in DeviceMetadata.objects.filter(mac_address=mac)]
        print device_metadata
        device_id = device_metadata[0]['device_id']
        device_type_id = device_metadata[0]['device_model_id']
        device_type_id = device_type_id.device_model_id

        if device_type_id == '2WL':
            device_status = [ob.data_as_json() for ob in Lighting.objects.filter(lighting_id=device_id)]
            device_zone = device_status[0]['zone']['id']
            device_nickname = device_status[0]['nickname']
            zone_nickname = device_status[0]['zone']['zone_nickname']
        else:
            device_status = [ob.data_as_json() for ob in Plugload.objects.filter(plugload_id=device_id)]
            device_zone = device_status[0]['zone']['id']
            device_nickname = device_status[0]['nickname']
            zone_nickname = device_status[0]['zone']['zone_nickname']
        _data = {}
        active_schedule = []
        disabled_range = __.DISABLED_VALUES_PLUGLOAD

        if device_type_id == '2WL':
            # Send message to OS to launch application
            app_launcher_topic = '/ui/appLauncher/lighting_scheduler/' + device_id + '/launch'
            token = {"auth_token": "bemoss"}
            zmq_pub.requestAgent(app_launcher_topic, json.dumps(token), "application/json", "UI")

            #Check if schedule file for this device exists
            _file_name = os.path.join(settings_tornado.PROJECT_DIR, 'resources/scheduler_data/lighting/' + device_id
                                      + '_schedule.json')
            if os.path.isfile(_file_name):
                json_file = open(_file_name, 'r+')
                _json_data = json.load(json_file)
                if device_id in _json_data['lighting']:
                    print 'device id present'
                    _data = _json_data['lighting'][device_id]['schedulers']

                    active_schedule = _json_data['lighting'][device_id]['active']
                    active_schedule = [str(x) for x in active_schedule]
                    disabled_range = get_disabled_date_ranges(_data, __.DISABLED_VALUES_LIGHTING)
                    _data = json.dumps(_data)
                    _data = json.loads(_data, object_hook=_decode_dict)
                json_file.close()
            else:
                #json_file = open(_file_name, 'w+')
                _json_data = {"lighting": {
                    device_id: {
                        "active": ['everyday', 'holiday'],
                        "inactive": [],
                        "schedulers": __.LIGHTING_DEFAULT_SCHEDULE_2WL
                    }}}

                with open(_file_name, 'w') as _new_file:
                    json.dump(_json_data, _new_file, sort_keys=True, indent=4, ensure_ascii=False)
                _new_file.close()
                if type(_json_data) is dict:
                    _data = _json_data['lighting'][device_id]['schedulers']
                else:
                    _json_data = json.loads(_json_data)
                    _data = _json_data['lighting'][device_id]['schedulers']
                active_schedule = ['everyday', 'holiday']
                disabled_range = get_disabled_date_ranges(_data, __.DISABLED_VALUES_LIGHTING)
        else:
            # Send message to OS to launch application
            app_launcher_topic = '/ui/appLauncher/plugload_scheduler/' + device_id + '/launch'
            token = {"auth_token": "bemoss"}
            zmq_pub.requestAgent(app_launcher_topic, json.dumps(token), "application/json", "UI")

            _file_name = os.path.join(settings_tornado.PROJECT_DIR, 'resources/scheduler_data/plugload/' + device_id
                                      + '_schedule.json')
            if os.path.isfile(_file_name):
                json_file = open(_file_name, 'r+')
                _json_data = json.load(json_file)
                if device_id in _json_data['plugload']:
                    print 'device id present'
                    _data = _json_data['plugload'][device_id]['schedulers']

                    active_schedule = _json_data['plugload'][device_id]['active']
                    active_schedule = [str(x) for x in active_schedule]
                    disabled_range = get_disabled_date_ranges(_data, __.DISABLED_VALUES_PLUGLOAD)
                    _data = json.dumps(_data)
                    _data = json.loads(_data, object_hook=_decode_dict)
                json_file.close()
            else:
                #json_file = open(_file_name, 'w+')
                _json_data = {"plugload": {
                    device_id: {
                        "active": ['everyday', 'holiday'],
                        "inactive": [],
                        "schedulers": __.PLUGLOAD_DEFAULT_SCHEDULE
                    }}}

                with open(_file_name, 'w') as _new_file:
                    json.dump(_json_data, _new_file, sort_keys=True, indent=4, ensure_ascii=False)
                _new_file.close()
                if type(_json_data) is dict:
                    _data = _json_data['plugload'][device_id]['schedulers']
                else:
                    _json_data = json.loads(_json_data)
                    _data = _json_data['plugload'][device_id]['schedulers']
                active_schedule = ['everyday', 'holiday']
                disabled_range = get_disabled_date_ranges(_data, __.DISABLED_VALUES_PLUGLOAD)



        device_list_side_nav = get_device_list_side_navigation()
        context.update(device_list_side_nav)
        active_al = get_notifications()
        context.update({'active_al': active_al})
        bemoss_not = general_notifications()
        context.update({'b_al': bemoss_not})
        return render_to_response(
            'schedule/pl_sch.html',
            {'device_id': device_id, 'device_zone': device_zone, 'zone_nickname': zone_nickname, 'mac_address': mac,
             'device_nickname': device_nickname, 'schedule': _data,
             'disabled_ranges': disabled_range, 'active_schedule': active_schedule, 'type': device_type_id,
             'device_type_id': device_type_id}, context)
    else:
        return HttpResponseRedirect('/home/')



@login_required(login_url='/login/')
def lighting_schedule(request, mac):
    print 'Inside Set Schedule method in Schedule app'
    context = RequestContext(request)
    username = request.user
    if request.user.get_profile().group.name.lower() == 'admin' or \
       request.user.get_profile().group.name.lower() == 'zone manager':
        print username
        print type(mac)
        mac = mac.encode('ascii', 'ignore')
        print type(mac)

        device_metadata = [ob.device_control_page_info() for ob in DeviceMetadata.objects.filter(mac_address=mac)]
        print device_metadata
        device_id = device_metadata[0]['device_id']
        device_type_id = device_metadata[0]['device_model_id']
        device_type_id = device_type_id.device_model_id
        device_status = [ob.data_as_json() for ob in Lighting.objects.filter(lighting_id=device_id)]
        device_zone = device_status[0]['zone']['id']
        device_nickname = device_status[0]['nickname']
        zone_nickname = device_status[0]['zone']['zone_nickname']

        # Send message to OS to launch application
        app_launcher_topic = '/ui/appLauncher/lighting_scheduler/' + device_id + '/launch'
        token = {"auth_token": "bemoss"}
        zmq_pub.requestAgent(app_launcher_topic, json.dumps(token), "application/json", "UI")

        _data = {}
        active_schedule = []
        disabled_range = __.DISABLED_VALUES_LIGHTING

        #Check if schedule file for this device exists
        _file_name = os.path.join(settings_tornado.PROJECT_DIR, 'resources/scheduler_data/lighting/' + device_id
                                  + '_schedule.json')
        if os.path.isfile(_file_name):
            json_file = open(_file_name, 'r+')
            _json_data = json.load(json_file)
            if device_id in _json_data['lighting']:
                print 'device id present'
                _data = _json_data['lighting'][device_id]['schedulers']

                active_schedule = _json_data['lighting'][device_id]['active']
                active_schedule = [str(x) for x in active_schedule]
                disabled_range = get_disabled_date_ranges(_data, __.DISABLED_VALUES_LIGHTING)
                _data = json.dumps(_data)
                _data = json.loads(_data, object_hook=_decode_dict)
            json_file.close()
        else:
            #json_file = open(_file_name, 'w+')
            if device_type_id == '2SDB' or device_type_id == '2DB' or device_type_id == '2WSL':
                _json_data = {"lighting": {
                device_id: {
                    "active": ['everyday', 'holiday'],
                    "inactive": [],
                    "schedulers": __.LIGHTING_DEFAULT_SCHEDULE_2DB_2SDB
                    }}}
            elif device_type_id == '2HUE':
                _json_data = {"lighting": {
                device_id: {
                    "active": ['everyday', 'holiday'],
                    "inactive": [],
                    "schedulers": __.LIGHTING_DEFAULT_SCHEDULE_2HUE
                    }}}

            with open(_file_name, 'w') as _new_file:
                json.dump(_json_data, _new_file, sort_keys=True, indent=4, ensure_ascii=False)
            _new_file.close()
            if type(_json_data) is dict:
                _data = _json_data['lighting'][device_id]['schedulers']
            else:
                _json_data = json.loads(_json_data)
                _data = _json_data['lighting'][device_id]['schedulers']
            active_schedule = ['everyday', 'holiday']
            disabled_range = get_disabled_date_ranges(_data, __.DISABLED_VALUES_LIGHTING)


        device_list_side_nav = get_device_list_side_navigation()
        context.update(device_list_side_nav)
        active_al = get_notifications()
        context.update({'active_al':active_al})
        bemoss_not = general_notifications()
        context.update({'b_al': bemoss_not})
        return render_to_response(
            'schedule/lt_sch.html',
            {'device_id': device_id, 'device_zone': device_zone, 'zone_nickname': zone_nickname, 'mac_address': mac,
             'device_nickname': device_nickname, 'schedule': _data,
             'disabled_ranges': disabled_range, 'active_schedule': active_schedule, 'type': device_type_id}, context)
    else:
        return HttpResponseRedirect('/home/')


def get_disabled_date_ranges(_data, disabled_values_type):
    disabled_values = disabled_values_type
    for sch_type in _data:
        if sch_type == 'holiday':
            for item in _data[sch_type]:
                value = []
                for _item in _data[sch_type][item]:
                    value.append(int(_item['at']))
                disabled_values[sch_type][item] = value
        else:
            for day in _data[sch_type]:
                value = []
                for item in _data[sch_type][day]:
                    value.append(int(item['at']))
                disabled_values[sch_type][day] = value
    print disabled_values
    return disabled_values


def _decode_list(data):
    rv = []
    for item in data:
        if isinstance(item, unicode):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = _decode_list(item)
        elif isinstance(item, dict):
            item = _decode_dict(item)
        rv.append(item)
    return rv


def _decode_dict(data):
    rv = {}
    for key, value in data.iteritems():
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        elif isinstance(value, list):
            value = _decode_list(value)
        elif isinstance(value, dict):
            value = _decode_dict(value)
        rv[key] = value
    return rv