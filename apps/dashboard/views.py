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


from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response
import json
import ast
import re
import time
import os
from _utils.page_load_utils import get_device_list_side_navigation, get_device_list_dashboard
from apps.alerts.views import get_notifications, general_notifications
from agents.ZMQHelper.zmq_pub import ZMQ_PUB
from _utils import config_helper
from .models import DeviceMetadata, Building_Zone, GlobalSetting
from apps.thermostat.models import Thermostat
from apps.smartplug.models import Plugload
from apps.lighting.models import Lighting
from apps.VAV.models import VAV
from apps.RTU.models import RTU
from apps.admin.models import NetworkStatus


import _utils.defaults as __

kwargs = {'subscribe_address': __.SUB_SOCKET,
                    'publish_address': __.PUSH_SOCKET}

zmq_pub = ZMQ_PUB(**kwargs)

APPROVED = 'APR'
NON_BEMOSS_DEVICE = 'NBD'
PENDING = 'PND'

APPROVAL_STATUS_CHOICES = {
    (APPROVED, 'Approved'),
    (PENDING, 'Pending'),
    (NON_BEMOSS_DEVICE, 'Non-BEMOSS Device')
}

@login_required(login_url='/login/')
def add_new_zone(request):
    if request.POST:
        _data = request.raw_post_data
        zone_id = ""
        a = re.compile("^[A-Za-z0-9_]{6,15}$")
        if (a.match(_data)):
            p = Building_Zone.objects.get_or_create(zone_nickname=str(_data))
            zone_id = Building_Zone.objects.get(zone_nickname=str(_data)).zone_id
            global_settings = GlobalSetting(id=zone_id, heat_setpoint=70, cool_setpoint=72, illuminance=67, zone_id=zone_id)
            global_settings.save()
            message = "success"
            if request.is_ajax():
                return HttpResponse(str(zone_id), mimetype='text/plain')
        else:
            message = "invalid"
            if request.is_ajax():
                return HttpResponse("invalid", mimetype='text/plain')
    

@login_required(login_url='/login/')
def save_changes_modal(request):
    if request.POST:
        _data = request.raw_post_data
        a = re.compile("^[A-Za-z0-9_]{6,15}$")
        _data = ast.literal_eval(_data)
        if a.match(_data['nickname']):
            device_id = _data['id']
            nickname = _data['nickname']
            device_type_id = _data['device_type']
            if device_type_id == '1TH' :
                device = Thermostat.objects.get(thermostat_id=device_id)
                device.nickname = nickname
                device.save()
            elif device_type_id == '1VAV':
                device = VAV.objects.get(vav_id=device_id)
                device.nickname = nickname
                device.save()
            elif device_type_id == '1RTU':
                device = RTU.objects.get(rtu_id=device_id)
                device.nickname = nickname
                device.save()
            elif device_type_id =='2HUE' or device_type_id =='2WL' or device_type_id == '2WSL':
                device = Lighting.objects.get(lighting_id=device_id)
                device.nickname = nickname
                device.save()
            elif device_type_id == '3WSP' or device_type_id == '3WP' or device_type_id == '3WIS':
                device = Plugload.objects.get(plugload_id=device_id)
                device.nickname = nickname
                device.save()


            message = {'status':'success',
                       'device_id':device_id,
                       'nickname':nickname}
            if request.is_ajax():
                return HttpResponse(json.dumps(message), mimetype='application/json')
        else:
            message = "invalid"
            if request.is_ajax():
                return HttpResponse(json.dumps(message), mimetype='application/json')


@login_required(login_url='/login/')
def save_zone_nickname_changes(request):
    context = RequestContext(request)
    if request.POST:
        _data = request.raw_post_data
        a = re.compile("^[A-Za-z0-9_]{6,15}$")
        _data = ast.literal_eval(_data)
        if a.match(_data['nickname']):
            zone_id = _data['id']
            nickname = _data['nickname']
            zone = Building_Zone.objects.get(zone_id=zone_id)
            zone.zone_nickname = nickname  # change field
            zone.save()
            message = {'status':'success',
                       'zone_id':zone_id,
                       'nickname':nickname}
            if request.is_ajax():
                return HttpResponse(json.dumps(message),mimetype='application/json')
        else:
            message = "invalid"
            if request.is_ajax():
                return HttpResponse(json.dumps(message),mimetype='application/json')


