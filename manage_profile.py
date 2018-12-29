#!/usr/bin/env python
# -*- coding: utf-8 -*-
# For AIX
# Imports# {{{

import argparse, textwrap
import os, errno
import collections
import subprocess
import re
import inspect
import logging
import sys
import shutil
import json
import socket
import platform
import datetime
import fileinput
import time
from argparse import RawTextHelpFormatter


# Needed for the chk_initialization file: 
# if __name__ == '__main__':
sys.path.append("/usr/local/rootbin/Pythonlib/")
import am_aix_user
import am_aix_lvm
import amdisplay

main_rc = 0

# }}}

# For AIX
# Metro Info#{{{
# ----------------------------------------------------------------------------
#
# NAME:         manage_profile.py
#
# Purpose:      
#
# Parameter:    see -h
#
# ----------------------------------------------------------------------------
#
# Author:       aldo@metrosystems.net
# 				mircea.aldo@gmail.com
#
# Date:    12.09.2018  
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
#  12.09.2018 v 1.00/history:
# 
#			  12.09.2018 v 1.0.0/Fist version
#
# ----------------------------------------------------------------------------
#
# ToDo:         Further tasks
#
# ----------------------------------------------------------------------------
#
#}}}




# Initial parser
## Parser: I'm using ArgumentParser for this solution: # {{{

def check_positive(value):# {{{
    try:
       ivalue = int(value)
    except Exception as e:
       raise argparse.ArgumentTypeError( "%s: Please enter an integer" %value)
    if ivalue <= 0:
         raise argparse.ArgumentTypeError("%s Are you sure you want to look into the future ?\n\
               Please enter a positive integer" % value)
    return ivalue
# }}}

parser = argparse.ArgumentParser(
   description= """Profile management for the lpars which are to be migrated to
   prevent accidental activations pre,during and post-migration and to address
   the RMC connectivity problems. Basically, the source lpar, the one that
   should be migrated is activated into the OK prompt using a dummy profile
   which will release IP/SAN resources.

EXAMPLES: lpar s135en0 on Managed System  S5 and hmc lxsrvhmc0001
  List existing profiles:
    manage_profile.py -l -s s135en0 -M S5 -H lxsrvhmc0001

  Create a dummy profile:
    manage_profile.py -a -s s135en0 -M S5 -H lxsrvhmc0001

  Create a dummy profile named "my_dummy":
    manage_profile.py -a -n my_dummy -s s135en0 -M S5 -H lxsrvhmc0001

  Rename the "default" profile to "my_default":
    manage_profile.py -r -n default -N my_default -s s135en0 -M S5 -H lxsrvhmc0001

  Delete the "dummy_profile":
    manage_profile.py -d -s s135en0 -M S5 -H lxsrvhmc0001

  Delete a custom profile "dummy_profile_v1":
    manage_profile.py -d -n dummy_profile_v1 -s s135en0 -M S5 -H lxsrvhmc0001

  Restore the "default" profile. Works only for non custom profile names
    manage_profile.py -u  -s s135en0 -M S5 -H lxsrvhmc0001


  Activate the lpar using the dummy profile
    manage_profile.py -A  -s s135en0 -M S5 -H lxsrvhmc0001
        
  Activate the lpar using the default profile
    manage_profile.py -R  -s s135en0 -M S5 -H lxsrvhmc0001

  Save/backup the "default" profile. Works only for non custom profile names
    manage_profile.py -b -f /tmp/s135en0_prof -s s135en0 -M S5 -H lxsrvhmc0001"""

        ,formatter_class=argparse.RawTextHelpFormatter
        )

#              e.g. Collect live_node_conf , live_wwns_conf data from s303en0\
#  migratevm.py -q -1 s303en0 " 

# Adding the action mutually exclusive groups
action_group = parser.add_argument_group()


action_group.add_argument("-a","--add_dummy_profile",
        action="store_true",
        help="""Creates a dummy profile:
    Default name is: dummy_profile
    This action is needed to prevent accidental lpar activation 
    which will result in IP/WWNS conflicts. 
    The preexisting "default" profile will be renamed to "default_premigration"
    so that the rpower.sh will not activate it
   """)

action_group.add_argument("-u","--restore_default_profile",
        action="store_true",
        help="""Restores the initial default profile.
    When the lpar is activated using a dummy profile, the default profile
    is renamed to "dafault_premigration"
    This action restores its name back to: "default"
    """)


action_group.add_argument("-d","--delete_profile",
    action="store_true",
    help="""Deletes a profile: default="dummy_profile"
    """)

action_group.add_argument("-l","--list_profiles",
        action="store_true",
        help="""Lists all the profiles assigned to a partition
    """)


action_group.add_argument("-r","--rename_profile",
        action="store_true",
        help="""Renames a profile.
      """)

action_group.add_argument("-A","--activate_dummy_profile",
        action="store_true",
        help="""!!!! This will shutdown the lpar.
    Activates the lpar using a dummy profile
    This is the main use-case. Its purpose is to prevent accidental 
    lpar activation pre/during/post migration. If the migration went well,
    the lpar will be deleted, if errors were encounted during the migration, 
    the source lpar can easily be reactivated using its initial profile,
    by using the -R flag which will delete the dummy profile, rename the 
    "default_premigration" profile to "default" and activate the lpar
    """)


action_group.add_argument("-U","--activate_default_profile",
        action="store_true",
        help="""Activates the lpar using the default profile.
    Essentially, this is a rollback mechanism which ensures a rapid service
    reactivation in case of migration failures. Please ensure the target lpar
    is deactivated before using this option""")


action_group.add_argument("-Z","--deactivate_lpar",
        action="store_true",
        help="""Deactivate/Shutdonw the lpar
    """)

action_group.add_argument("-n","--profile_name",
        action="store",
        help="""The name of the partition profile
    Default name is: dummy_profile
    Please refrain from using names with special characters 
    """)

action_group.add_argument("-N","--new_profile_name",
        action="store",
        help="""The name of the new partition profile
    Default name is: default_premigration
    Please refrain from using names with special characters 
    """)


action_group.add_argument("-b","--backup_profile",
        action="store_true",
        help="""dev: Save the lpar profile locally
    """)


action_group.add_argument("-f","--filename",
        action="store",
        help="""Specify the filename of the backup profile file
    """)


# Adding the required parameters
required_group=parser.add_argument_group("Required arguments")
required_group.add_argument("-s","--source_lpar",
        action="store",
        help="the name of the source lpar. e.g. s303en0",
        required=True)

required_group.add_argument("-M","--destination_managed_system",
        action="store",
        help="The name of the destination Managed System: e.g. S04",
        required=True)


required_group.add_argument("-H","--hmc",
        action="store",
        help="The name of the HMC used: e.g.:lxsrvhmc0001", 
        required=True)



# Adding the -v/-q mutually exclusive group
verbose_group=parser.add_mutually_exclusive_group()
verbose_group.add_argument("-v","--verbose",
        action="count",
        help="Show what is going on")



# Adding the -f/--force group
force_group=parser.add_mutually_exclusive_group()
force_group.add_argument("-F","--FORCE",
        action="store_true",
        help="Force a specific operation")



# Parsing all the arguments
args=parser.parse_args()
# args_help=parser.print_help()

# }}}

# Display module initialization 
amd=amdisplay.AmDisplay()

## Global variables: # {{{

amux = am_aix_user.am_aix_user()    # AIX User operations

# }}}
# CLASSES# {{{
class amgi():# AIX Metro  {{{
    """AIX Metro class\
        Used to retrieve lpar info such as: 
            Funktion:
            Criticality"""
    
    # Class Variables: 
    MGI_FILE="/etc/mgi_config"
    STATUS_TYPE=["Production","Unused", "prod","preprod","dev","development"]
    ENV_TYPE_LIST=["Prod",
         "PreProd",
         "Dev",
         "QA",
         "Offline"]

    def __init__(self,verbose=False):# {{{
        """docstring for __init__"""
        self.verbose=verbose
    # }}}
    def is_MGI_FILE(self,local_verbose=False): # Return : True of False# {{{
        """Checking if the MGI_FILE is present on the system\
            It will generate an error message if file is not found\
            It will return: True or False"""
        self.local_verbose=local_verbose

        if self.local_verbose:
            ok_msg("Checking if /etc/mgi_file exists.")

        if not os.path.isfile(self.MGI_FILE):
            err_msg("The /etc/mgi_config file does not exist.",\
                    emsg_var=False,\
                    call_admins=[False,False],\
                    local_exit=True)
        else:
            return os.path.isfile(self.MGI_FILE)
    # }}}
    def get_status(self):# returns str: status{{{
        """Retrieving the Funktion name from the /etc/mgi_file"""
        # Checking if mgi_file exists:
        is_mgi_file=self.is_MGI_FILE()
        try:
            file = open(self.MGI_FILE)
        except Exception as e:
            raise e
        else:
            is_status_line=False
            for line in file:
                if "Status" in line:
                    # print line
                    is_status_line=True
                    break

            if is_status_line:
                #print "Parsing the Status line to extract the env type"
                for env in self.STATUS_TYPE:
                    if env in line:
                        status = env
                        break
                    else:
                        status = "undefined"
            file.close()
        return status 
    # }}}
    def get_funktion(self):# returns str: Funktion: line{{{
        """Retrieving the Funktion line from the /etc/mgi_file
           e.g: MMS-Store MCC France Prod VI """
                
        # Checking if mgi_file exists:
        is_mgi_file=self.is_MGI_FILE()
        try:
            file = open(self.MGI_FILE)
        except Exception as e:
            raise e
        else:
        
            funktion_line=False
            for line in file:
                if "Funktion" in line:
                    # print line
                    funktion_line=line
                    break

            file.close()
        return funktion_line
    # }}}
    def get_env_type(self):# returns str: env_type .e.g prod{{{
       """Retrieve the env_type of a server .e.g prod
       from the funktion line: get_funktion()
       e.g: Prod, PreProd, Dev"""

       # Rertrieving the Funcktion line
       funktion_line = self.get_funktion()

       env_type = "offline"
       for env_type in self.ENV_TYPE_LIST:
           p = re.compile(r'\b{}\b'.format(env_type),re.IGNORECASE)
           m = p.search(funktion_line)
           if m:
              env_type = env_type
              return env_type
              break

       return env_type


    # }}}
    def get_iron(self):# returns str: Blech e.g I4: {{{
        """Retrieving the Managed System from /etc/mgi_config
           e.g: I4"""
                
        # Checking if mgi_file exists:
        is_mgi_file=self.is_MGI_FILE()
        
        try:
            file = open(self.MGI_FILE)
        except Exception as e:
            raise e
        else:
        
            Iron=False
            for line in file:
                if "Blech" in line:
                    # print line
                    Blech_line=line
                    # Retrieving the Blech: e.g. I4
                    Iron=Blech_line.split()[1].strip()
                    break
            file.close()

        return Iron 
    # }}}

    def get_service_hostname(self):# returns str: service_hostname e.g i133serv: {{{
        """Retrieving the service hostname from /etc/mgi_config
           e.g: i33serv"""
                
        # Checking if mgi_file exists:
        is_mgi_file=self.is_MGI_FILE()
        
        try:
            file = open(self.MGI_FILE)
        except Exception as e:
            raise e
        else:
        
            service_line=False
            for line in file:
                if "Service" in line:
                    # print line
                    service_line=line
                    # Retrieving the service hostname: e.g. i133serv
                    service_hostname=service_line.split()[1].strip()
                    break
            file.close()

        return service_hostname
    # }}}
    def get_service_IP(self,quit=False):# returns str (IP): service_IP e.g i133serv: {{{
        """Retrieving service_IP address associate with the service_hostname
           e.g: i33serv"""
                
        # Retrieving the service_hostname by calling get_service_hostname()
        service_hostname=self.get_service_hostname()
        
        # Retrieving the service_IP address:
        try:
            service_IP = socket.gethostbyname(service_hostname)
            return service_IP
        except Exception as e:
            err_msg("Unable to retrieve the service IP address.")
            raise e

    # }}}
    def get_service_fqdn(self,quit=False):# returns service fqdn or FALSE: {{{
        """Retrieving the service fqdn based on the  service_IP address
           e.g: i33serv"""
                
        # Retrieving the service_hostname by calling get_service_hostname()
        service_IP=self.get_service_IP()
        service_hostname =  False       # Assuming It cannot be retrieved\
                                        # a check is needed 
        
        unix_cmd = ("nslookup "\
               "-timeout=5 "\
               "{}"\
               ).format(service_IP) 
#         print ("Unix_cmd is: {} : ").format(unix_cmd) # FOR TESTING

        p = subprocess.Popen(unix_cmd,\
                shell=True, stdout=subprocess.PIPE,\
                stderr=subprocess.STDOUT)
        rc = p.wait()
        output_list=p.stdout.readlines()
        

        if self.verbose == 2:
            print "# unix_cmd is :{}".format(unix_cmd)     ##-- FOR_TESTING --##

        if rc!=0:           
            # unix_cmd has failed
            if self.verbose:
                err_msg("Unable to retrieve the service fqdn.\n"\
                        "    Please ensure that it is properly configured\n"\
                        "    e.g. i333serv.metro-dus.de", \
                        call_admins=[False,False])
            return service_hostname

        elif rc==0:         
            # unix_cmd executed successfully  
            # Parsing the output to retrieve the hostname line
            # 95.52.243.10.in-addr.arpa       name = i333serv.metro-dus.de.

            for i in output_list:
                if "name" in i:
                    return i.split("=")[1].strip()[:-1]

        # }}}
    def get_omd_criticality(self): # Compiling the OMD criticality  {{{
        """Determining  the OMD criticality based on the environment type
        generated by the get_env_type method. There are 4 OMD criticality
        fields: [prod, qa, test, offline]. They are matched as follows: 
        OMD     env_type
        prod    prod, production
        qa      preproduction
        test    dev
        offline offline
        "id": "criticality",
                "values": [
                    "Prod",
                    "PP",
                    "QA",
                    "Dev",
                    "Offline"
 
        """


        # Determining the env_type:
        env_type = self.get_env_type()

        # Determining criticality based on env_type
        criticality = "Offline"     # Assuming offline 
        if env_type == "Prod" or env_type == "production":
            criticality = "Prod"
            return criticality
        elif env_type == "PreProd" or env_type == "preproduction":
            criticality = "PP"
            return criticality
        elif env_type == "QA":
            criticality = env_type
            return criticality
        elif env_type == "Dev" or env_type == "Development":
            criticality = "Dev"
            return criticality
        else:
            return criticality

        # }}}


# TODO# {{{
# get_iron
# get_domain
# get_PscNumber
# }}}




# }}}
# }}}



# See IF YOU CAN REMOVE
# See IF YOU CAN REMOVE# {{{

# FUNCTIONS
   # PREPARE THE ENVIRONMENT


# TARGET LPAR PROCESSING
# LPAR
def get_template(verbose=False, silent=False, quit=False ): # {{{
    """Templating"""

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])
      

    # Start the validation process
    if verbose and not silent:
        amd.ok_msg("   >> Starting :")


    if verbose >= 1 and not silent:
        amd.ok_msg("   >> Configuration")



