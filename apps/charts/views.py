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
import json
import datetime
from django.http import HttpResponse
from _utils.page_load_utils import get_device_list_side_navigation
from apps.RTU.models import RTU
from apps.VAV.models import VAV
from apps.alerts.views import get_notifications, general_notifications
from apps.dashboard.models import DeviceMetadata
from apps.lighting.models import Lighting
from apps.smartplug.models import Plugload
from apps.thermostat.models import Thermostat

from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
import numpy
import itertools
import os
import sys
sys.path.insert(0,os.path.expanduser('~/workspace/bemoss_os/'))
from bemoss_lib.databases.cassandraAPI.cassandraDB import retrieve


def parse_resultset(variables, data_point, result_set):
    x = [[lst[variables.index('time')], lst[variables.index(data_point)]+0.0]
            for lst in result_set if lst[variables.index(data_point)] is not None]
    if len(x) == 0:
        return []
    #interleave redundant data to make it step-plot
    currentTime = int((datetime.datetime.utcnow()-datetime.datetime(1970,1,1)).total_seconds()*1000)
    old = numpy.array(x)
    newTime = numpy.append(old[1:,0],currentTime)-1.0 #decrease one millisecond time to arrange for chronological order
    newList = numpy.vstack((newTime,old[:,1])).transpose().tolist()
    old = old.tolist()
    finalResult = list(itertools.chain(*zip(old,newList)))
    print 'new things againins'
    return finalResult

@login_required(login_url='/login/')
def charts_thermostat(request, mac):
    """Page load definition for thermostat statistics."""
    print "inside cassandra view method"
    context = RequestContext(request)
    if request.method == 'GET':

        device_id = get_device_id_from_mac(mac)
        data_points, rs = retrieve(device_id, ['time', 'temperature',
                                   'heat_setpoint', 'cool_setpoint'])

        rs_temperature = parse_resultset(data_points, 'temperature', rs)
        rs_heat_setpoint = parse_resultset(data_points, 'heat_setpoint', rs)
        rs_cool_setpoint = parse_resultset(data_points, 'cool_setpoint', rs)

        device_status = [ob.data_as_json() for ob in Thermostat.objects.filter(thermostat_id=device_id)]
        device_nickname = device_status[0]['nickname']
        zone_nickname = device_status[0]['zone']['zone_nickname']

        context = update_context(context)

        return render_to_response(
            'charts/charts_thermostat.html',
            {'temperature': rs_temperature, 'heat_setpoint': rs_heat_setpoint, 'cool_setpoint': rs_cool_setpoint,
             'mac': mac, 'nickname': device_nickname, 'zone_nickname': zone_nickname}, context)


@login_required(login_url='/login/')
def auto_update_charts_thermostat(request):
    if request.method == 'POST':
        print 'inside cassandra auto update thermostat'
        _data = request.body
        _data = json.loads(_data)
        mac = _data['mac']
        if 'from_dt' in _data.keys():
            from_date = _data['from_dt']
            print from_date
        else:
            from_date = ''

        device_id = get_device_id_from_mac(mac)
        if from_date == '':
            data_points, rs = retrieve(device_id, ['time', 'temperature',
                                  'heat_setpoint', 'cool_setpoint'])
        else:
            from_date = datetime.datetime.strptime(from_date, '%Y/%m/%d %H:%M')
            data_points, rs = retrieve(device_id, ['time', 'temperature',
                                  'heat_setpoint', 'cool_setpoint'], from_date)

        rs_temperature = parse_resultset(data_points, 'temperature', rs)
        rs_heat_setpoint = parse_resultset(data_points, 'heat_setpoint', rs)
        rs_cool_setpoint = parse_resultset(data_points, 'cool_setpoint', rs)

        json_result = {
            'temperature': rs_temperature,
            'heat_setpoint': rs_heat_setpoint,
            'cool_setpoint': rs_cool_setpoint
        }

        print 'test'
        if request.is_ajax():
                return HttpResponse(json.dumps(json_result), mimetype='application/json')


