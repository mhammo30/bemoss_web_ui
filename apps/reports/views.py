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
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from apps.RTU.models import RTU
from apps.VAV.models import VAV
from apps.dashboard.models import DeviceMetadata
from apps.lighting.models import Lighting
from apps.smartplug.models import Plugload
from apps.thermostat.models import Thermostat
import settings_tornado
import sys
sys.path.insert(0,os.path.expanduser('~/workspace/bemoss_os/'))
from bemoss_lib.databases.cassandraAPI.cassandraDB import retrieve_for_export
# Modified by Xiangyu Zhang for Rearranging sequence of CSV file.

import json
import datetime
import tablib
from collections import OrderedDict


def parse_resultset(variables, data_point, result_set):
    return [{"time": lst[variables.index('time')],"temperature":lst[variables.index('temperature')], "heat_setpoint":lst[variables.index('temperature')]}for lst in result_set]


def get_device_id_from_mac(mac):
    device_metadata = [ob.device_control_page_info() for ob in DeviceMetadata.objects.filter(mac_address=mac)]
    print device_metadata
    device_id = device_metadata[0]['device_id']
    return device_id


def append_data_smap(_data, data):
    for smap_data in _data:
        s = smap_data[0] / 1000.0
        s = datetime.datetime.fromtimestamp(s).strftime('%Y-%m-%d %H:%M:%S')
        data.append((s, smap_data[1]))
    return data


def export_thermostat_time_series_data_spreadsheet(request):
    if request.method == 'POST':
        print 'inside export to spreadsheet for thermostat based on given from and to datetime'
        _data = request.body
        print _data
        _data = json.loads(_data)
        mac = _data['mac']
        from_date = _data['from_dt']
        to_date = _data['to_dt']
        print from_date

        device_id = get_device_id_from_mac(mac)

        if not from_date and not to_date:
            data_points, rs = retrieve_for_export(device_id, ['time', 'temperature',
                                                              'heat_setpoint', 'cool_setpoint'])
        elif not to_date and from_date:
            from_date = datetime.datetime.strptime(from_date, '%Y/%m/%d %H:%M')
            data_points, rs = retrieve_for_export(device_id, ['time', 'temperature',
                                                            'heat_setpoint', 'cool_setpoint'], from_date)
        else:
            from_date = datetime.datetime.strptime(from_date, '%Y/%m/%d %H:%M')
            to_date = datetime.datetime.strptime(to_date, '%Y/%m/%d %H:%M')
            data_points, rs = retrieve_for_export(device_id, ['time', 'temperature',
                                                              'heat_setpoint', 'cool_setpoint'], from_date, to_date)

        _data = list()
        for lst in rs:
            single_entry = {"1.time": lst[data_points.index('time')],
                   "2.temperature": lst[data_points.index('temperature')],
                   "3.heat_setpoint": lst[data_points.index('heat_setpoint')],
                   "4.cool_setpoint": lst[data_points.index('cool_setpoint')]}
            new_single = OrderedDict(sorted(single_entry.items(), key=lambda t:t[0]))
            _data.append(new_single)

        if request.is_ajax():
                return HttpResponse(json.dumps(_data), mimetype='application/json')


def export_plugload_time_series_data_spreadsheet(request):
    if request.method == 'POST':
        print 'inside export to spreadsheet for plugload/lighting with just status based on given from and to datetime'
        _data = request.body
        print _data
        _data = json.loads(_data)
        mac = _data['mac']
        from_date = _data['from_dt']
        to_date = _data['to_dt']
        print from_date

        device_id = get_device_id_from_mac(mac)

        if not from_date and not to_date:
            data_points, rs = retrieve_for_export(device_id, ['time', 'status'])
        elif not to_date and from_date:
            from_date = datetime.datetime.strptime(from_date, '%Y/%m/%d %H:%M')
            data_points, rs = retrieve_for_export(device_id, ['time', 'status'], from_date)
        else:
            from_date = datetime.datetime.strptime(from_date, '%Y/%m/%d %H:%M')
            to_date = datetime.datetime.strptime(to_date, '%Y/%m/%d %H:%M')
            data_points, rs = retrieve_for_export(device_id, ['time', 'status'], from_date, to_date)

        _data = list()
        for lst in rs:
            single_entry = {"1.time": lst[data_points.index('time')],
                   "2.status": lst[data_points.index('status')]}
            new_single = OrderedDict(sorted(single_entry.items(), key=lambda t:t[0]))
            _data.append(new_single)

        if request.is_ajax():
                return HttpResponse(json.dumps(_data), mimetype='application/json')


