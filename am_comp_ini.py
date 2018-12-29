#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" This module is used to compile the node_ini_lpar file.
It has two main use-cases: 
    -It compiles the network configuration strings which are used to build the 
        node_firstboot_migration_lpar file

    -It compiles the LVM strings used for importing the VGs after the migration

    Main functions: 
        # Networking
    compile_ip_string
    compile_ip_alias_string
    compile_default_route_string
Example:

    ip_string=compile_ip_string(ini_file)
    alias_string=compile_ip_alias_string(ini_file)
    route_string=compile_default_route_string(ini_file)



Todo:
    Compile  LVM Stings


"""





# Imports# {{{
import os
import argparse, textwrap
import subprocess
import socket
import inspect
import datetime
import fileinput
import time
import sys
import logging
from argparse import RawTextHelpFormatter
from ConfigParser import SafeConfigParser
sys.path.append("/usr/local/rootbin/Pythonlib/")
import amdisplay
import am_aix_hostname
import am_aix_user
# import am_aix_lvm
from  am_logging import pfn


# }}}
# For AIX
# Metro Info#{{{
# ----------------------------------------------------------------------------
#
# NAME:         get_premig_config.py
#
# Purpose:      Retrieves premigration configuration value from the fowlling
#               default location: /csmiages/node_ini_lpar_name
#
# Parameter:    see -h
#
# ----------------------------------------------------------------------------
#
# Author:       aldo@metrosystems.net
# 				mircea.aldo@gmail.com
#
# Date:    21.09.2018  
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
#  21.09.2018 v 1.00/history:
# 
#			  21.09.2018 v 1.0.0/Fist version
#
# ----------------------------------------------------------------------------
#
# ToDo:         Further tasks
#
# ----------------------------------------------------------------------------
#
#}}}




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
# my_name=__file__.split(\)[1]
my_name=__file__.split("/")[-1]
parser = argparse.ArgumentParser(
   description= """This utility collects the live configuration of a running
   partition. The configuration data is placed into an .ini file with a
   standard config format. Default file location is :/space/node_ini_lparname.
   The main use-case for this file is migration, post-migration configuration 

EXAMPLES:
# Collect live system configuration to the default location
    {}

# Collect live system configuration to /tmp/conf_file.ini
    {} -f /tmp/conf_file.ini