@login_required(login_url='/login/')
def get_statistics_datetime_thermostat(request):
    if request.method == 'POST':
        print 'inside cassandra get statistics for thermostat based on given from and to datetime'
        _data = request.body
        _data = json.loads(_data)
        mac = _data['mac']
        from_date = _data['from_dt']
        to_date = _data['to_dt']
        print from_date

        device_id = get_device_id_from_mac(mac)
        if not from_date and not to_date:
            data_points, rs = retrieve(device_id, ['time', 'temperature',
                                  'heat_setpoint', 'cool_setpoint'])
        elif not to_date and from_date:
            from_date = datetime.datetime.strptime(from_date, '%Y/%m/%d %H:%M')
            data_points, rs = retrieve(device_id, ['time', 'temperature',
                                  'heat_setpoint', 'cool_setpoint'], from_date)
        else:
            from_date = datetime.datetime.strptime(from_date, '%Y/%m/%d %H:%M')
            to_date = datetime.datetime.strptime(to_date, '%Y/%m/%d %H:%M')
            data_points, rs = retrieve(device_id, ['time', 'temperature',
                                  'heat_setpoint', 'cool_setpoint'], from_date, to_date)

        rs_temperature = parse_resultset(data_points, 'temperature', rs)
        rs_heat_setpoint = parse_resultset(data_points, 'heat_setpoint', rs)
        rs_cool_setpoint = parse_resultset(data_points, 'cool_setpoint', rs)

        json_result = {
            'temperature': rs_temperature,
            'heat_setpoint': rs_heat_setpoint,
            'cool_setpoint': rs_cool_setpoint
        }

        print 'Got results based on datetime'
        if request.is_ajax():
                return HttpResponse(json.dumps(json_result), mimetype='application/json')


@login_required(login_url='/login/')
def charts_vav(request, mac):
    """Page load definition for VAV statistics."""
    print "inside smap view method"
    context = RequestContext(request)
    if request.method == 'GET':

        device_id = get_device_id_from_mac(mac)

        device_status = [ob.as_json() for ob in VAV.objects.filter(vav_id=device_id)]
        device_nickname = device_status[0]['nickname']
        zone_nickname = device_status[0]['zone']['zone_nickname']

        data_points, rs = retrieve(device_id, ['time', 'temperature', 'supply_temperature',
                                  'heat_setpoint', 'cool_setpoint', 'flap_position'])

        rs_temperature = parse_resultset(data_points, 'temperature', rs)
        rs_supply_temperature = parse_resultset(data_points, 'supply_temperature', rs)
        rs_heat_setpoint = parse_resultset(data_points, 'heat_setpoint', rs)
        rs_cool_setpoint = parse_resultset(data_points, 'cool_setpoint', rs)
        rs_flap_position = parse_resultset(data_points, 'flap_position', rs)

        context = update_context(context)

        return render_to_response(
            'charts/charts_vav.html',
            {'temperature': rs_temperature, 'supply_temperature': rs_supply_temperature,
             'flap_position': rs_flap_position, 'heat_setpoint': rs_heat_setpoint, 'cool_setpoint': rs_cool_setpoint,
             'nickname': device_nickname, 'mac': mac,
             'zone_nickname': zone_nickname},
            context)


@login_required(login_url='/login/')
def auto_update_charts_vav(request):
    """Statistics page load for VAV"""
    if request.method == 'POST':
        print 'inside smap auto update VAV'
        _data = request.body
        _data = json.loads(_data)
        mac = _data['mac']
        print mac

        if 'from_dt' in _data.keys():
            from_date = _data['from_dt']
            print from_date
        else:
            from_date = ''

        device_id = get_device_id_from_mac(mac)
        if from_date == '':
            data_points, rs = retrieve(device_id, ['time', 'temperature', 'supply_temperature',
                                  'heat_setpoint', 'cool_setpoint', 'flap_position'])
        else:
            from_date = datetime.datetime.strptime(from_date, '%Y/%m/%d %H:%M')
            data_points, rs = retrieve(device_id, ['time', 'temperature', 'supply_temperature',
                                  'heat_setpoint', 'cool_setpoint', 'flap_position'], from_date)

        rs_temperature = parse_resultset(data_points, 'temperature', rs)
        rs_supply_temperature = parse_resultset(data_points, 'supply_temperature', rs)
        rs_heat_setpoint = parse_resultset(data_points, 'heat_setpoint', rs)
        rs_cool_setpoint = parse_resultset(data_points, 'cool_setpoint', rs)
        rs_flap_position = parse_resultset(data_points, 'flap_position', rs)

        json_result = {'temperature': rs_temperature,
                       'supply_temperature': rs_supply_temperature,
                        'flap_position': rs_flap_position,
                        'heat_setpoint': rs_heat_setpoint,
                        'cool_setpoint': rs_cool_setpoint}

        if request.is_ajax():
                return HttpResponse(json.dumps(json_result), mimetype='application/json')