@login_required(login_url='/login/')
def identify_device(request):
    if request.POST:
        _data = request.raw_post_data
        _data = json.loads(_data)
        device_info = [ob.data_as_json() for ob in DeviceMetadata.objects.filter(device_id=_data['id'])]
        device_id = device_info[0]['device_id']
        if 'zone_id' in _data:
            device_zone = _data['zone_id']
        device_model = device_info[0]['device_model_id']
        device_type_id = device_model.device_model_id
        device_type = ''
        device_zone = ''
        if device_type_id == '1TH' or device_type_id == '1NST' or device_type_id == '1HWT':
            device_zone = Thermostat.objects.get(thermostat_id=device_id).zone_id
            device_type = 'thermostat'
        elif device_type_id == '1RTU':
            device_zone = RTU.objects.get(rtu_id=device_id).zone_id
            device_type = 'rtu'
        elif device_type_id == '1VAV':
            device_zone = VAV.objects.get(vav_id=device_id).zone_id
            device_type = 'vav'
        elif device_type_id =='2HUE' or device_type_id =='2WL' or device_type_id == '2WSL':
            device_zone = Lighting.objects.get(lighting_id=device_id).zone_id
            device_type = 'lighting'
        elif device_type_id == '3WSP' or device_type_id == '3WP' or device_type_id == '3WIS':
            device_zone = Plugload.objects.get(plugload_id=device_id).zone_id
            device_type = 'plugload'


        info_required = "Identify device"
        ieb_topic = '/ui/agent/' + device_type + '/identify' + '/bemoss/' + str(device_zone) + '/' + device_id
        zmq_pub.requestAgent(ieb_topic, info_required, "text/plain", "UI")

    if request.is_ajax():
        return HttpResponse(json.dumps("success"), mimetype='application/json')


@login_required(login_url='/login/')
def identify_status(request):
    if request.POST:
        _data = request.raw_post_data
        device_info = [ob.data_as_json() for ob in DeviceMetadata.objects.filter(device_id=_data)]
        device_type_id = device_info[0]['device_model_id']
        device_type_id = device_type_id.device_model_id
        if device_type_id == '1TH' or device_type_id == '1NST' or device_type_id == '1HWT':
            device_type = 'thermostat'
        elif device_type_id == '1RTU':
            device_type = 'rtu'
        elif device_type_id == '1VAV':
            device_type = 'vav'
        elif device_type_id =='2HUE' or device_type_id =='2WL' or device_type_id == '2WSL':
            device_type = 'lighting'
        elif device_type_id == '3WSP'  or device_type_id == '3WP' or device_type_id == '3WIS':
            device_type = 'plugload'

        json_result = {'status': 'success'}

    if request.is_ajax():
        return HttpResponse(json.dumps(json_result), mimetype='application/json')


def recursive_get_device_update(update_variable):
    wifi_3m50_device_initial_update = config_helper.get_device_update_message(update_variable)
    vals = ""
    if wifi_3m50_device_initial_update != '{update_number}/{status}':
        vals = wifi_3m50_device_initial_update
        return vals
    else:
        time.sleep(5)
        recursive_get_device_update(update_variable)


@login_required(login_url='/login/')
def discover_all(request):
    if request.POST:
        #_data = request.body
        discover_all_topic = '/ui/discoveryagent/discover/all'
        zmq_pub.requestAgent(discover_all_topic, '{"auth_token": "bemoss"}', "text/plain", "UI")
        json_result = {'status': 'success'}

        if request.is_ajax():
            return HttpResponse(json.dumps(json_result), mimetype='application/json')



@login_required(login_url='/login/')
def discover_hvac(request):
    if request.POST:
        #_data = request.body
        discover_hvac_topic = '/ui/discoveryagent/discover/hvac/all'
        zmq_pub.requestAgent(discover_hvac_topic, '{"auth_token": "bemoss"}', "text/plain", "UI")
        json_result = {'status': 'success'}

        if request.is_ajax():
            return HttpResponse(json.dumps(json_result), mimetype='application/json')


@login_required(login_url='/login/')
def discover_lighting(request):
    if request.POST:
        #_data = request.body
        discover_lighting_topic = '/ui/discoveryagent/discover/lighting/all'
        zmq_pub.requestAgent(discover_lighting_topic, '{"auth_token": "bemoss"}', "text/plain", "UI")
        json_result = {'status': 'success'}

        if request.is_ajax():
            return HttpResponse(json.dumps(json_result), mimetype='application/json')


@login_required(login_url='/login/')
def discover_plugload(request):
    if request.POST:
        #_data = request.body
        discover_plugload_topic = '/ui/discoveryagent/discover/plugload/all'
        zmq_pub.requestAgent(discover_plugload_topic, '{"auth_token": "bemoss"}', "text/plain", "UI")
        json_result = {'status': 'success'}

        if request.is_ajax():
            return HttpResponse(json.dumps(json_result), mimetype='application/json')