def export_lighting_time_series_data_spreadsheet(request):
    if request.method == 'POST':
        print 'inside export to spreadsheet for lighting with just status based on given from and to datetime'
        _data = request.body
        print _data
        _data = json.loads(_data)
        mac = _data['mac']
        from_date = _data['from_dt']
        to_date = _data['to_dt']
        print from_date

        device_id = get_device_id_from_mac(mac)

        if not from_date and not to_date:
            data_points, rs = retrieve_for_export(device_id, ['time', 'status', 'brightness'])
        elif not to_date and from_date:
            from_date = datetime.datetime.strptime(from_date, '%Y/%m/%d %H:%M')
            data_points, rs = retrieve_for_export(device_id, ['time', 'status', 'brightness'], from_date)
        else:
            from_date = datetime.datetime.strptime(from_date, '%Y/%m/%d %H:%M')
            to_date = datetime.datetime.strptime(to_date, '%Y/%m/%d %H:%M')
            data_points, rs = retrieve_for_export(device_id, ['time', 'status', 'brightness'], from_date, to_date)

        _data = list()
        for lst in rs:
            single_entry = {"1.time": lst[data_points.index('time')],
                   "2.status": lst[data_points.index('status')],
                   "3.brightness": lst[data_points.index('brightness')]}
            new_single = OrderedDict(sorted(single_entry.items(), key=lambda t:t[0]))
            _data.append(new_single)

        if request.is_ajax():
                return HttpResponse(json.dumps(_data), mimetype='application/json')


def export_wattplug_time_series_data_spreadsheet(request):
    if request.method == 'POST':
        print 'inside export to spreadsheet for lighting with just status based on given from and to datetime'
        _data = request.body
        print _data
        _data = json.loads(_data)
        mac = _data['mac']
        from_date = _data['from_dt']
        to_date = _data['to_dt']
        print from_date

        device_id = get_device_id_from_mac(mac)

        if not from_date and not to_date:
            data_points, rs = retrieve_for_export(device_id, ['time', 'status', 'power'])
        elif not to_date and from_date:
            from_date = datetime.datetime.strptime(from_date, '%Y/%m/%d %H:%M')
            data_points, rs = retrieve_for_export(device_id, ['time', 'status', 'power'], from_date)
        else:
            from_date = datetime.datetime.strptime(from_date, '%Y/%m/%d %H:%M')
            to_date = datetime.datetime.strptime(to_date, '%Y/%m/%d %H:%M')
            data_points, rs = retrieve_for_export(device_id, ['time', 'status', 'power'], from_date, to_date)

        _data = list()
        for lst in rs:
            single_entry = {"1.time": lst[data_points.index('time')],
                   "2.status": lst[data_points.index('status')],
                   "3.power": lst[data_points.index('power')]}
            new_single = OrderedDict(sorted(single_entry.items(), key=lambda t:t[0]))
            _data.append(new_single)

        if request.is_ajax():
                return HttpResponse(json.dumps(_data), mimetype='application/json')