@login_required(login_url='/login/')
def get_statistics_datetime_vav(request):
    if request.method == 'POST':
        print 'inside cassandra get statistics for vav based on given from and to datetime'
        _data = request.body
        _data = json.loads(_data)
        mac = _data['mac']
        from_date = _data['from_dt']
        to_date = _data['to_dt']
        print from_date

        device_id = get_device_id_from_mac(mac)
        if not from_date and not to_date:
            data_points, rs = retrieve(device_id, ['time', 'temperature', 'supply_temperature',
                                  'heat_setpoint', 'cool_setpoint', 'flap_position'])
        elif not to_date and from_date:
            from_date = datetime.datetime.strptime(from_date, '%Y/%m/%d %H:%M')
            data_points, rs = retrieve(device_id, ['time', 'temperature', 'supply_temperature',
                                  'heat_setpoint', 'cool_setpoint', 'flap_position'], from_date)
        else:
            from_date = datetime.datetime.strptime(from_date, '%Y/%m/%d %H:%M')
            to_date = datetime.datetime.strptime(to_date, '%Y/%m/%d %H:%M')
            data_points, rs = retrieve(device_id, ['time', 'temperature', 'supply_temperature',
                                  'heat_setpoint', 'cool_setpoint', 'flap_position'], from_date, to_date)

        rs_temperature = parse_resultset(data_points, 'temperature', rs)
        rs_supply_temperature = parse_resultset(data_points, 'supply_temperature', rs)
        rs_heat_setpoint = parse_resultset(data_points, 'heat_setpoint', rs)
        rs_cool_setpoint = parse_resultset(data_points, 'cool_setpoint', rs)
        rs_flap_position = parse_resultset(data_points, 'flap_position', rs)

        json_result = {'temperature': rs_temperature,
                       'supply_temperature': rs_supply_temperature,
                        'flap_position': rs_flap_position,
                        'heat_setpoint': rs_heat_setpoint,
                        'cool_setpoint': rs_cool_setpoint}

        print 'Got results based on datetime'
        if request.is_ajax():
                return HttpResponse(json.dumps(json_result), mimetype='application/json')


@login_required(login_url='/login/')
def charts_rtu(request, mac):
    """Page load definition for RTU statistics."""
    print "inside smap view method"
    context = RequestContext(request)
    if request.method == 'GET':

        device_id = get_device_id_from_mac(mac)

        device_status = [ob.as_json() for ob in RTU.objects.filter(rtu_id=device_id)]
        device_nickname = device_status[0]['nickname']
        zone_nickname = device_status[0]['zone']['zone_nickname']

        data_points, rs = retrieve(device_id, ['time', 'outside_temperature', 'return_temperature', 'supply_temperature',
                                  'heat_setpoint', 'cool_setpoint', 'cooling_mode', 'heating',
                                  'outside_damper_position', 'bypass_damper_position'])

        rs_outside_temperature = parse_resultset(data_points, 'outside_temperature', rs)
        rs_return_temperature = parse_resultset(data_points, 'return_temperature', rs)
        rs_supply_temperature = parse_resultset(data_points, 'supply_temperature', rs)
        rs_heat_setpoint = parse_resultset(data_points, 'heat_setpoint', rs)
        rs_cool_setpoint = parse_resultset(data_points, 'cool_setpoint', rs)
        rs_cooling_mode = []

        rs_heating = parse_resultset(data_points, 'heating', rs)
        rs_outside_damper_position = parse_resultset(data_points, 'outside_damper_position', rs)
        rs_bypass_damper_position = parse_resultset(data_points, 'bypass_damper_position', rs)


        context = update_context(context)

        return render_to_response(
            'charts/charts_rtu.html',
            {'outside_temperature': rs_outside_temperature, 'supply_temperature': rs_supply_temperature,
             'return_temperature': rs_return_temperature, 'heating': rs_heating,
             'outside_damper_position': rs_outside_damper_position,
             'bypass_damper_position': rs_bypass_damper_position, 'cooling_mode': rs_cooling_mode,
             'heat_setpoint': rs_heat_setpoint, 'cool_setpoint': rs_cool_setpoint,
             'nickname': device_nickname, 'mac': mac,
             'zone_nickname': zone_nickname},
            context)


