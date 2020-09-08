###########################################################
#
# Copyright (c) 2005, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ['ADAuthenticate', 'ADException']

import types, os, six

from pyasm.common import SecurityException, Config, Common
from pyasm.security import Authenticate, TacticAuthenticate, Login, LoginInGroup
from pyasm.search import Search

from pyasm.common import Environment

try:
    #from ad import ADConnect, ADLookup, ADException
    from .ad_connect import ADConnect
    from .ad_lookup import ADLookup
except ImportError:
    print("WARNING: cannot import Active Directory classes")
    pass

class ADException(Exception):
    pass

INSTALL_DIR = Environment.get_install_dir()
BASE_DIR = "%s/src/tactic/active_directory" % INSTALL_DIR

class ADAuthenticate(Authenticate):
    '''Test authenticate mechanism which caches user info'''

    def __init__(self):
        self.ad_exists = True
        if os.name != 'nt':
            self.ad_exists = False

        self.groups = set()

        self.data = {}
        self.tactic_groups = []


    def get_mode(self):
        return 'cache'


    def verify(self, login_name, password):
            
        if login_name.find("\\") != -1:
            domain, base_login_name = login_name.split("\\")
        else:
            base_login_name = login_name
            domain = None

        # confirm that there is a domain present if required
        require_domain = Config.get_value("active_directory", "require_domain")
        domain_component = Config.get_value("active_directory","domain_component")
        script_path = Config.get_value("active_directory","allow_script")
        
        if script_path:
            flag = False
            try:
                from tactic.command import PythonCmd
                from pyasm.command import Command
                kwargs = {'login' : login_name}
                cmd = PythonCmd(script_path=script_path, **kwargs)
                #flag = Command.execute_cmd(cmd)
                flag = cmd.execute()
            except Exception as e:
                print(e)
                raise
            if flag != True:
                return False  
        
        if require_domain == "true" and not domain:
            raise SecurityException("Domain Selection Required")



        # skip authentication if ad does not exist
        if not self.ad_exists:
            print("WARNING: Active directory does not exist ... skipping verify")
            return True

        ad_connect = ADConnect()
        ad_connect.set_user(base_login_name)
        ad_connect.set_password(password)
        info = ad_connect.lookup()
        try:
            lookup_domain = info[1]
        except:
            lookup_domain = ''
        # lookup domain takes prescedence
        if lookup_domain:
            domain = lookup_domain
            #ad_connect.set_domain(lookup_domain)
        elif domain:
            pass
            
            #ad_connect.set_domain(domain)
        domain = "%s%s"%(domain,domain_component)
        ad_connect.set_domain(domain)

        #ad_connect.set_user(base_login_name)
        #ad_connect.set_password(password)
        is_logged_in = ad_connect.logon()

        # preload data for further use later with original full login_name
        if is_logged_in:
            self.load_user_data(base_login_name, domain)
        else:
            # If AD authentication fails, attempt login via Tactic database+
            # (Only allow login for external users)
            login = Login.get_by_login(base_login_name)
            if login and login.get_value('location', no_exception=True) == 'external':
                auth_class = "pyasm.security.TacticAuthenticate"
                authenticate = Common.create_from_class_path(auth_class)  
                is_authenticated = authenticate.verify(base_login_name, password)
                if is_authenticated == True:
                    return True

        return is_logged_in


    def get_user_mapping(self):
        '''returns a dictionary of the mappings between AD attributes to
        login table attributes'''
        # NOTE: ensure this syncs up with the map in get_user_info() 
        # in ad_get_user_info.py
        attrs_map = {
            'dn':               'dn',
            'displayName':      'display_name',
            'name':             'name',
            'sn':               'last_name',
            'givenName':        'first_name',
            'mail':             'email',
            'telephoneNumber':  'phone_number',
            'department':       'department',
            'employeeID':       'employee_id',
            'sAMAccountName':   'sAMAccountName',
            # some extras
            'l':                'location',
            'title':            'title',
            'tacticLicenseType': 'license_type'
        }
        return attrs_map


    def get_group_mapping(self):
        group_attrs_map = {
            'dn':               'dn',
            'name':             'name',
        }
        return group_attrs_map


    def get_tactic_license_type(self):
        '''determines from AD what license a particular user is entitled
        to'''
        key = 'tacticLicenseType'
        licence_type = self.data.get(key)
        if not license_type:
            return False
        else:
            return True


    def get_default_license_type(self):
        license_type = Config.get_value("active_directory", "default_license_type")
        if not license_type:
            license_type = 'user'
        return license_type


    def get_default_groups(self):
        groups = Config.get_value("active_directory", "default_groups")
        if not groups:
            groups = []
        else:
            groups = groups.split("|")

        return groups



    def get_user_data(self, key=None):
        if key:
            return self.data.get(key)
        else:
            return self.data


    def load_user_data(self, login_name, domain=None):
        '''get user data from active directory'''

        # get all of the tactic groups
        self.tactic_groups = Search.eval("@SOBJECT(sthpw/login_group)")

        # get the mappings
        attrs_map = self.get_user_mapping()
        group_attrs_map = self.get_group_mapping()

        if self.ad_exists:
            self.data = self.get_info_from_ad(login_name, attrs_map, domain=domain)
        else:
            #group_path = "%s/AD_group_export.ldif" % BASE_DIR
            #self.group_data = self.get_info_from_file(login_name, group_attrs_map, group_path)
            path = "%s/AD_user_export.ldif" % BASE_DIR
            self.data = self.get_info_from_file(attrs_map, path)

        if not self.data.get('sAMAccountName'):
            raise SecurityException("Could not get info from Active Directory for login [%s]. You may have selected the wrong domain." % login_name)
        return self.data



    def add_user_info(self, login, password):
        ''' sets all the information about the user'''

        login_name = login.get_value("login")
        data = self.data


        # split up display name into first and last name
        display_name = data.get('display_name')
        if data.get('first_name') and data.get('last_name'):
            first_name = data.get('first_name')
            last_name = data.get('last_name')
        else:
            try:
                first_name, last_name = display_name.split(' ', 1)
                first_name = first_name.replace(",","")
                last_name = last_name.replace(",", "")
            except:
                first_name = display_name
                last_name = ''

        # alter so that it works for now
        data = {
            'first_name': first_name,
            'last_name': last_name,
            'email': data.get('email'),
            'phone_number': data.get('phone_number'),
            'license_type': data.get('license_type'),
            'display_name': data.get('display_name'),
            'department':   data.get('department')
        }

        from pyasm.search import Search
        columns = Search("sthpw/login").get_columns()

        for name, value in data.items():
            if value == None:
                continue
            if value == 'None':
                value = ''

            # only add values that are actually in the login object
            if name not in columns:
                print("WARNING: skipping [%s].  Does not exist in login" % name)
                continue

            login.set_value(name, value)


        handle_groups = Config.get_value("active_directory", "handle_groups")
        if handle_groups == "false":
            self.add_default_group(login)
        else:
            # add all of the groups
            self.add_group_info(login)



    def get_info_from_ad(self, login_name, attrs_map, domain=None):

        data = {}
        if login_name == 'admin':
            return data

        """
        if login_name.find("\\") != -1:
            domain, login_name = login_name.split("\\")
        else:
            domain = None
        """
        python = Config.get_value('services', 'python')
        if not python:
            python = 'python'

        try:
            # get the info from a separate process
            from subprocess import Popen, PIPE
            if domain:
                cmd = [python, "%s/ad_get_user_info.py" % BASE_DIR, '-d', domain, "-u", login_name]
            else:
                cmd = [python, "%s/ad_get_user_info.py" % BASE_DIR, "-u", login_name,]

            output = Popen( cmd, stdout=PIPE).communicate()[0]
            import StringIO
            output = StringIO.StringIO(output)
            data = self.get_info_from_file(attrs_map, output)
            
            # get the license type from active directory
            license_type = data.get('tacticLicenseType')
            if not license_type:

                # TEST!!!! for MMS
                # FIXME: this logic is questionable.
                # if the user has no defined groups in Active Directory, then
                # it should use the default license type.
                if not self.groups:
                    license_type = self.get_default_license_type()
                    data['license_type'] = license_type
                else:
                    data['license_type'] = "user"

        except ADException:
            raise SecurityException("Could not get info from Active Directory for login [%s]" % login_name)
        return data 





    def get_info_from_file(self, attrs_map, path):
        '''for testing purposes'''

        data = {}

        if isinstance(path, six.string_types):
            f = open(path, 'r')
        else:
            f = path


        lines = []
        error_flag = False
        error = ''

        for line in f:
            if line.startswith("ERROR") or line.startswith("WARNING"):
                error_flag = True
                error = line
                print(line)
                continue

            if error_flag:
                print(line)
                continue


            if line.strip() == '':
                continue

            if line.startswith(" "):
                line = line.strip()
                lines[-1].append(line)
            else:
                line = line.strip()
                lines.append([line])

        if error_flag:
            raise SecurityException(error)

                

        for line in lines:
            line = "".join(line)
            #print "info line: ", line
            name, value = line.split(": ", 1)

            if name == 'memberOf':
                self.handle_group(value)
                continue

            attr_name = attrs_map.get(name)
            #print name
            if not attr_name:
                continue
            data[attr_name] = value

        # get the license type from active directory
        license_type = data.get('license_type')
        if not license_type:

            # TEST!!!! for MMS
            # FIXME: this logic is questionable.
            # if the user has no defined groups in Active Directory, then
            # it should use the default license type.
            if not self.groups:
                license_type = self.get_default_license_type()
                data['license_type'] = license_type
            else:
                data['license_type'] = "user"

        return data




    def handle_group(self, value):
        
        # some values have commas in them.
        value = value.replace("\\,", "|||")
        parts = value.split(",")

        # only deal with part 1 for now
        part = parts[0]
        name, value = part.split("=")
        ad_group_name = value.replace("|||", ",")

        # provide the column which stores the ad group.
        columns = Search("sthpw/login_group").get_columns()
        group_dict = {}

        # optional ad_login_group can record the actual group name in AD
        if "ad_login_group" in columns:
            mapping_col = "ad_login_group"
            for x in self.tactic_groups:
                value = x.get_value(mapping_col)
                if value:
                    group_dict[value] = x

        mapping_col = "login_group"
        for x in self.tactic_groups:
            value = x.get_value(mapping_col)
            if value:
                group_dict[value] = x


        # make sure the groups from AD are in the defined tactic groups
        if ad_group_name in group_dict:
            self.groups.add(group_dict[ad_group_name])



    def add_group_info(self, user):
        '''add the user to a specified group'''
        if not self.groups:
            default_groups = self.get_default_groups()
            self.groups.update(default_groups)


        # add a group
        skipped_connects = user.remove_all_groups(except_list=self.groups)
        skipped_group_names = [ x.get_value('login_group') for x in skipped_connects ]
        for group in self.groups:
            #print "user: ", user.get_value("login")
            if not isinstance(group, basestring): 
                group_name = group.get_value('login_group')
            else:
                group_name = group
            #print "adding to: ", group_name
            if group_name in skipped_group_names:
                continue
            user.add_to_group(group)

    def add_default_group(self, user):
        '''add the user to the default group only if he is groupless'''
        default_groups = self.get_default_groups()
        user_name = user.get_login()
        login_in_groups = LoginInGroup.get_by_login_name(user_name)

        if not login_in_groups:
            for group in default_groups:
                print("adding to: ", group)
                user.add_to_group(group)


