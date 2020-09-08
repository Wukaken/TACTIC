###########################################################
#
# Copyright (c) 2005-2009, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ['ADConnect']

import tacticenv

import os

from .ad_lookup import ADException


ERROR = ""
try:
    import win32security, pywintypes
    import active_directory
except ImportError as e:
    if os.name != 'nt':
        ERROR = "Active directory libraries only work on a Windows platform"
    else:
        ERROR = 'Cannot import Win32 modules,\n%s' %  str(e)

    
    


class ADConnect(object):
    
    def __init__(self):
        self.debug_flag= False
        self.domain=""
        self.username=""
        self.password=""

        if ERROR:
            raise ADException(ERROR)




    def set_user(self, username):
        self.username = username
        self.debug("Setting username to %s" % self.username)
        return True
    
    def set_password(self, password):
        self.password = password
        self.debug("Setting password to %s" % self.password)
        
    def set_domain(self, domain):
        self.domain = domain
        self.debug("Setting domain to %s" % self.domain)

    def set_debug(self, bool):
        self.debug_flag=True

    def set_ldap_string(self, ldapstring):
        self.ldap_string=ldapstring
        
    def debug(self, message):
        if self.debug_flag:
            print(message)

    def lookup(self):
        self.debug("Looking up info on %s." % (self.username)) 
        try: 
            account=win32security.LookupAccountName(None, self.username)
            return account
        except pywintypes.error as e:
            return False
    
    def logon(self):
        self.debug("Logging on %s to %s with %s." % (self.username, self.domain, self.password)) 
        try: 

             handle=win32security.LogonUser(self.username, self.domain, self.password,
                           win32security.LOGON32_LOGON_NETWORK,
                           win32security.LOGON32_PROVIDER_DEFAULT)

             # We're not going to use the handle, just seeing if we can get it.
             handle.Close()
             return True
        except pywintypes.error as e:
             # Because of the sheer number of Windows-specific errors that can
             # occur here, we have to assume any of them mean that the
             # credentials were not valid.
             print(e)
             return False

import sys, getopt

def usage():
    print("ADS credentials checker")
    print("Usage: ad_connect.py [Option]")
    print("Check for ADS connectivity")
    print("")
    print("-u <username>        username")
    print("-p <password>        password")
    print("-h, --help           Display this message, and exit")
    print("-a <domain>          Set domain")
    print("-c                   check credentials against server")
    print("-i                   lookup account info"      )
    print("-d                   Debug messages")
    print("")

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "u:p:a:hdci", ["help"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    #try:
    if len(opts) > 0:
        ads = ADConnect()
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                usage()
                sys.exit()
            elif opt == '-u':
                ads.set_user(arg)
            elif opt == '-p':
                ads.set_password(arg)
            elif opt == '-a':
                ads.set_domain(arg)
            elif opt == '-l':
                ads.set_logon(True)
            elif opt == '-d':
                ads.set_debug(True)
            elif opt == '-c':
                if ads.logon():
                    print("Successful logon")
                else:
                    print("Failed logon")
            elif opt == '-i':
                x=ads.lookup()
                print("SID:%s" % x[0])
                print("Domain:%s" % x[1])
            else:
                usage()
                sys.exit()
    else:
        print(("Try 'ad_connect.py -h' for more information."))

if __name__ == '__main__':
    main(sys.argv[1:])