@login_required(login_url='/login/')
def auto_update_charts_rtu(request):
    """Statistics page update for RTU"""
    if request.method == 'POST':
        print 'inside cassandra auto update RTU'
        _data = request.body
        _data = json.loads(_data)
        mac = _data['mac']
        if 'from_dt' in _data.keys():
            from_date = _data['from_dt']
            print from_date
        else:
            from_date = ''

        device_id = get_device_id_from_mac(mac)
        if from_date == '':
            data_points, rs = retrieve(device_id, ['time', 'outside_temperature', 'return_temperature', 'supply_temperature',
                                      'heat_setpoint', 'cool_setpoint', 'cooling_mode', 'heating',
                                      'outside_damper_position', 'bypass_damper_position'])
        else:
            from_date = datetime.datetime.strptime(from_date, '%Y/%m/%d %H:%M')
            data_points, rs = retrieve(device_id, ['time', 'outside_temperature', 'return_temperature', 'supply_temperature',
                                      'heat_setpoint', 'cool_setpoint', 'cooling_mode', 'heating',
                                      'outside_damper_position', 'bypass_damper_position'], from_date)

        rs_outside_temperature = parse_resultset(data_points, 'outside_temperature', rs)
        rs_return_temperature = parse_resultset(data_points, 'return_temperature', rs)
        rs_supply_temperature = parse_resultset(data_points, 'supply_temperature', rs)
        rs_heat_setpoint = parse_resultset(data_points, 'heat_setpoint', rs)
        rs_cool_setpoint = parse_resultset(data_points, 'cool_setpoint', rs)
        rs_cooling_mode = parse_resultset(data_points, 'cooling_mode', rs)
        rs_heating = parse_resultset(data_points, 'heating', rs)
        rs_outside_damper_position = parse_resultset(data_points, 'outside_damper_position', rs)
        rs_bypass_damper_position = parse_resultset(data_points, 'bypass_damper_position', rs)

        json_result = {'outside_temperature': rs_outside_temperature,
                       'supply_temperature': rs_supply_temperature,
                        'return_temperature': rs_return_temperature,
                        'heating': rs_heating,
                        'outside_damper_position': rs_outside_damper_position,
                        'bypass_damper_position': rs_bypass_damper_position,
                        'cooling_mode': rs_cooling_mode,
                        'heat_setpoint': rs_heat_setpoint,
                        'cool_setpoint': rs_cool_setpoint}

        print 'test'
        if request.is_ajax():
                return HttpResponse(json.dumps(json_result), mimetype='application/json')