# }}}
def get_domain(verbose=False, silent=False, quit=False ): # {{{
    """Determinig the domain of the host/lpar"""

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])
      

    # Starting the process 
    if verbose and not silent:
        amd.ok_msg("   >> Retrieving the domain name :")

    opt1 = args.source_lpar
    unix_cmd=("host"\
            " {}"\
            ).format(opt1)
    
    if verbose >= 2 and not silent:
       amd.info_msg("  unix_cmd is: ", unix_cmd)
    
    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
    
        # Unix_cmd has failed
    if rc!=0:
       if quit:
           amd.err_msg("Unable to retrive the domain name",
                   exit_code=17)
       else:
           return False
    
        # Unix_cmd executed successfully
    elif rc==0:
       for line in p.stdout:
           if "Aliases" in line:
               domain = line.split(" ")[0].strip()
               break

    if domain:
        if verbose >= 1 and not silent:
            amd.ok_msg("   >> Domain name is:", domain)
        return domain
    else:
       if quit:
           amd.err_msg("Unable to retrive the domain name",
                   exit_code=17)
       return False


# }}}

# TARGET MS / BLECH
def is_target_ms(verbose=False, silent=False, quit=False ): # {{{
    """Checks if the Target MS exists or it is defined on the NIM"""

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])
      

    # Starting the process 
    if verbose and not silent:
        amd.ok_msg("   >> Checking if the Destination MS exits/is configured")

    opt1 = args.destination_managed_system
    unix_cmd=("lsnim "\
            " {}"\
            ).format(opt1)
    
    if verbose >= 2 and not silent:
       amd.info_msg("  unix_cmd is: ", unix_cmd)

    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
    is_target_ms = False
        # Unix_cmd has failed
    if rc!=0:
       if quit:
           amd.err_msg("Unable to determine if target MS exists",
                   exit_code=19)
       else:
         return is_target_ms
    
        # Unix_cmd executed successfully
    elif rc==0:
       if verbose >= 1 and not silent:
          amd.ok_msg("   >> Target MS is defined in the NIM env.")
       is_target_ms = True

    return is_target_ms


# }}}
def get_target_ms_serial(verbose=False, silent=False, quit=False ): # {{{
    """ Determines the serial number of the targert managed system"""

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])
      


    # Checking if the target MS exists/is defined in the NIM server
    is_target_ms(verbose=args.verbose, quit=True)


    # Starting the process 
    if verbose and not silent:
        amd.ok_msg("   >> Retrieving the serial number of the Managed System:")

    opt1 = args.destination_managed_system
    unix_cmd=("lsnim -a serial "\
            " {}"\
            ).format(opt1)
    
    if verbose >= 2 and not silent:
       amd.info_msg("  unix_cmd is: ", unix_cmd)

    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
    serial = False    
        # Unix_cmd has failed
    if rc!=0:
       if quit:
           amd.err_msg("Unable to retrieve the serial of the MS",
                   exit_code=18)
       else:
           return False
    
        # Unix_cmd executed successfully
    elif rc==0:
       for line in p.stdout:
           if "serial" in line:
               serial = line.split("=")[1].strip()
               break

    if serial:
        if verbose >= 1 and not silent:
            amd.ok_msg("   >> Target MS serial is: ", serial)
        return serial
    else:
       if quit:
           amd.err_msg("Unable to retrieve the Target Managed System serial nr.",
                   exit_code=18)
       return False


# }}}

# HMC -> LPAR
def is_hmc_accesible(host,user="hscroot", verbose=False, silent=False, quit=False ): # {{{
    """Checking if a host is accessible over ssh"""

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])

    is_ssh_accesible(host,
            user,
            verbose=args.verbose,
            quit=True)

# }}}
def is_lpar_in_hmc(hmc, ms, lpar_name, verbose=False, silent=False, quit=False, do_prereq=False ): # {{{
    """Determines if the lpar is configured in HMC/MS: -> bool
    hmc:    Target HMC name
    ms:     Target Managed System
    lpar_name: The name of the lpar: e.g. s134en0"""

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])
      

    if do_prereq:
        # Checking if the target MS exists/is defined in the NIM server
        is_target_ms(verbose=args.verbose, quit=True)

        # Checking if hmc is accessible
        is_hmc_accesible(args.hmc,
                user="hscroot",
                verbose=args.verbose,
                silent=True,
                quit=True)


    # Starting the process 
    if verbose and not silent:
        amd.ok_msg("   >> Checking if the lpar is already defined/configured\
in the hmc/MS:")

    # lssyscfg -r lpar -m S04 --filter "lpar_names=s134en0"


    user = "hscroot"
    opt1 = "lssyscfg -r lpar -m "
    opt2 = " --filter \"lpar_names={}\"".format(lpar_name)
    unix_cmd=("ssh "\
            "{}"\
            "@{} "\
            "{}"\
            "{}"\
            " {}"\
            ).format(user,hmc, opt1, ms, opt2)
    
    if verbose >= 2 and not silent:
       amd.info_msg("  unix_cmd is: ", unix_cmd)

    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
    is_lpar = False    
        # Unix_cmd has failed
    if rc!=0:
        for line in p.stdout:
           if "HSCL8012" in line:
               return is_lpar
           


    
        # Unix_cmd executed successfully
    elif rc==0:
       is_lpar = True

       if verbose >= 2 and not silent:
            for line in p.stdout:
                print line
       if verbose and not silent:
          amd.ok_msg("   >> The LPAR:",args.source_lpar,
                "is already defined in the HMC on MS:", ms)

       return is_lpar




#  }}}
def get_lpar_id(hmc, ms, lpar_name, verbose=False, silent=False, quit=False, do_prereq=False ): # {{{
    """Determines the  LPAR ID available on the MS -> int: lpar_id
    hmc:    Target HMC name
    ms:     Target Managed System
    lpar_name: The name of the lpar: e.g. s134en0
    do_prereq: Check if HMC is accesible, if MS exists"""

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])
      

    if do_prereq:
        # Checking if the target MS exists/is defined in the NIM server
        is_target_ms(verbose=args.verbose, quit=True)

        # Checking if hmc is accessible
        is_hmc_accesible(args.hmc,
                user="hscroot",
                verbose=args.verbose,
                silent=True,
                quit=True)



    # Starting the process 
    if verbose and not silent:
        amd.ok_msg("   >> Retrieving LPAR ID:")

    # lssyscfg -r lpar -m S04 --filter "lpar_names=s134en0" -F "lpar_id"


    user = "hscroot"
    opt1 = "lssyscfg -r lpar -m "
    opt2 = " --filter \"lpar_names={}\"".format(lpar_name)
    opt3 = "-F \"lpar_id\""
    unix_cmd=("ssh "\
            "{}"\
            "@{} "\
            "{}"\
            "{}"\
            "{}"\
            " {}"\
            ).format(user,hmc, opt1, ms, opt2, opt3)
    
    if verbose >= 2 and not silent:
       amd.info_msg("  unix_cmd is: ", unix_cmd)

    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
    lpar_id = False    
        # Unix_cmd has failed
    if rc!=0:
       if quit:
           amd.err_msg("Unable to determine the  LPAR ID",
                   exit_code=21)
       else:
           return False
    
        # Unix_cmd executed successfully
    elif rc==0:
       id_list=[]
       for line in p.stdout:
           id_list.append(line[0].strip())


    lpar_id = int(id_list[0])
    if not  isinstance(lpar_id, int):
       amd.err_msg("Unable to determine the PAR ID", exit_code=22)
    else:
      if verbose and not silent:
         amd.ok_msg("   >> The  LPAR ID of:",
                 lpar_name,
                 "is:",
                 lpar_id)
      return lpar_id




#  }}}
def get_next_lpar_id(hmc, ms, verbose=False, silent=False, quit=False, do_prereq=False ): # {{{
    """Determines the next LPAR ID available on the MS -> int next_lpar_id
    hmc:    Target HMC name
    ms:     Target Managed System
    do_prereq: Check if HMC is accesible, if MS exists"""

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])
      

    if do_prereq:
        # Checking if the target MS exists/is defined in the NIM server
        is_target_ms(verbose=args.verbose, quit=True)

        # Checking if hmc is accessible
        is_hmc_accesible(args.hmc,
                user="hscroot",
                verbose=args.verbose,
                silent=True,
                quit=True)


    # Starting the process 
    if verbose and not silent:
        amd.ok_msg("   >> Retrieving the next available LPAR ID:")

    # unix_cmd: ssh hscroot@hmc lssyscfg -r lpar -m ms -F "lpar_id, name"

    user = "hscroot"
    opt1 = "lssyscfg -r lpar -m "
    opt2 = "-F \"lpar_id,name\""
    unix_cmd=("ssh "\
            "{}"\
            "@{} "\
            "{}"\
            "{}"\
            " {}"\
            ).format(user,hmc, opt1, ms, opt2)
    
    if verbose >= 2 and not silent:
       amd.info_msg("  unix_cmd is: ", unix_cmd)

    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
    lpar_id = False    
        # Unix_cmd has failed
    if rc!=0:
       if quit:
           amd.err_msg("Unable to determine the next LPAR ID",
                   exit_code=21)
       else:
           return False
    
        # Unix_cmd executed successfully
    elif rc==0:
       id_list=[]
       for line in p.stdout:
           if verbose >= 2 and not silent:
               amd.info_msg("   >> Exiting partitions:", line.strip())

           lp_id=line.split(",",1)
           id_list.append(lp_id[0])

           int_id_list=map(int,id_list)
           max_id=max(int_id_list)
    try:
        next_id=max_id+1
    except Exception as e:
          amd.err_msg("Unable to determine the next LPAR ID", exit_code=21)

    if verbose and not silent:
        amd.ok_msg("   >> The next available LPAR ID is:", next_id)
    return next_id
# }}}


# HMC -> VIOS
def get_vio_a_hostname(verbose=False,silent=False): # {{{
    """Returns the hostname of the vios_A -> str:"""

    l_ms = args.destination_managed_system.lower()
    vios_a_hostname = l_ms+"vp1en0"

    if verbose >= 1 and not silent:
       amd.ok_msg("   >> VIOS_A hostname is: ", vios_a_hostname)


    return vios_a_hostname
# }}}
def get_vio_b_hostname(verbose=False,silent=False): # {{{
    """Returns the hostname of the vios_A -> str:"""

    l_ms = args.destination_managed_system.lower()
    vios_a_hostname = l_ms+"vp2en0"

    if verbose >= 1 and not silent:
       amd.ok_msg("   >> VIOS_B hostname is: ", vios_a_hostname)


    return vios_a_hostname
# }}}
def get_vios_id(hmc, ms, vios_name, verbose=False, silent=False, quit=False, do_prereq=False ): # {{{
    """Determines the  VIOS ID available on the MS -> int: lpar_id
    hmc:    Target HMC name
    ms:     Target Managed System
    vios_name: The name of the lpar: e.g. s134en0
    do_prereq: Check if HMC is accesible, if MS exists"""

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])
      

    if do_prereq:
        # Checking if the target MS exists/is defined in the NIM server
        is_target_ms(verbose=args.verbose, quit=True)

        # Checking if hmc is accessible
        is_hmc_accesible(args.hmc,
                user="hscroot",
                verbose=args.verbose,
                silent=True,
                quit=True)

    # lssyscfg -r lpar -m S04 --filter "vios_names=s04vp1en0" -F "lpar_id"

    user = "hscroot"
    opt1 = "lssyscfg -r lpar -m "
    opt2 = " --filter \"lpar_names={}\"".format(vios_name)
    opt3 = "-F \"lpar_id\""
    unix_cmd=("ssh "\
            "{}"\
            "@{} "\
            "{}"\
            "{}"\
            "{}"\
            " {}"\
            ).format(user,hmc, opt1, ms, opt2, opt3)
    
    if verbose >= 2 and not silent:
       amd.info_msg("  unix_cmd is: ", unix_cmd)

    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
        # Unix_cmd has failed
    if rc!=0:
       if quit:
           amd.err_msg("Unable to determine the  VIOS ID",
                   exit_code=23)
       else:
           return False
    
        # Unix_cmd executed successfully
    elif rc==0:
       id_list=[]
       for line in p.stdout:
           id_list.append(line[0].strip())


    vios_id = int(id_list[0])
    if not  isinstance(vios_id, int):
       amd.err_msg("Unable to determine the VIOS ID", exit_code=23)
    else:
      if verbose and not silent:
         amd.ok_msg("   >> The  VIOS ID of:",
                 vios_name,
                 "is:",
                 vios_id)
    return vios_id

#  }}}
def is_ssh_accesible(host, user="root", verbose=False, silent=False, quit=False ): # {{{
    """Checking if a host is accessible over ssh"""

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])

    # Starting the process 
    if verbose and not silent:
        amd.ok_msg("   >> Checking if:", host, ": is accessible over ssh")
    
    unix_cmd=("ssh "\
            " {}@"\
            "{}"\
            " exit"\
            ).format(user, host)
    
    if verbose >= 2 and not silent:
       amd.info_msg("  unix_cmd is: ", unix_cmd)

    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
        # Unix_cmd has failed
    if rc!=0:
       if quit:
           amd.err_msg("   >> Host:",host,"cannot be reached over ssh", exit_code=20)
       else:
           return False
    
        # Unix_cmd executed successfully
    elif rc==0:
       if verbose and not silent:
         amd.ok_msg("   >> Host:",host,"is reachable over ssh")
       return True


# }}}
def get_eth_slot_ids(hmc, ms, verbose=False, silent=False, quit=False, do_prereq=False): # {{{
    """Determines the eth slot ids -> list: eth_slot_ids
    hmc:    Target HMC name
    ms:     Target Managed System
    do_prereq: Check if HMC is accessible, if MS exists"""

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])
      

    if do_prereq:
        # Checking if the target MS exists/is defined in the NIM server
        is_target_ms(verbose=args.verbose, quit=True)

        # Checking if hmc is accessible
        is_hmc_accesible(args.hmc,
                user="hscroot",
                verbose=args.verbose,
                silent=True,
                quit=True)


    # Starting the process 
    if verbose and not silent:
        amd.ok_msg("   >> Retrieving the eth slots IDs:")

    # unix_cmd: ssh hscroot@hmc lssyscfg -r lpar -m ms -F "lpar_id, name"

    user = "hscroot"
    opt1 = "lshwres -r virtualio --rsubtype eth -m "
    opt2 = "--level lpar -F slot_num"
    unix_cmd=("ssh "\
            "{}"\
            "@{} "\
            "{}"\
            "{}"\
            " {}"\
            ).format(user,hmc, opt1, ms, opt2)
    
    eth_slot_ids_list=[]
    non_uniq_list=[]

    if verbose >= 2 and not silent:
       amd.info_msg("  unix_cmd is: ", unix_cmd)

    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
    lpar_id = False    
        # Unix_cmd has failed
    if rc!=0:
       if quit:
           amd.err_msg("Unable to determine the eth SLOT IDs",
                   exit_code=23)
       else:
           return False
    
        # Unix_cmd executed successfully
    elif rc==0:
        for line in p.stdout:
           non_uniq_list.append(line.strip())

        eth_slot_ids_list = list(set(non_uniq_list))
        eth_slot_ids_list =  [ int(x) for x in eth_slot_ids_list ]
        eth_slot_ids_list.sort()
        if verbose >= 2 and not silent:
           amd.info_msg("   >> eth IDs", eth_slot_ids_list )

    if verbose  and not silent:
        amd.ok_msg("   >> Retrieved the eth slots IDs:")

    return eth_slot_ids_list
