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
from apps.dashboard.models import Building_Zone

from django.db import models
from agents.ZMQHelper.zmq_pub import ZMQ_PUB as zmqPub
import _utils.defaults as __


kwargs = {'subscribe_address': __.SUB_SOCKET,
                    'publish_address': __.PUSH_SOCKET}

zmq_pub = zmqPub(**kwargs)


class SupportedDevices(models.Model):
    device_model = models.CharField(primary_key=True, max_length=30)
    vendor_name = models.CharField(max_length=50)
    communication = models.CharField(max_length=10)
    device_type = models.CharField(max_length=20)
    discovery_type = models.CharField(max_length=20)
    device_model_id = models.CharField(max_length=5)
    api_name = models.CharField(max_length=50)
    identifiable = models.BooleanField()
    is_cloud_device = models.BooleanField(default=False)
    schedule_weekday_period = models.IntegerField(blank=True)
    schedule_weekend_period = models.IntegerField(blank=True)
    allow_schedule_period_delete = models.BooleanField(blank=True)

    class Meta:
        db_table = "supported_devices"

    def __unicode__(self):
        return self.device_model

    def as_json(self):
        return dict(
            device_model_id=self.device_model_id,
            vendor_name=self.vendor_name,
            is_cloud_device=self.is_cloud_device
        )

    def get_cloud_devices(self):
        return self.device_model

    def get_schedule_info(self):
        return dict(
            weekday_period=self.schedule_weekday_period,
            weekend_period=self.schedule_weekend_period,
            allow_delete=self.allow_schedule_period_delete
        )


class Miscellaneous(models.Model):
    key = models.CharField(max_length=50)
    value = models.CharField(max_length=50)

    class Meta:
        db_table = "miscellaneous"

    def __unicode__(self):
        return self.id

    def as_json(self):
        return dict(
            key=self.key,
            value=self.value
        )


class BEMOSSNotification(models.Model):
    message = models.CharField(max_length=1000)
    date_triggered = models.DateTimeField()
    not_type = models.CharField(max_length=100, null=True, blank=True)
    priority = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = "bemoss_notify"

    def __unicode__(self):
        return self.id

    def as_json(self):
        return dict(
            message=self.message,
            date_triggered=self.date_triggered,
            not_type=self.not_type,
            priority=self.priority
        )

