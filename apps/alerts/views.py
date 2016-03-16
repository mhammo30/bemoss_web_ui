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


#All classes for alerts and notifications page handling
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from _utils.page_load_utils import get_device_list_side_navigation
from apps.alerts.models import ActiveAlert, EventTrigger, Priority, NotificationChannel, Notification, \
    NotificationChannelAddress, DeviceType, TempRangeValue, TempFailureTime, SeenNotifications
from apps.accounts.models import UserFullName

import json
from datetime import datetime, timedelta
from apps.discovery.models import BEMOSSNotification


@login_required(login_url='/login/')
def alerts(request):
    print 'inside alerts view method'
    context = RequestContext(request)

    device_list_side_nav = get_device_list_side_navigation()
    context.update(device_list_side_nav)

    if request.user.get_profile().group.name.lower() == 'admin':

        usr = UserFullName.objects.filter(username=request.user)[0]
        _registered_alerts = [ob.as_json() for ob in ActiveAlert.objects.all()]
        _alerts = [ob.as_json() for ob in EventTrigger.objects.all()]
        _alert_pr = [ob.as_json() for ob in Priority.objects.all()]
        _n_type = [ob.as_json() for ob in NotificationChannel.objects.all()]
        active_al = get_notifications()
        bemoss_not = general_notifications()
        _temp_range = [ob.as_json() for ob in TempRangeValue.objects.all()]
        _temp_failure_time = [ob.as_json() for ob in TempFailureTime.objects.all()]
        context.update({'b_al': bemoss_not})
        return render_to_response(
            'admin/alarms.html',
            {'registered_alerts': _registered_alerts, 'alerts': _alerts, 'priority': _alert_pr, 'n_type': _n_type,
             'user_full_name': usr, 'temp_range': _temp_range,
             'temp_failure_time': _temp_failure_time,
             'active_al': active_al},
            context)
    else:
        return HttpResponseRedirect('/home/')


@login_required(login_url='/login/')
def no_of_seen_notifications_push(request):
    response_data = {}
    bemoss_not = general_notifications()
    post = SeenNotifications(id=1, counter=len(bemoss_not))
    post.save()
    print "succssful"
    response_data['result'] = 'succssful'
    return HttpResponse(
        json.dumps(response_data), mimetype="application/json")


@login_required(login_url='/login/')
def create_alert(request):
    # return HttpResponse('1234654654')
    # print 'inside create alert method'
    # if request.POST:

    _data = request.raw_post_data
    _data = json.loads(_data)
    print _data

    _alert = EventTrigger.objects.get(event_trigger_id=_data['alert'])
    print "hi"
    print _alert

    _priority = Priority.objects.get(priority_level=_data['priority'])

    _device_type = DeviceType.objects.get(id=_alert.device_type_id)

    asdad = temp_range_threshold = _data['temp_range_thresh'];
    print asdad

    ra = ActiveAlert(event_trigger=_alert, device_type=_device_type, trigger_parameter=_data['custom_alert'],
                     comparator=_data['custom_alert_comparator'], threshold=_data['value'],
                     priority_id=_priority.id, user_id=1, created_on=datetime.now(),
                     temp_range_threshold=_data['temp_range_thresh'], temp_time_threshold=_data['temp_time_thresh'], )
    ra.save()

    # print alerts
    for ntype in _data['n_type']:
        n_id = NotificationChannel.objects.get(notification_channel=ntype)
        if ntype == "Email":
            emails = _data['email']
            for every_email in emails:
                if every_email != "":
                    NotificationChannelAddress.objects.create(notification_channel=n_id, active_alert=ra,
                                                              notify_address=every_email.strip())
        if ntype == "Text":
            phone_numbers = _data['phone']
            for every_ph_number in phone_numbers:
                if every_ph_number != "":
                    NotificationChannelAddress.objects.create(notification_channel=n_id, active_alert=ra,
                                                              notify_address=every_ph_number.strip())

        if ntype == "BemossNotification":
            NotificationChannelAddress.objects.create(notification_channel=n_id, active_alert=ra,
                                                      notify_address="Bemoss")


    if request.is_ajax():
        return HttpResponse(json.dumps(_data), mimetype='application/json')

@login_required(login_url='/login/')
def delete_alert(request):
    print "Inside delete alert method"
    if request.POST:
        _data = request.raw_post_data

        ActiveAlert.objects.filter(id=int(_data)).delete()

    if request.is_ajax():
        return HttpResponse(json.dumps)


def get_notifications():
    print "Fetching active notifications from the database"
    active_alerts = [ob.as_json() for ob in Notification.objects.all().order_by('-dt_triggered')[:1000]]
    three_months_ago = datetime.now() - timedelta(days=60)
    return active_alerts


def general_notifications():
    three_months_ago = datetime.now() - timedelta(days=60)
    bemoss_discovery_alerts = [ob.as_json() for ob in BEMOSSNotification.objects.filter(
        date_triggered__range=(three_months_ago, datetime.now())).order_by('-date_triggered')]
    return bemoss_discovery_alerts


def notifications(request):
    print "Notifications page load"
    context = RequestContext(request)

    device_list_side_nav = get_device_list_side_navigation()
    context.update(device_list_side_nav)

    active_al = get_notifications()

    context.update({"active_al": active_al})
    bemoss_not = general_notifications()
    context.update({'b_al': bemoss_not})

    if request.user.get_profile().group.name.lower() == 'admin':
        usr = UserFullName.objects.filter(username=request.user)[0]
        _registered_alerts = [ob.as_json() for ob in ActiveAlert.objects.all()]
        _alerts = [ob.as_json() for ob in EventTrigger.objects.all()]
        _alert_pr = [ob.as_json() for ob in Priority.objects.all()]
        _n_type = [ob.as_json() for ob in NotificationChannel.objects.all()]
        active_al = get_notifications()
        # print context
        return render_to_response(
            'admin/notifications.html',
            {'registered_alerts': _registered_alerts, 'alerts': _alerts, 'priority': _alert_pr, 'n_type': _n_type,
             'user_full_name': usr,
             'active_al': active_al},
            context)
    else:
        return HttpResponseRedirect('/home/')