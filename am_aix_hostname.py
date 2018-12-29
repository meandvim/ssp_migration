#!/usr/bin/env python
# -*- coding: utf-8 -*-


# For AIX

# For AIX
# Metro Info#{{{
# ----------------------------------------------------------------------------
#
# NAME:         am_aix_user.py
#
# Purpose:      Simple Metro AIX hostname operations: 
#               - check if hostname is correct 
#               - extract prefix: e.g i333
#               - extract numerical prefix: e.g 333
#               - determine server type by prefix
#               - determine the fqdn
#               = determine the alternative hostnames
#               
#
# Parameter:    see -h
#
# ----------------------------------------------------------------------------
#
# Author:       aldo@metrosystems.net
#
# Date:    30.04.2018  
#
# Disclaimer:   This program should be used for reference only. It has not been
#               submitted to any formal test and is distributed AS IS.
#
# ----------------------------------------------------------------------------
#
# Needed customization in case of porting this Script to other machines:
#
# ----------------------------------------------------------------------------
#
# Well known Bugs:
#               none, it is perfect ;-)
#
# ----------------------------------------------------------------------------
#
#  30.04.2018 v 1.00/history:
# 
#			  30.04.2018 v 1.0.0/Fist version
#
# ----------------------------------------------------------------------------
#
# ToDo:         Further tasks
#
# ----------------------------------------------------------------------------
#
#}}}


import amdisplay
import re
import socket


amd = amdisplay.AmDisplay()

class am_aix_hostname(object):# {{{

    """
     - get_local_fqnd() # Determine the local fqdn: i333.metro.dus.de

     - get_hostname() # Determine the AIX hostname. e.g. i333en0 

     - is_valid_hostname() # Determines if the hostname if valid

     - get_prefix() # extracting the prefix: e.g. i333

     - get numerical_prefix() # extracting the numerical prefix e.g. 333
    
     - get_os_type_by_hostname() # e.g. S, I, M

     - TODO:
     -get_fqdn() # Determines the fqdn
     -get_alternative_hostnames() # Determining the alternative hostnames
    """

    def __init__(self,verbose=False):
        """TODO: Not used at the moment. """

    

    def get_local_fqnd(self, verbose=False):# {{{
        # ixxxen0.metro.dus.de Retruns str: local_fqdn 
        """Retrieving the fqdn of the local server\
                I'm using the socket module for this action\
                Internal review is needed to determine if \
                using the fqdn is the right approach"""
        self.verbose = verbose
        local_fqdn = False

        try:
            local_fqdn=socket.getfqdn()
        except Exception as  e:
            
            if  verbose:
                amd.err_msg("Unable to retrieve the fqdn of this server",\
                        emsg_var=e ,\
                        call_admins=True, \
                        exit_code=1)
    
        else:
            if verbose:
                amd.ok_msg("The management fqdn of this server is:",local_fqdn)
            return local_fqdn

        return local_fqdn
# }}}
    def get_hostname(self,verbose=False):# {{{
        # ixxxen0: hostname
        """Retrieving the hostname of the local server
            It relies on get_local_fqnd()
            returns:str:hostname:False"""
        self.verbose = verbose
        hostname = False

        try:
            hostname = self.get_local_fqnd()
        except Exception as  e:
            
            if verbose:
                amd.err_msg("Unable to retrieve the hostnme of this server",\
                        emsg_var=e ,\
                        call_admins=True, \
                        exit_code=1)
    
        else:
            if verbose:
                amd.ok_msg("The hostname of this server is:",hostname)
            return hostname

        return hostname
# }}}
    def get_short_hostname(self,verbose=False):# {{{
        # ixxxen0: hostname
        """Retrieving the short hostname of the local server
            It relies on get_local_fqnd()
            returns:str:hostname:False"""
        self.verbose = verbose
        short_hostname = False

        try:
            hostname = self.get_local_fqnd()
        except Exception as  e:
            
            if verbose:
                amd.err_msg("Unable to retrieve the hostnme of this server",\
                        emsg_var=e ,\
                        call_admins=True, \
                        exit_code=1)
    
        else:
            short_hostname=hostname.split(".")[0]