@login_required(login_url='/login/')
def discover_nodes(request):
    context = RequestContext(request)

    if request.user.get_profile().group.name.lower() == 'admin':
        device_list_side_nav = get_device_list_side_navigation()
        bemoss_lite = [ob.data_dashboard() for ob in NetworkStatus.objects.filter(node_status='ONLINE')]
        active_al = get_notifications()
        context.update({'active_al':active_al})
        bemoss_not = general_notifications()
        context.update({'b_al': bemoss_not})
        context.update(device_list_side_nav)

        return render_to_response(
            'dashboard/node_discovery.html',
            {'lites': bemoss_lite}, context)
    else:
        return HttpResponseRedirect('/home/')


#Version 2.2
#Change: Includes the new field 'approval_status' for manual approval process
@login_required(login_url='/login/')
def discover(request):
    print "Discovering devices"
    context = RequestContext(request)

    username = request.user

    device_list_side_nav = get_device_list_side_navigation()
    print device_list_side_nav

    # Check Philips Hue Username Exists or not:
    # Set default value as no:
    hue_username_exists = 'no'
    DIR = os.path.dirname(__file__)
    DIR = DIR.replace('/bemoss_web_ui/apps/dashboard', '/bemoss_os/')

    LAUNCHFILES_DIR = os.path.join(DIR, 'Agents/LaunchFiles/')

    for idx in os.listdir(LAUNCHFILES_DIR):
        if '2HUE' in idx and '.json~' not in idx:
            _launch_file = os.path.join(LAUNCHFILES_DIR, idx)
            f = open(_launch_file, 'r')
            data = json.load(f)
            if 'username' in data.keys():
                hue_username_exists = 'yes'


    if request.user.get_profile().group.name.lower() == 'admin':
        # Get data for display on discovery dashboard
        data_dashboard = get_device_list_dashboard()
        #Update side navigation context
        context.update(device_list_side_nav)
        #Get alerts and notifications list
        active_al = get_notifications()
        context.update({'active_al':active_al})
        bemoss_not = general_notifications()
        context.update({'b_al': bemoss_not})
        context.update({'username_exists': hue_username_exists})
        return render_to_response(
            'dashboard/discovery.html', data_dashboard, context)
    else:
        return HttpResponseRedirect('/home/')


@login_required(login_url='/login/')
def change_zones_thermostats(request):
    #print "Inside change zones for hvac controllers"
    if request.POST:
        _data = request.body
        _data = json.loads(_data)

        for thermostat in _data['thermostats']:
            if thermostat[1] != "Assign a New Zone":
                zone = Building_Zone.objects.get(zone_nickname__iexact=thermostat[1])
                th_instance = Thermostat.objects.get(thermostat_id=thermostat[0])
                updated_approval_status = thermostat[3]
                for status_key, status_val in APPROVAL_STATUS_CHOICES:
                    if updated_approval_status == status_val:
                        updated_approval_status = status_key
                        break

                zone_update_send_topic = '/ui/networkagent/' + str(thermostat[0]) + '/' + str(th_instance.zone_id) + '/' + str(zone.zone_id) + '/change'+'/'+updated_approval_status
                zmq_pub.requestAgent(zone_update_send_topic, '{"auth_token": "bemoss"}', "text/plain", "UI")

                old_zone_id = th_instance.zone_id
                th_instance.zone = zone  # change field
                th_instance.nickname = thermostat[2]

                # Update device approval status
                d_info = DeviceMetadata.objects.get(device_id=thermostat[0])
                current_approval_status = d_info.approval_status
                print current_approval_status
                if updated_approval_status != current_approval_status:
                    d_info.approval_status = updated_approval_status
                    d_info.save()
                th_instance.save()
        for vav in _data['vav']:
            if vav[1] != "Assign a New Zone":
                zone = Building_Zone.objects.get(zone_nickname__iexact=vav[1])
                vav_instance = VAV.objects.get(vav_id=vav[0])

                updated_approval_status = vav[3]
                for status_key, status_val in APPROVAL_STATUS_CHOICES:
                    if updated_approval_status == status_val:
                        updated_approval_status = status_key
                        break

                # if zone.zone_id != vav_instance.zone_id:
                zone_update_send_topic = '/ui/networkagent/' + str(vav[0]) + '/' + str(vav_instance.zone_id) + '/' + str(zone.zone_id) + '/change'+'/'+updated_approval_status
                zmq_pub.requestAgent(zone_update_send_topic, '{"auth_token": "bemoss"}', "text/plain", "UI")
                old_zone_id = vav_instance.zone_id
                vav_instance.zone = zone  # change field
                vav_instance.nickname = vav[2]
                d_info = DeviceMetadata.objects.get(device_id=vav[0])
                current_approval_status = d_info.approval_status
                print current_approval_status

                if updated_approval_status != current_approval_status:
                    d_info.approval_status = updated_approval_status
                    d_info.save()
                vav_instance.save()

        for rtu in _data['rtu']:
            if rtu[1] != "Assign a New Zone":
                zone = Building_Zone.objects.get(zone_nickname__iexact=rtu[1])
                rtu_instance = RTU.objects.get(rtu_id=rtu[0])
                updated_approval_status = rtu[3]
                for status_key, status_val in APPROVAL_STATUS_CHOICES:
                    if updated_approval_status == status_val:
                        updated_approval_status = status_key
                        break

                #if zone.zone_id != rtu_instance.zone_id:
                zone_update_send_topic = '/ui/networkagent/' + str(rtu[0]) + '/' + str(rtu_instance.zone_id) + '/' + str(zone.zone_id) + '/change'+'/'+updated_approval_status
                zmq_pub.requestAgent(zone_update_send_topic, '{"auth_token": "bemoss"}', "text/plain", "UI")
                old_zone_id = rtu_instance.zone_id
                rtu_instance.zone = zone  # change field
                rtu_instance.nickname = rtu[2]
                d_info = DeviceMetadata.objects.get(device_id=rtu[0])
                current_approval_status = d_info.approval_status
                print current_approval_status


                if updated_approval_status != current_approval_status:
                    d_info.approval_status = updated_approval_status
                    d_info.save()
                rtu_instance.save()
    if request.is_ajax():
        return HttpResponse(json.dumps("success"), mimetype='application/json')


