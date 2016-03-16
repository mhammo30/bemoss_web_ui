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


#Database models for alerts and notifications
from django.db import models
from django.contrib.auth.models import User


class DeviceType(models.Model):
    device_type = models.CharField(max_length=30) #system, thermostat, plugload, lighting

    class Meta:
        db_table = "device_type"

    def __unicode__(self):
        return str(self.as_json())

    def as_json(self):
        return dict(
            id=self.id,
            alarm_type=self.device_type.encode('utf-8').title())


class TempRangeValue(models.Model):
    temp_range = models.CharField(max_length=50)  # system, thermostat, plugload, lighting

    class Meta:
        db_table = "temp_alert_range"

    def __unicode__(self):
        return str(self.as_json())

    def as_json(self):
        return dict(
            id=self.id,
            temp_range_=self.temp_range.encode('utf-8'))

class TempFailureTime(models.Model):
    hours = models.CharField(max_length=50)
    counter = models.CharField(max_length=50)  # system, thermostat, plugload, lighting

    class Meta:
        db_table = "temp_failure_time"

    def __unicode__(self):
        return str(self.as_json())

    def as_json(self):
        return dict(
            id=self.id,
            temp_failure_time=self.hours.encode('utf-8') if self.hours else '',
            temp_failure_count=self.counter.encode('utf-8') if self.counter else '')

class EventTrigger(models.Model):
    device_type = models.ForeignKey(DeviceType)  # system, thermostat, plugload, lighting
    event_trigger_desc = models.CharField(max_length=50)  # temperature exceeds, humidity exceeds, low battery etc.
    event_trigger_id = models.CharField(max_length=50)
    event_trigger_class = models.CharField(max_length=50)

    class Meta:
        db_table = "event_trigger"

    def __unicode__(self):
        return str(self.id)

    def as_json(self):
        device_type = DeviceType.as_json(self.device_type)
        return dict(
            id=self.id,
            alarm_type=device_type['alarm_type'].encode('utf-8') if device_type['alarm_type'] else '',
            alarm_desc=self.event_trigger_desc.encode('utf-8') if self.event_trigger_desc else '',
            alarm_desc_id=self.event_trigger_id.encode('utf-8') if self.event_trigger_id else '',
            alarm_desc_class=self.event_trigger_class.encode('utf-8') if self.event_trigger_class else '')

class TempTimeCounter(models.Model):
    alert_id = models.CharField(max_length=50)  # temperature exceeds, humidity exceeds, low battery etc.
    device_id = models.CharField(max_length=50)
    temp_time_count = models.CharField(max_length=50)
    priority_counter = models.CharField(max_length=50)
    no_notifications_sent = models.CharField(max_length=50)

    class Meta:
        db_table = "temp_time_counter"

    def __unicode__(self):
        return str(self.id)

class TempFailureTime(models.Model):
    hours = models.CharField(max_length=50)  # temperature exceeds, humidity exceeds, low battery etc.
    counter = models.CharField(max_length=50)

    class Meta:
        db_table = "temp_failure_time"


class SeenNotifications(models.Model):
    counter = models.CharField(max_length=50)  # temperature exceeds, humidity exceeds, low battery etc.

    class Meta:
        db_table = "seen_notifications_counter"

    def __unicode__(self):
        return str(self.counter)

    def as_json(self):
        return dict(
            id=self.id,
            alarm_desc=self.counter.encode('utf-8') if self.counter else '')


class NotificationChannel(models.Model):
    notification_channel = models.CharField(max_length=50)

    class Meta:
        db_table = "notification_channel"

    def __str__(self):
        return self.notification_channel

    def __unicode__(self):
        return str(self.notification_channel)

    def as_json(self):
        return dict(
            id=self.id,
            notification_channel=self.notification_channel.encode('utf-8') if self.notification_channel else '')


class Priority(models.Model):
    priority_level = models.CharField(max_length=10)
    priority_notification_hours = models.CharField(max_length=50)
    priority_counter = models.CharField(max_length=50)

    class Meta:
        db_table = "priority"

    def __unicode__(self):
        return str(self.as_json())

    def as_json(self):
        return dict(
            id=self.id,
            priority=self.priority_level.encode('utf-8').title() if self.priority_level else '')


class ActiveAlert(models.Model):
    device_type = models.ForeignKey(DeviceType)
    event_trigger = models.ForeignKey(EventTrigger)
    trigger_parameter = models.CharField(max_length=40)
    comparator = models.CharField(max_length=20)
    threshold = models.CharField(max_length=5)
    notification_channel = models.ManyToManyField(NotificationChannel, through="NotificationChannelAddress")
    priority = models.ForeignKey(Priority)
    user = models.ForeignKey(User)
    created_on = models.DateTimeField()
    temp_range_threshold = models.CharField(max_length=50)
    temp_time_threshold = models.CharField(max_length=50)

    class Meta:
        db_table = "active_alert"

    def __unicode__(self):
        return str(self.id)

    def as_json(self):
        alarm_type = DeviceType.as_json(self.device_type)
        alarm = EventTrigger.as_json(self.event_trigger)
        notification = self.notification_channel.all()
        # notification = NotificationType.as_json(self.notification_type)
        notify_address = [ob.as_json() for ob in NotificationChannelAddress.objects.filter(active_alert_id=self.id)]
        # print notify_address
        user = User.objects.get(id=1)
        priority = Priority.as_json(self.priority)

        return dict(
            id=self.id,
            alarm=alarm,
            alarm_type=alarm_type,
            trigger_parameter=self.trigger_parameter.encode('utf-8').title() if self.trigger_parameter else '',
            comparator=self.comparator,
            value=self.threshold,
            notification=notification,
            notify_address=notify_address,
            priority=priority,
            created_on=self.created_on,
            created_by=user,
            temp_range_threshold=self.temp_range_threshold,
            temp_time_threshold=self.temp_time_threshold)


class NotificationChannelAddress(models.Model):
    notification_channel = models.ForeignKey(NotificationChannel)
    active_alert = models.ForeignKey(ActiveAlert)
    notify_address = models.CharField(max_length=50)

    def __unicode__(self):
        return str(self.notify_address)

    def as_json(self):
        return dict(
            channel=self.notification_channel.notification_channel,
            address=self.notify_address
        )


class Notification(models.Model):
    active_alert = models.ForeignKey(ActiveAlert)
    alert_notification_status = models.BooleanField()  # TRUE OR FALSE - if notification was sent successfully then TRUE else FALSE
    dt_triggered = models.DateTimeField()

    class Meta:
        db_table = "notification"

    def __unicode__(self):
        return str(self.as_json())

    def as_json(self):
        ra = ActiveAlert.as_json(self.active_alert)

        return dict(
            id=self.id,
            reg_alert=ra,
            alert_status=self.alert_notification_status,
            active_dt=self.dt_triggered)