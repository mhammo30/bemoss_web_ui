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
from django.contrib.auth.models import User
from apps.admin.models import NetworkStatus
from django import template
from apps.thermostat.models import Thermostat
from apps.lighting.models import Lighting
from apps.smartplug.models import Plugload
from apps.VAV.models import VAV
from apps.RTU.models import RTU
from django.db.models import Q

register = template.Library()


@register.filter
def device_count(zone_id):
    th_count = Thermostat.objects.filter(network_status='ONLINE', zone_id=zone_id,
                                         thermostat_id__approval_status='APR').count()
    vav_count = VAV.objects.filter(network_status='ONLINE', zone_id=zone_id, vav_id__approval_status='APR').count()
    rtu_count = RTU.objects.filter(network_status='ONLINE', zone_id=zone_id, rtu_id__approval_status='APR').count()
    pl_count = Plugload.objects.filter(network_status='ONLINE', zone_id=zone_id,
                                       plugload_id__approval_status='APR').count()
    lt_count = Lighting.objects.filter(network_status='ONLINE', zone_id=zone_id,
                                       lighting_id__approval_status='APR').count()
    lengthh = th_count + vav_count + rtu_count + pl_count + lt_count
    return lengthh


@register.filter
def dev_emsys_count(zone_id):
    th_count = Thermostat.objects.filter(network_status='ONLINE', zone_id=zone_id,
                                         thermostat_id__approval_status='APR').count()
    vav_count = VAV.objects.filter(network_status='ONLINE', zone_id=zone_id, vav_id__approval_status='APR').count()
    rtu_count = RTU.objects.filter(network_status='ONLINE', zone_id=zone_id, rtu_id__approval_status='APR').count()
    pl_count = Plugload.objects.filter(network_status='ONLINE', zone_id=zone_id,
                                       plugload_id__approval_status='APR').count()
    lt_count = Lighting.objects.filter(network_status='ONLINE', zone_id=zone_id,
                                       lighting_id__approval_status='APR').count()
    bemoss_lite = NetworkStatus.objects.filter(node_status='ONLINE').count()
    lengthh = th_count + vav_count + rtu_count + pl_count + lt_count + bemoss_lite
    return lengthh


@register.filter
def dev_emsys_ct_all(zone_id):

    lengthh = all_dev_ct(000) + embsys_count(000)
    return lengthh


@register.filter
def all_dev_ct(what):
    th_count = Thermostat.objects.filter(network_status='ONLINE', thermostat_id__approval_status='APR').count()
    vav_count = VAV.objects.filter(network_status='ONLINE', vav_id__approval_status='APR').count()
    rtu_count = RTU.objects.filter(network_status='ONLINE', rtu_id__approval_status='APR').count()
    lt_count = Lighting.objects.filter(network_status='ONLINE', lighting_id__approval_status='APR').count()
    pl_count = Plugload.objects.filter(network_status='ONLINE', plugload_id__approval_status='APR').count()
    count = th_count + vav_count + rtu_count + lt_count + pl_count
    return count

@register.filter
def embsys_count(zone_id):
    bemoss_lite = NetworkStatus.objects.filter(node_status='ONLINE').count()
    return bemoss_lite


@register.filter
def all_count(zone_id):
    th_count = Thermostat.objects.filter(network_status='ONLINE', zone_id=zone_id,
                                         thermostat_id__approval_status='APR').count()
    vav_count = VAV.objects.filter(network_status='ONLINE', zone_id=zone_id, vav_id__approval_status='APR').count()
    rtu_count = RTU.objects.filter(network_status='ONLINE', zone_id=zone_id, rtu_id__approval_status='APR').count()
    lt_count = Lighting.objects.filter(network_status='ONLINE', zone_id=zone_id,
                                       lighting_id__approval_status='APR').count()
    pl_count = Plugload.objects.filter(network_status='ONLINE', zone_id=zone_id,
                                       plugload_id__approval_status='APR').count()
    count = th_count + vav_count + rtu_count + lt_count + pl_count
    return count


@register.filter
def hvac_count(zone_id):
    th_count = Thermostat.objects.filter(network_status='ONLINE', zone_id=zone_id,
                                         thermostat_id__approval_status='APR').count()
    vav_count = VAV.objects.filter(network_status='ONLINE', zone_id=zone_id, vav_id__approval_status='APR').count()
    rtu_count = RTU.objects.filter(network_status='ONLINE', zone_id=zone_id, rtu_id__approval_status='APR').count()
    count = th_count + vav_count + rtu_count
    return count


@register.filter
def d_ct(_d_type):
    if _d_type == 'hvac':
        th_count = Thermostat.objects.filter(network_status='ONLINE', zone_id=999,
                                             thermostat_id__approval_status='APR').count()
        vav_count = VAV.objects.filter(network_status='ONLINE', zone_id=999, vav_id__approval_status='APR').count()
        rtu_count = RTU.objects.filter(network_status='ONLINE', zone_id=999, rtu_id__approval_status='APR').count()
        count = th_count + vav_count + rtu_count
        return count
    elif _d_type == 'light':
        lt_count = Lighting.objects.filter(network_status='ONLINE', zone_id=999,
                                           lighting_id__approval_status='APR').count()
        return lt_count
    elif _d_type == 'plug':
        pl_count = Plugload.objects.filter(network_status='ONLINE', zone_id=999,
                                           plugload_id__approval_status='APR').count()
        return pl_count