@login_required(login_url='/login/')
def change_zones_plugloads(request):
    #print "Inside change zones for plugloads"
    if request.POST:
        _data = request.body
        _data = json.loads(_data)

        for plugload in _data['data']:
            if plugload[1] != "Assign a New Zone":
                zone = Building_Zone.objects.get(zone_nickname__iexact=plugload[1])
                pl_instance = Plugload.objects.get(plugload_id=plugload[0])
                updated_approval_status = plugload[3]
                for status_key, status_val in APPROVAL_STATUS_CHOICES:
                    if updated_approval_status == status_val:
                        updated_approval_status = status_key
                        break

                #if zone.zone_id != pl_instance.zone_id:
                zone_update_send_topic = '/ui/networkagent/' + str(plugload[0]) + '/' + str(pl_instance.zone_id) + '/' + str(zone.zone_id) + '/change'+'/'+updated_approval_status
                zmq_pub.requestAgent(zone_update_send_topic, '{"auth_token": "bemoss"}', "text/plain", "UI")
                old_zone_id = pl_instance.zone_id
                pl_instance.zone = zone  # change field
                pl_instance.nickname = plugload[2]
                d_info = DeviceMetadata.objects.get(device_id=plugload[0])
                current_approval_status = d_info.approval_status
                print current_approval_status

                if updated_approval_status != current_approval_status:
                    d_info.approval_status = updated_approval_status
                    d_info.save()
                pl_instance.save()

    if request.is_ajax():
        return HttpResponse(json.dumps("success"), mimetype='application/json')


@login_required(login_url='/login/')
def change_zones_lighting_loads(request):
    #print "Inside change zones for lighting loads"
    if request.POST:
        _data = request.body
        _data = json.loads(_data)
        #print _data

        for lt_load in _data['data']:
            if lt_load[1] != "Assign a New Zone":
                zone = Building_Zone.objects.get(zone_nickname__iexact=lt_load[1])
                lt_instance = Lighting.objects.get(lighting_id=lt_load[0])
                updated_approval_status = lt_load[3]
                for status_key, status_val in APPROVAL_STATUS_CHOICES:
                    if updated_approval_status == status_val:
                        updated_approval_status = status_key
                        break

                # if zone.zone_id != lt_instance.zone_id:
                zone_update_send_topic = '/ui/networkagent/' + str(lt_load[0]) + '/' + str(lt_instance.zone_id) + '/' + str(zone.zone_id) + '/change'+'/'+updated_approval_status
                zmq_pub.requestAgent(zone_update_send_topic, '{"auth_token": "bemoss"}', "text/plain", "UI")
                old_zone_id = lt_instance.zone_id
                lt_instance.zone = zone  # change field
                lt_instance.nickname = lt_load[2]
                d_info = DeviceMetadata.objects.get(device_id=lt_load[0])
                current_approval_status = d_info.approval_status
                print current_approval_status


                if updated_approval_status != current_approval_status:
                    d_info.approval_status = updated_approval_status
                    d_info.save()
                lt_instance.save()

    if request.is_ajax():
        return HttpResponse(json.dumps("success"), mimetype='application/json')