def export_vav_time_series_data_spreadsheet(request):
    if request.method == 'POST':
        print 'inside export to spreadsheet for vav based on given from and to datetime'
        _data = request.body
        print _data
        _data = json.loads(_data)
        mac = _data['mac']
        from_date = _data['from_dt']
        to_date = _data['to_dt']
        print from_date

        device_id = get_device_id_from_mac(mac)

        if not from_date and not to_date:
            data_points, rs = retrieve_for_export(device_id, ['time', 'temperature', 'supply_temperature',
                                                              'heat_setpoint', 'cool_setpoint', 'flap_position'])
        elif not to_date and from_date:
            from_date = datetime.datetime.strptime(from_date, '%Y/%m/%d %H:%M')
            data_points, rs = retrieve_for_export(device_id, ['time', 'temperature', 'supply_temperature',
                                                              'heat_setpoint', 'cool_setpoint', 'flap_position'], from_date)
        else:
            from_date = datetime.datetime.strptime(from_date, '%Y/%m/%d %H:%M')
            to_date = datetime.datetime.strptime(to_date, '%Y/%m/%d %H:%M')
            data_points, rs = retrieve_for_export(device_id, ['time', 'temperature', 'supply_temperature',
                                                              'heat_setpoint', 'cool_setpoint', 'flap_position'], from_date, to_date)

        _data = list()
        for lst in rs:
            single_entry = {"1.time": lst[data_points.index('time')],
                  "2.temperature": lst[data_points.index('temperature')],
                  "3.supply_temperature": lst[data_points.index('supply_temperature')],
                  "4.heat_setpoint": lst[data_points.index('heat_setpoint')],
                  "5.cool_setpoint": lst[data_points.index('cool_setpoint')],
                  "6.flap_position": lst[data_points.index('flap_position')]}
            new_single = OrderedDict(sorted(single_entry.items(), key=lambda t:t[0]))
            _data.append(new_single)

        if request.is_ajax():
                return HttpResponse(json.dumps(_data), mimetype='application/json')


def export_rtu_time_series_data_spreadsheet(request):
    if request.method == 'POST':
        print 'inside export to spreadsheet for rtu based on given from and to datetime'
        _data = request.body
        print _data
        _data = json.loads(_data)
        mac = _data['mac']
        from_date = _data['from_dt']
        to_date = _data['to_dt']
        print from_date

        device_id = get_device_id_from_mac(mac)

        if not from_date and not to_date:
            data_points, rs = retrieve_for_export(device_id, ['time', 'outside_temperature', 'supply_temperature',
                                                              'return_temperature', 'heating', 'heat_setpoint',
                                                              'cool_setpoint', 'outside_damper_position',
                                                              'bypass_damper_position'])
        elif not to_date and from_date:
            from_date = datetime.datetime.strptime(from_date, '%Y/%m/%d %H:%M')
            data_points, rs = retrieve_for_export(device_id, ['time', 'outside_temperature', 'supply_temperature',
                                                              'return_temperature', 'heating', 'heat_setpoint',
                                                              'cool_setpoint', 'outside_damper_position',
                                                              'bypass_damper_position'], from_date)
        else:
            from_date = datetime.datetime.strptime(from_date, '%Y/%m/%d %H:%M')
            to_date = datetime.datetime.strptime(to_date, '%Y/%m/%d %H:%M')
            data_points, rs = retrieve_for_export(device_id, ['time', 'outside_temperature', 'supply_temperature',
                                                              'return_temperature', 'heating', 'heat_setpoint',
                                                              'cool_setpoint', 'outside_damper_position',
                                                              'bypass_damper_position'], from_date, to_date)


        _data = list()
        for lst in rs:
            single_entry = {"1.time": lst[data_points.index('time')],
                  "2.outside_temperature": lst[data_points.index('outside_temperature')],
                  "3.supply_temperature": lst[data_points.index('supply_temperature')],
                  "4.return_temperature": lst[data_points.index('return_temperature')],
                  "5.heating": lst[data_points.index('heating')],
                  "6.heat_setpoint": lst[data_points.index('heat_setpoint')],
                  "7.cool_setpoint": lst[data_points.index('cool_setpoint')],
                  "8.outside_damper_position": lst[data_points.index('outside_damper_position')],
                  "9.bypass_damper_position": lst[data_points.index('bypass_damper_position')]}
            new_single = OrderedDict(sorted(single_entry.items(), key=lambda t:t[0]))
            _data.append(new_single)

        if request.is_ajax():
                return HttpResponse(json.dumps(_data), mimetype='application/json')


@login_required(login_url='/login/')
def export_thermostat_to_spreadsheet(request):
    _data_th = [ob.device_status() for ob in Thermostat.objects.filter(thermostat_id__approval_status='APR')]
    _data_vav = [ob.device_status() for ob in VAV.objects.filter(vav_id__approval_status='APR')]
    _data_rtu = [ob.device_status() for ob in RTU.objects.filter(rtu_id__approval_status='APR')]
    response = get_data([_data_th, _data_vav, _data_rtu], "thermostat")
    return response