#             print short_hostname
            if verbose:
                amd.ok_msg("The short  hostname of this server is:",
                    short_hostname)
            return short_hostname

        return hostname
# }}}
    def is_valid_hostname(self,hostname=False,verbose=False):# {{{
        """Checking if it's a valid hostname
            It relies on get_local_fqnd()
            usage: is_valid_hosname("hostname")
            usage: is_valid_hosname(verbose=True)
            returns:bool"""
        if not hostname:
            hostname=self.get_hostname()

        reg = re.compile('^[a-z][0-9][0-9][0-9]en0')
#         reg = re.compile('webdev')
        m = reg.match(hostname)
        if m:
           if verbose:
               amd.ok_msg("Determining hostname validity")
           return True
        else:
           return False
# }}}
    def get_prefix(self,hostname=False, verbose=False):# {{{
        # ixxxen0: hostname
        """Determining the prefix of the hosname: e.g. i333
            It relies on get_local_fqnd()
            usage: get_prefix()
            usage: get_prefix("i12334")

            returns:str:ixxx:False"""
       
        if not hostname:
            hostname=self.get_hostname()

        try:
           prefix=hostname[:4]
        except Exception as e:
           raise e
         
        if verbose:
            amd.ok_msg("Determining the prefix:", prefix)
    
        return prefix

# }}}
    def get_numerical_prefix(self,hostname=False, verbose=False):# {{{
        # ixxxen0: hostname
        """Determining the prefix of the hosname: e.g. i333
            It relies on get_local_fqnd()
            usage: get_numerical_prefix()
            usage: get_numerical_prefix("i12334")

            returns:str:222:False"""
       
        if not hostname:
            hostname=self.get_hostname()

        try:
           prefix=hostname[1:4]
        except Exception as e:
           raise e
         
        if verbose:
            amd.ok_msg("Determining the numerical prefix:", prefix)
    
        return prefix

# }}}
    def get_cluster_type(self,hostname=False, verbose=False):# {{{
        """Determining Cluster type based on hostname: e.g. S, I, G
            It relies on get_local_fqnd()
            usage: get_numerical_prefix()
            usage: get_numerical_prefix("i12334")

            returns:str:S,G,I:False"""
       
        if not hostname:
            hostname=self.get_hostname()

        try:
           cluster_type=hostname[0].capitalize()
        except Exception as e:
           raise e
         
        if verbose:
            amd.ok_msg("Determining the cluster Type:", cluster_type)
    
        return cluster_type

# }}}

# }}}
class am_aix_sap_hostname(object):# {{{

    """
     - SAP HOSTNAME  for non_sap use am_aix_hostname
      
     - get_local_fqnd() # Determine the local fqdn: s333.metro.dus.de

     - get_hostname() # Determine the AIX hostname. e.g. s333en0 

     - is_valid_hostname() # Determines if the hostname if valid

     - get_prefix() # extracting the prefix: e.g. s333

     - get numerical_prefix() # extracting the numerical prefix e.g. 333

     - TODO:
     -get_fqdn() # Determines the fqdn
     -get_alternative_hostnames() # Determining the alternative hostnames
    """

    def __init__(self,verbose=False):
        """TODO: Not used at the moment. """

    

    def get_local_fqnd(self, verbose=False):# {{{
        # sxxxen0.metro.dus.de Retruns str: local_fqdn 
        """Retrieving the fqdn of the local server\
                I'm using the socket module for this action\
                Internal review is needed to determine if \
                using the fqdn is the right approach"""
        self.verbose = verbose
        local_fqdn = False

        try:
            local_fqdn=socket.getfqdn()
        except Exception as  e:
            
            if  verbose:
                amd.err_msg("Unable to retrieve the fqdn of this server",\
                        emsg_var=e ,\
                        call_admins=True, \
                        exit_code=1)
    
        else:
            if verbose:
                amd.ok_msg("The management fqdn of this server is:",local_fqdn)
            return local_fqdn

        return local_fqdn