@register.filter
def md_ct(_d_type):
    if _d_type == 'hvac':
        th_count = Thermostat.objects.filter(network_status='ONLINE', thermostat_id__approval_status='APR').count()
        vav_count = VAV.objects.filter(network_status='ONLINE', vav_id__approval_status='APR').count()
        rtu_count = RTU.objects.filter(network_status='ONLINE', rtu_id__approval_status='APR').count()
        count = th_count + vav_count + rtu_count
        return count
    elif _d_type == 'light':
        lt_count = Lighting.objects.filter(network_status='ONLINE', lighting_id__approval_status='APR').count()
        return lt_count
    elif _d_type == 'plug':
        pl_count = Plugload.objects.filter(network_status='ONLINE', plugload_id__approval_status='APR').count()
        return pl_count


@register.filter
def nbd_ct(_d_type):
    if _d_type == 'hvac':
        th_count = Thermostat.objects.filter(network_status='ONLINE', thermostat_id__approval_status='NBD').count()
        vav_count = VAV.objects.filter(network_status='ONLINE', vav_id__approval_status='NBD').count()
        rtu_count = RTU.objects.filter(network_status='ONLINE', rtu_id__approval_status='NBD').count()
        count = th_count + vav_count + rtu_count
        return count
    elif _d_type == 'light':
        lt_count = Lighting.objects.filter(network_status='ONLINE', lighting_id__approval_status='NBD').count()
        return lt_count
    elif _d_type == 'plug':
        pl_count = Plugload.objects.filter(network_status='ONLINE', plugload_id__approval_status='NBD').count()
        return pl_count


@register.filter
def lt_count(zone_id):
    lt_count = Lighting.objects.filter(network_status='ONLINE', zone_id=zone_id,
                                       lighting_id__approval_status='APR').count()
    return lt_count


@register.filter
def pl_count(zone_id):
    pl_count = Plugload.objects.filter(network_status='ONLINE', zone_id=zone_id,
                                       plugload_id__approval_status='APR').count()
    return pl_count


@register.filter
def new_users(users):
    nusers = User.objects.filter(is_active=False).count()
    return nusers


@register.filter
def d_ct_all(_d_type):
    if _d_type == 'hvac':
        th_count = Thermostat.objects.filter(Q(thermostat_id__approval_status='PND'), network_status='ONLINE',
                                             zone_id=999).count()
        vav_count = VAV.objects.filter(Q(vav_id__approval_status='PND'), network_status='ONLINE', zone_id=999).count()
        rtu_count = RTU.objects.filter(Q(rtu_id__approval_status='PND'), network_status='ONLINE', zone_id=999).count()
        count = th_count + vav_count + rtu_count
        return count
    elif _d_type == 'light':
        lt_count = Lighting.objects.filter(Q(lighting_id__approval_status='PND'), network_status='ONLINE',
                                           zone_id=999).count()
        return lt_count
    elif _d_type == 'plug':
        pl_count = Plugload.objects.filter(Q(plugload_id__approval_status='PND'), network_status='ONLINE',
                                           zone_id=999).count()
        return pl_count


@register.filter
def all_dev_ct_pnd(what):
    th_count = Thermostat.objects.filter(network_status='ONLINE', thermostat_id__approval_status='PND').count()
    vav_count = VAV.objects.filter(network_status='ONLINE', vav_id__approval_status='PND').count()
    rtu_count = RTU.objects.filter(network_status='ONLINE', rtu_id__approval_status='PND').count()
    lt_count = Lighting.objects.filter(network_status='ONLINE', lighting_id__approval_status='PND').count()
    pl_count = Plugload.objects.filter(network_status='ONLINE', plugload_id__approval_status='PND').count()
    count = th_count + vav_count + rtu_count + lt_count + pl_count
    return count


@register.filter
def device_count_pnd(zone_id):
    th_count = Thermostat.objects.filter(network_status='ONLINE', zone_id=zone_id,
                                         thermostat_id__approval_status='PND').count()
    vav_count = VAV.objects.filter(network_status='ONLINE', zone_id=zone_id, vav_id__approval_status='PND').count()
    rtu_count = RTU.objects.filter(network_status='ONLINE', zone_id=zone_id, rtu_id__approval_status='PND').count()
    pl_count = Plugload.objects.filter(network_status='ONLINE', zone_id=zone_id,
                                       plugload_id__approval_status='PND').count()
    lt_count = Lighting.objects.filter(network_status='ONLINE', zone_id=zone_id,
                                       lighting_id__approval_status='PND').count()
    bemoss_lite = NetworkStatus.objects.filter(node_status='ONLINE').count()
    lengthh = th_count + vav_count + rtu_count + pl_count + lt_count + bemoss_lite
    return lengthh