@login_required(login_url='/login/')
def change_zones_lite(request):
    #print "Inside change zones for bemoss lite"
    if request.POST:
        _data = request.body
        _data = json.loads(_data)

        for lite in _data['data']:
            if lite[1] != "Associate with Zone":
                zone = Building_Zone.objects.get(zone_nickname__iexact=lite[1])
                lite_instance = NetworkStatus.objects.get(node_id=lite[0])
                lite_instance.associated_zone = zone  # change field
                lite_instance.save()

    if request.is_ajax():
        return HttpResponse(json.dumps("success"), mimetype='application/json')


@login_required(login_url='/login/')
def bemoss_home(request):
    context = RequestContext(request)
    username = request.user

    device_list_side_nav = get_device_list_side_navigation()

    device_count ={
                    "devices": {
                    }
                    }

    all_zones = Building_Zone.objects.all()
    for zone in all_zones:
        th_count = Thermostat.objects.filter(network_status='ONLINE', zone_id=zone.zone_id,
                                             thermostat_id__approval_status='APR').count()
        vav_count = VAV.objects.filter(network_status='ONLINE', zone_id=zone.zone_id,
                                       vav_id__approval_status='APR').count()
        rtu_count = RTU.objects.filter(network_status='ONLINE', zone_id=zone.zone_id,
                                       rtu_id__approval_status='APR').count()
        t_count = th_count + vav_count + rtu_count

        pl_count = Plugload.objects.filter(network_status='ONLINE', zone_id=zone.zone_id,
                                           plugload_id__approval_status='APR').count()
        lt_count = Lighting.objects.filter(network_status='ONLINE', zone_id=zone.zone_id,
                                           lighting_id__approval_status='APR').count()


        device_count['devices'][zone.zone_id] = {'th': 0, 'pl': 0, 'lt': 0, }
        device_count['devices'][zone.zone_id]['th'] = t_count
        device_count['devices'][zone.zone_id]['pl'] = pl_count
        device_count['devices'][zone.zone_id]['lt'] = lt_count


    zones_p = [ob.data_dashboard() for ob in Building_Zone.objects.all().order_by('zone_nickname')]

    for zone in zones_p:
        z_id = zone['id']
        zone['t_count'] = device_count['devices'][z_id]['th']
        zone['pl_count'] = device_count['devices'][z_id]['pl']
        zone['lt_count'] = device_count['devices'][z_id]['lt']

    active_al = get_notifications()
    context.update({'active_al':active_al})
    bemoss_not = general_notifications()
    context.update({'b_al': bemoss_not})
    context.update(device_list_side_nav)

    return render_to_response(
        'dashboard/dashboard.html',
        {'zones_p': zones_p}, context)


@login_required(login_url='/login/')
def change_global_settings(request):
    if request.POST:
        _data = request.body
        _data = json.loads(_data)

        zone_id = _data['zone_id']
        zone = Building_Zone.objects.get(zone_id=zone_id)
        gsettings = GlobalSetting.objects.get(zone_id=zone)
        gsettings.heat_setpoint = _data['heat_setpoint']
        gsettings.cool_setpoint = _data['cool_setpoint']
        gsettings.illuminance = _data['illumination']
        gsettings.save()

        if request.is_ajax():
            return HttpResponse(json.dumps("success"), mimetype='application/json')


@login_required(login_url='/login/')
def zone_device_listing(request, zone_dev):
    context = RequestContext(request)
    username = request.user

    zone_dev = zone_dev.encode('ascii', 'ignore')
    zone_info = zone_dev.split("_")
    zone_id = zone_info[0]
    device_type = zone_info[1]

    #Side navigation bar
    device_list_side_nav = get_device_list_side_navigation()

    context.update(device_list_side_nav)

    #For the page
    if device_type == 'th':
        thermostats = [ob.data_as_json() for ob in
                       Thermostat.objects.filter(zone_id=zone_id, thermostat_id__approval_status='APR',
                                                  network_status='ONLINE')]
        if len(thermostats) != 0:
            zone_nickname = thermostats[0]['zone']['zone_nickname']

        rtu = [ob.as_json() for ob in RTU.objects.filter(zone_id=zone_id, rtu_id__approval_status='APR',
                                                          network_status='ONLINE')]
        if len(rtu) != 0:
            zone_nickname = rtu[0]['zone']['zone_nickname']

        vav = [ob.as_json() for ob in VAV.objects.filter(zone_id=zone_id, vav_id__approval_status='APR',
                                                          network_status='ONLINE')]
        if len(vav) != 0:
            zone_nickname = vav[0]['zone']['zone_nickname']
        active_al = get_notifications()
        context.update({'active_al':active_al})
        bemoss_not = general_notifications()
        context.update({'b_al': bemoss_not})
        context.update(device_list_side_nav)
        return render_to_response(
            'dashboard/thermostats.html',
            {'thermostats': thermostats, 'rtu': rtu, 'vav': vav, 'zone_id': zone_id, 'zone_nickname': zone_nickname,
             }, context)

    elif device_type == 'lt':
        lighting = [ob.data_as_json() for ob in
                    Lighting.objects.filter(zone_id=zone_id, lighting_id__approval_status='APR',
                                             network_status='ONLINE')]
        zone_nickname = lighting[0]['zone']['zone_nickname']

        return render_to_response(
            'dashboard/lighting_loads.html',
            {'lighting_loads': lighting, 'zone_id': zone_id, 'zone_nickname': zone_nickname}, context)

    elif device_type == 'pl':
        plugloads = [ob.data_as_json() for ob in
                     Plugload.objects.filter(zone_id=zone_id, plugload_id__approval_status='APR',
                                              network_status='ONLINE')]
        zone_nickname = plugloads[0]['zone']['zone_nickname']
        context.update(device_list_side_nav)
        return render_to_response(
            'dashboard/plugloads.html',
            {'plugloads': plugloads, 'zone_id': zone_id, 'zone_nickname': zone_nickname}, context)