@login_required(login_url='/login/')
def get_statistics_datetime_rtu(request):
    if request.method == 'POST':
        print 'inside cassandra get statistics for rtu based on given from and to datetime'
        _data = request.body
        _data = json.loads(_data)
        mac = _data['mac']
        from_date = _data['from_dt']
        to_date = _data['to_dt']
        print from_date

        device_id = get_device_id_from_mac(mac)
        if not from_date and not to_date:
            data_points, rs = retrieve(device_id, ['time', 'outside_temperature', 'return_temperature', 'supply_temperature',
                                      'heat_setpoint', 'cool_setpoint', 'cooling_mode', 'heating',
                                      'outside_damper_position', 'bypass_damper_position'])
        elif not to_date and from_date:
            from_date = datetime.datetime.strptime(from_date, '%Y/%m/%d %H:%M')
            data_points, rs = retrieve(device_id, ['time', 'outside_temperature', 'return_temperature', 'supply_temperature',
                                      'heat_setpoint', 'cool_setpoint', 'cooling_mode', 'heating',
                                      'outside_damper_position', 'bypass_damper_position'], from_date)
        else:
            from_date = datetime.datetime.strptime(from_date, '%Y/%m/%d %H:%M')
            to_date = datetime.datetime.strptime(to_date, '%Y/%m/%d %H:%M')
            data_points, rs = retrieve(device_id, ['time', 'outside_temperature', 'return_temperature', 'supply_temperature',
                                      'heat_setpoint', 'cool_setpoint', 'cooling_mode', 'heating',
                                      'outside_damper_position', 'bypass_damper_position'], from_date, to_date)

        rs_outside_temperature = parse_resultset(data_points, 'outside_temperature', rs)
        rs_return_temperature = parse_resultset(data_points, 'return_temperature', rs)
        rs_supply_temperature = parse_resultset(data_points, 'supply_temperature', rs)
        rs_heat_setpoint = parse_resultset(data_points, 'heat_setpoint', rs)
        rs_cool_setpoint = parse_resultset(data_points, 'cool_setpoint', rs)
        rs_cooling_mode = parse_resultset(data_points, 'cooling_mode', rs)
        rs_heating = parse_resultset(data_points, 'heating', rs)
        rs_outside_damper_position = parse_resultset(data_points, 'outside_damper_position', rs)
        rs_bypass_damper_position = parse_resultset(data_points, 'bypass_damper_position', rs)


        json_result = {'outside_temperature': rs_outside_temperature,
                       'supply_temperature': rs_supply_temperature,
                       'return_temperature': rs_return_temperature,
                       'heating': rs_heating,
                       'outside_damper_position': rs_outside_damper_position,
                       'bypass_damper_position': rs_bypass_damper_position,
                       'cooling_mode': rs_cooling_mode,
                       'heat_setpoint': rs_heat_setpoint,
                       'cool_setpoint': rs_cool_setpoint
                       }

        print 'Got results based on datetime'
        if request.is_ajax():
                return HttpResponse(json.dumps(json_result), mimetype='application/json')


@login_required(login_url='/login/')
def auto_update_charts_lighting(request):
    if request.method == 'POST':
        print 'inside cassandra auto update lighting'
        _data = request.body
        _data = json.loads(_data)
        mac = _data['mac']

        if 'from_dt' in _data.keys():
            from_date = _data['from_dt']
            print from_date
        else:
            from_date = ''

        device_id = get_device_id_from_mac(mac)
        if from_date == '':
            data_points, rs = retrieve(device_id, ['time', 'status', 'brightness'])
        else:
            from_date = datetime.datetime.strptime(from_date, '%Y/%m/%d %H:%M')
            data_points, rs = retrieve(device_id, ['time', 'status', 'brightness'], from_date)

        rs_status = parse_resultset(data_points, 'status', rs)
        rs_brightness = parse_resultset(data_points, 'brightness', rs)

        json_result = {
            'status': rs_status,
            'brightness': rs_brightness
        }

        if request.is_ajax():
            return HttpResponse(json.dumps(json_result), mimetype='application/json')


@login_required(login_url='/login/')
def get_statistics_datetime_lighting(request):
    if request.method == 'POST':
        print 'inside cassandra get statistics for lighting based on given from and to datetime'
        _data = request.body
        _data = json.loads(_data)
        mac = _data['mac']
        from_date = _data['from_dt']
        to_date = _data['to_dt']
        print from_date

        device_id = get_device_id_from_mac(mac)
        if not from_date and not to_date:
            data_points, rs = retrieve(device_id, ['time', 'status', 'brightness'])
        elif not to_date and from_date:
            from_date = datetime.datetime.strptime(from_date, '%Y/%m/%d %H:%M')
            data_points, rs = retrieve(device_id, ['time', 'status', 'brightness'], from_date)
        else:
            from_date = datetime.datetime.strptime(from_date, '%Y/%m/%d %H:%M')
            to_date = datetime.datetime.strptime(to_date, '%Y/%m/%d %H:%M')
            data_points, rs = retrieve(device_id, ['time', 'status', 'brightness'], from_date, to_date)

        rs_status = parse_resultset(data_points, 'status', rs)
        rs_brightness = parse_resultset(data_points, 'brightness', rs)

        json_result = {
            'status': rs_status,
            'brightness': rs_brightness
        }

        print 'Got results based on datetime'
        if request.is_ajax():
                return HttpResponse(json.dumps(json_result), mimetype='application/json')