# }}}
def get_scsi_slot_ids(hmc, ms, verbose=False, silent=False, quit=False, do_prereq=False): # {{{
    """Determines the scsi slot ids -> list: scsi_slot_ids
    hmc:    Target HMC name
    ms:     Target Managed System
    do_prereq: Check if HMC is accessible, if MS exists"""

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])
      

    if do_prereq:
        # Checking if the target MS exists/is defined in the NIM server
        is_target_ms(verbose=args.verbose, quit=True)

        # Checking if hmc is accessible
        is_hmc_accesible(args.hmc,
                user="hscroot",
                verbose=args.verbose,
                silent=True,
                quit=True)


    # Starting the process 
    if verbose and not silent:
        amd.ok_msg("   >> Retrieving the scsi slots IDs:")

    # unix_cmd: ssh hscroot@hmc lssyscfg -r lpar -m ms -F "lpar_id, name"

    user = "hscroot"
    opt1 = "lshwres -r virtualio --rsubtype scsi -m "
    opt2 = "--level lpar -F slot_num"
    unix_cmd=("ssh "\
            "{}"\
            "@{} "\
            "{}"\
            "{}"\
            " {}"\
            ).format(user,hmc, opt1, ms, opt2)
    
    scsi_slot_ids_list=[]
    non_uniq_list=[]

    if verbose >= 2 and not silent:
       amd.info_msg("  unix_cmd is: ", unix_cmd)

    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
    lpar_id = False    
        # Unix_cmd has failed
    if rc!=0:
       if quit:
           amd.err_msg("Unable to determine the scsi SLOT IDs",
                   exit_code=23)
       else:
           return False
    
        # Unix_cmd executed successfully
    elif rc==0:
        for line in p.stdout:
            if "No results were found" in line:
                # No results means that this is the first lpar. 
                # I'm adding 9 into this list so that the mapping can begin from 10
                non_uniq_list.append(9)
            else:
               non_uniq_list.append(line.strip())

        scsi_slot_ids_list = list(set(non_uniq_list))
        scsi_slot_ids_list =  [ int(x) for x in scsi_slot_ids_list ]
        scsi_slot_ids_list.sort()
        if verbose >= 2 and not silent:
           amd.info_msg("   >> SCSI IDs", scsi_slot_ids_list )

    if verbose and not silent:
        amd.ok_msg("   >> Retrieved the scsi slots IDs:")

    return scsi_slot_ids_list
# }}}
def get_fc_slot_ids(hmc, ms, verbose=False, silent=False, quit=False, do_prereq=False): # {{{
    """Determines the FC slot ids -> list: fc_slot_ids
    hmc:    Target HMC name
    ms:     Target Managed System
    do_prereq: Check if HMC is accessible, if MS exists"""

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])
      

    if do_prereq:
        # Checking if the target MS exists/is defined in the NIM server
        is_target_ms(verbose=args.verbose, quit=True)

        # Checking if hmc is accessible
        is_hmc_accesible(args.hmc,
                user="hscroot",
                verbose=args.verbose,
                silent=True,
                quit=True)


    # Starting the process 
    if verbose and not silent:
        amd.ok_msg("   >> Retrieving the FC slots IDs:")

    # unix_cmd: ssh hscroot@hmc lssyscfg -r lpar -m ms -F "lpar_id, name"

    user = "hscroot"
    opt1 = "lshwres -r virtualio --rsubtype fc -m "
    opt2 = "--level lpar -F slot_num"
    unix_cmd=("ssh "\
            "{}"\
            "@{} "\
            "{}"\
            "{}"\
            " {}"\
            ).format(user,hmc, opt1, ms, opt2)
    
    fc_slot_ids_list=[]
    non_uniq_list=[]

    if verbose >= 2 and not silent:
       amd.info_msg("  unix_cmd is: ", unix_cmd)

    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
    lpar_id = False    
        # Unix_cmd has failed
    if rc!=0:
       if quit:
           amd.err_msg("Unable to determine the scsi SLOT IDs",
                   exit_code=23)
       else:
           return False
    
        # Unix_cmd executed successfully
    elif rc==0:
        for line in p.stdout:
            if "No results were found" in line:
                # No results means that this is the first lpar. 
                # I'm adding 9 into this list so that the mapping can begin from 10
                non_uniq_list.append(9)
            else:
               non_uniq_list.append(line.strip())

        fc_slot_ids_list = list(set(non_uniq_list))
        fc_slot_ids_list =  [ int(x) for x in fc_slot_ids_list ]
        fc_slot_ids_list.sort()
        if verbose >= 2 and not silent:
           amd.info_msg("   >> The FC  IDs", fc_slot_ids_list )

    if verbose and not silent:
        amd.ok_msg("   >> Retrieved the FC slots IDs:")

    return fc_slot_ids_list
# }}}
def get_next_slot_id(eth_list, scsi_list, fc_list, verbose=False, silent=False, quit=False, do_prereq=False): # {{{
    """Determines the last slot id -> int: last_slot_id
    hmc:    Target HMC name
    ms:     Target Managed System
    do_prereq: Check if HMC is accessible, if MS exists"""

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])
      

    if do_prereq:
        # Checking if the target MS exists/is defined in the NIM server
        is_target_ms(verbose=args.verbose, quit=True)

        # Checking if hmc is accessible
        is_hmc_accesible(args.hmc,
                user="hscroot",
                verbose=args.verbose,
                silent=True,
                quit=True)

    all_slot_ids_list=[]

    all_slot_ids_list += eth_list
    all_slot_ids_list += scsi_list
    all_slot_ids_list += fc_list

    all_slot_ids_list =  [ int(x) for x in all_slot_ids_list ]
    all_slot_ids_list.sort(reverse=True)
    next_slot_id =  all_slot_ids_list[0]+1



    # Starting the process 
    if verbose and not silent:
        amd.ok_msg("   >> Determining the next available slot ID:")


    if verbose and not silent:
        amd.ok_msg("   >> Next available slot ID:", next_slot_id)


    vio_a=get_vio_a_hostname(silent=True)
    vio_b=get_vio_b_hostname(silent=True)
    root_vg_slot_id = next_slot_id
    datavg1_slot_id = next_slot_id+1
    datavg2_slot_id = next_slot_id+2

    if verbose and not silent:
        amd.info2_msg("   Slot allocation to be used:")
        amd.info2_msg("   VSCSI:rootvg", vio_a, ",", vio_b ,
                "SLOT:",next_slot_id, "--->",args.source_lpar,"SLOTS: 5,6")

        amd.info2_msg("   FC:datavg1", vio_a, ",", vio_b ,
                "SLOT:",datavg1_slot_id, "--->",args.source_lpar,"SLOTS: 7,9")

        amd.info2_msg("   FC:datavg2", vio_a, ",", vio_b ,
                "SLOT:",datavg2_slot_id, "--->",args.source_lpar,"SLOTS: 8,10")


    # Writing slots to files# {{{
        # Writing VIOS slots to file
    vios_slot_file=get_vios_slot_file()
    with open(vios_slot_file,'w') as f:
       # Append with a new line
       f.write("rootvg "+str(next_slot_id)+ "\n")
       f.write("datavg1 "+str(datavg1_slot_id)+ "\n")
       f.write("datavg2 "+str(datavg2_slot_id) + "\n")
    f.close()


        # Writing LPAR to VIOS1 slots to file
    lpar_vios1_slots_file=get_lpar_vios1_slot_file()
    with open(lpar_vios1_slots_file,'w') as f:
       # Append with a new line
       f.write("rootvg "+ str(root_vg_slot_a)+"\n")
       f.write("datavg1 "+ str(data_vg1_slot_a)+"\n")
       f.write("datavg2 "+str(data_vg2_slot_a)+"\n")
    f.close()


        # Writing LPAR to VIOS2 slots to file
    lpar_vios2_slots_file=get_lpar_vios2_slot_file()
    with open(lpar_vios2_slots_file,'w') as f:
       # Append with a new line
       f.write("rootvg "+ str(root_vg_slot_b)+"\n")
       f.write("datavg1 "+ str(data_vg1_slot_b)+"\n")
       f.write("datavg2 "+str(data_vg2_slot_b)+"\n")
    f.close()


# }}}


    return next_slot_id
# }}}
def create_target_lpar(hmc, ms, next_slot_id, next_lpar_id, verbose=False, silent=False, quit=False, do_prereq=False): # {{{
    """Creating the target LPAR or partition
    hmc:    Target HMC name
    ms:     Target Managed System
    do_prereq: Check if HMC is accessible, if MS exists"""

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])

    profile_string=compile_lpar_profile_string(args.hmc,
        args.destination_managed_system,
        next_slot_id,
        next_lpar_id,
        verbose=verbose,
        quit=True)


    amd.ok_msg("   >> Creating partition:",args.source_lpar,
            "on:", args.destination_managed_system)

    user = "hscroot"
    opt1 = "mksyscfg -r lpar -m "
    unix_cmd=("ssh "\
            "{}"\
            "@{} "\
            "{}"\
            "{}"\
            " -i \" {} \""\
            ).format(user,hmc, opt1, ms, profile_string)
    

    if verbose >= 2 and not silent:
       amd.info_msg("  unix_cmd is: ", unix_cmd)

    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
        # Unix_cmd has failed
    if rc!=0:
        if verbose >= 2 and not silent:
            for line in p.stdout:
                print line.strip()

        if quit:
           amd.err_msg("Unable to create the LPAR/partition",
                   exit_code=25)
        else:
           return False
    
        # Unix_cmd executed successfully
    elif rc==0:
        if verbose >= 2 and not silent:
            for line in p.stdout:
                print line.strip()

        if verbose and not silent:
            amd.ok_msg("   >> The partition has been created:")

        return True

# }}}# }}}

#-------------------------- HERE ---------------


# PREREQUISITES
def do_infra_prereq(hmc, ms, verbose=False, silent=False, quit=False, ): # {{{
    """Performing a complete infrastructure prerequisites checks
    hmc:    Target HMC name
    ms:     Target Managed System """

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])
      


    # Starting  HMC/MS
    if verbose and not silent:
        amd.stage_msg("Starting the HMC/MS prerequisites checks")

    is_hmc_accesible(args.hmc, user="hscroot",
       verbose=args.verbose, silent=True, quit=True)

    get_target_ms_serial(verbose=args.verbose, quit=True)

    # Starting VIOS checking
    if verbose and not silent:
        amd.stage_msg("Starting the VIOS prerequisites checks")
    get_vio_a_hostname(verbose=args.verbose)
    get_vio_b_hostname(verbose=args.verbose)
    if verbose and not silent:
        amd.ok_msg("   >> Retrieving VIOS ID:")
    get_vios_id(args.hmc,
       args.destination_managed_system,
       get_vio_a_hostname(silent=True),
       verbose=args.verbose,
       quit=True) 

    get_vios_id(args.hmc,
       args.destination_managed_system,
       get_vio_b_hostname(silent=True),
       verbose=args.verbose,
       quit=True) 

    # check if vioss are  accessible over  ssh
    is_ssh_accesible(get_vio_a_hostname(silent=True),
       user="padmin",
       verbose=args.verbose,
       quit=True)

    is_ssh_accesible(get_vio_b_hostname(silent=True),
       user="padmin",
       verbose=args.verbose,
       quit=True)



    if verbose and not silent:
        amd.ok_msg("End of: infrastructure prerequisites\n")
# }}}

# PROFILE MANAGEMENT
def compile_dummy_lpar_profile_string(hmc, ms,  lpar_name,   profile_name="dummy_profile", verbose=False, silent=False, quit=False, do_prereq=False): # {{{
    """Compiling the Profile String -> str: string
    hmc:    Target HMC name
    ms:     Target Managed System
    do_prereq: Check if HMC is accessible, if MS exists"""
# V2 {{{
    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])
      # }}}
# Do prereq if necessarily# {{{
    if do_prereq:
        # Checking if the target MS exists/is defined in the NIM server
        is_target_ms(verbose=args.verbose, quit=True)

        # Checking if hmc is accessible
        is_hmc_accesible(args.hmc,
                user="hscroot",
                verbose=args.verbose,
                silent=True,
                quit=True)
# }}}
# V1 {{{
    # Starting the process 
    if verbose and not silent:
        amd.ok_msg("   >> Compiling the LPAR profile string:")
# }}}
#     To remove once on the actual AIX env
##    lpar_id=get_lpar_id(args.hmc,
##            args.destination_managed_system,
##            args.source_lpar,
##            verbose=args.verbose, quit=True)



    profile_string=""
    profile_string+="name={},".format(profile_name)
    profile_string+="lpar_name={},".format(args.source_lpar)
    profile_string+="all_resources=0,"
    profile_string+="min_mem=256,"
    profile_string+="desired_mem=256,"
    profile_string+="max_mem=256,"
    profile_string+="min_num_huge_pages=0,"
    profile_string+="desired_num_huge_pages=0,"
    profile_string+="max_num_huge_pages=0,"
    profile_string+="mem_mode=ded,"
    profile_string+="mem_expansion=0.0,"
    profile_string+="hpt_ratio=1:128,"
    profile_string+="proc_mode=shared,"
    profile_string+="min_proc_units=0.1,"
    profile_string+="desired_proc_units=0.1,"
    profile_string+="max_proc_units=0.1,"
    profile_string+="min_procs=1,"
    profile_string+="desired_procs=1,"
    profile_string+="max_procs=1,"
    profile_string+="sharing_mode=cap,"
    profile_string+="uncap_weight=0,"
    profile_string+="shared_proc_pool_name=DefaultPool,"
    profile_string+="affinity_group_id=none,"
    profile_string+="io_slots=none,"
    profile_string+="lpar_io_pool_ids=none,"
    profile_string+="max_virtual_slots=10,"

    profile_string+="virtual_scsi_adapters=none,"
    profile_string+="virtual_eth_adapters=none,"
    profile_string+="virtual_eth_vsi_profiles=none,"
    profile_string+="virtual_fc_adapters=none,"
    profile_string+="vtpm_adapters=none,"
    profile_string+="hca_adapters=none,"
    profile_string+="boot_mode=sms,"
    profile_string+="conn_monitoring=0,"
    profile_string+="auto_start=0,"
    profile_string+="power_ctrl_lpar_ids=none,"
    profile_string+="work_group_id=none,"
    profile_string+="redundant_err_path_reporting=0,"
    profile_string+="bsr_arrays=0,"
    profile_string+="lpar_proc_compat_mode=default,"
    profile_string+="sriov_eth_logical_ports=none"

