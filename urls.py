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


from django.conf.urls.defaults import patterns, include, url
from django.utils.functional import curry
from django.views.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
import settings_tornado

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'bemoss_web_ui.views.home', name='home'),
    # url(r'^bemoss_web_ui/', include('bemoss_web_ui.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    #register user
    (r'^register/$', 'apps.accounts.views.register'),
    #(r'^accounts/', include('apps.registration.backends.default.urls')),
    #login
    (r'^login/$', 'apps.accounts.views.login_user'),
    #user manager
    (r'^usr_mngr/$', 'apps.accounts.views.user_manager'),
    #approve users
    (r'^approve_users/$', 'apps.accounts.views.approve_users'),
    #modify user permissions
    (r'^modify_user_permissions/$', 'apps.accounts.views.modify_user_permissions'),
    #delete user
    (r'^delete_user/$', 'apps.accounts.views.delete_user'),
    #redirect to login page or home page
    (r'^$', 'apps.dashboard.views.bemoss_home'),
    #logout
    (r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/login'}),
    #(r'^logout_bemoss/$', 'accounts.views.logout_user'),
    (r'^tstat/(?P<mac>[a-zA-Z0-9]+)/$', 'apps.thermostat.views.thermostat'),
    (r'^submitdata3m50/$', 'apps.thermostat.views.submit_values'),
    #plugload
    (r'^plug/(?P<mac>[a-zA-Z0-9]+)/$', 'apps.smartplug.views.smartplug'),
    #philips hue
    (r'^hue/$', 'lighting.views.philipshue'),
    #lighting controller
    (r'^light/(?P<mac>[a-zA-Z0-9]+)/$', 'apps.lighting.views.lighting'),
    #lighting controller update device 
    (r'^update_light/$', 'apps.lighting.views.update_device_light'),
    #lighting controller update device 
    (r'^update_light_device_status/$', 'apps.lighting.views.update_device_agent_status'),
    #get light status realtime
    (r'^lt_stat/$', 'apps.lighting.views.get_lighting_current_status'),
    #set schedule form
    (r'^schedule/$', 'apps.schedule.views.thermostat_schedule'),
    #thermostat_scheduling
    (r'^th_schedule/(?P<mac>[a-zA-Z0-9]+)/$', 'apps.schedule.views.thermostat_schedule'),
    #lighting_scheduling
    (r'^lt_schedule/(?P<mac>[a-zA-Z0-9]+)/$', 'apps.schedule.views.lighting_schedule'),
    #plugload_scheduling
    (r'^pl_schedule/(?P<mac>[a-zA-Z0-9]+)/$', 'apps.schedule.views.plugload_schedule'),
    #update thermostat schedule
    (r'^submit_schedule/$', 'apps.schedule.views.update_thermostat_schedule'),
    #update schedule
    (r'^update_schedule/$', 'apps.schedule.views.update_schedule_status_to_browser'),
    #periodic update of thermostat
    (r'^thstat/$', 'apps.thermostat.views.get_thermostat_current_status'),
    #wunderground
    (r'^weather/$', 'apps.thermostat.views.weather'),
    #device_update
    (r'^update_3m50/$', 'apps.thermostat.views.deviceupdatemessagetobrowser'),
    #dashboard
    (r'^dashboard/$', 'apps.dashboard.views.dashboard'),
    #dashboard
    (r'^identify_device/$', 'apps.dashboard.views.identify_device'),
    #identify_device_status
    (r'^identify_status/$', 'apps.dashboard.views.identify_status'),
    #dashboard - add new zone
    (r'^add_new_zone/$', 'apps.dashboard.views.add_new_zone'),
    #dashboard - add new zone
    (r'^save_view_edit_changes_dashboard/$', 'apps.dashboard.views.save_changes_modal'),
    #dashboard - change nickname
    (r'^save_zone_nickname_change/$', 'apps.dashboard.views.save_zone_nickname_changes'),
    #update_plugload
    (r'^update_plugload/$', 'apps.smartplug.views.submit_changes'),
    #update_plugload_status
    (r'^update_plugload_status/$', 'apps.smartplug.views.update_device_agent_status'),
    #get plugload current status
    (r'^plugload_stat/$', 'apps.smartplug.views.get_plugload_current_status'),
    #alerts and notifications home
    (r'^alerts/$', 'apps.alerts.views.alerts'),
    #create new alert
    (r'^create_alert/$', 'apps.alerts.views.create_alert'),
    # the number of unseen notifications
    (r'^no_of_seen_notifications_push/$', 'apps.alerts.views.no_of_seen_notifications_push'),
    #delete alert
    (r'^del_alert/$', 'apps.alerts.views.delete_alert'),

    (r'^submit_active_schedule/$', 'apps.schedule.views.activate_schedule'),
    #device_status
    (r'^dstat/$', 'apps.admin.views.device_status'),
    #network status
    (r'^nwstat/$', 'apps.admin.views.network_status'),
    #notifications
    (r'^ntfns/$', 'apps.alerts.views.notifications'),
    #discovery
    (r'^discover/$', 'apps.dashboard.views.discover'),
    (r'^ndiscover/$', 'apps.dashboard.views.discover_nodes'),
    #change_zone_thermostat
    (r'^change_zones_thermostats/$', 'apps.dashboard.views.change_zones_thermostats'),
    #change_zone_plugload
    (r'^change_zones_plugloads/$', 'apps.dashboard.views.change_zones_plugloads'),
    #change_zone_lighting
    (r'^change_zones_lighting/$', 'apps.dashboard.views.change_zones_lighting_loads'),
    #modify thermostats
    (r'^modify_thermostats/$', 'apps.dashboard.views.modify_thermostats'),
    #modify plugloads
    (r'^modify_plugloads/$', 'apps.dashboard.views.modify_plugloads'),
    #modify lighting
    (r'^modify_lighting_loads/$', 'apps.dashboard.views.modify_lighting_loads'),
    #change_zones_lite
    (r'^change_zones_lite/$', 'apps.dashboard.views.change_zones_lite'),
    #home page (new dashboard)
    (r'^home/$', 'apps.dashboard.views.bemoss_home'),
    #change global settings
    (r'^change_global_settings/$', 'apps.dashboard.views.change_global_settings'),
    #dashboard_devices_in_zone
    (r'^devices/(?P<zone_dev>[a-zA-Z0-9_]+)$', 'apps.dashboard.views.zone_device_listing'),
    (r'^all_devices/(?P<zone_dev>[a-zA-Z0-9_]+)$', 'apps.dashboard.views.zone_device_all_listing'),
    #vav page load
    (r'^vav/(?P<mac>[a-zA-Z0-9]+)$', 'apps.VAV.views.vav_view'),
    #rtu page load
    (r'^rtu/(?P<mac>[a-zA-Z0-9]+)$', 'apps.RTU.views.rtu_view'),
    #rtu update
    (r'^submit_rtu_data/', 'apps.RTU.views.submit_rtu_data'),
    #submit vav data
    (r'^submit_vav_data/', 'apps.VAV.views.submit_vav_data'),
    #bemoss_settings
    (r'^bemoss_settings/', 'apps.admin.views.bemoss_settings'),
    # delete holiday
    (r'^delete_holiday/', 'apps.admin.views.delete_holiday'),
    # add holiday
    (r'^add_holiday/', 'apps.admin.views.add_holiday'),
    #bemoss location (weather requirement)
    (r'^b_location_modify/', 'apps.admin.views.update_bemoss_location'),
    #export to excel
    (r'^export_excel/', 'apps.reports.views.export_to_spreadsheet'),
    #export device data
    (r'^export_thd/', 'apps.reports.views.export_thermostat_to_spreadsheet'),
    (r'^export_ltd/', 'apps.reports.views.export_lighting_to_spreadsheet'),
    (r'^export_pld/', 'apps.reports.views.export_plugload_to_spreadsheet'),
    (r'^export_alld/', 'apps.reports.views.export_all_device_information'),
    (r'^report_thschd/(?P<mac>[a-zA-Z0-9]+)$', 'apps.reports.views.export_schedule_thermostats_daily'),
    (r'^report_thschh/(?P<mac>[a-zA-Z0-9]+)$', 'apps.reports.views.export_schedule_thermostats_holiday'),
    (r'^report_ltschd/(?P<mac>[a-zA-Z0-9]+)$', 'apps.reports.views.export_schedule_lighting_daily'),
    (r'^report_ltschh/(?P<mac>[a-zA-Z0-9]+)$', 'apps.reports.views.export_schedule_lighting_holiday'),
    (r'^report_plschd/(?P<mac>[a-zA-Z0-9]+)$', 'apps.reports.views.export_schedule_plugload_daily'),
    (r'^report_plschh/(?P<mac>[a-zA-Z0-9]+)$', 'apps.reports.views.export_schedule_plugload_holiday'),
    (r'^discover_all/$', 'apps.dashboard.views.discover_all'),
    (r'^discover_hvac/$', 'apps.dashboard.views.discover_hvac'),
    (r'^discover_lighting/$', 'apps.dashboard.views.discover_lighting'),
    (r'^discover_plugloads/$', 'apps.dashboard.views.discover_plugload'),
    #Modify NBD Devices Discovery Page
    (r'^modify_nbd_thermostats/$', 'apps.dashboard.views.modify_nbd_thermostats'),
    (r'^modify_nbd_lighting_loads/$', 'apps.dashboard.views.modify_nbd_lighting_loads'),
    (r'^modify_nbd_plugloads/$', 'apps.dashboard.views.modify_nbd_plugloads'),

    # Cassandra charts and statistics loading
    (r'^th_statistics/(?P<mac>[a-zA-Z0-9]+)$', 'apps.charts.views.charts_thermostat'),
    (r'^th_smap_update/$', 'apps.charts.views.auto_update_charts_thermostat'),
    (r'^lt_statistics/(?P<mac>[a-zA-Z0-9]+)$', 'apps.charts.views.charts_lighting'),
    (r'^lt_smap_update/$', 'apps.charts.views.auto_update_charts_lighting'),
    (r'^pl_statistics/(?P<mac>[a-zA-Z0-9]+)$', 'apps.charts.views.charts_plugload'),
    (r'^pl_smap_update/$', 'apps.charts.views.auto_update_charts_plugload'),
    (r'^wtpl_statistics/(?P<mac>[a-zA-Z0-9]+)$', 'apps.charts.views.charts_wattstopper_plugload'),
    (r'^wtpl_smap_update/$', 'apps.charts.views.auto_update_charts_wattstopper_plugload'),
    (r'^vav_statistics/(?P<mac>[a-zA-Z0-9]+)$', 'apps.charts.views.charts_vav'),
    (r'^vav_smap_update/$', 'apps.charts.views.auto_update_charts_vav'),
    (r'^rtu_statistics/(?P<mac>[a-zA-Z0-9]+)$', 'apps.charts.views.charts_rtu'),
    (r'^rtu_smap_update/$', 'apps.charts.views.auto_update_charts_rtu'),

    # Get statistics based on date and time
    (r'^th_smap_get_stat/$', 'apps.charts.views.get_statistics_datetime_thermostat'),
    (r'^lt_smap_get_stat/$', 'apps.charts.views.get_statistics_datetime_lighting'),
    (r'^pl_smap_get_stat/$', 'apps.charts.views.get_statistics_datetime_plugload'),
    (r'^wtpl_smap_get_stat/$', 'apps.charts.views.get_statistics_datetime_wattstopper_plugload'),
    (r'^vav_smap_get_stat/$', 'apps.charts.views.get_statistics_datetime_vav'),
    (r'^rtu_smap_get_stat/$', 'apps.charts.views.get_statistics_datetime_rtu'),

    #Manual discovery
    (r'^mdiscover/', 'apps.discovery.views.discover_devices'),
    (r'^mdiscover_more/', 'apps.discovery.views.discover_new_devices'),
    (r'^th_export_tsd/', 'apps.reports.views.export_thermostat_time_series_data_spreadsheet'),
    (r'^authenticate_hue/', 'apps.discovery.views.authenticate_hue_device'),
    (r'^wtpl_export_tsd/', 'apps.reports.views.export_wattplug_time_series_data_spreadsheet'),
    (r'^pl_export_tsd/', 'apps.reports.views.export_plugload_time_series_data_spreadsheet'),
    (r'^lt_export_tsd/', 'apps.reports.views.export_lighting_time_series_data_spreadsheet'),
    (r'^vav_export_tsd/', 'apps.reports.views.export_vav_time_series_data_spreadsheet'),
    (r'^rtu_export_tsd/', 'apps.reports.views.export_rtu_time_series_data_spreadsheet'),

)
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings_tornado.MEDIA_URL, document_root=settings_tornado.MEDIA_ROOT)

#handler404 = 'error.views.error404'    
#handler500 = 'error.views.error500'
handler500 = 'apps.error.views.handler500'
handler404 = 'apps.error.views.handler404'