@login_required(login_url='/login/')
def export_lighting_to_spreadsheet(request):
    _data = [ob.device_status() for ob in Lighting.objects.filter(lighting_id__approval_status='APR')]
    response = get_data([_data], "lighting")
    return response


@login_required(login_url='/login/')
def export_plugload_to_spreadsheet(request):
    _data = [ob.device_status() for ob in Plugload.objects.filter(plugload_id__approval_status='APR')]
    response = get_data([_data], "plugload")
    return response


def get_data(__data, device_type):
    headers = ('Device Nickname', 'Zone', 'Device Model', 'Device Added On', 'Network Status', 'Last Scanned Time',
               'Last Offline Time')
    data = []
    data = tablib.Dataset(*data, headers=headers, title=device_type)
    for _data in __data:
        for device in _data:
            data.append((device['nickname'], device['zone_nickname'], device['device_model'],
                        str(device['date_added']),
                        device['network_status'],
                        str(device['last_scanned']),
                         str(device['last_offline'])))
    response = HttpResponse(data.xls, content_type='application/vnd.ms-excel;charset=utf-8')
    response['Content-Disposition'] = "attachment; filename=bemoss_" + device_type + ".xls"
    return response


@login_required(login_url='/login/')
def export_all_device_information(request):
    _data_th = [ob.device_status() for ob in Thermostat.objects.filter(thermostat_id__approval_status='APR')]
    _data_vav = [ob.device_status() for ob in VAV.objects.filter(vav_id__approval_status='APR')]
    _data_rtu = [ob.device_status() for ob in RTU.objects.filter(rtu_id__approval_status='APR')]
    _data_hvac = data_this([_data_th, _data_vav, _data_rtu], "Thermostats")
    _data_lt = [ob.device_status() for ob in Lighting.objects.filter(lighting_id__approval_status='APR')]
    _data_lt = data_this([_data_lt], "Lighting Loads")
    _data_pl = [ob.device_status() for ob in Plugload.objects.filter(plugload_id__approval_status='APR')]
    _data_pl = data_this([_data_pl], "Plugloads")

    devices = tablib.Databook((_data_hvac, _data_lt, _data_pl))
    with open('bemoss_devices.xls', 'wb') as f:
        f.write(devices.xls)
    response = HttpResponse(devices.xls, content_type='application/vnd.ms-excel;charset=utf-8')
    response['Content-Disposition'] = "attachment; filename=bemoss_devices.xls"
    return response


def data_this(__data, sheetname):
    headers = ('Device Nickname', 'Zone', 'Device Model', 'Device Added On', 'Network Status', 'Last Scanned Time',
               'Last Offline Time')
    data = []
    data = tablib.Dataset(*data, headers=headers,  title=sheetname)
    for _data in __data:
        for device in _data:
            data.append((device['nickname'], device['zone_nickname'], device['device_model'],
                        str(device['date_added']),
                        device['network_status'],
                        str(device['last_scanned']),
                         str(device['last_offline'])))
    return data


@login_required(login_url='/login/')
def export_schedule_thermostats_holiday(request, mac):
    mac = mac.encode('ascii', 'ignore')
    device = DeviceMetadata.objects.get(mac_address=mac)

    _file_name = os.path.join(settings_tornado.PROJECT_DIR, 'resources/scheduler_data/thermostat/' + device.device_id
                              + '_schedule.json')
    if os.path.isfile(_file_name):
            json_file = open(_file_name, 'r+')
            _json_data = json.load(json_file)
            if device.device_id in _json_data['thermostat']:
                print 'device id present'
                _data = _json_data['thermostat'][device.device_id]['schedulers']['holiday']
                _data = json.dumps(_data)
                _data = json.loads(_data, object_hook=_decode_dict)
            json_file.close()

    headers = ('Period Name', 'From', 'Heat Setpoint (F)', 'Cool Setpoint (F)')
    data = []
    data = tablib.Dataset(*data, headers=headers,  title='Holiday')

    for record in _data:
        rec_time = str(int(record['at'])/60) + ':' + str(int(record['at']) % 60)
        data.append((record['nickname'], rec_time, record['heat_setpoint'], record['cool_setpoint']))

    response = HttpResponse(data.xls, content_type='application/vnd.ms-excel;charset=utf-8')
    response['Content-Disposition'] = "attachment; filename=" + device.device_model + "_holiday_sch.xls"
    return response