#         I had to remove these due to inconsistencies
#     profile_string+="lpar_id={},".format(lpar_id)
#     profile_string+="lpar_env=aixlinux,"
#     profile_string+="shared_proc_pool_id=0,"
#     profile_string+="electronic_err_reporting=null,"

    amd.ok_msg("   >> The profile string is ready:")

    if verbose >=2  and not silent:
        amd.ok_msg("   >> lpar profile string:", profile_string)

    return profile_string

# }}}

def is_lpar_profile(hmc, ms, lpar_name, profile_name, verbose=False, silent=False, quit=False, do_prereq=False): # {{{
    """Creating the target LPAR or partition
    hmc:    Target HMC name
    ms:     Target Managed System
    lpar_name   The name of the lpar
    profile_name    The name of the lpar profile. e.g default, dummy_profile
    do_prereq: Check if HMC is accessible, if MS exists
    lssyscfg -r prof -m S5 --filter "lpar_names=s135en0,profile_names=default"

    """

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])


    amd.ok_msg("   >> Checking if the profile name exists:",profile_name,
            "on:", args.source_lpar)

    user = "hscroot"
    opt1 = "lssyscfg -r prof -m "
    opt2 = " --filter \"lpar_names={},profile_names={}".format(lpar_name, profile_name)
    unix_cmd=("ssh "\
            "{}"\
            "@{} "\
            "{}"\
            "{}"\
            "{}\""\
            ).format(user,hmc, opt1, ms, opt2)
    

    if verbose >= 2 and not silent:
       amd.info_msg("  unix_cmd is: ", unix_cmd)

    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
        # Unix_cmd has failed
    if rc!=0:
        # You still need to parse the output. 
        # The HMC will return 1 if profile does not exist
        # Search for: HSCL800F : which is error code for: Inexistent profile
        if verbose >= 2 and not silent:
            for line in p.stdout:
                if "HSCL800F" in line:
                    amd.err_msg("gasit")
                    return False
                else:
                    if quit:
                       amd.err_msg("Unable to determine if profile exists",
                               exit_code=25)
                    else:
                       return False
    
        # Unix_cmd executed successfully
    elif rc==0:
        if verbose >= 2 and not silent:
            for line in p.stdout:
                print line.strip()

        if verbose and not silent:
            amd.ok_msg("   >> The profile:", profile_name, "is defined")

        return True

# }}}
def create_dummy_profile(hmc, ms, lpar_name, profile_name="dummy_profile",verbose=False, silent=False, quit=False, do_prereq=False): # {{{
    """Creates a dummy profile with the default noem of "dummy_profile
    hmc:    Target HMC name
    ms:     Target Managed System
    lpar_name:  The short hostname of the lpar
    profile_name: The name of the dummy profile you want to create
    verbose:    Show what is going on
    cmd: mksyscfg -r prof -m MS -i "profile_string"
    """

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])


    is_profile=is_lpar_profile(args.hmc,
        args.destination_managed_system,
        args.source_lpar,
        profile_name=profile_name,
        verbose=verbose,
        silent=True,
        quit=True)

    
    if is_profile:
        amd.ok_msg("   >> The profile exists, nothing to do")
        return True

    profile_string=compile_dummy_lpar_profile_string(args.hmc,
        args.destination_managed_system,
        args.source_lpar,
        verbose=verbose,
        profile_name=profile_name,
        quit=True)

    amd.ok_msg("   >> Creating dummy profile for:",args.source_lpar,
            "on:", args.destination_managed_system)

    user = "hscroot"
 
    opt1 = "mksyscfg -r prof -m "
    unix_cmd=("ssh "\
            "{}"\
            "@{} "\
            "{}"\
            "{}"\
            " -i \" {} \""\
            ).format(user,hmc, opt1, ms, profile_string)
    

    if verbose >= 2 and not silent:
       amd.info_msg("  unix_cmd is: ", unix_cmd)

    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
        # Unix_cmd has failed
    if rc!=0:
        if verbose >= 2 and not silent:
            for line in p.stdout:
                print line.strip()

        if quit:
           amd.err_msg("   >> Unable to create the dummy profile",
                   exit_code=25)
        else:
           return False
    
        # Unix_cmd executed successfully
    elif rc==0:
        if verbose >= 2 and not silent:
            for line in p.stdout:
                print line.strip()

        if verbose and not silent:
            amd.ok_msg("   >> The dummy profile has been created:")

        return True
# }}}
def remove_profile(hmc, ms, lpar_name,profile_name, verbose=False, silent=False, quit=False, do_prereq=False): # {{{
    """Deleting the profile of a partition
    hmc:    Target HMC name
    ms:     Target Managed System
    lpar_name   The name of the lpar
    prof_name: The name of the profile
    rmsyscfg -r prof -m MS -n prof1 -p lpar3
    """

    if not profile_name:
        profile_name="dummy_profile"
   

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])


    amd.ok_msg("   >> Removing profile:",profile_name,"from:",args.source_lpar)

    is_profile=is_lpar_profile(args.hmc,
        args.destination_managed_system,
        args.source_lpar,
        profile_name=profile_name,
        verbose=verbose,
        silent=True,
        quit=True)

    
    if not is_profile:
        amd.ok_msg("   >> The profile does not exist, nothing to do")
        return True

    user = "hscroot"
    opt1 = "rmsyscfg -r prof -m "
    opt2 = " -n {} -p {}".format(profile_name, lpar_name)
    unix_cmd=("ssh "\
            "{}"\
            "@{} "\
            "{}"\
            "{}"\
            "{}"\
            ).format(user,hmc, opt1, ms, opt2)
    

    if verbose >= 2 and not silent:
       amd.info_msg("  unix_cmd is: ", unix_cmd)

    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
        # Unix_cmd has failed
    if rc!=0:
        for line in p.stdout:
            if "HSCL07D1" in line: 
                amd.info_cyan_msg(line)
            else:
                if verbose >= 2 and not silent:
                    for line in p.stdout:
                        print line.strip()

        if quit:
            amd.err_msg("Unable to remove profile:",
                    profile_name,
                   exit_code=25)
        else:
           return False
    
        # Unix_cmd executed successfully
    elif rc==0:
        if verbose >= 2 and not silent:
            for line in p.stdout:
                print line.strip()

        if verbose and not silent:
            amd.ok_msg("   >> The profile", profile_name, " has been removed:")

        return True

# }}}

def get_current_profile(hmc, ms, lpar_name, verbose=False, silent=False, quit=False, do_prereq=False ): # {{{
    """Determines the  current profile -> str: lpar_state
    hmc:    Target HMC name
    ms:     Target Managed System
    lpar:   The name of the lpar: e.g. s134en0
    do_prereq: Check if HMC is accesible, if MS exists"""

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])

    is_lpar=is_lpar_in_hmc(args.hmc,
            args.destination_managed_system,
            args.source_lpar,
            quit=False)

    if  is_lpar:

       # lssyscfg -r lpar -m S8 -F "curr_profile" --filter "lpar_names=s203en0"
        user = "hscroot"
        opt1 = "lssyscfg -r lpar -m "
        opt2 = " --filter \"lpar_names={}\"".format(lpar_name)
        opt3 = "-F \"curr_profile\""
        unix_cmd=("ssh "\
                "{}"\
                "@{} "\
                "{}"\
                "{}"\
                "{}"\
                " {}"\
                ).format(user,hmc, opt1, ms, opt2, opt3)
        
        if verbose >= 2 and not silent:
           amd.info_msg("  unix_cmd is: ", unix_cmd)

        p = subprocess.Popen(unix_cmd,\
                shell=True, stdout=subprocess.PIPE,\
                stderr=subprocess.STDOUT)
        rc = p.wait()
        
            # Unix_cmd has failed
        if rc!=0:
           if quit:
               amd.info_cyan_msg("Unable to determine current profile")
           else:
               return False
        
            # Unix_cmd executed successfully
        elif rc==0:
           line = p.stdout.readlines()[0].strip()
           if verbose and not silent:
                  amd.ok_msg("   >> The current profile is::", line)

           return line.strip()

#  }}}

def rename_profile(hmc, ms, lpar_name, old_prof_name,new_prof_name,verbose=False, silent=False, quit=False, do_prereq=False): # {{{
    """Creating the target LPAR or partition
    hmc:    Target HMC name
    ms:     Target Managed System
    lpar_name   The name of the lpar
    old_prof_name: The name of the old profile: e.g default
    new_prof_name: The name of the new profile: e.g default_premigration
    chsyscfg -r prof -m S5 -i "lpar_name=s135en0,name=default, new_name=default_premigration" --force
    """

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])


    amd.ok_msg("   >> Renaming partition profile for:",args.source_lpar,
        "from:", old_prof_name, "to:", new_prof_name)

    is_profile=is_lpar_profile(args.hmc,
        args.destination_managed_system,
        args.source_lpar,
        profile_name=old_prof_name,
        verbose=verbose,
        silent=True,
        quit=True)

    
    
    if not is_profile:
        amd.info_msg("   >> The profile you want to rename does not exist.")
        amd.info_msg("   >> Use the -l flag to list the avilable profiles.")
        amd.info_msg("   >> Nothing do do. Exiting...")
        return True


    user = "hscroot"
    opt1 = "chsyscfg -r prof -m "
    opt2 = "lpar_name={},name={},new_name={}"\
            .format(lpar_name, old_prof_name, new_prof_name)
    unix_cmd=("ssh "\
            "{}"\
            "@{} "\
            "{}"\
            "{}"\
            " -i \"{}\""\
            " --force"\
            ).format(user,hmc, opt1, ms, opt2)
    

    if verbose >= 2 and not silent:
       amd.info_msg("  unix_cmd is: ", unix_cmd)

    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
        # Unix_cmd has failed
    if rc!=0:
        if verbose >= 2 and not silent:
            for line in p.stdout:
                print line.strip()

        if quit:
           amd.err_msg("Unable to rename the profile",
                   exit_code=25)
        else:
           return False
    
        # Unix_cmd executed successfully
    elif rc==0:
        if verbose >= 2 and not silent:
            for line in p.stdout:
                print line.strip()

        if verbose and not silent:
            amd.ok_msg("   >> The profile has been renamed.")

        return True

# }}}
def list_all_lpar_profiles(hmc, ms, lpar_name, verbose=False, silent=False, quit=False, do_prereq=False): # {{{
    """Creating the target LPAR or partition
    hmc:    Target HMC name
    ms:     Target Managed System
    lpar_name   The name of the lpar
    lssyscfg -r prof -m S5 --filter "lpar_names=s135en0" -F "lpar_name,name"

    """

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])


    amd.ok_msg("   >> Listing all the profiles of :",args.source_lpar,)

    # Used for logic and display
    current_profile=get_current_profile(args.hmc,
            args.destination_managed_system,
            args.source_lpar, 
            verbose=False,
            quit=True)

    # Used for display only
    lpar_state=get_lpar_state(args.hmc,
            args.destination_managed_system,
            args.source_lpar, 
            verbose=False,
            quit=True)


    
    user = "hscroot"
    opt1 = "lssyscfg -r prof -m "
    opt2 = "lpar_names={}".format(lpar_name)
    unix_cmd=("ssh "\
            "{}"\
            "@{} "\
            "{}"\
            "{}"\
            " --filter \"{}\" -F name"\
            ).format(user,hmc, opt1, ms, opt2)
    

    if verbose >= 2 and not silent:
       amd.info_msg("  unix_cmd is: ", unix_cmd)

    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
        # Unix_cmd has failed
    if rc!=0:
        if verbose >= 2 and not silent:
            for line in p.stdout:
                print line.strip()

        if quit:
           amd.err_msg("Unable to list all the profiles",
                   exit_code=25)
        else:
           return False
    
        # Unix_cmd executed successfully
    elif rc==0:
        if verbose >= 2 and not silent:
            for line in p.stdout:
                print line.strip()

        amd.info_green_msg("Current lpar state:", lpar_state)
        if current_profile:
            amd.info_green_msg("Current lpar profile:", current_profile)
        print "\n    LPAR:     PROFILE"
        for line in p.stdout:
            print "    {}:  {}".format(lpar_name, line.strip())

        print""
        amd.ok_msg("   >> All profile names have been retrieved:\n")
        return True

# }}}
def restore_default_profile(hmc, ms, lpar_name, profile_name="default",verbose=False, silent=False, quit=False, do_prereq=False): # {{{
    """Creating the target LPAR or partition
    hmc:    Target HMC name
    ms:     Target Managed System
    do_prereq: Check if HMC is accessible, if MS exists
    """

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])

    #  >>>>>>>>>>>> state_collection

    is_default=is_lpar_profile(args.hmc,
        args.destination_managed_system,
        args.source_lpar,
        profile_name="default", 
        verbose=verbose,
        silent=True,
        quit=True)

    is_default_premigration=is_lpar_profile(args.hmc,
        args.destination_managed_system,
        args.source_lpar,
        profile_name="default_premigration", 
        verbose=verbose,
        silent=True,
        quit=True)
    

    #  >>>>>>>>>>>> logic 

    if is_default:
        # RESTORE DEFAULT   
        amd.ok_msg("The default profile exists. Nothing to do.")
        return True
    else:
        if is_default_premigration:
            print "RENAME DEFAULT_PREMIGRATION TO DEFAULT"

            rename_profile(args.hmc,
                args.destination_managed_system,
                args.source_lpar,
                old_prof_name="default_premigration", 
                new_prof_name="default", 
                verbose=True,
                quit=True)


            amd.ok_msg("The default profile has been restored")
            return True
        else:
            amd.err_msg("Unable to restore the default profile", exit_code=1)


# }}}

# BACKUP Profile
def check_dir_path(path):# {{{
    """Checking if the dirpath of the filename exists

    :path: the full path of the file
    :returns: BOOL
    """
    if os.path.exists(os.path.dirname(path)):
        return True
    else:
        return False
# }}}

def save_profile(hmc, ms, lpar_name, file_name, prof_name="default", verbose=False, silent=False, quit=False, do_prereq=False ): # {{{
    """Saving the default profile locally
    hmc:    Target HMC name
    ms:     Target Managed System
    lpar_name:   The name of the lpar: e.g. s134en0
    prof_name:   The name of profile of the lpar
    file_name:   The name of the file where the profile will be stored
    do_prereq: Check if HMC is accessible, if MS exists"""

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])

    is_lpar=is_lpar_in_hmc(args.hmc,
            args.destination_managed_system,
            args.source_lpar,
            quit=False)

    # checking if the dirpath of the file_name exists
    if not check_dir_path(file_name):
        base_dir=os.path.dirname(file_name)
        amd.err_msg("Inexistent basedir:", base_dir, exit_code=5)


    if  is_lpar:
       # ssh hscroot@lxsrvhmc0001 lssyscfg -r prof -m S04  --filter "lpar_names=s230en0,profile_names=default"
       # lssyscfg -r lpar -m S8 -F name
        user = "hscroot"
        opt1 = "lssyscfg -r prof -m "
        opt2 = " --filter \"lpar_names={},profile_names={}\""\
                .format(lpar_name,prof_name)
        unix_cmd=("ssh "\
                "{}"\
                "@{} "\
                "{}"\
                "{}"\
                " {}"\
                ).format(user,hmc, opt1, ms, opt2)
        
        if verbose >= 2 and not silent:
           amd.info_msg("  unix_cmd is: ", unix_cmd)

        p = subprocess.Popen(unix_cmd,\
                shell=True, stdout=subprocess.PIPE,\
                stderr=subprocess.STDOUT)
        rc = p.wait()
        
            # Unix_cmd has failed
        if rc!=0:
           if quit:
               amd.info_cyan_msg("Unable to determine default profile")
           else:
               return False
        
            # Unix_cmd executed successfully
        elif rc==0:
           line = p.stdout.readlines()[0].strip()
           if verbose and not silent:
                  amd.ok_msg("   >> The current profile is::", line)

           with open(file_name,'w') as f:
              f.write(line)
           f.close()

           amd.ok_msg("The profile has been saved into:",file_name)