@login_required(login_url='/login/')
def zone_device_all_listing(request, zone_dev):
    context = RequestContext(request)
    username = request.user

    zone_id = zone_dev.encode('ascii', 'ignore')

    #Side navigation bar
    active_al = get_notifications()
    context.update({'active_al':active_al})
    bemoss_not = general_notifications()
    context.update({'b_al': bemoss_not})
    device_list_side_nav = get_device_list_side_navigation()
    context.update(device_list_side_nav)

    #For the page

    thermostats = [ob.data_as_json() for ob in
                   Thermostat.objects.filter(zone_id=zone_id, thermostat_id__approval_status='APR')]
    if len(thermostats) != 0:
        zone_nickname = thermostats[0]['zone']['zone_nickname']

    rtu = [ob.as_json() for ob in RTU.objects.filter(zone_id=zone_id, rtu_id__approval_status='APR')]
    if len(rtu) != 0:
        zone_nickname = rtu[0]['zone']['zone_nickname']

    vav = [ob.as_json() for ob in VAV.objects.filter(zone_id=zone_id, vav_id__approval_status='APR',
                                                      network_status='ONLINE')]
    if len(vav) != 0:
        zone_nickname = vav[0]['zone']['zone_nickname']

    lighting = [ob.data_as_json() for ob in Lighting.objects.filter(zone_id=zone_id, lighting_id__approval_status='APR',
                                                                     network_status='ONLINE')]
    if len(lighting) != 0:
        zone_nickname = lighting[0]['zone']['zone_nickname']

    plugloads = [ob.data_as_json() for ob in
                 Plugload.objects.filter( network_status='ONLINE',zone_id=zone_id, plugload_id__approval_status='APR')]
    if len(plugloads) != 0:
        zone_nickname = plugloads[0]['zone']['zone_nickname']



    return render_to_response(
        'dashboard/zone_devices_all.html',
        {'thermostats': thermostats, 'vav': vav, 'rtu': rtu, 'lighting_loads': lighting,
         'plugloads': plugloads, 'zone_id': zone_id, 'zone_nickname': zone_nickname,
         }, context)


#@login_required(login_url='/login/')
def change_approval_status(device_id, app_status_updated):
    d_info = DeviceMetadata.objects.get(device_id=device_id)
    current_approval_status = d_info.approval_status
    print current_approval_status

    updated_approval_status = app_status_updated

    for status_key, status_val in APPROVAL_STATUS_CHOICES:
        if updated_approval_status == status_val:
            updated_approval_status = status_key
            break

    if updated_approval_status != current_approval_status:
        d_info.approval_status = updated_approval_status
        d_info.save()
    return True


