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


from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from datetime import datetime
from django.shortcuts import render_to_response
from _utils.page_load_utils import get_device_list_side_navigation
from apps.alerts.views import get_notifications, general_notifications
from apps.dashboard.models import DeviceMetadata
from apps.smartplug.models import Plugload
from agents.ZMQHelper.zmq_pub import ZMQ_PUB
from _utils import page_load_utils as _helper
import json

from _utils import defaults as __


kwargs = {'subscribe_address': __.SUB_SOCKET,
                    'publish_address': __.PUSH_SOCKET}

zmq_pub = ZMQ_PUB(**kwargs)

@login_required(login_url='/login/')
def smartplug(request, mac):
    print 'inside plugload view method'
    context = RequestContext(request)
    username = request.session.get('user')
    print username
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

    print type(mac)
    mac = mac.encode('ascii', 'ignore')
    print type(mac)

    device_metadata = [ob.device_control_page_info() for ob in DeviceMetadata.objects.filter(mac_address=mac)]
    print device_metadata
    device_id = device_metadata[0]['device_id']
    device_type_id = device_metadata[0]['device_model_id']
    device_type_id = device_type_id.device_model_id

    device_status = [ob.data_as_json() for ob in Plugload.objects.filter(plugload_id=device_id)]
    device_zone = device_status[0]['zone']['id']
    device_nickname = device_status[0]['nickname']
    zone_nickname = device_status[0]['zone']['zone_nickname']

    _data = _helper.get_page_load_data(device_id, 'plugload', device_type_id)

    device_list_side_nav = get_device_list_side_navigation()
    context.update(device_list_side_nav)
    active_al = get_notifications()
    context.update({'active_al':active_al})
    bemoss_not = general_notifications()
    context.update({'b_al': bemoss_not})

    return render_to_response(
        'plugload/plugload.html',
        {'device_data': _data, 'device_id': device_id, 'device_zone': device_zone, 'zone_nickname': zone_nickname,
         'mac_address': mac, 'device_nickname': device_nickname, 'device_type_id': device_type_id},
        context)


@login_required(login_url='/login/')
def submit_changes(request):
    print 'inside plug load update device method'
    if request.POST:
        _data = request.body
        print _data
        _data = json.loads(_data)
        print _data

        device_info = _data['device_info']
        #_data = {"status": _data['status']}
        _data.pop('device_info')
        print _data
        print device_info
        content_type = "application/json"
        fromUI = "UI"
        print "created instance of the zmqpub class"

        device_info = device_info.split('/')  # e.g. 999/lighting/1NST18b43017e76a
        # TODO fix building name -> should be changeable from 'bemoss'
        plugload_update_send_topic = '/ui/agent/'+device_info[1]+'/update/bemoss/'+device_info[0]+'/'+device_info[2]
        print plugload_update_send_topic
        zmq_pub.sendToAgent(plugload_update_send_topic, _data, content_type, fromUI)
        print "success in sending message to agent"

    if request.is_ajax():
            return HttpResponse(json.dumps(_data), mimetype='application/json')

def get_plugload_current_status(request):
    print "getting current status of plug load"
    if request.method == 'POST':
        data_recv = request.body
        data_recv = json.loads(data_recv)
        device_info = data_recv['device_info']
        # same as the thermostat load method
        print "created instance of the zmqpub class"

        info_required = "Update Hue data"

        device_info = device_info.split('/')  # e.g. 999/lighting/1NST18b43017e76a
        # TODO fix building name -> should be changeable from 'bemoss'
        plugload_update_send_topic = '/ui/agent/'+device_info[1]+'/device_status/bemoss/'+device_info[0]+'/'+device_info[2]
        print plugload_update_send_topic

        zmq_pub.requestAgent(plugload_update_send_topic, info_required, "text/plain", "UI")
        jsonresult = {'status': 'sent'}
        if request.is_ajax():
            return HttpResponse(json.dumps(jsonresult), mimetype='application/json')