#  }}}


# LPAR ACTIVATION
def get_lpar_state(hmc, ms, lpar_name, verbose=False, silent=False, quit=False, do_prereq=False ): # {{{
    """Determines the  lpar state -> str: lpar_state
    hmc:    Target HMC name
    ms:     Target Managed System
    lpar:   The name of the lpar: e.g. s134en0
    do_prereq: Check if HMC is accesible, if MS exists"""

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])

    is_lpar=is_lpar_in_hmc(args.hmc,
            args.destination_managed_system,
            args.source_lpar,
            quit=False)

    if  is_lpar:

    # ssh hscroot@lxsrvhmc0001 lssyscfg -m S04 -r lpar --filter "lpar_names=s370en0" -F state

        user = "hscroot"
        opt1 = "lssyscfg -r lpar -m "
        opt2 = " --filter \"lpar_names={}\"".format(lpar_name)
        opt3 = "-F \"state\""
        unix_cmd=("ssh "\
                "{}"\
                "@{} "\
                "{}"\
                "{}"\
                "{}"\
                " {}"\
                ).format(user,hmc, opt1, ms, opt2, opt3)
        
        if verbose >= 2 and not silent:
           amd.info_msg("  unix_cmd is: ", unix_cmd)

        p = subprocess.Popen(unix_cmd,\
                shell=True, stdout=subprocess.PIPE,\
                stderr=subprocess.STDOUT)
        rc = p.wait()
        
            # Unix_cmd has failed
        if rc!=0:
           if quit:
               amd.err_msg("Unable to determine the LPAR STATE",
                       exit_code=23)
           else:
               return False
        
            # Unix_cmd executed successfully
        elif rc==0:
           line = p.stdout.readlines()[0].strip()
           if verbose and not silent:
                  amd.ok_msg("   >> The  state of the lpar is::", line)

           return line

#  }}}

def do_lpar_deactivate(hmc, ms, lpar_name, verbose=False, silent=False, quit=False, ): # {{{
    """Deactivating the lpar into: "Not Activated"
    This action is needed to activate the lpar into different states forcibly 

    hmc:    Target HMC name
    ms:     Target Managed System 
    lpar_name:  The name of the lpar
    lpar:   the lpar name"""

    

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])


    if verbose and not silent:
        amd.ok_msg("Starting lpar deactivation ")
      
    lpar_state=get_lpar_state(args.hmc,
            args.destination_managed_system,
            args.source_lpar, 
            verbose=False,
            silent=True,
            quit=True)

    if "Not Activated" not in lpar_state:
    # ssh hscroot@lxsrvhmc0001 chsysstate -m S04 -r lpar  -o shutdown -n s370en0 --immed

        user = "hscroot"
        opt1 = "chsysstate -r lpar -m "
        if args.FORCE:
            opt2 = "  -o shutdown -n {} --immed".format(lpar_name)
        else:
            opt2 = "  -o shutdown -n {} ".format(lpar_name)
        unix_cmd=("ssh "\
                "{}"\
                "@{} "\
                "{}"\
                "{}"\
                " {}"\
                ).format(user,hmc, opt1, ms, opt2)
        
        if verbose >= 2 and not silent:
           amd.info_msg("  unix_cmd is: ", unix_cmd)

        p = subprocess.Popen(unix_cmd,\
                shell=True, stdout=subprocess.PIPE,\
                stderr=subprocess.STDOUT)
        rc = p.wait()
        
            # Unix_cmd has failed
        if rc!=0:
           if quit:
               amd.err_msg("Unable deactivate the lpar",
                       exit_code=23)
           else:
               return False
        
            # Unix_cmd executed successfully
        elif rc==0:
           if verbose and not silent:
               amd.ok_msg("   >> Lpar mode: Not Activated")



    else:
        if verbose and not silent:
            amd.ok_msg("   >> Lpar already in state:", lpar_state)



    if verbose and not silent:
        amd.ok_msg("End of: LPAR DEACTIVATION \n")



# }}}
# -A
def do_lpar_activate_ok_prompt(hmc, ms, lpar_name, profile_name, verbose=False, silent=False, quit=False, ): # {{{
    """Activating the lpar into Open Firwmare prompt

    hmc:    Target HMC name
    ms:     Target Managed System 
    profile_name: The name of the pfrofile to be used: 
    lpar:   the lpar name"""

    

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])


    if verbose and not silent:
        amd.ok_msg("Starting dummy lpar activation into OK Prompt")
      
    lpar_state=get_lpar_state(args.hmc,
            args.destination_managed_system,
            args.source_lpar, 
            verbose=False,
            silent=True,
            quit=True)


    # Deactivate the LPAR
    if "Open Firmware"  in lpar_state:
        amd.ok_msg("   >> Lpar already in state:", lpar_state)
    else:
        if "Not Activated" not in lpar_state:
            do_lpar_deactivate(args.hmc,
                args.destination_managed_system,
                args.source_lpar,
                verbose=verbose,
                quit=True)
        
            # This is bad. I need to implement some semaphores instead 
            amd.info_msg("Allowing the lpar to shutdown")
            time.sleep(90)  
        
    lpar_state=get_lpar_state(args.hmc,
            args.destination_managed_system,
            args.source_lpar, 
            verbose=False,
            silent=True,
            quit=True)

    if "Not Activated" in lpar_state:
        user = "hscroot"
        opt1 = "chsysstate -r lpar -m "
        opt2 = " -f {} -o on -n {} -b of".format(profile_name, lpar_name)
        unix_cmd=("ssh "\
                "{}"\
                "@{} "\
                "{}"\
                "{}"\
                " {}"\
                ).format(user,hmc, opt1, ms, opt2)
        
        if verbose >= 2 and not silent:
           amd.info_msg("  unix_cmd is: ", unix_cmd)

        p = subprocess.Popen(unix_cmd,\
                shell=True, stdout=subprocess.PIPE,\
                stderr=subprocess.STDOUT)
        rc = p.wait()
        
            # Unix_cmd has failed
        if rc!=0:
           if quit:
               amd.err_msg("Unable activate the lpar into OK prompt",
                       exit_code=23)
           else:
               return False
        
            # Unix_cmd executed successfully
        elif rc==0:
           if verbose and not silent:
               amd.ok_msg("   >> Lpar mode:  OK prompt")

    if verbose and not silent:
        amd.ok_msg("End of: dummy lpar activation")



# }}}

# -U
def do_lpar_activate_normal(hmc, ms, lpar_name, profile_name, verbose=False, silent=False, quit=False, ): # {{{
    """Activating the lpar using a specified profile_name

    hmc:    Target HMC name
    ms:     Target Managed System 
    lpar:   the lpar name
    profile_name:   The name of the profile to be used for lpar activation"""


    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])


    if verbose and not silent:
        amd.ok_msg("Starting lpar activation ")
      
    lpar_state=get_lpar_state(args.hmc,
            args.destination_managed_system,
            args.source_lpar, 
            verbose=False,
            quit=True)

   
    # Deactivate the LPAR
    if "Running" in lpar_state:
        amd.ok_msg("   >> Lpar already in state:", lpar_state)
    else:
        if "Not Activated" not in lpar_state:
            do_lpar_deactivate(args.hmc,
                args.destination_managed_system,
                args.source_lpar,
                verbose=verbose,
                quit=True)
        
            # This is bad. I need to implement some semaphores instead 
            amd.info_msg("Allowing the lpar time to shutdonw")
            time.sleep(7) 

    lpar_state=get_lpar_state(args.hmc,
            args.destination_managed_system,
            args.source_lpar, 
            verbose=False,
            quit=True)

    if ("Not Activated") in str(lpar_state):
        user = "hscroot"
        opt1 = "chsysstate -r lpar -m "
        opt2 = " -f {} -o on -n {} ".format(profile_name,lpar_name)
        unix_cmd=("ssh "\
                "{}"\
                "@{} "\
                "{}"\
                "{}"\
                " {}"\
                ).format(user,hmc, opt1, ms, opt2)
        
        if verbose >= 2 and not silent:
           amd.info_msg("  unix_cmd is: ", unix_cmd)

        p = subprocess.Popen(unix_cmd,\
                shell=True, stdout=subprocess.PIPE,\
                stderr=subprocess.STDOUT)
        rc = p.wait()
        
            # Unix_cmd has failed
        if rc!=0:
           if quit:
               amd.err_msg("Unable activate the lpar",
                       exit_code=23)
           else:
               return False
        
            # Unix_cmd executed successfully
        elif rc==0:
           if verbose and not silent:
               amd.ok_msg("   >> Lpar mode:  Activated")






    if verbose and not silent:
        amd.ok_msg("End of: LPAR ACTIVATION")



# }}}


# DUMMY 
def activate_dummy_profile_v2(hmc, ms, lpar_name, profile_name="dummy_profile",verbose=False, silent=False, quit=False, do_prereq=False): # {{{

    """Creating the target LPAR or partition
    hmc:    Target HMC name
    ms:     Target Managed System
    do_prereq: Check if HMC is accessible, if MS exists
    chsyscfg -r lpar -m MS -i profile_string
    """

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])

    #  >>>>>>>>>>>> state_collection

    is_dummy=is_lpar_profile(args.hmc,
        args.destination_managed_system,
        args.source_lpar,
        profile_name="dummy_profile", 
        verbose=verbose,
        silent=True,
        quit=True)
    
    is_default=is_lpar_profile(args.hmc,
        args.destination_managed_system,
        args.source_lpar,
        profile_name="default", 
        verbose=verbose,
        silent=True,
        quit=True)
   

    
#    amd.ok_msg("====START D DEBUGGING ======")
#    #is_dummy=False
#    #is_default=True
#    #is_default_premigration=True
#    amd.ok_msg("==== DEBUG EXITING ======")
    





    #  >>>>>>>>>>>> logic 

    if is_default:
        print "  RENAME DEFAULT -> DEFAULT_PREMIGRATION"        
        # RENAME DEFAULT -> DEFAULT_PREMIGRATION        
        rename_profile(args.hmc,
            args.destination_managed_system,
            args.source_lpar,
            old_prof_name="default",
            new_prof_name="default_premigration",
            verbose=args.verbose,
            quit=True)


    if is_dummy:
#         print "  ACTIVATE DUMMY"
        do_lpar_activate_ok_prompt(args.hmc,
                args.destination_managed_system,
                args.source_lpar,
                profile_name="dummy_profile",
                verbose=args.verbose,
                quit=True
                )
#        do_lpar_activate(args.hmc,
#            args.destination_managed_system,
#            args.source_lpar, 
#            profile_name="dummy_profile",
#            verbose=args.verbose,
#            quit=True)

        pass
    else:
#         print "  ADD DUMMY, CREATE DUMMY "
        create_dummy_profile(args.hmc,
            args.destination_managed_system,
            args.source_lpar,
            verbose=args.verbose,
            quit=True)

#         print "  ACTIVATE DUMMY"
        do_lpar_activate_ok_prompt(args.hmc,
                args.destination_managed_system,
                args.source_lpar,
                profile_name="dummy_profile",
                verbose=args.verbose,
                quit=True
                )





# }}}
# DEFAULT ACTIVATION
def activate_default_profile(hmc, ms, lpar_name, profile_name="default",verbose=False, silent=False, quit=False, do_prereq=False): # {{{
    """Creating the target LPAR or partition
    hmc:    Target HMC name
    ms:     Target Managed System
    do_prereq: Check if HMC is accessible, if MS exists
    chsyscfg -r lpar -m MS -i profile_string
    """

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])

    #  >>>>>>>>>>>> state_collection

    is_default=is_lpar_profile(args.hmc,
        args.destination_managed_system,
        args.source_lpar,
        profile_name="default", 
        verbose=verbose,
        silent=True,
        quit=True)

    is_default_premigration=is_lpar_profile(args.hmc,
        args.destination_managed_system,
        args.source_lpar,
        profile_name="default_premigration", 
        verbose=verbose,
        silent=True,
        quit=True)
    
    
#    amd.ok_msg("====START D DEBUGGING ======")
#    print "is_default_lpar={}".format(is_default)
#    print "is_default_lpar_premigration={}".format(is_default_premigration)
#    amd.ok_msg("==== DEBUG EXITING ======")
    
    

    #  >>>>>>>>>>>> logic 

    if is_default:
        # ACTIVATE DEFAULT 
        print "ACTIVATE DEFAULT"
        do_lpar_activate_normal(args.hmc,
            args.destination_managed_system,
            args.source_lpar, 
            profile_name="default",
            verbose=verbose,
            quit=True)
        return True
    else:
        if is_default_premigration:
        # ACTIVATE  DEFAULT_PREMIGRATION        
            rename_profile(args.hmc,
                args.destination_managed_system,
                args.source_lpar,
                old_prof_name="default_premigration", 
                new_prof_name="default", 
                verbose=args.verbose,
                quit=True)

            do_lpar_activate_normal(args.hmc,
                args.destination_managed_system,
                args.source_lpar, 
                profile_name="default",
                verbose=verbose,
                quit=True)
            print "ACTIVATE DEFAULT"
        else:
            amd.err_msg("Unable to identify a valid premigration profile", exit_code=1)


# }}}

#-------------------------- HERE ---------------



# See IF YOU CAN REMOVE
# See IF YOU CAN REMOVE# {{{
# VIOS VIOS VIOS # {{{
# VIOS VIOS VIOS 
   # LU, LOGICAL UNIT rootvg
def get_rootvg_lu_name(lpar_name): # {{{
    """Returns the name of the Logical Unit used by rootvg : str 
    e.g. s370_rvg
    return str: 
    """
    rootvg_lu_name = lpar_name[0:4]+"_rvg"
    return rootvg_lu_name

   
