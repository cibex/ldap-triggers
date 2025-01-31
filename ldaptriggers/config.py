from pathlib import Path
import ruamel.yaml

from .params import CONFIG_PATH

yaml = ruamel.yaml.YAML()


class Config:

    def __init__(self):
        """
        ldap_uri: Ldap server uri
        ldap_secret: Where the ldap password is stored
        org: Directory
        admin: The admin user
        people: Users
        groups: Groups
        timeout: The wait time until next ldap server fetch
        """
        self.ldap_uri = 'ldap://localhost'
        self.ldap_secret = '/etc/ldap.secret'
        self.ldap_root_cert = '/etc/ldap_root_cert.crt'
        self.org = "dc=org,dc=company,dc=com"
        self.admin = "cn=admin," + self.org
        self.people = "ou=people," + self.org
        self.groups = "ou=groups," + self.org
        self.timeout = 60

        self.load()

    def save(self):
        """
        Stores the current configuration in CONFIG_PATH
        """
        with open(CONFIG_PATH, 'w') as f:
            yaml.dump(self, f)

    def load(self):
        """
        Loads the configuration stored in CONFIG_PATH
        """
        stored_config = Path(CONFIG_PATH)

        if stored_config.is_file():
            with open(CONFIG_PATH, 'r') as f:
                stored_config = yaml.load(f)

            self.ldap_uri = stored_config.ldap_uri
            self.ldap_secret = stored_config.ldap_secret
            self.ldap_root_cert = stored_config.ldap_root_cert
            self.org = stored_config.org
            self.admin = stored_config.admin
            self.people = stored_config.people
            self.groups = stored_config.groups
            self.timeout = stored_config.timeout


yaml.register_class(Config)

config = Config()
"""
config should be the only instance of this class. 
For accessing or modifying the configuration, config should be used.
"""