@login_required(login_url='/login/')
def export_schedule_thermostats_daily(request, mac):
    mac = mac.encode('ascii', 'ignore')
    device = DeviceMetadata.objects.get(mac_address=mac)

    _file_name = os.path.join(settings_tornado.PROJECT_DIR, 'resources/scheduler_data/thermostat/' + device.device_id
                              + '_schedule.json')
    if os.path.isfile(_file_name):
            json_file = open(_file_name, 'r+')
            _json_data = json.load(json_file)
            if device.device_id in _json_data['thermostat']:
                print 'device id present'
                _data = _json_data['thermostat'][device.device_id]['schedulers']['everyday']
                _data = json.dumps(_data)
                _data = json.loads(_data, object_hook=_decode_dict)
            json_file.close()

    headers = ('Period Name', 'From', 'Heat Setpoint (F)', 'Cool Setpoint (F)')
    _data_mon = _data_tue = _data_wed = _data_thu = _data_fri = _data_sat = _data_sun = []

    for day in _data:
        data = []
        data = tablib.Dataset(*data, headers=headers,  title=day)
        day_data = _data[day]
        for record in day_data:
            rec_time = str(int(record['at'])/60) + ':' + str(int(record['at']) % 60)
            data.append((record['nickname'], rec_time, record['heat_setpoint'], record['cool_setpoint']))

        if day == 'monday':
            _data_mon = data
        elif day == 'tuesday':
            _data_tue = data
        elif day == 'wednesday':
            _data_wed = data
        elif day == 'thursday':
            _data_thu = data
        elif day == 'friday':
            _data_fri = data
        elif day == 'saturday':
            _data_sat = data
        elif day == 'sunday':
            _data_sun = data

    schedule = tablib.Databook((_data_mon, _data_tue, _data_wed, _data_thu, _data_fri, _data_sat, _data_sun))

    with open(device.device_model + "_daily_sch.xls", 'wb') as f:
        f.write(schedule.xls)
    response = HttpResponse(schedule.xls, content_type='application/vnd.ms-excel;charset=utf-8')
    response['Content-Disposition'] = "attachment; filename=" +device.device_model + "_daily_sch.xls"
    return response


