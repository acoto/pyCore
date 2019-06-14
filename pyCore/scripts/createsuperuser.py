import sys
import getpass
import os
import transaction
import validators

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars

from {{cookiecutter.repo_name}}.models.meta import Base
from {{cookiecutter.repo_name}}.models import (
    get_engine,
    get_session_factory,
    get_tm_session,
    )
from {{cookiecutter.repo_name}}.models import User
from {{cookiecutter.repo_name}}.config.encdecdata import encode_data_with_aes_key


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> user_email=value user_name=value\n'
          "(example: %s development.ini user_email=me@mydomain.com user_name=admin)" % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 4:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    if 'user_email' not in options.keys():
        usage(argv)
    if 'user_name' not in options.keys():
        usage(argv)

    pass1 = getpass.getpass("User password:")
    pass2 = getpass.getpass("Confirm the password:")
    if pass1 == '':
        print("The password cannot be empty")
        sys.exit(1)
    if pass1 != pass2:
        print("The password and its confirmation are not the same")
        sys.exit(1)

    email_valid = validators.email(options["user_email"])
    if not email_valid:
        print("Invalid email")
        sys.exit(1)

    setup_logging(config_uri)
    settings = get_appsettings(config_uri, 'stock')
    enc_pass = encode_data_with_aes_key(pass1, settings['aes.key'])

    engine = get_engine(settings)
    Base.metadata.create_all(engine)

    session_factory = get_session_factory(engine)

    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)
        try:
            if dbsession.query(User).filter(User.user_email == options["user_email"]).first() is None:
                new_user = User(user_email=options["user_email"], user_name=options["user_name"],
                                user_pass=enc_pass, user_super=1)
                dbsession.add(new_user)
                print("The super user has been added with the following information:")
                print("Email: %s" % (options["user_email"]))
                print("Name: %s" % (options["user_name"]))
            else:
                print('An user with email "%s" already exists' % (options["user_email"]))
                sys.exit(1)
        except Exception as e:
            print(str(e))
            sys.exit(1)