@login_required(login_url='/login/')
def charts_lighting(request, mac):
    print "inside cassandra view method for lighting"
    context = RequestContext(request)
    if request.method == 'GET':

        device_id = get_device_id_from_mac(mac)

        device_status = [ob.data_as_json() for ob in Lighting.objects.filter(lighting_id=device_id)]
        device_nickname = device_status[0]['nickname']
        zone_nickname = device_status[0]['zone']['zone_nickname']

        data_points, rs = retrieve(device_id, ['time', 'status', 'brightness'])

        rs_status = parse_resultset(data_points, 'status', rs)
        rs_brightness = parse_resultset(data_points, 'brightness', rs)

        context = update_context(context)

        return render_to_response(
            'charts/charts_lighting.html',
            {'status': rs_status, 'brightness': rs_brightness,
             'nickname': device_nickname, 'zone_nickname': zone_nickname,
             'mac': mac}, context)


@login_required(login_url='/login/')
def charts_plugload(request, mac):
    print "inside cassandra view method for plugload"
    context = RequestContext(request)
    if request.method == 'GET':

        device_metadata = [ob.device_control_page_info() for ob in DeviceMetadata.objects.filter(mac_address=mac)]
        device_id = device_metadata[0]['device_id']
        device_type_id = device_metadata[0]['device_model_id']
        device_type_id = device_type_id.device_model_id

        if device_type_id == '2WL':
            device_status = [ob.data_as_json() for ob in Lighting.objects.filter(lighting_id=device_id)]
            device_nickname = device_status[0]['nickname']
            zone_nickname = device_status[0]['zone']['zone_nickname']
        else:
            device_status = [ob.data_as_json() for ob in Plugload.objects.filter(plugload_id=device_id)]
            device_nickname = device_status[0]['nickname']
            zone_nickname = device_status[0]['zone']['zone_nickname']

        data_points, rs = retrieve(device_id, ['time', 'status'])
        rs_status = parse_resultset(data_points, 'status', rs)

        update_context(context)

        return render_to_response(
            'charts/charts_plugload.html',
            {'status': rs_status, 'mac': mac, 'nickname': device_nickname, 'zone_nickname': zone_nickname,
             'device_type_id': device_type_id}, context)


@login_required(login_url='/login/')
def auto_update_charts_plugload(request):
    if request.method == 'POST':
        print 'inside cassandra auto update plugload'
        _data = request.body
        _data = json.loads(_data)
        mac = _data['mac']
        if 'from_dt' in _data.keys():
            from_date = _data['from_dt']
            print from_date
        else:
            from_date = ''

        device_id = get_device_id_from_mac(mac)
        if from_date == '':
            data_points, rs = retrieve(device_id, ['time', 'status'])
        else:
            from_date = datetime.datetime.strptime(from_date, '%Y/%m/%d %H:%M')
            data_points, rs = retrieve(device_id, ['time', 'status'], from_date)

        rs_status = parse_resultset(data_points, 'status', rs)

        json_result = {
            'status': rs_status
        }

        print 'test'
        if request.is_ajax():
            return HttpResponse(json.dumps(json_result), mimetype='application/json')


@login_required(login_url='/login/')
def get_statistics_datetime_plugload(request):
    if request.method == 'POST':
        print 'inside cassandra get statistics for plugload based on given from and to datetime'
        _data = request.body
        _data = json.loads(_data)
        mac = _data['mac']
        from_date = _data['from_dt']
        to_date = _data['to_dt']
        print from_date

        device_id = get_device_id_from_mac(mac)
        if not from_date and not to_date:
            data_points, rs = retrieve(device_id, ['time', 'status'])
        elif not to_date and from_date:
            from_date = datetime.datetime.strptime(from_date, '%Y/%m/%d %H:%M')
            data_points, rs = retrieve(device_id, ['time', 'status'], from_date)
        else:
            from_date = datetime.datetime.strptime(from_date, '%Y/%m/%d %H:%M')
            to_date = datetime.datetime.strptime(to_date, '%Y/%m/%d %H:%M')
            data_points, rs = retrieve(device_id, ['time', 'status'], from_date, to_date)

        rs_status = parse_resultset(data_points, 'status', rs)

        json_result = {
            'status': rs_status
        }

        print 'Got results based on datetime'
        if request.is_ajax():
                return HttpResponse(json.dumps(json_result), mimetype='application/json')


