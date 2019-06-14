from ...models import map_to_schema, User, map_from_schema
from sqlalchemy.exc import IntegrityError
import logging
import validators

__all__ = [
    'register_user', 'user_exists', 'get_user_details', 'update_profile', 'get_user_name'
]

log = logging.getLogger(__name__)


def register_user(request, user_data):
    user_data.pop('user_password2', None)
    mapped_data = map_to_schema(User, user_data)
    email_valid = validators.email(mapped_data["user_email"])
    if email_valid:
        res = request.dbsession.query(User).filter(User.user_email == mapped_data["user_email"]).first()
        if res is None:
            new_user = User(**mapped_data)
            try:
                request.dbsession.add(new_user)
                request.dbsession.flush()
                return True, ""
            except IntegrityError:
                request.dbsession.rollback()
                log.error("Duplicated user {}".format(mapped_data["user_email"]))
                return False, request.translate("Username is already taken")
            except Exception as e:
                request.dbsession.rollback()
                log.error("Error {} when inserting user {}".format(str(e), mapped_data["user_email"]))
                return False, str(e)
        else:
            log.error("Duplicated user with email {}".format(mapped_data["user_email"]))
            return False, request.translate("Email already taken")
    else:
        log.error("Email {} is not valid".format(mapped_data["user_email"]))
        return False, request.translate("Email is invalid")


def user_exists(request, user):
    res = request.dbsession.query(User).filter(User.user_email == user).first()
    if res is None:
        return False
    return True


def get_user_details(request, user):
    res = request.dbsession.query(User).filter(User.user_email == user).first()
    if res is not None:
        result = map_from_schema(res)
        return result
    return {}


def get_user_name(request, user):
    res = request.dbsession.query(User).filter(User.user_email == user).first()
    if res is not None:
        return res.user_name
    else:
        return None


def update_profile(request, user, profile_data):
    mapped_data = map_to_schema(User, profile_data)
    try:
        request.dbsession.query(User).filter(User.user_email == user).update(mapped_data)
        request.dbsession.flush()
        return True, ""
    except Exception as e:
        request.dbsession.rollback()
        log.error("Error {} when updating user user {}".format(str(e), user))
        return False, str(e)