@login_required(login_url='/login/')
def modify_thermostats(request):
    print "Inside modify hvac controllers"
    if request.POST:
        _data = request.body
        _data = json.loads(_data)

        for thermostat in _data['thermostats']:
            zone = Building_Zone.objects.get(zone_nickname__iexact=thermostat[2])
            th_instance = Thermostat.objects.get(thermostat_id=thermostat[0])

            updated_approval_status = thermostat[3]

            for status_key, status_val in APPROVAL_STATUS_CHOICES:
                if updated_approval_status == status_val:
                    updated_approval_status = status_key
                    break

            #if zone.zone_id != th_instance.zone_id:
            zone_update_send_topic = '/ui/networkagent/' + str(thermostat[0]) + '/' + str(th_instance.zone_id) + '/' + str(zone.zone_id) + '/change'+'/'+updated_approval_status
            zmq_pub.requestAgent(zone_update_send_topic, '{"auth_token": "bemoss"}', "text/plain", "UI")
            th_instance.zone = zone  # change field
            th_instance.nickname = thermostat[1]
            th_instance.save()
            change_approval_status(thermostat[0], thermostat[3])

        for vav in _data['vav']:
            zone = Building_Zone.objects.get(zone_nickname__iexact=vav[2])
            vav_instance = VAV.objects.get(vav_id=vav[0])

            updated_approval_status = vav[3]
            for status_key, status_val in APPROVAL_STATUS_CHOICES:
                if updated_approval_status == status_val:
                    updated_approval_status = status_key
                    break

            zone_update_send_topic = '/ui/networkagent/' + str(vav[0]) + '/' + str(vav_instance.zone_id) + '/' + str(zone.zone_id) + '/change'+'/'+updated_approval_status
            zmq_pub.requestAgent(zone_update_send_topic, '{"auth_token": "bemoss"}', "text/plain", "UI")
            vav_instance.zone = zone  # change field
            vav_instance.nickname = vav[1]
            vav_instance.save()
            change_approval_status(vav[0], vav[3])

        for rtu in _data['rtu']:
            zone = Building_Zone.objects.get(zone_nickname__iexact=rtu[2])
            rtu_instance = RTU.objects.get(rtu_id=rtu[0])

            updated_approval_status = rtu[3]
            for status_key, status_val in APPROVAL_STATUS_CHOICES:
                if updated_approval_status == status_val:
                    updated_approval_status = status_key
                    break

            zone_update_send_topic = '/ui/networkagent/' + str(rtu[0]) + '/' + str(rtu_instance.zone_id) + '/' + str(zone.zone_id) + '/change/' + updated_approval_status
            zmq_pub.requestAgent(zone_update_send_topic, '{"auth_token": "bemoss"}', "text/plain", "UI")
            rtu_instance.zone = zone  # change field
            rtu_instance.nickname = rtu[1]
            rtu_instance.save()
            change_approval_status(rtu[0], rtu[3])

    if request.is_ajax():
        return HttpResponse(json.dumps("success"), mimetype='application/json')


@login_required(login_url='/login/')
def modify_plugloads(request):
    #print "Inside modify plugloads"
    if request.POST:
        _data = request.body
        _data = json.loads(_data)

        for plugload in _data:
            zone = Building_Zone.objects.get(zone_nickname__iexact=plugload[2])
            pl_instance = Plugload.objects.get(plugload_id=plugload[0])

            updated_approval_status = plugload[3]
            for status_key, status_val in APPROVAL_STATUS_CHOICES:
                if updated_approval_status == status_val:
                    updated_approval_status = status_key
                    break

            zone_update_send_topic = '/ui/networkagent/' + str(plugload[0]) + '/' + str(pl_instance.zone_id) + '/' + str(zone.zone_id) + '/change/'+updated_approval_status
            zmq_pub.requestAgent(zone_update_send_topic, '{"auth_token": "bemoss"}', "text/plain", "UI")
            pl_instance.zone = zone  # change field
            pl_instance.nickname = plugload[1]
            pl_instance.save()
            change_approval_status(plugload[0], plugload[3])

    if request.is_ajax():
        return HttpResponse(json.dumps("success"), mimetype='application/json')


@login_required(login_url='/login/')
def modify_lighting_loads(request):
    #print "Inside modify lighting loads"
    if request.POST:
        _data = request.body
        _data = json.loads(_data)

        for lt_load in _data:
            zone = Building_Zone.objects.get(zone_nickname__iexact=lt_load[2])
            lt_instance = Lighting.objects.get(lighting_id=lt_load[0])

            updated_approval_status = lt_load[3]
            for status_key, status_val in APPROVAL_STATUS_CHOICES:
                if updated_approval_status == status_val:
                    updated_approval_status = status_key
                    break

            zone_update_send_topic = '/ui/networkagent/' + str(lt_load[0]) + '/' + str(lt_instance.zone_id) + '/' + str(zone.zone_id) + '/change/'+updated_approval_status
            zmq_pub.requestAgent(zone_update_send_topic, '{"auth_token": "bemoss"}', "text/plain", "UI")
            lt_instance.zone = zone  # change field
            lt_instance.nickname = lt_load[1]
            lt_instance.save()
            change_approval_status(lt_load[0], lt_load[3])

    if request.is_ajax():
        return HttpResponse(json.dumps("success"), mimetype='application/json')