@login_required(login_url='/login/')
def export_schedule_lighting_daily(request, mac):
    mac = mac.encode('ascii', 'ignore')
    device = DeviceMetadata.objects.get(mac_address=mac)

    if device.device_model_id.device_model_id == '2WL':

        _file_name = os.path.join(settings_tornado.PROJECT_DIR, 'resources/scheduler_data/lighting/' + device.device_id
                                  + '_schedule.json')
        if os.path.isfile(_file_name):
                json_file = open(_file_name, 'r+')
                _json_data = json.load(json_file)
                if device.device_id in _json_data['lighting']:
                    print 'device id present'
                    _data = _json_data['lighting'][device.device_id]['schedulers']['everyday']
                    _data = json.dumps(_data)
                    _data = json.loads(_data, object_hook=_decode_dict)
                json_file.close()

        headers = ('Period Name', 'From', 'Status')
        _data_mon = _data_tue = _data_wed = _data_thu = _data_fri = _data_sat = _data_sun = []

        for day in _data:
            data = []
            data = tablib.Dataset(*data, headers=headers,  title=day)
            day_data = _data[day]
            for record in day_data:
                rec_time = str(int(record['at'])/60) + ':' + str(int(record['at']) % 60)
                data.append((record['nickname'], rec_time, record['status']))

            if day == 'monday':
                _data_mon = data
            elif day == 'tuesday':
                _data_tue = data
            elif day == 'wednesday':
                _data_wed = data
            elif day == 'thursday':
                _data_thu = data
            elif day == 'friday':
                _data_fri = data
            elif day == 'saturday':
                _data_sat = data
            elif day == 'sunday':
                _data_sun = data

        schedule = tablib.Databook((_data_mon, _data_tue, _data_wed, _data_thu, _data_fri, _data_sat, _data_sun))

        with open(device.device_model + "_daily_sch.xls", 'wb') as f:
            f.write(schedule.xls)
        response = HttpResponse(schedule.xls, content_type='application/vnd.ms-excel;charset=utf-8')
        response['Content-Disposition'] = "attachment; filename=" +device.device_model + "_daily_sch.xls"
        return response

    elif device.device_model_id.device_model_id == '2DB' or \
                    device.device_model_id.device_model_id == '2SDB' or \
                    device.device_model_id.device_model_id == '2WSL':

        _file_name = os.path.join(settings_tornado.PROJECT_DIR, 'resources/scheduler_data/lighting/' + device.device_id
                                  + '_schedule.json')
        if os.path.isfile(_file_name):
                json_file = open(_file_name, 'r+')
                _json_data = json.load(json_file)
                if device.device_id in _json_data['lighting']:
                    print 'device id present'
                    _data = _json_data['lighting'][device.device_id]['schedulers']['everyday']
                    _data = json.dumps(_data)
                    _data = json.loads(_data, object_hook=_decode_dict)
                json_file.close()

        headers = ('Period Name', 'From', 'Status (ON/OFF)', 'Brightness (%)')
        _data_mon = _data_tue = _data_wed = _data_thu = _data_fri = _data_sat = _data_sun = []

        for day in _data:
            data = []
            data = tablib.Dataset(*data, headers=headers,  title=day)
            day_data = _data[day]
            for record in day_data:
                rec_time = str(int(record['at'])/60) + ':' + str(int(record['at']) % 60)
                data.append((record['nickname'], rec_time, record['status'], record['brightness']))

            if day == 'monday':
                _data_mon = data
            elif day == 'tuesday':
                _data_tue = data
            elif day == 'wednesday':
                _data_wed = data
            elif day == 'thursday':
                _data_thu = data
            elif day == 'friday':
                _data_fri = data
            elif day == 'saturday':
                _data_sat = data
            elif day == 'sunday':
                _data_sun = data

        schedule = tablib.Databook((_data_mon, _data_tue, _data_wed, _data_thu, _data_fri, _data_sat, _data_sun))

        with open(device.device_model + "_daily_sch.xls", 'wb') as f:
            f.write(schedule.xls)
        response = HttpResponse(schedule.xls, content_type='application/vnd.ms-excel;charset=utf-8')
        response['Content-Disposition'] = "attachment; filename=" +device.device_model + "_daily_sch.xls"
        return response

    elif device.device_model_id.device_model_id == '2HUE':

        _file_name = os.path.join(settings_tornado.PROJECT_DIR, 'resources/scheduler_data/lighting/' + device.device_id
                                  + '_schedule.json')
        if os.path.isfile(_file_name):
                json_file = open(_file_name, 'r+')
                _json_data = json.load(json_file)
                if device.device_id in _json_data['lighting']:
                    print 'device id present'
                    _data = _json_data['lighting'][device.device_id]['schedulers']['everyday']
                    _data = json.dumps(_data)
                    _data = json.loads(_data, object_hook=_decode_dict)
                json_file.close()

        headers = ('Period Name', 'From', 'Status (ON/OFF)', 'Brightness (%)', 'Color')
        _data_mon = _data_tue = _data_wed = _data_thu = _data_fri = _data_sat = _data_sun = []

        for day in _data:
            data = []
            data = tablib.Dataset(*data, headers=headers,  title=day)
            day_data = _data[day]
            for record in day_data:
                rec_time = str(int(record['at'])/60) + ':' + str(int(record['at']) % 60)
                data.append((record['nickname'], rec_time, record['status'], record['brightness'], record['color']))

            if day == 'monday':
                _data_mon = data
            elif day == 'tuesday':
                _data_tue = data
            elif day == 'wednesday':
                _data_wed = data
            elif day == 'thursday':
                _data_thu = data
            elif day == 'friday':
                _data_fri = data
            elif day == 'saturday':
                _data_sat = data
            elif day == 'sunday':
                _data_sun = data

        schedule = tablib.Databook((_data_mon, _data_tue, _data_wed, _data_thu, _data_fri, _data_sat, _data_sun))

        with open(device.device_model + "_daily_sch.xls", 'wb') as f:
            f.write(schedule.xls)
        response = HttpResponse(schedule.xls, content_type='application/vnd.ms-excel;charset=utf-8')
        response['Content-Disposition'] = "attachment; filename=" +device.device_model + "_daily_sch.xls"
        return response