@login_required(login_url='/login/')
def charts_wattstopper_plugload(request, mac):
    context = RequestContext(request)
    if request.method == 'GET':

        device_id = get_device_id_from_mac(mac)

        device_status = [ob.data_as_json() for ob in Plugload.objects.filter(plugload_id=device_id)]
        device_nickname = device_status[0]['nickname']
        zone_nickname = device_status[0]['zone']['zone_nickname']

        data_points, rs = retrieve(device_id, ['time', 'status', 'power'])

        rs_status = parse_resultset(data_points, 'status', rs)
        rs_power = parse_resultset(data_points, 'power', rs)

        context = update_context(context)

        return render_to_response(
            'charts/charts_wtplug.html',
            {'status': rs_status, 'power': rs_power, 'nickname': device_nickname, 'zone_nickname': zone_nickname,
             'mac': mac}, context)


@login_required(login_url='/login/')
def auto_update_charts_wattstopper_plugload(request):
    if request.method == 'POST':
        print 'inside cassandra auto update wattstopper plugload'
        _data = request.body
        _data = json.loads(_data)
        mac = _data['mac']
        if 'from_dt' in _data.keys():
            from_date = _data['from_dt']
            print from_date
        else:
            from_date = ''

        device_id = get_device_id_from_mac(mac)
        if from_date == '':
            data_points, rs = retrieve(device_id, ['time', 'status', 'power'])
        else:
            from_date = datetime.datetime.strptime(from_date, '%Y/%m/%d %H:%M')
            data_points, rs = retrieve(device_id, ['time', 'status', 'power'], from_date)

        rs_status = parse_resultset(data_points, 'status', rs)
        rs_power = parse_resultset(data_points, 'power', rs)

        json_result = {
            'status': rs_status,
            'power': rs_power
        }

        if request.is_ajax():
            return HttpResponse(json.dumps(json_result), mimetype='application/json')


@login_required(login_url='/login/')
def get_statistics_datetime_wattstopper_plugload(request):
    if request.method == 'POST':
        print 'inside cassandra get statistics for wattstopper plugload based on given from and to datetime'
        _data = request.body
        _data = json.loads(_data)
        mac = _data['mac']
        from_date = _data['from_dt']
        to_date = _data['to_dt']
        print from_date

        device_id = get_device_id_from_mac(mac)
        if not from_date and not to_date:
            data_points, rs = retrieve(device_id, ['time', 'status', 'power'])
        elif not to_date and from_date:
            from_date = datetime.datetime.strptime(from_date, '%Y/%m/%d %H:%M')
            data_points, rs = retrieve(device_id, ['time', 'status', 'power'], from_date)
        else:
            from_date = datetime.datetime.strptime(from_date, '%Y/%m/%d %H:%M')
            to_date = datetime.datetime.strptime(to_date, '%Y/%m/%d %H:%M')
            print from_date, to_date
            data_points, rs = retrieve(device_id, ['time', 'status', 'power'], from_date, to_date)

        rs_status = parse_resultset(data_points, 'status', rs)
        rs_power = parse_resultset(data_points, 'power', rs)

        json_result = {
            'status': rs_status,
            'power': rs_power
        }

        print 'Got results based on datetime'
        if request.is_ajax():
                return HttpResponse(json.dumps(json_result), mimetype='application/json')




def get_device_id_from_mac(mac):
    device_metadata = [ob.device_control_page_info() for ob in DeviceMetadata.objects.filter(mac_address=mac)]
    print device_metadata
    device_id = device_metadata[0]['device_id']
    return device_id


def update_context(context):
    device_list_side_nav = get_device_list_side_navigation()
    context.update(device_list_side_nav)
    active_al = get_notifications()
    context.update({'active_al': active_al})
    bemoss_not = general_notifications()
    context.update({'b_al': bemoss_not})
    return context


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