# }}}
def is_rootvg_lu(vios, lpar_name, verbose=False, silent=False, quit=True, do_prereq=False): # {{{
    """Check if the Logical Unit exists
    vios: vios hostname
    lpar_name : the name of the lpar
    $cmd="ssh padmin\@$VIO_A ioscli lu -list |grep $LU";
    do_prereq: Check if HMC is accessible, if MS exists"""

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])


    is_rootvg_lu=False
    rootvg_lu_name=get_rootvg_lu_name(lpar_name)

    user = "padmin"
    opt1 = " ioscli lu -list "

    unix_cmd=("ssh "\
            "{}"\
            "@{} "\
            "{}"\
            ).format(user,
                  vios,
                  opt1)
    
    if verbose >= 2 and not silent:
       amd.info_msg("  unix_cmd is: ", unix_cmd)

    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
        # Unix_cmd has failed
    if rc!=0:
        if verbose >= 2 and not silent:
            for line in p.stdout:
                print line.strip()

        if quit:
            amd.err_msg("Unable to determine if ", rootvg_lu_name, "exists:",
                   exit_code=27)
        else:
           return False
    
        # Unix_cmd executed successfully

    elif rc==0:
       for line in p.stdout:
           if rootvg_lu_name in line:
               is_rootvg_lu = True
               break

    if is_rootvg_lu:
       if verbose and not silent:
           amd.ok_msg("   >> Logical Unit servicing the rootvg exists:", 
             rootvg_lu_name)
  
    return is_rootvg_lu
    

# }}}
def mk_rootvg_lu(vios, lpar_name, verbose=False, silent=False, quit=True, do_prereq=False): # {{{
    """Create the rotovg Logical Unit
    vios: vios hostname
    lpar_name : the name of the lpar
    cmdd="ssh padmin\@$VIO_A \"ioscli mkbdsp -clustername SSPFFM01 -sp SSPFFM01 100G -bd $LU \"   " ;
    do_prereq: Check if HMC is accessible, if MS exists"""

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])


    rootvg_lu_name=get_rootvg_lu_name(lpar_name)

    user = "padmin"
    opt1 = " ioscli mkbdsp -clustername SSPFFM01 -sp SSPFFM01 122880M -bd {} "\
            .format(rootvg_lu_name)

    unix_cmd=("ssh "\
            "{}"\
            "@{} "\
            "{}"\
            ).format(user,
                  vios,
                  opt1)
    
    if verbose >= 2 and not silent:
       amd.info_msg("  unix_cmd is: ", unix_cmd)

    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
        # Unix_cmd has failed
    if rc!=0:
        if verbose >= 2 and not silent:
            for line in p.stdout:
                print line.strip()

        if quit:
           amd.err_msg("Unable to create", rootvg_lu_name,
                   exit_code=27)
        else:
           return False
    
        # Unix_cmd executed successfully
    elif rc==0:
       if verbose and not silent:
          amd.ok_msg("   >> Successfully created the Logical Unit:", 
             rootvg_lu_name)
       return True

# }}}
   # UPDATE VIOS_PROFILE
def update_vios_scsi_profile(hmc, ms, lpar_vsci_slot_id, lpar_id, vios_id, vios_slot_id,  verbose=False, silent=False, quit=False, do_prereq=False): # {{{
    """Updating the VIOSs profiles to integrate the SCSI slots
    hmc:    Target HMC name
    ms:     Target Managed System
    lpar_vsci_slot_id: The slot id of the lpar : 5 by default
    lpar_id : The lpar_id of the lpar. determined by get_next_lpar_id
    vios_id : The ID of the VIOS usually eigher 1 or 2
    vios_slot_id: The slot id of the vios. Usually this is equal to nex_slot  id
    do_prereq: Check if HMC is accessible, if MS exists"""

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])


# Compiling  the profile string -> profile_string # {{{
    profile_string=""

# Example commands# {{{
#  cmd: chsyscfg -r prof -m S02 -i \'name=default_profile,lpar_id=1,\"virtual_scsi_adapters+=28/server/8/s372en0/5/0\"\'
#  virtual_scsi_adapters=<slot_num>/<adapter_type>/[<remote_lpar_id>]/[<remote_lpar_name>]/[<remote_slot_num>]/<is_required>,.""
# my $cmd=" ssh hscroot\@$HMC chsyscfg -m $BLECH -r prof -i \\'name=default_profile,lpar_id=$VIO_ID,\\\"virtual_scsi_adapters+=$ADAPTERSTRING\\\"\\' --force";
# }}}

    profile_string +="name=default_profile,"
    profile_string +="lpar_id={},".format(vios_id)
    


#   profile_string +="{vios_slot_id}/server/{lpar_id}/{lpar_name}/{lpar_slot_nr}/0,".\

    profile_string +="\\\\\\\"virtual_scsi_adapters+="
    profile_string +="{}/server/{}/{}/{}/0".\
    format(vios_slot_id, lpar_id, args.source_lpar, lpar_vsci_slot_id)
    profile_string +="\\\\\\\""

    if verbose  and not silent:
       amd.ok_msg("   >> VIOS:",vios_id, "virtual_scsi_adapters profile string is ready:")


# V2 {{{
    if verbose >=2  and not silent:
       amd.ok_msg("   >> VIOS:  SCSI profile string:", profile_string)
# }}}

# }}}

    user = "hscroot"
    opt1 = "chsyscfg -r prof -m "
    unix_cmd=("ssh "\
            "{}"\
            "@{} "\
            "{}"\
            "{}"\
            " -i \\\\\"{} --force\\\\\"" \
            ).format(user,hmc, opt1, ms, profile_string)
    

    if verbose >= 2 and not silent:
       amd.info_msg("  unix_cmd is: ", unix_cmd)

    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
        # Unix_cmd has failed
    if rc!=0:
        if verbose >= 2 and not silent:
            for line in p.stdout:
                print line.strip()

        if quit:
           amd.err_msg("Unable to update the VIOS profile",
                   exit_code=27)
        else:
           return False
    
        # Unix_cmd executed successfully
    elif rc==0:
        if verbose >= 2 and not silent:
            for line in p.stdout:
                print line.strip()

        if verbose and not silent:
           amd.ok_msg("   >> SCSI profile successfully updated for VIOS:", vios_id)

        return True

# }}}
def update_vios_FC_profile(hmc, ms, lpar_slot_id_1, lpar_slot_id_2, lpar_id, vios_id, next_slot_id,  verbose=False, silent=False, quit=False, do_prereq=False): # {{{
    """Updating the VIOSs profiles to integrate the FC slots
    hmc:    Target HMC name
    ms:     Target Managed System
    data_vg1_slot_a : Lpar slot id : 
    lpar_slot_id_1 : Lpar slot id : usually 7 or 9
    lpar_slot_id_2 : Lpar slot id : usually 8 or 10
    lpar_vsci_slot_id: The slot id of the lpar : 5 by default
    lpar_id : The lpar_id of the lpar. determined by get_next_lpar_id
    vios_id : The ID of the VIOS usually eigher 1 or 2
    next_slot_id: VIOS slot id based on the previously determined next_slot_id value
    do_prereq: Check if HMC is accessible, if MS exists"""

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])


# Compiling  the profile string -> profile_string # {{{
    #  ssh hscroot@hmc11en0 chsyscfg -m I23 -r prof -i \'name=default_profile,lpar_id=1,\"virtual_fc_adapters=100/server/100//100//1,300/server/100//300//1\"\'
    
# virtual-slot-number/client-or-server/ 
# [remote-lpar-ID]/[remote-lpar-name]/ 
# remote-slot-number/[wwpns]/is-required



    vios_slot_datavg1=next_slot_id+1
    vios_slot_datavg2=next_slot_id+2

    profile_string=""

# Example commands# {{{
#  cmd: chsyscfg -r prof -m S02 -i \'name=default_profile,lpar_id=1,\"virtual_scsi_adapters+=28/server/8/s372en0/5/0\"\'
#  virtual_scsi_adapters=<slot_num>/<adapter_type>/[<remote_lpar_id>]/[<remote_lpar_name>]/[<remote_slot_num>]/<is_required>,.""
# my $cmd=" ssh hscroot\@$HMC chsyscfg -m $BLECH -r prof -i \\'name=default_profile,lpar_id=$VIO_ID,\\\"virtual_scsi_adapters+=$ADAPTERSTRING\\\"\\' --force";
# }}}

    profile_string +="name=default_profile,"
    profile_string +="lpar_id={},".format(vios_id)
    


# \"virtual_fc_adapters=100/server/100//100//1,300/server/100//300//1\"\'
# \"virtual_fc_adapters=13/server/4/s370en0/7//0,14/server/4/s370en0/8//0\"\'

    profile_string +="\\\\\\\"virtual_fc_adapters+="
    profile_string +="{}/server/{}/{}/{}//0,".\
    format(vios_slot_datavg1, lpar_id, args.source_lpar, lpar_slot_id_1)
    profile_string +="{}/server/{}/{}/{}//0".\
    format(vios_slot_datavg2, lpar_id, args.source_lpar, lpar_slot_id_2)
    profile_string +="\\\\\\\""

    if verbose  and not silent:
       amd.ok_msg("   >> VIOS:",vios_id, "virtual_FC_adapters profile string is ready:")


# V2 {{{
    if verbose >=2  and not silent:
       amd.ok_msg("   >> VIOS:  FC profile string:", profile_string)
# }}}

# }}}

    user = "hscroot"
    opt1 = "chsyscfg -r prof -m "
    unix_cmd=("ssh "\
            "{}"\
            "@{} "\
            "{}"\
            "{}"\
            " -i \\\\\"{} --force\\\\\"" \
            ).format(user,hmc, opt1, ms, profile_string)
    

    if verbose >= 2 and not silent:
       amd.info_msg("  unix_cmd is: ", unix_cmd)

    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
        # Unix_cmd has failed
    if rc!=0:
        if verbose >= 2 and not silent:
            for line in p.stdout:
                print line.strip()

        if quit:
           amd.err_msg("Unable to update the VIOS profile",
                   exit_code=29)
        else:
           return False
    
        # Unix_cmd executed successfully
    elif rc==0:
        if verbose >= 2 and not silent:
            for line in p.stdout:
                print line.strip()

        if verbose and not silent:
           amd.ok_msg("   >> SCSI profile successfully updated for VIOS:", vios_id)

        return True

# }}}
   # DLPAR
def dlpar_scsi_slot_mapping(hmc, ms, lpar_vsci_slot_id, lpar_id, vios_id, vios_slot_id,  verbose=False, silent=False, quit=False, do_prereq=False): # {{{
    """Performing dlpar for scsi
    hmc:    Target HMC name
    ms:     Target Managed System
    lpar_vsci_slot_id: The slot id of the lpar : 5 by default
    lpar_id : The lpar_id of the lpar. determined by get_next_lpar_id
    vios_id : The ID of the VIOS usually eigher 1 or 2
    vios_slot_id: The slot id of the vios. Usually this is equal to nex_slot  id
    do_prereq: Check if HMC is accessible, if MS exists"""

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])


    user = "hscroot"
    opt1 = "chhwres -r virtualio --rsubtype scsi"
    unix_cmd=("ssh "\
            "{}"\
            "@{} "\
            "{}"\
            " -m {}"\
            " -o a"\
            " --id {}"\
            " -s {}"\
            " -a remote_slot_num={},"\
            " remote_lpar_id={},"\
            " adapter_type=server"\
            " "
            ).format(user,
                  hmc,
                  opt1,
                  ms,
                  vios_id,
                  vios_slot_id,
                  lpar_vsci_slot_id,
                  lpar_id)
    

    if verbose >= 2 and not silent:
       amd.info_msg("  unix_cmd is: ", unix_cmd)

    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
        # Unix_cmd has failed
    if rc!=0:
        if verbose >= 2 and not silent:
            for line in p.stdout:
                print line.strip()

        if quit:
           amd.err_msg("Unable to perform the scsi mappings",
                   exit_code=27)
        else:
           return False
    
        # Unix_cmd executed successfully
    elif rc==0:
        if verbose >= 2 and not silent:
            for line in p.stdout:
                print line.strip()

        if verbose and not silent:
           amd.ok_msg("   >> SCSI mappings are in place for VIOS:", vios_id,": ",
                 vios_slot_id, "-->", lpar_vsci_slot_id)
        return True

# }}}
def dlpar_FC_slot_mapping(hmc, ms, lpar_fc_slot_id, lpar_id, vios_id, vios_slot_id,  verbose=False, silent=False, quit=False, do_prereq=False): # {{{
    """performing dlpar for FC
    hmc:    Target HMC name
    ms:     Target Managed System
    lpar_fc_slot_id: The slot id of the lpar : 5 by default
    lpar_id : The lpar_id of the lpar. determined by get_next_lpar_id
    vios_id : The ID of the VIOS usually either 1 or 2
    vios_slot_id: The slot id of the vios. Usually this is equal to nex_slot  id
    do_prereq: Check if HMC is accessible, if MS exists"""

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])


    user = "hscroot"
    opt1 = "chhwres -r virtualio --rsubtype fc"
    unix_cmd=("ssh "\
            "{}"\
            "@{} "\
            "{}"\
            " -m {}"\
            " -o a"\
            " --id {}"\
            " -s {}"\
            " -a remote_slot_num={},"\
            " remote_lpar_id={},"\
            " adapter_type=server"\
            " "
            ).format(user,
                  hmc,
                  opt1,
                  ms,
                  vios_id,
                  vios_slot_id,
                  lpar_fc_slot_id,
                  lpar_id)
    

    if verbose >= 2 and not silent:
       amd.info_msg("  unix_cmd is: ", unix_cmd)

    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
        # Unix_cmd has failed
    if rc!=0:
        if verbose >= 2 and not silent:
            for line in p.stdout:
                print line.strip()

        if quit:
           amd.err_msg("Unable to perform the FC mappings",
                   exit_code=27)
        else:
           return False
    
        # Unix_cmd executed successfully
    elif rc==0:
        if verbose >= 2 and not silent:
            for line in p.stdout:
                print line.strip()

        if verbose and not silent:
           amd.ok_msg("   >> FC mappings are in place for VIOS:", vios_id,": ",
                 vios_slot_id, "-->", lpar_fc_slot_id)

        return True

# }}}
   # REDISCOVER DEVICES
def do_FC_cfgdev(vios,  verbose=False, silent=False, quit=False, do_prereq=False): # {{{
    """Performing cfgdev for FC
    vios:    The name of the vios
    do_prereq: Check if HMC is accessible, if MS exists"""

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])

    user = "padmin"
    opt1 = " ioscli cfgdev -dev vio0"
    unix_cmd=("ssh "\
            "{}"\
            "@{} "\
            "{}"\
            ).format(user,
                  vios,
                  opt1)
    
    if verbose >= 2 and not silent:
       amd.info_msg("  unix_cmd is: ", unix_cmd)

    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
        # Unix_cmd has failed
    if rc!=0:
        if verbose >= 2 and not silent:
            for line in p.stdout:
                print line.strip()

        if quit:
           amd.err_msg("Unable to run cfgdev",
                   exit_code=27)
        else:
           return False
    
        # Unix_cmd executed successfully
    elif rc==0:
        if verbose >= 2 and not silent:
            for line in p.stdout:
                print line.strip()

        if verbose and not silent:
            amd.ok_msg("   >> Virtual adapters are in place for:", vios)
        return True

