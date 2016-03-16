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
from apps.dashboard.models import Building_Zone, DeviceMetadata


#Thermostat device information - for all thermostats in BEMOSS
class Thermostat(models.Model):
    thermostat = models.ForeignKey(DeviceMetadata,max_length=50, primary_key=True)
    temperature = models.FloatField(null=True, blank=True)
    thermostat_mode = models.CharField(max_length=4, null=True, blank=True)
    fan_mode = models.CharField(max_length=10, null=True, blank=True)
    heat_setpoint = models.FloatField(null=True, blank=True)
    cool_setpoint = models.FloatField(null=True, blank=True)
    thermostat_state = models.CharField(max_length=4, null=True, blank=True)
    fan_state = models.CharField(max_length=4, null=True, blank=True)
    ip_address = models.IPAddressField(null=True, blank=True)
    nickname = models.CharField(max_length=30, null=True, blank=True)
    zone = models.ForeignKey(Building_Zone, null=True, blank=True)
    network_status = models.CharField(max_length=7, null=True, blank=True)
    other_parameters = models.CharField(max_length=200, null=True, blank=True)
    last_scanned_time = models.DateTimeField(null=True, blank=True)
    last_offline_time = models.DateTimeField(null=True, blank=True)
    battery = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], null=True, blank=True)
    override = models.NullBooleanField()
    hold = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)], null=True, blank=True)

    class Meta:
        db_table = "thermostat"

    def __unicode__(self):
        return self.thermostat_id

    def get_zone(self):
        zone_req = Building_Zone.as_json(self.zone)
        return zone_req

    def data_as_json(self):
        zone_req = Building_Zone.as_json(self.zone)
        device_info = DeviceMetadata.objects.get(device_id=self.thermostat_id)
        metadata = DeviceMetadata.data_as_json(device_info)
        return dict(
            id=self.thermostat_id,
            temperature=self.temperature,
            heat_setpoint=self.heat_setpoint,
            cool_setpoint=self.cool_setpoint,
            thermostat_mode=self.thermostat_mode.encode('utf-8') if self.thermostat_mode else '',
            fan_mode=self.fan_mode.encode('utf-8') if self.fan_mode else '',
            device_model_id=metadata['device_model_id'],
            device_type=metadata['device_type'].encode('utf-8') if metadata['device_type'] else '',
            identifiable=metadata['identifiable'],
            mac_address=metadata['mac_address'].encode('utf-8') if metadata['mac_address'] else '',
            vendor_name=metadata['vendor_name'].encode('utf-8') if metadata['vendor_name'] else '',
            device_model=metadata['device_model'].encode('utf-8') if metadata['device_model'] else '',
            battery=self.battery,
            override=self.override,
            hold=self.hold,
            # bemoss=metadata['bemoss'],
            zone=zone_req,
            zone_id=zone_req['id'],
            nickname=self.nickname.encode('utf-8').title() if self.nickname else '',
            approval_status=metadata['approval_status'],
            approval_status_choices=metadata['approval_status_choices'])

    def device_status(self):
        zone_req = Building_Zone.as_json(self.zone)
        device_info = DeviceMetadata.objects.get(device_id=self.thermostat_id)
        metadata = DeviceMetadata.data_as_json(device_info)
        return dict(
            id=self.thermostat_id,
            nickname=self.nickname.encode('utf-8').title() if self.nickname else '',
            device_model=metadata['device_model'],
            date_added=metadata['date_added'],
            zone_id=zone_req['id'],
            #bemoss=metadata['bemoss'],
            zone_nickname=zone_req['zone_nickname'],
            battery=self.battery,
            override=self.override,
            hold=self.hold,
            network_status=self.network_status.capitalize(),
            last_scanned=self.last_scanned_time,
            last_offline=self.last_offline_time,
            approval_status=metadata['approval_status'],
            approval_status_choices=metadata['approval_status_choices'])

    def data_dashboard(self):
        zone_req = Building_Zone.as_json(self.zone)
        device_info = DeviceMetadata.objects.get(device_id=self.thermostat_id)
        metadata = DeviceMetadata.data_as_json(device_info)
        return dict(
            device_id=self.thermostat_id,
            device_type=metadata['device_type'].encode('utf-8') if metadata['device_type'] else '',
            vendor_name=metadata['vendor_name'].encode('utf-8') if metadata['vendor_name'] else '',
            device_model=metadata['device_model'].encode('utf-8') if metadata['device_model'] else '',
            device_model_id=metadata['device_model_id'],
            identifiable=metadata['identifiable'],
            mac_address=metadata['mac_address'].encode('utf-8') if metadata['mac_address'] else '',
            nickname=self.nickname.encode('utf-8').title() if self.nickname else '',
            date_added=metadata['date_added'],
            zone_id=zone_req['id'],
            #bemoss=metadata['bemoss'],
            battery=self.battery,
            override=self.override,
            hold=self.hold,
            zone_nickname=zone_req['zone_nickname'],
            network_status=self.network_status.capitalize(),
            last_scanned=self.last_scanned_time,
            approval_status=metadata['approval_status'],
            approval_status_choices=metadata['approval_status_choices'])

    def data_side_nav(self):
        zone_req = Building_Zone.as_json(self.zone)
        device_info = DeviceMetadata.objects.get(device_id=self.thermostat_id)
        metadata = DeviceMetadata.data_as_json(device_info)
        return dict(
            device_id=self.thermostat_id,
            device_model_id=metadata['device_model_id'],
            mac_address=metadata['mac_address'].encode('utf-8') if metadata['mac_address'] else '',
            nickname=self.nickname.encode('utf-8').title() if self.nickname else '',
            zone_id=zone_req['id'],
            #bemoss=metadata['bemoss'],
            zone_nickname=zone_req['zone_nickname'],
            network_status=self.network_status.capitalize(),
            approval_status=metadata['approval_status'],
            approval_status_choices=metadata['approval_status_choices'])