# }}}
    def get_hostname(self,verbose=False):# {{{
        # ixxxen0: hostname
        """Retrieving the hostname of the local server
            It relies on get_local_fqnd()
            returns:str:hostname:False"""
        self.verbose = verbose
        hostname = False

        try:
            hostname = self.get_local_fqnd()
        except Exception as  e:
            
            if verbose:
                amd.err_msg("Unable to retrieve the hostnme of this server",\
                        emsg_var=e ,\
                        call_admins=True, \
                        exit_code=1)
    
        else:
            if verbose:
                amd.ok_msg("The hostname of this server is:",hostname)
            return hostname

        return hostname
# }}}
    def is_valid_hostname(self,hostname=False,verbose=False):# {{{
        """Checking if it's a valid hostname
            It relies on get_local_fqnd()
            usage: is_valid_hosname("hostname")
            usage: is_valid_hosname(verbose=True)
            returns:bool"""
        if not hostname:
            hostname=self.get_hostname()

        reg = re.compile('^s[0-9][0-9][0-9]en0')
#         reg = re.compile('webdev')
        m = reg.match(hostname)
        if m:
           if verbose:
               amd.ok_msg("Determining SAP AIX hostname validity")
           return True
        else:
           amd.err_msg("Invalid AIX SAP hostname: ",\
                 hostname,\
                 call_admins=True,\
                 exit_code=4)
           return False
# }}}
    def get_prefix(self,hostname=False, verbose=False):# {{{
        # ixxxen0: hostname
        """Determining the prefix of the hosname: e.g. i333
            It relies on get_local_fqnd()
            usage: get_prefix()
            usage: get_prefix("i12334")

            returns:str:sxxx:False"""
       
        if not hostname:
            hostname=self.get_hostname()

        try:
           prefix=hostname[:4]
        except Exception as e:
           raise e
         
        if verbose:
            amd.ok_msg("Determining the prefix:", prefix)
    
        return prefix

# }}}
    def get_numerical_prefix(self,hostname=False, verbose=False):# {{{
        # ixxxen0: hostname
        """Determining the prefix of the hosname: e.g. i333
            It relies on get_local_fqnd()
            usage: get_numerical_prefix()
            usage: get_numerical_prefix("i12334")

            returns:str:222:False"""
       
        if not hostname:
            hostname=self.get_hostname()

        try:
           prefix=hostname[1:4]
        except Exception as e:
           raise e
         
        if verbose:
            amd.ok_msg("Determining the numerical prefix:", prefix)
    
        return prefix

# }}}

# }}}

def do_aix_hostname_prereq(verbose=False):# {{{
   """Performing standard aix hostname prerequisites:

   :verbose: spew verbose output"""

   amd.info_msg("   Performing general AIX hostname prerequisites.")
   hostname_obj=am_aix_hostname(verbose=verbose) 
   hostname_obj.get_local_fqnd(verbose=verbose)
   hostname_obj.get_hostname(verbose=verbose)
   hostname_obj.is_valid_hostname(verbose=verbose)
   hostname_obj.get_prefix(verbose=verbose)
   hostname_obj.get_numerical_prefix(verbose=verbose)
# }}}
def do_aix_sap_hostname_prereq(verbose=False):# {{{
   """Performing standard AIX SAP hostname prerequisites:

   :verbose: spew verbose output"""

   amd.info_msg("   Performing general AIX  SAP hostname prerequisites.")
   host_sap_obj=am_aix_sap_hostname(verbose=verbose) 
   host_sap_obj.get_local_fqnd(verbose=verbose)
   host_sap_obj.get_hostname(verbose=verbose)
   host_sap_obj.is_valid_hostname(verbose=verbose)
   host_sap_obj.get_prefix(verbose=verbose)
   host_sap_obj.get_numerical_prefix(verbose=verbose)
# }}}

# HERE IT GOES        
if __name__ == "__main__":    
  do_aix_hostname_prereq(True)  
  print
  do_aix_sap_hostname_prereq(True)  








