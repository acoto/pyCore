# -*- coding: utf-8 -*-
"""
    stock.resources.resources
    ~~~~~~~~~~~~~~~~~~

    Provides the basic view classes for Stock and
    the Digest Authorization for ODK

    :copyright: (c) 2017 by QLands Technology Consultants.
    :license: AGPL, see LICENSE for more details.
"""

from ..config.auth import get_user_data
from pyramid.httpexceptions import HTTPFound
from pyramid.session import check_csrf_token
from pyramid.httpexceptions import HTTPNotFound
from formencode.variabledecode import variable_decode
from babel import Locale
from ast import literal_eval
import logging
from pyCore.processes.db import get_user_details, user_exists

log = logging.getLogger(__name__)


class PublicView(object):
    """
    This is the most basic public view. Used for 404 and 500. But then used for others more advanced classes
    """
    def __init__(self, request):
        self.request = request
        self._ = self.request.translate
        self.resultDict = {"errors": []}
        self.errors = []
        self.returnRawViewResult = False
        locale = Locale(request.locale_name)
        if locale.character_order == "left-to-right":
            self.resultDict["rtl"] = False
        else:
            self.resultDict["rtl"] = True

    def __call__(self):
        self.resultDict["errors"] = self.errors
        process_dict = self.process_view()
        if not self.returnRawViewResult:
            self.resultDict.update(process_dict)
            return self.resultDict
        else:
            return process_dict

    def process_view(self):
        raise NotImplementedError("process_view must be implemented in subclasses")

    def get_post_dict(self):
        dct = variable_decode(self.request.POST)
        return dct


class PrivateView(object):
    def __init__(self, request):
        self.request = request
        self.user = None
        self._ = self.request.translate
        self.errors = []
        self.userID = ''
        self.classResult = {"activeUser": None, "userProjects": [], 'activeProject': {}}
        self.viewResult = {}
        self.returnRawViewResult = False
        self.privateOnly = True
        self.guestAccess = False
        self.viewingSelfAccount = True
        self.showWelcome = False
        self.checkCrossPost = True
        self.queryProjects = True
        locale = Locale(request.locale_name)
        if locale.character_order == "left-to-right":
            self.classResult["rtl"] = False
        else:
            self.classResult["rtl"] = True
        self.classResult['activeMenu'] = ""

    def get_policy(self, policy_name):
        policies = self.request.policies()
        for policy in policies:
            if policy['name'] == policy_name:
                return policy['policy']
        return None

    def __call__(self):
        error = self.request.session.pop_flash(queue='error')
        if len(error) > 0:
            self.errors.append(error[0])

        # login_data = authenticated_userid(self.request)
        policy = self.get_policy('main')
        login_data = policy.authenticated_userid(self.request)

        if login_data is not None:
            login_data = literal_eval(login_data)
        self.guestAccess = False
        self.userID = self.request.matchdict['userid']
        if not user_exists(self.request, self.userID):
            raise HTTPNotFound()
        self.classResult["userDetails"] = get_user_details(self.request, self.userID)
        if self.request.method == 'POST' or self.request.method == 'PUT' or self.request.method == 'DELETE':
            if login_data is not None:
                if login_data["group"] == "mainApp":
                    self.user = get_user_data(login_data["login"], self.request)
                    if self.user is not None:
                        safe = check_csrf_token(self.request, raises=False)
                        if not safe:
                            self.request.session.pop_flash()
                            log.error("SECURITY-CSRF error at {} ".format(self.request.url))
                            raise HTTPFound(self.request.route_url('refresh'))
                        else:
                            if self.checkCrossPost:
                                if self.request.referer != self.request.url:
                                    self.request.session.pop_flash()
                                    log.error(
                                        "SECURITY-CrossPost error. Posting at {} from {} ".format(self.request.url,
                                                                                                  self.request.referer))
                                    raise HTTPNotFound()
                    else:
                        raise HTTPFound(location=self.request.route_url('login'))
                else:
                    raise HTTPFound(location=self.request.route_url('login'))
            else:
                raise HTTPFound(location=self.request.route_url('login'))

        if login_data is not None:
            if login_data["group"] == "mainApp":
                self.user = get_user_data(login_data["login"], self.request)
                if self.user is None:
                    if self.request.registry.settings['auth.allow_guest_access'] == 'false' or self.privateOnly:
                        raise HTTPFound(location=self.request.route_url('login', _query={'next': self.request.url}))
                    else:
                        self.guestAccess = True
            else:
                if self.request.registry.settings['auth.allow_guest_access'] == 'false' or self.privateOnly:
                    raise HTTPFound(location=self.request.route_url('login', _query={'next': self.request.url}))
                else:
                    self.guestAccess = True
        else:
            if self.request.registry.settings['auth.allow_guest_access'] == 'false' or self.privateOnly:
                raise HTTPFound(location=self.request.route_url('login', _query={'next': self.request.url}))
            else:
                self.guestAccess = True
        if not self.guestAccess:
            self.classResult["activeUser"] = self.user
            if self.user.login != self.userID:
                self.viewingSelfAccount = False
        else:
            self.classResult["activeUser"] = None
            self.viewingSelfAccount = False

        self.classResult["viewingSelfAccount"] = self.viewingSelfAccount
        self.classResult["errors"] = self.errors
        self.classResult["showWelcome"] = self.showWelcome
        self.viewResult = self.process_view()
        if not self.returnRawViewResult:
            self.classResult.update(self.viewResult)
            return self.classResult
        else:
            return self.viewResult

    def process_view(self):
        return {'activeUser': self.user}

    def set_active_menu(self, menu_name):
        self.classResult['activeMenu'] = menu_name

    def get_post_dict(self):
        dct = variable_decode(self.request.POST)
        return dct

    def reload_user_details(self):
        self.classResult["userDetails"] = get_user_details(self.request, self.userID)

    def add_error(self, message):
        self.request.session.flash(message, queue='error')