@login_required(login_url='/login/')
def modify_nbd_thermostats(request):
    print "Inside modify nbd hvac controllers"
    if request.POST:
        _data = request.body
        _data = json.loads(_data)

        # 0 -> device_id
        # 1 -> nickname
        # 2 -> approval status

        for thermostat in _data['thermostats']:
            th_instance = Thermostat.objects.get(thermostat_id=thermostat[0])

            updated_approval_status = thermostat[2]
            for status_key, status_val in APPROVAL_STATUS_CHOICES:
                if updated_approval_status == status_val:
                    updated_approval_status = status_key
                    break

            zone_update_send_topic = '/ui/networkagent/' + str(thermostat[0]) + '/' + str(th_instance.zone_id) + '/' + str(th_instance.zone_id) + '/change/'+updated_approval_status
            zmq_pub.requestAgent(zone_update_send_topic, '{"auth_token": "bemoss"}', "text/plain", "UI")

            th_instance.nickname = thermostat[1]
            th_instance.save()
            change_approval_status(thermostat[0], thermostat[2])

        for vav in _data['vav']:
            vav_instance = VAV.objects.get(vav_id=vav[0])

            updated_approval_status = vav[2]
            for status_key, status_val in APPROVAL_STATUS_CHOICES:
                if updated_approval_status == status_val:
                    updated_approval_status = status_key
                    break
            zone_update_send_topic = '/ui/networkagent/' + str(vav[0]) + '/' + str(vav_instance.zone_id) + '/' + str(vav_instance.zone_id) + '/change/'+updated_approval_status
            zmq_pub.requestAgent(zone_update_send_topic, '{"auth_token": "bemoss"}', "text/plain", "UI")


            vav_instance.nickname = vav[1]
            vav_instance.save()
            change_approval_status(vav[0], vav[2])

        for rtu in _data['rtu']:
            rtu_instance = RTU.objects.get(rtu_id=rtu[0])

            updated_approval_status = rtu[2]
            for status_key, status_val in APPROVAL_STATUS_CHOICES:
                if updated_approval_status == status_val:
                    updated_approval_status = status_key
                    break
            zone_update_send_topic = '/ui/networkagent/' + str(rtu[0]) + '/' + str(rtu_instance.zone_id) + '/' + str(rtu_instance.zone_id) + '/change/'+updated_approval_status
            zmq_pub.requestAgent(zone_update_send_topic, '{"auth_token": "bemoss"}', "text/plain", "UI")

            rtu_instance.nickname = rtu[1]
            rtu_instance.save()
            change_approval_status(rtu[0], rtu[2])

    if request.is_ajax():
        return HttpResponse(json.dumps("success"), mimetype='application/json')


@login_required(login_url='/login/')
def modify_nbd_plugloads(request):
    #print "Inside modify nbd plugloads"
    if request.POST:
        _data = request.body
        _data = json.loads(_data)

        for plugload in _data:
            pl_instance = Plugload.objects.get(plugload_id=plugload[0])

            updated_approval_status = plugload[2]
            for status_key, status_val in APPROVAL_STATUS_CHOICES:
                if updated_approval_status == status_val:
                    updated_approval_status = status_key
                    break
            zone_update_send_topic = '/ui/networkagent/' + str(plugload[0]) + '/' + str(pl_instance.zone_id) + '/' + str(pl_instance.zone_id) + '/change/'+updated_approval_status
            zmq_pub.requestAgent(zone_update_send_topic, '{"auth_token": "bemoss"}', "text/plain", "UI")

            pl_instance.nickname = plugload[1]
            pl_instance.save()
            change_approval_status(plugload[0], plugload[2])

    if request.is_ajax():
        return HttpResponse(json.dumps("success"), mimetype='application/json')

@login_required(login_url='/login/')
def modify_nbd_lighting_loads(request):
    #print "Inside modify lighting loads"
    if request.POST:
        _data = request.body
        _data = json.loads(_data)

        for lt_load in _data:
            lt_instance = Lighting.objects.get(lighting_id=lt_load[0])

            updated_approval_status = lt_load[2]
            for status_key, status_val in APPROVAL_STATUS_CHOICES:
                if updated_approval_status == status_val:
                    updated_approval_status = status_key
                    break
            zone_update_send_topic = '/ui/networkagent/' + str(lt_load[0]) + '/' + str(lt_instance.zone_id) + '/' + str(lt_instance.zone_id) + '/change/'+updated_approval_status
            zmq_pub.requestAgent(zone_update_send_topic, '{"auth_token": "bemoss"}', "text/plain", "UI")

            lt_instance.nickname = lt_load[1]
            lt_instance.save()
            change_approval_status(lt_load[0], lt_load[2])

    if request.is_ajax():
        return HttpResponse(json.dumps("success"), mimetype='application/json')