# }}}
   # SLOT PROCESSING
def get_slot_id_from_file(slot_file, slot_type,  verbose=False, silent=False, quit=True, do_prereq=False): # {{{
    """Retrieving the slot id from file
    file: the file where the slots assignements are keept
        get_vios_slot_file(), get_lpar_vios1_slot_file(), get_lpar_vios2_slot_file()
    slot_type: rootvg, datavg1, datavg2
    do_prereq: Check if HMC is accessible, if MS exists"""

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])


    is_slot=False
    with open(slot_file,'r') as f:
       # Read/print file line by line: 
       for line in f:
           if slot_type in line:
               is_slot=line.split()[1]
               break
    f.close()

    if quit:
        if not is_slot:
            amd.err_msg("Unable to retrieve slot id:",
                    slot_type,
                    "for:",
                    slot_file,
                    exit_code=31)
 
    return is_slot

# }}}
def get_vfchost_based_on_slot(vios, slot_nr, verbose=False, silent=False, quit=True, do_prereq=False): # {{{
    """Determines the vFChost name based on the slot nr.  --> str: vhostN|vfchostN
    slot_nr:    The number of the vios slot
            get_slot_id_from_file()
    $cmd="ssh padmin\@$VIO_B \"ioscli lsmap -all -npiv|grep -w C$_|grep vfchost|awk '{print \\\$1}'\"";
    do_prereq: Check if HMC is accessible, if MS exists"""

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])

    user = "padmin"
    opt1 = " ioscli lsmap -all -npiv|grep -w C{}".format(slot_nr)
    unix_cmd=("ssh "\
            "{}"\
            "@{} "\
            "{}"\
            ).format(user,
                  vios,
                  opt1)
    
    if verbose >= 2 and not silent:
       amd.info_msg("  unix_cmd is: ", unix_cmd)

    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
        # Unix_cmd has failed
    if rc!=0:
        if verbose >= 2 and not silent:
            for line in p.stdout:
                print line.strip()

        if quit:
           amd.err_msg("Unable to identify the vfchost number.",
                   exit_code=27)
        else:
           return False
    
        # Unix_cmd executed successfully

    elif rc==0:
        for line in p.stdout:
            if slot_nr in line:
               return  line.split()[0].strip()
            else:
                amd.err_msg("Unable to retrieve the vfchost nr.", exit_code=31)

        if verbose and not silent:
            amd.ok_msg("   >> vfchost successfully retrieved")

# }}}
def get_vhost_based_on_slot(vios, slot_nr, verbose=False, silent=False, quit=True, do_prereq=False): # {{{
    """Determines the vhost name based on the slot nr.  --> str: vhostN|vfchostN
    slot_nr:    The number of the vios slot
            get_slot_id_from_file()
    $cmd="ssh padmin\@$VIO_B \"ioscli lsmap -all -npiv|grep -w C$_|grep vfchost|awk '{print \\\$1}'\"";
    do_prereq: Check if HMC is accessible, if MS exists"""

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])

    user = "padmin"
    opt1 = " ioscli lsmap -all |grep -w C{}".format(slot_nr)
    unix_cmd=("ssh "\
            "{}"\
            "@{} "\
            "{}"\
            ).format(user,
                  vios,
                  opt1)
    
    if verbose >= 2 and not silent:
       amd.info_msg("  unix_cmd is: ", unix_cmd)

    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
        # Unix_cmd has failed
    if rc!=0:
        if verbose >= 2 and not silent:
            for line in p.stdout:
                print line.strip()

        if quit:
           amd.err_msg("Unable to identify the vhost number.",
                   exit_code=27)
        else:
           return False
    
        # Unix_cmd executed successfully

    elif rc==0:
        for line in p.stdout:
            if slot_nr in line:
               return  line.split()[0].strip()
            else:
                amd.err_msg("Unable to retrieve the vhost nr.", exit_code=31)

        if verbose and not silent:
            amd.ok_msg("   >> vhost successfully retrieved")

# }}}
   # POPULATE VIOS FILES    
def populate_vios_vhost_vfchost_files(vios, vios_slot_file, verbose=False, silent=False, quit=True, do_prereq=False): # {{{
    """Populates the vios_host_file for  the rotovg  slot_nr found in vios_slots file
    e.g 
    rootvg vhostn 
    vios: vios_hostname
    vios_slots_file: filepath: retrieved by: get_vios_slot_file()
    do_prereq: Check if HMC is accessible, if MS exists"""

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])

    vios_vfchost_file=get_vios_processing_dir()+"vfchost_"+str(vios)
    vios_vhost_file=get_vios_processing_dir()+"vhost_"+str(vios)

    vios_vfchost_slots_dic={}
    vios_vhost_slots_dic={}

    with open(vios_slot_file) as f:
        for line in f:
               # DATAVG
            if "rootvg" not in line:
               (key, val) = line.split()
               vios_vfchost_slots_dic[key] = val
            else:
                # ROOTVG
               (key, val) = line.split()
               vios_vhost_slots_dic[key] = val
    f.close()

        
              # DATAVG
    with open(vios_vfchost_file,'w') as f:
        for key,value in vios_vfchost_slots_dic.items():
           f.write(str(key) +" "+ get_vfchost_based_on_slot(vios, value, verbose=verbose) + "\n")
    #      print key,value
    #      print get_vfchost_based_on_slot(vios, value, verbose=verbose)

    f.close()

    
    with open(vios_vhost_file,'w') as f:
        for key,value in vios_vhost_slots_dic.items():
           f.write(str(key) +" "+ get_vhost_based_on_slot(vios, value, verbose=verbose) + "\n")
    #      print key,value
    #      print get_vfchost_based_on_slot(vios, value, verbose=verbose)

    f.close()


    if verbose and not silent:
       amd.ok_msg("   >> File is in place:", vios_vfchost_file)
       amd.ok_msg("   >> File is in place:", vios_vhost_file)

# }}}
def populate_vios_fcs_files(vios, verbose=False, silent=False, quit=True, do_prereq=False): # {{{
    """Populates the vios_fcs_file 
    e.g 
    datavg1  fcs5
    datavg2  fcs7
    vios: vios_hostname
    do_prereq: Check if HMC is accessible, if MS exists"""

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])

    vios_fcs_file=get_vios_fcs_file(vios)   
              # DATAVG
    with open(vios_fcs_file,'w') as f:
           f.write("datavg1 " + datavg1_fcs + "\n")
           f.write("datavg2 " + datavg2_fcs + "\n")
    f.close()

    


    if verbose and not silent:
       amd.ok_msg("   >> File is in place:", vios_fcs_file)

# }}}
   # PHYSICAL TO VIRTUAL FC MAPPINGS
# get_fcs_from_file
def get_fcs_from_file(vios, datavg_type, verbose=False, silent=False, quit=True, do_prereq=False): # {{{
    """Retrieving the fcs from file based on the datavg_type
    file: the file where the datavg_type to fcs mapping is kept
        get_vios_slot_file(), get_lpar_vios1_slot_file(), get_lpar_vios2_slot_file()
    datavg_type:  datavg1, datavg2
    do_prereq: Check if HMC is accessible, if MS exists"""

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])

    local_file = get_vios_fcs_file(vios)

    is_fcs=False
    with open(local_file,'r') as f:
       # Read/print file line by line: 
       for line in f:
           if datavg_type in line:
               is_fcs=line.split()[1]
               break
    f.close()

    if quit:
        if not is_fcs:
            amd.err_msg("Unable to retrieve fcs:", datavg_type,
               "from", local_file, 
               exit_code=31)
 
    return is_fcs

# }}}
# get_vfchost_from_file
def get_vfchost_from_file(vios, datavg_type, verbose=False, silent=False, quit=True, do_prereq=False): # {{{
    """Retrieving the vfchost from file based on the datavg_type
    file: the file where the datavg_type to fcs mapping is kept
    datavg_type:  datavg1, datavg2
    do_prereq: Check if HMC is accessible, if MS exists"""

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])

    local_file = get_vios_vfchost_file(vios)

    is_vfchost=False
    with open(local_file,'r') as f:
       # Read/print file line by line: 
       for line in f:
           if datavg_type in line:
               is_vfchost=line.split()[1]
               break
    f.close()

    if quit:
        if not is_vfchost:
            amd.err_msg("Unable to retrieve vfchost:", datavg_type,
               "from", local_file, 
               exit_code=31)
 
    return is_vfchost

# }}}
# Map vfchost to physical 
def do_physical_to_virtual_vfc_mappings(vios, datavg_type, verbose=False, silent=False, quit=True, do_prereq=False): # {{{
    """Do a physical to virtual mapping for FC
    vios: vios hostname
    datavg_type:  datavg1, datavg2
      based on datavg_type -> vfchost and fcs will be extracted
    $cmd="ssh padmin\@$VIO_B \"ioscli vfcmap -vadapter vfchostN -fcp fcsM";
    do_prereq: Check if HMC is accessible, if MS exists"""

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])

    vfchost = get_vfchost_from_file(vios, datavg_type)
    fcs = get_fcs_from_file(vios, datavg_type)

    user = "padmin"
    opt1 = " ioscli vfcmap -vadapter {} -fcp {}".format(vfchost, fcs)
    unix_cmd=("ssh "\
            "{}"\
            "@{} "\
            "{}"\
            ).format(user,
                  vios,
                  opt1)
    
    if verbose >= 2 and not silent:
       amd.info_msg("  unix_cmd is: ", unix_cmd)

    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
        # Unix_cmd has failed
    if rc!=0:
        if verbose >= 2 and not silent:
            for line in p.stdout:
                print line.strip()

        if quit:
           amd.err_msg("Unable to map physical to virtual FC adaters.",
                   exit_code=27)
        else:
           return False
    
        # Unix_cmd executed successfully
    elif rc==0:
       if verbose and not silent:
          amd.ok_msg("   >> Successfully mapped:", 
             datavg_type, "-->", vios, "-->", vfchost,"-->",fcs)
       return True

# }}}

   # PHYSICAL TO VIRTUAL LU  MAPPINGS
# get_vhost_from_file
def get_vhost_from_file(vios, verbose=False, silent=False, quit=True, do_prereq=False): # {{{
    """Retrieving the vhost from file: str --> vhost
    vios: the vios hostname
    do_prereq: Check if HMC is accessible, if MS exists"""

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])

    local_file = get_vios_vhost_file(vios)

    is_vhost = False
    with open(local_file,'r') as f:
       # Read/print file line by line: 
       for line in f:
           if "rootvg" in line:
               is_vhost=line.split()[1]
               break
    f.close()

    if quit:
        if not is_vhost:
            amd.err_msg("Unable to retrieve vhost:" "from", local_file, 
               exit_code=31)
 
    return is_vhost

# }}}
# Map vfchost to physical 
def do_vhost_to_lu_mapping(vios, lpar_name, verbose=False, silent=False, quit=True, do_prereq=False): # {{{
    """Map vhost to Logical unit
    vios: vios hostname
     mkbdsp -clustername SSPFFM01 -sp SSPFFM01 -vadapter vhost2 
     -bd s370_rvg -tn vtscsi_s370en0
    do_prereq: Check if HMC is accessible, if MS exists"""

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])

    vhost = get_vhost_from_file(vios)
    lu = get_rootvg_lu_name(lpar_name)
    vtscsi_name = "vtscsi_"+str(lpar_name).strip()

    user = "padmin"
    opt1 = "ioscli mkbdsp -clustername SSPFFM01 -sp SSPFFM01 -vadapter {} -bd {} -tn {}".format(vhost, lu, vtscsi_name)
    unix_cmd=("ssh "\
            "{}"\
            "@{} "\
            "{}"\
            ).format(user,
                  vios,
                  opt1)
    
    if verbose >= 2 and not silent:
       amd.info_msg("  unix_cmd is: ", unix_cmd)

    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
        # Unix_cmd has failed
    if rc!=0:
        if verbose >= 2 and not silent:
            for line in p.stdout:
                print line.strip()

        if quit:
            amd.err_msg("Unable to map LU:", lu, "to vhost:",vhost, exit_code=27)
        else:
           return False
    
        # Unix_cmd executed successfully
    elif rc==0:
       if verbose and not silent:
          amd.ok_msg("   >> Successfully mapped:", 
             "rootvg", "-->", vios, "-->", vhost,"-->",lu)
       return True

#}}}
# }}}

# LPAR
   # ACTIVATE SMS MODE
def get_lpar_state(hmc, ms, lpar_name, verbose=False, silent=False, quit=False, do_prereq=False ): # {{{
    """Determines the  lpar state -> str: lpar_state
    hmc:    Target HMC name
    ms:     Target Managed System
    lpar:   The name of the lpar: e.g. s134en0
    do_prereq: Check if HMC is accesible, if MS exists"""

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])

    is_lpar=is_lpar_in_hmc(args.hmc,
            args.destination_managed_system,
            args.source_lpar,
            quit=False)

    if  is_lpar:

    # ssh hscroot@lxsrvhmc0001 lssyscfg -m S04 -r lpar --filter "lpar_names=s370en0" -F state

        user = "hscroot"
        opt1 = "lssyscfg -r lpar -m "
        opt2 = " --filter \"lpar_names={}\"".format(lpar_name)
        opt3 = "-F \"state\""
        unix_cmd=("ssh "\
                "{}"\
                "@{} "\
                "{}"\
                "{}"\
                "{}"\
                " {}"\
                ).format(user,hmc, opt1, ms, opt2, opt3)
        
        if verbose >= 2 and not silent:
           amd.info_msg("  unix_cmd is: ", unix_cmd)

        p = subprocess.Popen(unix_cmd,\
                shell=True, stdout=subprocess.PIPE,\
                stderr=subprocess.STDOUT)
        rc = p.wait()
        
            # Unix_cmd has failed
        if rc!=0:
           if quit:
               amd.err_msg("Unable to determine the LPAR STATE",
                       exit_code=23)
           else:
               return False
        
            # Unix_cmd executed successfully
        elif rc==0:
           line = p.stdout.readlines()[0].strip()
           if verbose and not silent:
                  amd.ok_msg("   >> The  state of the lpar is::", line)

           return line

#  }}}
    # GET MAC
def get_lpar_mac(hmc, ms, lpar_name, verbose=False, silent=False, quit=False, ): # {{{
    """Retrieving the LPAR mac address

    hmc:    Target HMC name
    ms:     Target Managed System 
    lpar_name:   the lpar name"""

    

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])

    local_mac=False

    if verbose and not silent:
        amd.ok_msg("Retrieving the MAC address of the LPAR")
      
    lpar_state=get_lpar_state(args.hmc,
            args.destination_managed_system,
            args.source_lpar, 
            verbose=False,
            silent=True,
            quit=True)

    if "Not Activated" in lpar_state:

            do_lpar_activate_ok_prompt(args.hmc,
            args.destination_managed_system,
            args.source_lpar, 
            verbose=args.verbose,
            quit=True)

