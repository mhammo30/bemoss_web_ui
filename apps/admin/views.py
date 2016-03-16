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
import os
from django.forms.models import modelformset_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from datetime import datetime
from django.db import IntegrityError
from _utils.page_load_utils import get_device_list_side_navigation
from apps.admin.forms import PasswordManagerForm
from apps.alerts.views import get_notifications, general_notifications
import settings_tornado
from apps.thermostat.models import Thermostat
from apps.lighting.models import Lighting
from apps.smartplug.models import Plugload
from apps.schedule.models import Holiday
from apps.VAV.models import VAV
from apps.RTU.models import RTU
from .models import NetworkStatus, PasswordsManager
from agents.ZMQHelper.zmq_pub import ZMQ_PUB
import _utils.defaults as __
from _utils.encrypt import encrypt_value

kwargs = {'subscribe_address': __.SUB_SOCKET,
                    'publish_address': __.PUSH_SOCKET}

zmq_pub = ZMQ_PUB(**kwargs)


@login_required(login_url='/login/')
def device_status(request):
    print 'Device status page load'
    context = RequestContext(request)
    if request.session.get('last_visit'):
    # The session has a value for the last visit
        last_visit_time = request.session.get('last_visit')
        visits = request.session.get('visits', 0)

        if (datetime.now() - datetime.strptime(last_visit_time[:-7], "%Y-%m-%d %H:%M:%S")).days > 0:
            request.session['visits'] = visits + 1
    else:
        # The get returns None, and the session does not have a value for the last visit.
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = 1

    if request.user.get_profile().group.name.lower() == 'admin':
        thermostats = [ob.device_status() for ob in Thermostat.objects.filter(thermostat_id__approval_status='APR')]
        print thermostats
        vavs = [ob.device_status() for ob in VAV.objects.filter(vav_id__approval_status='APR')]
        rtus = [ob.device_status() for ob in RTU.objects.filter(rtu_id__approval_status='APR')]
        plugloads = [ob.device_status() for ob in Plugload.objects.filter(plugload_id__approval_status='APR')]
        print plugloads
        lighting = [ob.device_status() for ob in Lighting.objects.filter(lighting_id__approval_status='APR')]

        device_list_side_nav = get_device_list_side_navigation()
        context.update(device_list_side_nav)
        active_al = get_notifications()
        context.update({'active_al':active_al})
        bemoss_not = general_notifications()
        context.update({'b_al': bemoss_not})

        return render_to_response(
            'admin/device_status.html',
            {'thermostats': thermostats, 'vavs': vavs, 'rtus': rtus, 'plugloads': plugloads, 'lighting': lighting},
            context)
    else:
        return HttpResponseRedirect('/home/')


@login_required(login_url='/login/')
def network_status(request):
    print 'Network status page load'
    context = RequestContext(request)
    if request.session.get('last_visit'):
    # The session has a value for the last visit
        last_visit_time = request.session.get('last_visit')

        visits = request.session.get('visits', 0)

        if (datetime.now() - datetime.strptime(last_visit_time[:-7], "%Y-%m-%d %H:%M:%S")).days > 0:
            request.session['visits'] = visits + 1
    else:
        # The get returns None, and the session does not have a value for the last visit.
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = 1

    active_al = get_notifications()
    context.update({'active_al': active_al})
    bemoss_not = general_notifications()
    context.update({'b_al': bemoss_not})
    device_list_side_nav = get_device_list_side_navigation()
    context.update(device_list_side_nav)

    if request.user.get_profile().group.name.lower() == 'admin':
        nw_status = [ob.network_status() for ob in NetworkStatus.objects.all()]

        return render_to_response(
            'admin/network_status.html',
            {'nw_status': nw_status},
            context)
    else:
        return HttpResponseRedirect('/home/')


def bemoss_settings(request):
    print 'BEMOSS Settings page load'
    context = RequestContext(request)
    if request.session.get('last_visit'):
    # The session has a value for the last visit
        last_visit_time = request.session.get('last_visit')

        visits = request.session.get('visits', 0)

        if (datetime.now() - datetime.strptime(last_visit_time[:-7], "%Y-%m-%d %H:%M:%S")).days > 0:
            request.session['visits'] = visits + 1
    else:
        # The get returns None, and the session does not have a value for the last visit.
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = 1

    holidays = [ob.as_json() for ob in Holiday.objects.all()]
    print holidays


    json_file = open(os.path.join(settings_tornado.PROJECT_DIR, 'resources/metadata/bemoss_metadata.json'), "r+")
    _json_data = json.load(json_file)
    b_location = _json_data['building_location_zipcode']
    json_file.close()

    device_list_side_nav = get_device_list_side_navigation()
    context.update(device_list_side_nav)
    active_al = get_notifications()
    context.update({'active_al':active_al})
    bemoss_not = general_notifications()
    context.update({'b_al': bemoss_not})

    if request.user.get_profile().group.name.lower() == 'admin':
        return render_to_response(
            'admin/bemoss_settings.html',
            {'holidays': holidays, 'b_location': b_location},
            context)
    else:
        return HttpResponseRedirect('/home/')


@login_required(login_url='/login/')
def delete_holiday(request):
    if request.POST:
        _data = request.body
        _data = json.loads(_data)

        if _data['id']:
            h_id = int(_data['id'])
            Holiday.objects.filter(holiday_id=h_id).delete()

        info_required = "Holiday removed"
        ieb_topic = '/ui/agent/bemoss/holiday/' + str(h_id) + '/remove'
        zmq_pub.requestAgent(ieb_topic, info_required, "text/plain", "UI")

        json_text = {"status": "success"}

    if request.is_ajax():
        return HttpResponse(json.dumps(json_text), mimetype='application/json')


@login_required(login_url='/login/')
def add_holiday(request):

    if request.POST:
        _data = request.body
        _data = json.loads(_data)
        print _data

        _date = _data['date']
        if _date:
            _date = _date.split("T")
            _date = _date[0]
            _date = _date.split("-")
            year = int(_date[0])
            month = int(_date[1])
            day = int(_date[2])
            h_date = datetime(year, month, day).date()
            print _date
            new_holiday = Holiday(date=h_date, description=_data['desc'])
            new_holiday.save()

        new_h = Holiday.objects.get(date=h_date)

        info_required = "Holiday added"
        ieb_topic = '/ui/agent/bemoss/holiday/' + str(new_h.holiday_id) + '/added'
        zmq_pub.requestAgent(ieb_topic, info_required, "text/plain", "UI")

    json_text = {"status": "success"}

    if request.is_ajax():
        return HttpResponse(json.dumps(json_text), mimetype='application/json')


@login_required(login_url='/login/')
def update_bemoss_location(request):
    if request.POST:
        _data = request.body
        _data = json.loads(_data)

        b_location = _data['b_loc']

        json_file = open(os.path.join(settings_tornado.PROJECT_DIR, 'resources/metadata/bemoss_metadata.json'), "r+")
        _json_data = json.load(json_file)
        _json_data['building_location_zipcode'] = b_location

        json_file.seek(0)
        json_file.write(json.dumps(_json_data, indent=4, sort_keys=True))
        json_file.truncate()
        json_file.close()

    json_text = {"status": "success"}

    if request.is_ajax():
        return HttpResponse(json.dumps(json_text), mimetype='application/json')

