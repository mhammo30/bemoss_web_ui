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
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from _utils.page_load_utils import get_device_list_side_navigation
from apps.alerts.views import get_notifications, general_notifications
from apps.discovery.models import SupportedDevices, Miscellaneous
import json
from agents.ZMQHelper.zmq_pub import ZMQ_PUB
import _utils.defaults as __
import ast


kwargs = {'subscribe_address': __.SUB_SOCKET,
          'publish_address': __.PUSH_SOCKET}

zmq_pub = ZMQ_PUB(**kwargs)


@login_required(login_url='/login')
def discover_devices(request):
    if request.user.get_profile().group.name.lower() == 'admin':
        context = RequestContext(request)
        discovery_status = Miscellaneous.objects.get(key='auto_discovery')
        print discovery_status.value
        hvac = SupportedDevices.objects.filter(device_type__in=["thermostat", "vav", "rtu"])
        lt_loads = SupportedDevices.objects.filter(device_type="lighting")
        plugloads = SupportedDevices.objects.filter(device_type="plugload")

        print lt_loads
        print hvac
        print plugloads

        device_list_side_nav = get_device_list_side_navigation()
        context.update(device_list_side_nav)
        active_al = get_notifications()
        context.update({'active_al': active_al})
        bemoss_not = general_notifications()
        context.update({'b_al': bemoss_not})

        return render_to_response('dashboard/manual_discovery.html', {'hvac': hvac, 'lt_loads': lt_loads,
                                                                      'plugloads': plugloads,
                                                                      'discovery_status': discovery_status}, context
                                  )
    else:
        return HttpResponseRedirect('/home/')


def discover_new_devices(request):
    if request.POST:
        _data = request.raw_post_data
        _data = json.loads(_data)
        _data = [x.encode('utf-8') for x in _data]
        print _data
        message = {'devices': _data}
        print message
        print type(message)

        topic = '/ui/agent/misc/bemoss/discovery_request'

        zmq_pub.sendToAgent(topic, _data, "text/plain", "UI")
        if request.is_ajax():
            return HttpResponse(json.dumps("success"), mimetype='application/json')

def authenticate_hue_device(request):
    if request.POST:
        _data = request.raw_post_data
        _data = ast.literal_eval(_data)
        print _data
        device_id = _data['id']
        message = {'DeviceId': device_id}
        print message
        print type(message)

        topic = '/ui/agent/misc/bemoss/approvalhelper_get_hue_username'

        zmq_pub.sendToAgent(topic, message, "text/plain", "UI")
        if request.is_ajax():
            return HttpResponse(json.dumps("success"), mimetype='application/json')
