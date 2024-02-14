import os
import sys
from pathlib import Path
import click
import ldap
import ruamel.yaml

from .params import *
from .config import config, Config
from .model import Person, Group

yaml = ruamel.yaml.YAML()
yaml.register_class(Person)
yaml.register_class(Group)
yaml.register_class(Config)


def sudo():
    """
    Checks that the program is running as root, otherwise asks for permissions and it runs again.
    """
    euid = os.geteuid()
    if euid != 0:
        print("Script not started as root. Running sudo...")
        args = ['sudo', sys.executable] + sys.argv + [os.environ]
        os.execlpe('sudo', *args)  # Replaces the current process with the sudo

    print("Running as sudo")


def get_ldap_password():
    """
    Reads the content of config.ldap_secret file
    :return: String
    """
    with open(config.ldap_secret, 'r') as file:
        password = file.read()
    return password.rstrip()


def fetch_ldap():
    """
    Fetches LDAP server information
    """
    con = ldap.initialize(config.ldap_uri)
    if config.ldap_root_cert:
        con.set_option(ldap.OPT_X_TLS_CACERTFILE, config.ldap_root_cert)
        con.set_option(ldap.OPT_X_TLS_NEWCTX, 0)
        con.start_tls_s()
    password = get_ldap_password()
    con.bind_s(config.admin, password, ldap.AUTH_SIMPLE)

    people = con.search_s(config.people, ldap.SCOPE_SUBTREE, '(objectclass=person)')
    people = list(map(lambda p: Person(p), people))
    groups = con.search_s(config.groups, ldap.SCOPE_SUBTREE, '(objectclass=posixGroup)')
    groups = list(map(lambda g: Group(g), groups))

    # TODO: Maybe ldap query can be tuned to return this information

    # Map person gidNumber to groupName
    for p in people:
        group = list(filter(lambda g: g.gidNumber == p.gidNumber, groups))[0]
        p.groupName = group.cn

    # Add extra groups to user
    for group in groups:
        for memberUid in group.memberUid:
            person = list(filter(lambda p: p.uid == memberUid, people))[0]
            person.groups.append(group.cn)

    con.unbind_s()

    return people, groups


def store_to_yaml(object, path):
    """
    Writes the Python object as YAML in path
    :param object: Python object
    :param path: String
    :return:
    """
    print("Writing to %s" % path)
    with open(path, 'w') as f:
        yaml.dump(object, f)


def read_from_yaml(path):
    """
    Restores the Python object stored in path as YAML
    :param path: String
    :return: Python object
    """
    with open(path, 'r') as f:
        object = yaml.load(f)
    return object


def initialize():
    """
    Creates the required directories and initializes config
    """
    print("Creating directory /etc/ldaptriggers/")
    Path(TRIGGERS_PATH).mkdir(parents=True, exist_ok=True)

    # Create config file
    print("The following prompts will configure /etc/ldaptriggers/config.yaml")
    config.ldap_uri = click.prompt('Enter ldap server uri', default='ldap://localhost')
    config.ldap_secret = click.prompt('Enter ldap server secret', default='/etc/ldap.secret')
    config.org = click.prompt('Enter ldap organization', default='dc=vc,dc=in,dc=tum,dc=de')
    config.admin = click.prompt('Enter admin', default='cn=admin,') + config.org
    config.people = click.prompt('Enter people', default='ou=people,') + config.org
    config.groups = click.prompt('Enter groups', default='ou=groups,') + config.org
    config.timeout = click.prompt('Enter sync time', default=60)
    config.save()

    # Create first ldap record
    sync = click.prompt('Do you want to sync with ldap now?', type=click.Choice(['Y', 'n']))
    if sync == 'Y':
        print("Synchronizing with ldap server...")
        people, groups = fetch_ldap()
        store_to_yaml(people, PEOPLE_PATH)
        store_to_yaml(groups, GROUPS_PATH)
