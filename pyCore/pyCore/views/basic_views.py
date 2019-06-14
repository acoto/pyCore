from pyramid.security import remember
from pyramid.httpexceptions import HTTPFound
from ..config.auth import get_user_data
from .classes import PublicView
from pyramid.session import check_csrf_token
from pyramid.httpexceptions import HTTPNotFound
from formencode.variabledecode import variable_decode
import pyCore.plugins as p
from ast import literal_eval


class HomeView(PublicView):
    def process_view(self):
        return {'activeUser': None, 'projectName': "pyCore"}


class NotFoundView(PublicView):
    def process_view(self):
        self.request.response.status = 404
        return {}


class LoginView(PublicView):
    def process_view(self):
        # If we logged in then go to dashboard
        next_page = self.request.params.get('next')
        if self.request.method == 'GET':
            policy = get_policy(self.request, 'main')
            login_data = policy.authenticated_userid(self.request)
            if login_data is not None:
                login_data = literal_eval(login_data)
                if login_data["group"] == "mainApp":
                    current_user = get_user_data(login_data["login"], self.request)
                    if current_user is not None:
                        self.returnRawViewResult = True
                        return HTTPFound(location=self.request.route_url('dashboard', userid=current_user.login))
        else:
            safe = check_csrf_token(self.request, raises=False)
            if not safe:
                raise HTTPNotFound()
            data = variable_decode(self.request.POST)
            login = data['email']
            passwd = data['passwd']
            user = get_user_data(login, self.request)
            login_data = {"login": login, "group": "mainApp"}
            if user is not None:
                if user.check_password(passwd, self.request):
                    continue_login = True
                    # Load connected plugins and check if they modify the login authorization
                    for plugin in p.PluginImplementations(p.IAuthorize):
                        continue_with_login, error_message = plugin.after_login(self.request, user)
                        if not continue_with_login:
                            self.errors.append(error_message)
                            continue_login = False
                        break  # Only one plugging will be called to extend after_login
                    if continue_login:
                        headers = remember(self.request, str(login_data), policies=['main'])
                        next_page = self.request.params.get('next') or self.request.route_url('dashboard',
                                                                                              userid=user.login)
                        self.returnRawViewResult = True
                        return HTTPFound(location=next_page, headers=headers)
                else:
                    self.errors.append(self._("The user account does not exists or the password is invalid"))
            else:
                self.errors.append(self._("The user account does not exists or the password is invalid"))
        return {'next': next_page}


class RefreshSessionView(PublicView):
    def process_view(self):
        return {}


def get_policy(request, policy_name):
    policies = request.policies()
    for policy in policies:
        if policy['name'] == policy_name:
            return policy['policy']
    return None


def log_out_view(request):
    policy = get_policy(request, 'main')
    headers = policy.forget(request)
    loc = request.route_url('home')
    raise HTTPFound(location=loc, headers=headers)