@login_required(login_url='/login/')
def export_schedule_lighting_holiday(request, mac):
    mac = mac.encode('ascii', 'ignore')
    device = DeviceMetadata.objects.get(mac_address=mac)

    if device.device_model_id.device_model_id == '2WL':

        _file_name = os.path.join(settings_tornado.PROJECT_DIR, 'resources/scheduler_data/lighting/' + device.device_id
                                  + '_schedule.json')
        if os.path.isfile(_file_name):
                json_file = open(_file_name, 'r+')
                _json_data = json.load(json_file)
                if device.device_id in _json_data['lighting']:
                    print 'device id present'
                    _data = _json_data['lighting'][device.device_id]['schedulers']['holiday']['holiday']
                    _data = json.dumps(_data)
                    _data = json.loads(_data, object_hook=_decode_dict)
                json_file.close()

        headers = ('Period Name', 'From', 'Status')
        _data_mon = _data_tue = _data_wed = _data_thu = _data_fri = _data_sat = _data_sun = []
        data = []
        data = tablib.Dataset(*data, headers=headers,  title='Holiday')
        for record in _data:
            rec_time = str(int(record['at'])/60) + ':' + str(int(record['at']) % 60)
            data.append((record['nickname'], rec_time, record['status']))

        response = HttpResponse(data.xls, content_type='application/vnd.ms-excel;charset=utf-8')
        response['Content-Disposition'] = "attachment; filename=" + device.device_model + "_holiday_sch.xls"
        return response

    elif device.device_model_id.device_model_id == '2DB' or \
                    device.device_model_id.device_model_id == '2SDB' or \
                    device.device_model_id.device_model_id == '2WSL':

        _file_name = os.path.join(settings_tornado.PROJECT_DIR, 'resources/scheduler_data/lighting/' + device.device_id
                                  + '_schedule.json')
        if os.path.isfile(_file_name):
                json_file = open(_file_name, 'r+')
                _json_data = json.load(json_file)
                if device.device_id in _json_data['lighting']:
                    print 'device id present'
                    _data = _json_data['lighting'][device.device_id]['schedulers']['holiday']['holiday']
                    _data = json.dumps(_data)
                    _data = json.loads(_data, object_hook=_decode_dict)
                json_file.close()

        headers = ('Period Name', 'From', 'Status (ON/OFF)', 'Brightness (%)')
        data = []
        data = tablib.Dataset(*data, headers=headers,  title='Holiday')
        for record in _data:
            rec_time = str(int(record['at'])/60) + ':' + str(int(record['at']) % 60)
            data.append((record['nickname'], rec_time, record['status'], record['brightness']))

        response = HttpResponse(data.xls, content_type='application/vnd.ms-excel;charset=utf-8')
        response['Content-Disposition'] = "attachment; filename=" + device.device_model + "_holiday_sch.xls"
        return response

    elif device.device_model_id.device_model_id == '2HUE':

        _file_name = os.path.join(settings_tornado.PROJECT_DIR, 'resources/scheduler_data/lighting/' + device.device_id
                                  + '_schedule.json')
        if os.path.isfile(_file_name):
                json_file = open(_file_name, 'r+')
                _json_data = json.load(json_file)
                if device.device_id in _json_data['lighting']:
                    print 'device id present'
                    _data = _json_data['lighting'][device.device_id]['schedulers']['holiday']['holiday']
                    _data = json.dumps(_data)
                    _data = json.loads(_data, object_hook=_decode_dict)
                json_file.close()

        headers = ('Period Name', 'From', 'Status (ON/OFF)', 'Brightness (%)', 'Color')
        data = []
        data = tablib.Dataset(*data, headers=headers,  title='Holiday')
        for record in _data:
            rec_time = str(int(record['at'])/60) + ':' + str(int(record['at']) % 60)
            data.append((record['nickname'], rec_time, record['status'], record['brightness'], record['color']))

        response = HttpResponse(data.xls, content_type='application/vnd.ms-excel;charset=utf-8')
        response['Content-Disposition'] = "attachment; filename=" + device.device_model + "_holiday_sch.xls"
        return response