# List live system configuration in config format
    {} -l 

    """.format(my_name,my_name,my_name)

        ,formatter_class=argparse.RawTextHelpFormatter
        )


# Adding the action mutually exclusive groups
action_group = parser.add_argument_group()


file_group=parser.add_mutually_exclusive_group()
file_group.add_argument("-f","--file_path",
        action="store",
        help="""Specify the file location
     Custom configuration names are not allowed""")

file_group.add_argument("-l","--list_conf",
        action="store_true",
        help="""List the current partition configuration """)


# Adding the -v/-q mutually exclusive group
verbose_group=parser.add_mutually_exclusive_group()
verbose_group.add_argument("-v","--verbose",
        action="count",
        help="Show what is going on")




# }}}
# Display mnd logging initialization # {{{
amd=amdisplay.AmDisplay()
# LOGGING Settings
logging.basicConfig(format='%(asctime)s %(message)s',
    level=logging.DEBUG,
    datefmt='%d-%m-%Y %I:%M:%S ')

# }}}

# Temp
ini_file = '/space/node_ini_s230en0'

# General Functions
    # Atomic
def get_ini_sections(ini_file, verbose=False, quit=True):# {{{
    """Retrieves the list of sections names
    :conf_file: The ini configuration file 
    :verbose:   Show what is going on
    :quit:      Suppresses output 
    :: TODO
    """
    pfn(verbose=verbose)

    conf_file=ini_file  # Configuration file filename
    
    config = SafeConfigParser()
    config.optionxform = str
    config.read(conf_file)
   
    return config.sections()
    # }}}
def get_ini_options(ini_file, section, verbose=False, quit=True):# {{{
    """Retrieves the options of a given section name
    :conf_file: The ini configuration file 
    :verbose:   Show what is going on
    :quit:      Exit on errr
    :returns:   list
    """
    pfn(verbose=verbose)

    conf_file=ini_file  # Configuration file filename

    config = SafeConfigParser()
    config.optionxform = str
    config.read(conf_file)
  
    if not config.has_section(section):
        amd.err_msg("Inexistent section:", section, exit_code=1)

    option_list=config.options(section)

    return option_list

# }}}
def get_ini_items(ini_file, section, verbose=False, quit=True):# {{{
    """Retrieves the items of a section
    :conf_file: The ini configuration file 
    :verbose:   Show what is going on
    :quit:      Exit on errr
    """
    pfn(verbose=verbose)

    conf_file=ini_file  # Configuration file filename

    config = SafeConfigParser()
    config.optionxform = str
    config.read(conf_file)
  
    if not config.has_section(section):
        amd.err_msg("Inexistent section:", section, exit_code=1)

    items=config.items(section)

    return items

# }}}
def get_ini_value(ini_file, section, option, verbose=False, quit=True):# {{{
    """Retrieves the value of an option
    :conf_file: The ini configuration file 
    :verbose:   Show what is going on
    :quit:      Exit on errr
    """
    pfn(verbose=verbose)

    conf_file=ini_file  # Configuration file filename

    config = SafeConfigParser()
    config.optionxform = str
    config.read(conf_file)
  
    if not config.has_section(section):
        amd.err_msg("Inexistent section:", section, exit_code=1)
    if not config.has_option(section, option):
        amd.err_msg("Inexistent option:",
            option,
            "in section:",
            section,
            "in the file:",
            ini_file,
            exit_code=1)


    value = config.get(section, option)

    return value

# }}}
def get_ini_values(ini_file, section,  verbose=False, quit=True):# {{{
    """Returns all the  values of a section
    :conf_file: The ini configuration file 
    :verbose:   Show what is going on
    :quit:      Exit on err
    """
    pfn(verbose=verbose)

    conf_file=ini_file  # Configuration file filename

    config = SafeConfigParser()
    config.optionxform = str
    config.read(conf_file)
  
    if not config.has_section(section):
        amd.err_msg("Inexistent section:", section, exit_code=1)

    values_list=[]


    opt_value_items=get_ini_items(ini_file, section)
    # Converting the list of tuples into a dictionary for better parsing
    opt_value_dct = dict(opt_value_items)

    for opt,val in opt_value_dct.items():
        values_list.append(val)

    return values_list



# }}}


# ROOT Functions
    # Atomic
def get_root_homedir(ini_file, verbose=False, quit=True):# {{{
    """Returns the 
    :verbose:   Show what is going on
    :quit:      Exit on err
    """
    pfn(verbose=verbose)
   
    root_home=False
    root_home=get_ini_value(ini_file, "root", "home")
    return root_home

# }}}



# IP Functions
    # Atomic
def get_net_adapters(ini_file, verbose=False, quit=True):# {{{
    """Returns a list of active net addapters
    :verbose:   Show what is going on
    :quit:      Exit on err
    """
    pfn(verbose=verbose)
    return get_ini_options(ini_file, "net_adapters",verbose=verbose, quit=True)

# }}}
def get_ip_addrs(ini_file, section="net_addapters",verbose=False,  quit=True):# {{{
    """Returns all the ip addresses
    :verbose:   Show what is going on
    :quit:      Exit on err
    """
    pfn(verbose=verbose)
    ip_addrs_list=[]
    net_adapters_list=get_net_adapters(ini_file)
    for adapter in net_adapters_list:
        ip_addr = get_ini_value(ini_file, "ip_addr", adapter)
        ip_addrs_list.append(ip_addr)
    return ip_addrs_list

# }}}
def get_alias_addrs(ini_file, section="alias_addr",verbose=False,  quit=True):# {{{
    """Returns all the IP ALIASES 
    :verbose:   Show what is going on
    :quit:      Exit on err
    """
    pfn(verbose=verbose)
    ip_alias_list=[]
    alias_items=get_ini_items(ini_file, section)
    for item in alias_items:
        ip_alias_list.append(item[1])

    return ip_alias_list

# }}}
def get_def_routes(ini_file, section="default_route",verbose=False,  quit=True):# {{{
    """Returns all the Default Routes
    :verbose:   Show what is going on
    :quit:      Exit on err
    """
    pfn(verbose=verbose)
    default_route_list=[]
    default_route=get_ini_options(ini_file, section)
    for route in default_route:
        if route:
            default_route_list.append(route)

    return default_route_list

# }}}


    # Composite / Firstboot
def compile_ip_string(ini_file,verbose=False, quit=True):# {{{
    """Compiles the ip configuration and returns a string
    # /usr/sbin/chdev -l $dev -a netaddr=$addr -a netmask=$mask -a state=$state 2>&1)

    :conf_file: The ini configuration file : default : /space/node_ini_lpar
    :returns: string
    """
    pfn(verbose=verbose)

    adapter_list=get_ini_options(ini_file, "ip_addr")
    ip_config_string=""
    for adapter in adapter_list:
        ip = get_ini_value(ini_file, "ip_addr", adapter)
        mask = get_ini_value(ini_file, "ip_netmask", adapter)
        ip_config_string +=\
                "/usr/sbin/chdev -l {} -a netaddr={} -a netmask={} -a state=up \n".\
                format(adapter, ip, mask)

    return ip_config_string
# }}}
def compile_ip_alias_string(ini_file,verbose=False, quit=True):# {{{
    """Compiles the ip Alias  configuration and returns a string
    # /usr/sbin/chdev -l en2 -a alias4=164.139.216.14,255.255.255.128

    :conf_file: The ini configuration file : default : /space/node_ini_lpar
    :returns: string
    """
    pfn(verbose=verbose)

    adapter_list=get_ini_options(ini_file, "alias_addr")
    alias_config_string=""
    for adapter in adapter_list:
        ip = get_ini_value(ini_file, "alias_addr", adapter)
        mask = get_ini_value(ini_file, "alias_netmask", adapter)
        alias_config_string +=\
                "/usr/sbin/chdev -l {} -a alias4={},{}\n".\
                format(adapter, ip, mask)

    return alias_config_string
# }}}
def compile_default_route_string(ini_file,verbose=False, quit=True):# {{{
    """Compiles default route string
    #/usr/sbin/chdev -l inet0 -a route=net,-hopcount,0,,,,,,0,$gw 

    :conf_file: The ini configuration file : default : /space/node_ini_lpar
    :returns: string
    """
    pfn(verbose=verbose)

    route_list=get_ini_options(ini_file, "default_route")
    default_route_config_string=""
    for route in route_list:
        default_route_config_string +=\
                "/usr/sbin/chdev -l inet0 -a route=net,-hopcount,0,,,,,,0,{}\n".\
                format(route)

    return default_route_config_string
# }}}



# LVM Functions
    # Atomic
def get_active_vg_and_major(ini_file, verbose=False, quit=True):# {{{
    """Returns a list of of active VGs and their Major Numbers
    :verbose:   Show what is going on
    :quit:      Exit on err
    """
    pfn(verbose=verbose)

    return get_ini_items(ini_file, "vg_active",verbose=verbose, quit=True)

# }}}
def get_active_vg(ini_file, verbose=False, quit=True):# {{{
    """Returns a list of active VGs 
    :verbose:   Show what is going on
    :quit:      Exit on err
    """
    pfn(verbose=verbose)

    return get_ini_options(ini_file, "vg_active",verbose=verbose, quit=True)

# }}}
def get_Major(ini_file, vg,  verbose=False, quit=True):# {{{
    """Returns a string representing the Major number of  the file
    :verbose:   Show what is going on
    :quit:      Exit on err
    """
    pfn(verbose=verbose)
   
    major=False
    major=get_ini_value(ini_file, "vg_active", vg)

    return major

# }}}
def get_vgid(ini_file, vg,  verbose=False, quit=True):# {{{
    """Returns a string representing the vgid number of  the file
    :verbose:   Show what is going on
    :quit:      Exit on err
    """
    pfn(verbose=verbose)
   
    vgid=False
    vgid=get_ini_value(ini_file, "vg_id", vg)

    return vgid

# }}}



# GPFS Functions
    # Atomic
def get_gpfs_manager(ini_file, verbose=False, quit=True):# {{{
    """Returns  list|False:    The ip ddr/hostname of the gpfs manager
    :verbose:   Show what is going on
    :quit:      Exit on error
    """
    pfn(verbose=verbose)

    return get_ini_options(ini_file,
            "gpfs_cluster_manager",
            verbose=verbose,
            quit=True)

# }}}
def get_gpfs_nsd(ini_file, verbose=False, quit=True):# {{{
    """Returns  list|False:    The NSD list of the gpfs
    :verbose:   Show what is going on
    :quit:      Exit on error
    """
    pfn(verbose=verbose)

    return get_ini_options(ini_file,
            "gpfs_nsd_list",
            verbose=verbose,
            quit=True)

# }}}
def get_gpfs_fs_list(ini_file, verbose=False, quit=True):# {{{
    """Returns  list|False:    The NSD list of the gpfs
    :verbose:   Show what is going on
    :quit:      Exit on error =verbose)"""

    pfn(verbose=verbose)

    return get_ini_values(ini_file,
#             "gpfs_mounted_fs",
           "gpfs_mounted_fs",
            verbose=verbose,
            quit=True)


# }}}


# AME Function
def get_ame_factor(ini_file, verbose=False, quit=True):# {{{
    """Returns the Active Memory Expansion factor
    :verbose:   Show what is going on
    :quit:      Exit on err
    """
    pfn(verbose=verbose)
   
    ame=False
    ame=get_ini_value(ini_file, "lparstat", "target memory expansion factor")
    return ame

# }}}
def get_ame_max_memory(ini_file, verbose=False, quit=True):# {{{
    """Returns str: the Maximum Memory in MB
    :verbose:   Show what is going on
    :quit:      Exit on err
    """
    pfn(verbose=verbose)
   
    max_mem=False
    max_mem=get_ini_value(ini_file, "lparstat", "maximum memory")
    if "MB" in max_mem:
       max_mem=max_mem.split()[0]
    return max_mem

# }}}
def get_ame_target_memory(ini_file, verbose=False, quit=True):# {{{
    """Returns str: the target Memory Expansion Size MB
                  : This is the actual memory size of the lpar
    :verbose:   Show what is going on
    :quit:      Exit on err
    """
    pfn(verbose=verbose)
   
    target_mem=False
    target_mem=get_ini_value(ini_file,
          "lparstat",
          "target memory expansion size")
    if "MB" in target_mem:
       target_mem=target_mem.split()[0]
    return target_mem

# }}}





# Here it goes
# Playing Around
if __name__ == "__main__":
    pass
#
#    # Parsing all the arguments
#    args=parser.parse_args()
#    # args_help=parser.print_help()
#
#
#    print get_ini_sections(ini_file, verbose=args.verbose)
#
#    print get_ini_options(ini_file, "ip_netmask",verbose=args.verbose, quit=True)
#    print get_ini_options(ini_file, "net_adapters",verbose=args.verbose, quit=True)
#    print get_ini_options(ini_file, "ip_addr",verbose=args.verbose, quit=True)
#    print get_ini_options(ini_file, "default_route",verbose=args.verbose, quit=True)
#    print get_ini_options(ini_file, "rootvg",verbose=args.verbose, quit=True)
#
#
#    ip_addr_option_list=get_ini_options(ini_file, "ip_addr", verbose=args.verbose)
#    print "---{}".format(ip_addr_option_list)
#    print ""
#    for option in ip_addr_option_list:
#        value = get_ini_value(ini_file, "ip_addr", option, verbose=args.verbose, quit=True)
#        print option + " "+ value
#
#
#    amd.info_green_msg("LVM FUNCTIONS")
#    print get_vgid(ini_file, "VGS230DB1")
#







