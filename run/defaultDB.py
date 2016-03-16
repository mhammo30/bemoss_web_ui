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

__author__ = 'kruthika'
import os
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)).replace('/run', ''))
from django.core.management import setup_environ
import settings_tornado

setup_environ(settings_tornado)

from apps.alerts.models import Priority, NotificationChannel, EventTrigger, DeviceType, SeenNotifications, TempFailureTime
from apps.dashboard.models import DeviceModel, Building_Zone
from django.contrib.auth.models import Group, User
from apps.dashboard.models import GlobalSetting
from apps.schedule.models import Holiday
from apps.discovery.models import Miscellaneous
import datetime

DEVICE_TYPE_CHOICES = (
    ('1TH', 'thermostat'),
    ('1VAV', 'VAV'),
    ('1RTU', 'RTU'),
    ('2HUE', 'philips hue'),
    ('2WL', 'wemo light switch'),
    ('2WSL', 'wattstopper lighting'),
    ('3WSP', 'wemo smart plug'),
    ('3WIS', 'wemo insight switch'),
    ('3WP', 'wattstopper plugload'))

thermostat = DeviceModel(device_model_id='1TH', device_model_name='Thermostat')
thermostat.save()

VAV = DeviceModel(device_model_id='1VAV', device_model_name='VAV')
VAV.save()

RTU = DeviceModel(device_model_id='1RTU', device_model_name='RTU')
RTU.save()

hue = DeviceModel(device_model_id='2HUE', device_model_name='Philips Hue')
hue.save()

wemo_light_switch = DeviceModel(device_model_id='2WL', device_model_name='Wemo Light Switch')
wemo_light_switch.save()

wattstopper_lighting = DeviceModel(device_model_id='2WSL', device_model_name='Wattstopper Lighting Product')
wattstopper_lighting.save()

wemo_smart_plug = DeviceModel(device_model_id='3WSP', device_model_name='Wemo Smart Plug')
wemo_smart_plug.save()

wemo_smart_plug = DeviceModel(device_model_id='3WIS', device_model_name='Wemo Insight Switch')
wemo_smart_plug.save()

wattstopper_plugload = DeviceModel(device_model_id='3WP', device_model_name='Wattstopper Plugload')
wattstopper_plugload.save()

print "device_model table updated with device model information."

zone_999 = Building_Zone(zone_id=999, zone_nickname="BEMOSS Core")
zone_999.save()


#Adding global settings

gz999 = GlobalSetting(id=999,heat_setpoint=70, cool_setpoint=72, illuminance=67, zone_id=999)
gz999.save()


#User groups

zonemgr = Group(id=2, name="Zone Manager")
zonemgr.save()

tenant = Group(id=3, name="Tenant")
tenant.save()

#admin = Group(id=4, name="Admin")
#admin.save()

#Add admin to user profile
admin = User.objects.get(username='admin')
admin.first_name = "Admin"
admin.save()
adminprof = admin.get_profile()
adminprof.group = Group.objects.get(name='Admin')
adminprof.save()

#Holidays

newyear = Holiday(holiday_id=1, date=datetime.datetime(2014,01,01),description="New Year")
newyear.save()

mlk = Holiday(holiday_id=2, date=datetime.datetime(2014,01,20),description="MLK Holiday")
mlk.save()

#Alerts and Notifications

#Priority
low_p = Priority(id=1, priority_level='Low', priority_notification_hours='12', priority_counter='2')
low_p.save()

med_p = Priority(id=2, priority_level='Warning', priority_notification_hours='4', priority_counter='720')
med_p.save()

high_p = Priority(id=3, priority_level='Critical', priority_notification_hours='1', priority_counter='180')
high_p.save()

#NotificationChannel
emailN = NotificationChannel(id=1, notification_channel='Email')
emailN.save()

textN = NotificationChannel(id=2, notification_channel='Text')
textN.save()

#Device Type
dt1 = DeviceType(id=1, device_type='Thermostat')
dt1.save()

dt2 = DeviceType(id=2, device_type='Plugload')
dt2.save()

dt3 = DeviceType(id=3, device_type='Lighting')
dt3.save()

dt4 = DeviceType(id=4, device_type='Custom')
dt4.save()

dt5 = DeviceType(id=5, device_type='Platform')
dt5.save()

#Event Trigger
et1 = EventTrigger(id=1, device_type_id=1, event_trigger_desc="Unauthorized Changes To Thermostat Mode/SetPoint", event_trigger_id="Unauthorized", event_trigger_class="desc_prio")
et1.save()

et2 = EventTrigger(id=2, device_type_id=1, event_trigger_desc="AC System Failure", event_trigger_id="ACFailure", event_trigger_class="desc_prio_thresh")
et2.save()

et3 = EventTrigger(id=3, device_type_id=5, event_trigger_desc="Any BEMOSS Node Offline", event_trigger_id="BEMOSSOffline", event_trigger_class="desc_prio")
et3.save()

et4 = EventTrigger(id=4, device_type_id=5, event_trigger_desc="Any BEMOSS Device Offline", event_trigger_id="BEMOSSDeviceOffline", event_trigger_class="desc_prio")
et4.save()

# Initialize the seen notifications table
sn1 = SeenNotifications(id=1, counter='0')
sn1.save()

# Initialize the TempFailureTime table
tft1 = TempFailureTime(id=1, hours='2', counter='360')
tft1.save()
tft2 = TempFailureTime(id=2, hours='4', counter='720')
tft2.save()
tft3 = TempFailureTime(id=3, hours='6', counter='1080')
tft3.save()


#Miscellaneous table update with auto_discovery
auto_disc = Miscellaneous(key='auto_discovery', value='ON')
auto_disc.save()



