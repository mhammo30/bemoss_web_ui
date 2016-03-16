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
from django.db import transaction

from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
from _utils.lockout import LockedOut
from _utils.page_load_utils import get_device_list_side_navigation
from apps.alerts.views import get_notifications, general_notifications
from apps.dashboard.models import Building_Zone
from forms import RegistrationForm, RegistrationForm1
import logging
import _utils.messages as _
import json

logger = logging.getLogger("views")


def login_user(request):
    print "User login request"
    #Obtain the context for the user's request.
    context = RequestContext(request)

    if request.method == 'POST':     
            # Gather the username and password provided by the user.
            # This information is obtained from the login form.
            username = request.POST['username']
            password = request.POST['password']
            user = None
            # Use Django's machinery to attempt to see if the username/password
            # combination is valid - a User object is returned if it is.
            try:
                user = authenticate(username=username, password=password)
            except LockedOut:
                messages.warning(request, 'Your account has been locked out because of too many failed login attempts.')

            # If we have a User object, the details are correct.
            # If None (Python's way of representing the absence of a value), no user
            # with matching credentials was found.
            if user is not None:
                # Is the account active? It could have been disabled.
                if user.is_active:
                    # If the account is valid and active, we can log the user in.
                    # We'll send the user back to the homepage.
                    login(request, user)
                    request.session['zipcode'] = '22204'
                    logger.info("Login of user : %s", user.username)
                    redirect_to = str(request.META.get('HTTP_REFERER', '/'))
                    if redirect_to.__contains__('next='):
                        redirect_to = str(redirect_to).split('=')
                        redirect_to = redirect_to[1]
                        return HttpResponseRedirect(redirect_to)
                    else:
                        return HttpResponseRedirect('/home/')
                else:
                    # An inactive account was used - no logging in!
                    messages.error(request, _.INACTIVE_USER)
                    return HttpResponseRedirect('/login/')

            else:
                # Bad login details were provided. So we can't log the user in.
                print "Invalid login details: {0}, {1}".format(username, password)
                messages.error(request, _.INCORRECT_USER_PASSWORD)
                #return HttpResponse("Invalid login details supplied.")
                return HttpResponseRedirect('/login/')

    else:
        print request
        if request.user.is_authenticated():
            return HttpResponseRedirect('/home/')
        else:
        # The request is not a HTTP POST, so display the login form.
        # This scenario would most likely be a HTTP GET.
            return render_to_response('accounts/login.html', {}, context)
    

# Use the login_required() decorator to ensure only those logged in can access the view.
@login_required(login_url='/login/')
def logout_user(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)
    # Take the user back to the homepage.
    return HttpResponseRedirect('/login/')


def register(request):
    if request.method == "POST":
        form = RegistrationForm1(request.POST)

        if form.is_valid():
            kwargs = form.cleaned_data
            new_user = create_user(request, **kwargs)

            messages.success(request, "Thanks for creating an account!  Your login id is %s. "
                                      "Please wait for an email from BEMOSS admin for account activation." % kwargs['username'])
            #return HttpResponseRedirect(reverse('registration_complete'))

            return HttpResponseRedirect('/register/')
        else:
            errors = json.dumps(form.errors)
            errors = json.loads(errors)
            for error in errors:
                message = ""
                for mesg in errors[error]:
                    message = message + "," + mesg
                message = message[:-1]
                message = message[1:]
                messages.error(request, message)

            return HttpResponseRedirect('/register/')

    else:
        form = RegistrationForm()
        context = RequestContext(request)
        return render_to_response('accounts/registration_form.html', {form: form}, context)

@transaction.commit_on_success
def create_user(request, *args, **kwargs):
    new_user = User.objects.create_user(kwargs['username'], kwargs['email'], kwargs['password1'])
    new_user.save()
    new_user.is_active = False
    new_user.save()
    uuser = User.objects.get(username=kwargs['username'])
    uuser.first_name = kwargs['first_name']
    uuser.last_name = kwargs['last_name']
    uuser.save()
    return new_user


@login_required(login_url='/login/')
def user_manager(request):
    context = RequestContext(request)
    zones = [ob.as_json() for ob in Building_Zone.objects.all()]

    active_al = get_notifications()
    context.update({'active_al':active_al})
    device_list_side_nav = get_device_list_side_navigation()
    context.update(device_list_side_nav)
    bemoss_not = general_notifications()
    context.update({'b_al': bemoss_not})

    if request.user.get_profile().group.name.lower() == 'admin':
        _users = User.objects.all()
        groups = Group.objects.all()
        print _users
        return render_to_response('admin/user_manager.html', {"users": _users, 'zones': zones, 'groups': groups},
                                  context)
    else:
        return HttpResponseRedirect('/home/')


@login_required(login_url='/login/')
def approve_users(request):
    if request.POST:
        _data = request.body
        _data = json.loads(_data)
        print _data

        for user in _data['data']:
            usr = User.objects.get(id=user[0])
            if user[1] == "true":
                usr.is_active = True
            uprofile = usr.get_profile()
            uprofile.group_id = Group.objects.get(name=user[2])
            uprofile.save()
            usr.save()
            send_mail(_.EMAIL_USER_APPROVED_SUBJECT,
                      _.EMAIL_USER_MESSAGE.format(usr.first_name + ' ' + usr.last_name,
                                                  request.get_host()), _.EMAIL_FROM_ADDRESS,
                      [usr.email], fail_silently=True)

        print "user accounts activated"
        json_text = {
            "status": "success"
        }

    return HttpResponse(json.dumps(json_text), mimetype='text/plain')


@login_required(login_url='/login/')
def modify_user_permissions(request):
    if request.POST:
        _data = request.body
        _data = json.loads(_data)
        print _data

        for user in _data['data']:
            usr = User.objects.get(id=user[0])
            uprofile = usr.get_profile()
            uprofile.group_id = Group.objects.get(name=user[1])
            uprofile.save()
            usr.save()

        print "user accounts permissions modified"
        json_text = {
            "status": "success"
        }

    return HttpResponse(json.dumps(json_text), mimetype='text/plain')


@login_required(login_url='/login/')
def delete_user(request):
    if request.POST:
        _data = request.body
        _data = json.loads(_data)
        print _data

        user_id = _data['id']
        usr = User.objects.get(id=user_id)
        usrprof = usr.get_profile()
        usrprof.delete()
        usr.delete()

        print "user account removed"
        json_text = {
            "status": "success"
        }

    return HttpResponse(json.dumps(json_text), mimetype='text/plain')