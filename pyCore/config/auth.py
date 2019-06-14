from pyCore.models import User as userModel
from .encdecdata import decode_data
import urllib
import hashlib
from ..models import map_from_schema
from pyCore.plugins.core import PluginImplementations
from pyCore.plugins.interfaces import IAuthorize


class User(object):
    """
    This class represents a user in the system
    """
    def __init__(self, user_data):
        default = "identicon"
        size = 45
        self.id = user_data["user_email"]
        self.email = user_data["user_email"]
        self.tele = user_data["user_tele"]
        self.super = user_data["user_super"]
        self.company_id = user_data["company_id"]
        gravatar_url = "https://www.gravatar.com/avatar/" + hashlib.md5(
            self.email.lower().encode('utf8')).hexdigest() + "?"
        gravatar_url += urllib.parse.urlencode({'d': default, 's': str(size)})
        self.userData = user_data
        self.login = user_data["user_email"]
        self.name = user_data["user_name"]
        self.gravatarURL = gravatar_url

    def check_password(self, password, request):
        # Load connected plugins and check if they modify the password authentication
        plugin_result = None
        for plugin in PluginImplementations(IAuthorize):
            plugin_result = plugin.on_authenticate_password(request, self.login, password)
            break  # Only one plugging will be called to extend authenticate_user
        if plugin_result is None:
            return check_login(self.login, password, request)
        else:
            return plugin_result

    def get_gravatar_url(self, size):
        default = "identicon"
        gravatar_url = "https://www.gravatar.com/avatar/" + hashlib.md5(self.email.lower()).hexdigest() + "?"
        gravatar_url += urllib.parse.urlencode({'d': default, 's': str(size)})
        return gravatar_url

    def update_gravatar_url(self):
        default = "identicon"
        size = 45
        gravatar_url = "https://www.gravatar.com/avatar/" + hashlib.md5(self.email.lower()).hexdigest() + "?"
        gravatar_url += urllib.parse.urlencode({'d': default, 's': str(size)})
        self.gravatarURL = gravatar_url


def get_stock_user_data(request, user):
    return map_from_schema(request.dbsession.query(userModel).filter(userModel.user_email == user).first())


def get_user_data(user, request):
    # Load connected plugins and check if they modify the user authentication
    plugin_result = None
    plugin_result_dict = {}
    for plugin in PluginImplementations(IAuthorize):
        plugin_result, plugin_result_dict = plugin.on_authenticate_user(request, user)
        break  # Only one plugging will be called to extend authenticate_user
    if plugin_result is not None:
        if plugin_result:
            # The plugin authenticated the user. Check now that such user exists in Stock.
            internal_user = get_stock_user_data(request, user)
            if internal_user:
                return User(plugin_result_dict)
            else:
                return None
        else:
            return None
    else:
        result = get_stock_user_data(request, user)
        if result:
            result["user_pass"] = ""  # Remove the password form the result
            return User(result)
        return None


def check_login(user, password, request):
    result = request.dbsession.query(userModel).filter(userModel.user_email == user).first()
    if result is None:
        return False
    else:
        cpass = decode_data(request, result.user_pass.encode())
        if cpass == bytearray(password.encode()):
            return True
        else:
            return False