@login_required(login_url='/login/')
def export_schedule_plugload_daily(request, mac):
    mac = mac.encode('ascii', 'ignore')
    device = DeviceMetadata.objects.get(mac_address=mac)

    _file_name = os.path.join(settings_tornado.PROJECT_DIR, 'resources/scheduler_data/plugload/' + device.device_id
                              + '_schedule.json')
    if os.path.isfile(_file_name):
            json_file = open(_file_name, 'r+')
            _json_data = json.load(json_file)
            if device.device_id in _json_data['plugload']:
                print 'device id present'
                _data = _json_data['plugload'][device.device_id]['schedulers']['everyday']
                _data = json.dumps(_data)
                _data = json.loads(_data, object_hook=_decode_dict)
            json_file.close()

    headers = ('Period Name', 'From', 'Status')
    _data_mon = _data_tue = _data_wed = _data_thu = _data_fri = _data_sat = _data_sun = []

    for day in _data:
        data = []
        data = tablib.Dataset(*data, headers=headers,  title=day)
        day_data = _data[day]
        for record in day_data:
            rec_time = str(int(record['at'])/60) + ':' + str(int(record['at']) % 60)
            data.append((record['nickname'], rec_time, record['status']))

        if day == 'monday':
            _data_mon = data
        elif day == 'tuesday':
            _data_tue = data
        elif day == 'wednesday':
            _data_wed = data
        elif day == 'thursday':
            _data_thu = data
        elif day == 'friday':
            _data_fri = data
        elif day == 'saturday':
            _data_sat = data
        elif day == 'sunday':
            _data_sun = data

    schedule = tablib.Databook((_data_mon, _data_tue, _data_wed, _data_thu, _data_fri, _data_sat, _data_sun))

    with open(device.device_model + "_daily_sch.xls", 'wb') as f:
        f.write(schedule.xls)
    response = HttpResponse(schedule.xls, content_type='application/vnd.ms-excel;charset=utf-8')
    response['Content-Disposition'] = "attachment; filename=" +device.device_model + "_daily_sch.xls"
    return response


@login_required(login_url='/login/')
def export_schedule_plugload_holiday(request, mac):
    mac = mac.encode('ascii', 'ignore')
    device = DeviceMetadata.objects.get(mac_address=mac)

    _file_name = os.path.join(settings_tornado.PROJECT_DIR, 'resources/scheduler_data/plugload/' + device.device_id
                              + '_schedule.json')
    if os.path.isfile(_file_name):
            json_file = open(_file_name, 'r+')
            _json_data = json.load(json_file)
            if device.device_id in _json_data['plugload']:
                print 'device id present'
                _data = _json_data['plugload'][device.device_id]['schedulers']['holiday']['holiday']
                _data = json.dumps(_data)
                _data = json.loads(_data, object_hook=_decode_dict)
            json_file.close()

    headers = ('Period Name', 'From', 'Status')
    _data_mon = _data_tue = _data_wed = _data_thu = _data_fri = _data_sat = _data_sun = []
    data = []
    data = tablib.Dataset(*data, headers=headers,  title='Holiday')
    for record in _data:
        rec_time = str(int(record['at'])/60) + ':' + str(int(record['at']) % 60)
        data.append((record['nickname'], rec_time, record['status']))

    response = HttpResponse(data.xls, content_type='application/vnd.ms-excel;charset=utf-8')
    response['Content-Disposition'] = "attachment; filename=" + device.device_model + "_holiday_sch.xls"
    return response


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

