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


from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


# Database models for Dashboard page
class Building_Zone(models.Model):
    zone_id = models.AutoField(primary_key=True)
    zone_nickname = models.CharField(max_length=30)

    class Meta:
        db_table = "building_zone"

    def __unicode__(self):
        return str(self.zone_id)
       
    def as_json(self):
        return dict(
            id=self.zone_id,
            zone_nickname=self.zone_nickname.encode('utf-8').title())

    def data_dashboard_global(self):
        gsetting = GlobalSetting.objects.get(zone=self)
        global_setting = GlobalSetting.as_json(gsetting)
        return dict(
            id=self.zone_id,
            zone_nickname=self.zone_nickname.encode('utf-8').title() if self.zone_nickname else '',
            global_setting=global_setting,
        )

    def data_dashboard(self):
        gsetting = GlobalSetting.objects.get(zone=self)
        global_setting = GlobalSetting.as_json(gsetting)
        return dict(
            id=self.zone_id,
            zone_nickname=self.zone_nickname.encode('utf-8').title() if self.zone_nickname else '',
            global_setting=global_setting,
            t_count=0,
            pl_count=0,
            lt_count=0,
        )


class DeviceModel(models.Model):
    device_model_id = models.CharField(primary_key=True, max_length=5)
    device_model_name = models.CharField(max_length=40)

    class Meta:
        db_table = "device_model"

    def __unicode__(self):
        return self.device_model_id

    def as_json(self):
        return dict(
            device_model_id=self.device_model_id,
            device_model_name=self.device_model_name
        )

#Table to store device metadata for all devices in BEMOSS system
class DeviceMetadata(models.Model):
    APPROVED = 'APR'
    NON_BEMOSS_DEVICE = 'NBD'
    PENDING = 'PND'

    DEVICE_TYPE_CHOICES = (
        ('1TH', 'thermostat'),
        ('2DB', 'dimmable ballast'),
        ('2HUE', 'philips hue'),
        ('2SDB', 'step dim ballast'),
        ('2WL', 'wemo light switch'),
        ('2WSL', 'wattstopper lighting'),
        ('3WSP', 'wemo smart plug'),
        ('3MOD', 'modlet smart plug'),
        ('3WP', 'wattstopper plugload'),
    )

    APPROVAL_STATUS_CHOICES = (
        (APPROVED, 'Approved'),
        (PENDING, 'Pending'),
        (NON_BEMOSS_DEVICE, 'Non-BEMOSS Device')
    )

    device_id = models.CharField(primary_key=True, max_length=50)
    device_type = models.CharField(max_length=20)
    vendor_name = models.CharField(max_length=50)
    device_model = models.CharField(max_length=30)
    #device_model_id = models.CharField(max_length=5, choices=DEVICE_TYPE_CHOICES)
    device_model_id = models.ForeignKey(DeviceModel, db_column="device_model_id")
    mac_address = models.CharField(max_length=50, null=True, blank=True)
    min_range = models.IntegerField(null=True, blank=True)
    max_range = models.IntegerField(null=True, blank=True)
    identifiable = models.BooleanField()
    communication = models.CharField(max_length=10)
    date_added = models.DateTimeField()
    factory_id = models.CharField(max_length=50, null=True, blank=True)
    # bemoss = models.BooleanField()
    approval_status = models.CharField(max_length=3,
                                       choices=APPROVAL_STATUS_CHOICES,
                                       default=PENDING)

    class Meta:
        db_table = "device_info"

    def __unicode__(self):
        return self.device_id

    def data_as_json(self):
        return dict(
            device_id=self.device_id,
            device_type=self.device_type.encode('utf-8') if self.device_type else '',
            vendor_name=self.vendor_name.encode('utf-8') if self.vendor_name else '',
            device_model=self.device_model.encode('utf-8') if self.device_model else '',
            device_model_id=self.device_model_id,
            mac_address=self.mac_address.encode('utf-8') if self.mac_address else '',
            min_range=self.min_range,
            max_range=self.max_range,
            identifiable=self.identifiable,
            date_added=self.date_added,
            #bemoss=self.bemoss,
            approval_status=self.get_approval_status_display().encode('utf-8') if self.get_approval_status_display() else '',
            approval_status_choices=self.APPROVAL_STATUS_CHOICES)

    def data_dashboard(self):

        return dict(
            device_id=self.device_id,
            device_type=self.device_type.encode('utf-8') if self.device_type else '',
            vendor_name=self.vendor_name.encode('utf-8') if self.vendor_name else '',
            device_model=self.device_model.encode('utf-8') if self.device_model else '',
            device_model_id=self.device_model_id,
            mac_address=self.mac_address.encode('utf-8') if self.mac_address else '',
            min_range=self.min_range,
            max_range=self.max_range,
            identifiable=self.identifiable,
            #bemoss=self.bemoss,
            approval_status=self.approval_status,
            approval_status_choices=self.APPROVAL_STATUS_CHOICES)

    def device_control_page_info(self):
        return dict(
            device_id=self.device_id,
            device_model_id=self.device_model_id,
            mac_address=self.mac_address.encode('utf-8') if self.mac_address else '',
            device_type=self.device_type.encode('utf-8') if self.device_type else '',
            min_range=self.min_range,
            max_range=self.max_range,
            device_model=self.device_model,
            approval_status=self.approval_status)

    def device_status(self):
        return dict(
            device_model=self.device_model.encode('utf-8').capitalize() if self.device_model else '',
            date_added=self.date_added)


#Table to store floor-wise setpoints for devices. These setpoints will be overridden by local device settings.
class GlobalSetting(models.Model):
    zone = models.ForeignKey(Building_Zone)
    heat_setpoint = models.IntegerField(null=True, blank=True)
    cool_setpoint = models.IntegerField(null=True, blank=True)
    illuminance = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], null=True,
                                              blank=True)

    class Meta:
        db_table = "global_zone_setting"

    def __unicode__(self):
        return self.id

    def as_json(self):
        return dict(
            zone=self.zone,
            heat_setpoint=self.heat_setpoint,
            cool_setpoint=self.cool_setpoint,
            illumination=self.illuminance
        )