# ssh hscroot@lxsrvhmc0001 lshwres -r virtualio --rsubtype eth -m S04 --level lpar  --filter "lpar_names=s370en0,slots=2" -F mac_addr


    user = "hscroot"
    opt1 = "lshwres -r virtualio --rsubtype eth --level lpar -m "
    opt2 = " --filter \"lpar_names={},slots=2\" -F mac_addr".format(lpar_name)
    unix_cmd=("ssh "\
            "{}"\
            "@{} "\
            "{}"\
            "{}"\
            " {}"\
            ).format(user,hmc, opt1, ms, opt2)
    
    if verbose >= 2 and not silent:
       amd.info_msg("  unix_cmd is: ", unix_cmd)

    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
        # Unix_cmd has failed
    if rc!=0:
       if quit:
           amd.err_msg("Unable retrieve the MAC address",
                   exit_code=23)
       else:
           return False
    
        # Unix_cmd executed successfully
    elif rc==0:
        output_list=p.stdout.readlines()
        local_mac=output_list[0].strip()
        if verbose and not silent:
           amd.ok_msg("   >> Mac address is:", local_mac)





    return local_mac



# }}}


    
# STAGE_FUNCTIONS
# Q-1 Collect Node Info# {{{
def do_all_collect_info(source_csm, verbose=False, silent=False, quit=False, ): # {{{
    """Collecting NODE info

    source_csm: Source CSM
    ms:     Target Managed System """
    

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])
      
    if verbose and not silent:
        amd.stage_msg("Starting the SOURCE CSM/LPAR checks")
    is_source_csm_accesible(source_csm, user="root",
       verbose=verbose, silent=True, quit=True)
    
    is_source_lpar_dsh_accesible(args.source_lpar, verbose=verbose, quit=True)



    # Starting  NIM RESOURCE DEFINITION
    if verbose and not silent:
        amd.info_cyan_msg("Starting nim operations: define resources ")


# ---------------TEST 
    amd.ok_msg("Starting NIM test section")
    is_nim_client(args.source_lpar, verbose=verbose, quit=False, silent=False)

# ---------------end_testTEST 


# }}}


# Q3_Q4 HMC/VIOS
def do_hmc_vios_target_lpar_operations(hmc, ms, verbose=False, silent=False, quit=False, ): # {{{
    """Performing hmc operations  related to the target lpar:

    hmc:    Target HMC name
    ms:     Target Managed System """
    

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])
      

    # Starting  HMC/MS
    if verbose and not silent:
        amd.info_cyan_msg("Starting the HMC lpar operations ")

   # Variable collections
    is_lpar=is_lpar_in_hmc(args.hmc,
            args.destination_managed_system,
            args.source_lpar,
            verbose=args.verbose,
            quit=False)

    vios_a_id=get_vios_id(args.hmc,
       args.destination_managed_system,
       get_vio_a_hostname(silent=True),
       verbose=args.verbose,
       silent=True,
       quit=True) 

    vios_b_id=get_vios_id(args.hmc,
       args.destination_managed_system,
       get_vio_b_hostname(silent=True),
       verbose=args.verbose,
       silent=True,
       quit=True) 

    vios_a_hostname=get_vio_a_hostname(silent=True)
    vios_b_hostname=get_vio_b_hostname(silent=True)

    mk_vios_processing_dir(verbose=verbose, quit=True)


    # TESTING with Existing LPAR

    # END OF TESTING with Existing LPAR


    if not is_lpar:

        # Identifying the next available LPAR ID
        if verbose and not silent:
            amd.info_cyan_msg("Identifying the next available LPAR ID")
        next_lpar_id=get_next_lpar_id(args.hmc,
           args.destination_managed_system,
           verbose=args.verbose,
           quit=True) 

        # Identifying three contiguous slots starting from the first one available
        if verbose and not silent:
            amd.info_cyan_msg("Identifying three contiguous slots starting from the first one available")

        eth_slot_id_list=get_eth_slot_ids(args.hmc,
           args.destination_managed_system,
           verbose=args.verbose,
           quit=True) 

        scsi_slot_ids_list=get_scsi_slot_ids(args.hmc,
           args.destination_managed_system,
           verbose=args.verbose,
           quit=True) 




        fc_slot_ids_list=get_fc_slot_ids(args.hmc,
           args.destination_managed_system,
           verbose=args.verbose,
           quit=True) 



        next_slot_id=get_next_slot_id(eth_slot_id_list, scsi_slot_ids_list,
            fc_slot_ids_list,verbose=args.verbose, quit=True) 


        # Creating the Logical Unit to be used as a rootvg substorage system
        if verbose and not silent:
            amd.info_cyan_msg("Creating the rootvg Logical Unit")
            
            if not is_rootvg_lu(vios_a_hostname,args.source_lpar,verbose=verbose):
                mk_rootvg_lu(vios_a_hostname,args.source_lpar,verbose=verbose )




#         amd.ok_msg("==== DEBUG EXITING ======")
#         sys.exit(0)

        # Creating the lpar 
        if verbose and not silent:
            amd.info_cyan_msg("Creating the lpar")
        create_target_lpar(args.hmc,
            args.destination_managed_system,
            next_slot_id,
                next_lpar_id,
                verbose=verbose,
                quit=True)

        # Updating the VIOS virtual_scsi  profile
        if verbose and not silent:
            amd.info_cyan_msg("Updating the VIOSs profiles to include virtual_scsi mappings")




            # Updating the VIOS_A virtual_scsi  profile
        update_vios_scsi_profile(hmc,
              ms,
              root_vg_slot_a,
              next_lpar_id,
              vios_a_id,
              next_slot_id,
              verbose=verbose,
              quit=True)

            # Updating the VIOS_A virtual_scsi  profile
        update_vios_scsi_profile(hmc,
              ms,
              root_vg_slot_b,
              next_lpar_id,
              vios_b_id,
              next_slot_id,
              verbose=verbose,
              quit=True)


        # Updating the VIOS virtual_FC  profile
        if verbose and not silent:
            amd.info_cyan_msg("Updating the VIOSs profiles to include virtual_FC mappings")

            # Updating the VIOS_A virtual_scsi  profile
        update_vios_FC_profile(hmc,
              ms,
              data_vg1_slot_a,
              data_vg2_slot_a,
              next_lpar_id,
              vios_a_id,
              next_slot_id,
              verbose=verbose,
              quit=True)


            # Updating the VIOS_B virtual_scsi  profile
        update_vios_FC_profile(hmc,
              ms,
              data_vg1_slot_b,
              data_vg2_slot_b,
              next_lpar_id,
              vios_b_id,
              next_slot_id,
              verbose=verbose,
              quit=True)




        #  DLPAR
        # Performing VIOS mapping for vscsi
        if verbose and not silent:
            amd.info_cyan_msg("Performing VIOS slot mapping for vscsi (VIOS --> LPAR)")

         #  VSCSI mappings VIOS_A
        dlpar_scsi_slot_mapping(hmc,
              ms,
              root_vg_slot_a,
              next_lpar_id,
              vios_a_id,
              next_slot_id,
              verbose=verbose,
              quit=True)


         #  VSCSI mappings VIOS_A
        dlpar_scsi_slot_mapping(hmc,
              ms,
              root_vg_slot_b,
              next_lpar_id,
              vios_b_id,
              next_slot_id,
              verbose=verbose,
              quit=True)





        # Performing VIOS mapping for FC/NPIV 
        if verbose and not silent:
            amd.info_cyan_msg("Performing VIOS slot mapping for FC (VIOS --> LPAR)")

         #  VSCSI mappings VIOS_A
        dlpar_FC_slot_mapping(hmc,
              ms,
              data_vg1_slot_a,
              next_lpar_id,
              vios_a_id,
              next_slot_id + 1,
              verbose=verbose,
              quit=True)


        dlpar_FC_slot_mapping(hmc,
              ms,
              data_vg2_slot_a,
              next_lpar_id,
              vios_a_id,
              next_slot_id + 2,
              verbose=verbose,
              quit=True)


         #  VSCSI mappings VIOS_B
        dlpar_FC_slot_mapping(hmc,
              ms,
              data_vg1_slot_b,
              next_lpar_id,
              vios_b_id,
              next_slot_id + 1,
              verbose=verbose,
              quit=True)


        dlpar_FC_slot_mapping(hmc,
              ms,
              data_vg2_slot_b,
              next_lpar_id,
              vios_b_id,
              next_slot_id + 2,
              verbose=verbose,
              quit=True)


        # CFGDEV
        if verbose and not silent:
            amd.info_cyan_msg("Detecting the new virtual adapters")
        do_FC_cfgdev(get_vio_a_hostname(), verbose=verbose, quit=True)
        do_FC_cfgdev(get_vio_b_hostname(), verbose=verbose, quit=True)


        # Populating vios_host file
        if verbose and not silent:
            amd.info_cyan_msg("Populating the vfchost, fcs and vhost  files")
        for vios in [vios_a_hostname, vios_b_hostname]:
            populate_vios_vhost_vfchost_files(vios,
                    get_vios_slot_file(),
                    verbose=verbose)

            # Populating FCS  file # These are the Physical ports
            populate_vios_fcs_files(vios,verbose=verbose)


        # Performing VIOS Physical to Virtual
        if verbose and not silent:
            amd.info_cyan_msg("Performing VIOS Physical to Virtual mappings")
        for vios in [vios_a_hostname, vios_b_hostname]:
           for datavg_type in ["datavg1", "datavg2"]:
              do_physical_to_virtual_vfc_mappings(vios,
                    datavg_type,
                    verbose=verbose)


        # Performing VIOS LU to vhost mapping
        if verbose and not silent:
            amd.info_cyan_msg("Performing VIOS Logical Unit to vhost mappings")
        for vios in [vios_a_hostname, vios_b_hostname]:
            do_vhost_to_lu_mapping(vios, args.source_lpar, verbose=verbose)


    if verbose and not silent:
        amd.ok_msg("End of: HMC/VIOS Operations \n")



# }}}

# Q4 LPAR_ACTIVATE_OK
# ACTIVATE LPAR INTO OK PROMPT
# EXTRACT MAC ADDRESS
def do_lpar_all_activation_operations(hmc, ms, lpar_name, verbose=False, silent=False, quit=False, ): # {{{
    """Performing Lpar Activation and mac retrieval

    hmc:    Target HMC name
    ms:     Target Managed System 
    lpar_name The name of the lpar e.g. s370en0"""

    

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])

    #

    do_lpar_activate_ok_prompt(args.hmc,
            args.destination_managed_system,
            args.source_lpar, 
            verbose=args.verbose,
            quit=True)





# }}}

# Q-4 LPAR_SHUTDOWN
# DEACTIVATE LPAR INTO OK PROMPT
def do_lpar_all_deactivation_operations(hmc, ms, lpar_name, verbose=False, silent=False, quit=False, ): # {{{
    """Performing Lpar Activation and mac retrieval

    hmc:    Target HMC name
    ms:     Target Managed System 
    lpar_name The name of the lpar e.g. s370en0"""

    

    if verbose >= 2:
       amd.debug_msg("Start of:#  ", inspect.stack()[0][3])

    #

    do_lpar_deactivate(args.hmc,
            args.destination_managed_system,
            args.source_lpar, 
            verbose=args.verbose,
            quit=True)





# }}}

# }}}
# }}}

#       HERE IT GOES            ## {{{
# ------------------------------# 
# ------------------------------# 
#if ((not args.add_dummy_profile) and 
#    (not args.delete_profile) and
#    (not args.list_profiles) and 
#    (not args.rename_profile) and 
#    (not args.restore_default_profile) and 
#    (not args.activate_dummy_profile) and 
#    (not args.activate_default_profile)): 
#    amd.err_msg("No Action has been specified")
#    sys.exit(1)


amd.ok_msg("Here it goes:")

# -b (check for syntax error)
if args.backup_profile and not args.filename:
    amd.err_msg("Please specify the file name by using the -f flag, see bellow:")
    print "# manage_profile.py  -s s230en0 -M S04 -H lxsrvhmc0001 -b -f /tmp"
    sys.exit(5)

elif args.filename and not args.backup_profile:
    amd.err_msg("Please specify the backup action -b, see bellow:")
    print "# manage_profile.py  -s s230en0 -M S04 -H lxsrvhmc0001 -b -f /tmp"
    sys.exit(5)





# PREREQUISITES
amd.info_msg("START OF:  INFRASTRUCTURE PREREQUISITES")
do_infra_prereq(args.hmc, 
   args.destination_managed_system,
   verbose=args.verbose, quit=True)


amd.info_msg("START OF:  PROFILE MANAGEMENT")
# Add dummy profile
# -a
if args.add_dummy_profile:
    if args.profile_name:
        amd.info_msg("Custum dummy names not allowed, using dummy_profile")
        amd.info_msg("-n flag will be ignored for this action")
    amd.ok_msg("Creating the dummy profile")
    create_dummy_profile(args.hmc,
        args.destination_managed_system,
        args.source_lpar,
        verbose=args.verbose,
        quit=True)

# -b
if args.backup_profile and args.filename:
    save_profile(args.hmc,
        args.destination_managed_system,
        args.source_lpar,
        file_name=args.filename,
        prof_name="default",
        verbose=args.verbose,
        quit=True)

# -d
if args.delete_profile:
    if not args.profile_name:
        amd.info_msg("You haven't specified a profile name, dummy_profile will be used")
        amd.ok_msg("Deleting  dummy_profile")
    remove_profile(args.hmc,
        args.destination_managed_system,
        args.source_lpar,
        profile_name=args.profile_name,
        verbose=args.verbose,
        quit=True)

# -l
if args.list_profiles:
    amd.ok_msg("Listing profiles")
    list_all_lpar_profiles(args.hmc,
        args.destination_managed_system,
        args.source_lpar,
        verbose=args.verbose,
        quit=True)

# -r
if args.rename_profile:
    if (not args.profile_name or not args.new_profile_name):
       amd.err_msg("-n and -N are mandatory for this action see help/EXAMPLES")
#        args_help
       sys.exit(1)
    amd.ok_msg("Renaming a profile")

    rename_profile(args.hmc,
        args.destination_managed_system,
        args.source_lpar,
        old_prof_name=args.profile_name, 
        new_prof_name=args.new_profile_name, 
        verbose=args.verbose,
        quit=True)


# -u
if args.restore_default_profile:
    print "Restoring the default profile"
    restore_default_profile(args.hmc,
        args.destination_managed_system,
        args.source_lpar,
        profile_name="default",
        verbose=args.verbose,
        quit=True)


# -A
if args.activate_dummy_profile:
    print "Activating the dummy profile"
    activate_dummy_profile_v2(args.hmc,
        args.destination_managed_system,
        args.source_lpar,
        verbose=args.verbose,
        quit=True)

# -R
if args.activate_default_profile:
    print "Reactivating the premigration profile"
    activate_default_profile(args.hmc,
        args.destination_managed_system,
        args.source_lpar,
        verbose=args.verbose,
        quit=True)


# -Z
if args.deactivate_lpar:
    print "Shutting down the lpar"
    do_lpar_deactivate(args.hmc,
        args.destination_managed_system,
        args.source_lpar,
        verbose=args.verbose,
        quit=True)







# }}}

















