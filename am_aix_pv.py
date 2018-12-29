#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" This module is used to retrieve PV Physical Volume information
It contains the following main sections
    get_all_pv
        - Returns a list of all the Physical Volumes
    get_all_pvid_pv
        - Returns a list of all the Physical Volumes that have a PVID
    get_all_root_pv
        - Returns a list of all the Physical Volumes included into rootvg
    get_all_nonvg_pv: get_all_free_pv
        - Returns a list of all the PV that do not belong to a Volume Group
    - returns all pv-pvid dictionary
    get_all_none_pv
    - returns pv names list of pv that do not belong to a VG
Example:
import am_aix_pv
pv_lit=get_all_pv()

Todo:
"""

# For AIX
# Metro Info#{{{
# ----------------------------------------------------------------------------
#
# NAME:         am_aix_pv.py
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
# Date:    24.09.2018  
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
#  24.09.2018 v 1.00/history:
# 
#			  24.09.2018 v 1.0.0/Fist version
#
# ----------------------------------------------------------------------------
#
# ToDo:         Further tasks
#
# ----------------------------------------------------------------------------
#
#}}}



import subprocess
import sys
sys.path.append("/usr/local/rootbin/Pythonlib/")
import amdisplay
amd=amdisplay.AmDisplay()

def get_all_pv():# {{{
    """Returns a list of all PV names
    :returns: list: pv_name
    """
    unix_cmd=("/usr/sbin/lspv")
    
    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
   
    pv_list=[]
    if rc!=0:
       return False
    
    elif rc==0:
       for line in p.stdout:
           pv=line.split()[0]
           if pv:
               pv=pv.strip()
               pv_list.append(pv)
    
       return pv_list
    
# }}}
def get_all_pvid_pv():# {{{
    """Returns a list of all PV names that have an PVID assigned
    :returns: list: pv_name
    """
    unix_cmd=("/usr/sbin/lspv")
    
    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
   
    pv_list=[]
    if rc!=0:
       return False
    
    elif rc==0:
       for line in p.stdout:
           pv=line.split()[0]
           pvid=line.split()[1]
           if pvid:
               if not "none" in pvid:
                   pv=pv.strip()
                   pv_list.append(pv)

       return pv_list
    
# }}}
def get_all_root_pv():# {{{
    """Returns a list of all the PV names included into rootvg
    :returns: list: pv_name
    """
    unix_cmd=("/usr/sbin/lspv")
    
    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
   
    pv_list=[]
    if rc!=0:
       return False
    
    elif rc==0:
       for line in p.stdout:
           pv=line.split()[0]
           vg_name=line.split()[2]
           if vg_name:
               if "rootvg" in vg_name:
                   pv=pv.strip()
                   pv_list.append(pv)

       return pv_list
    
# }}}
def get_all_free_pv():# {{{
    """Returns a list of all the PV that do not belong to a Volume Group
    :returns: list: pv_name
    """
    unix_cmd=("/usr/sbin/lspv")
    
    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
   
    pv_list=[]
    if rc!=0:
       return False
    
    elif rc==0:
       for line in p.stdout:
           pv=line.split()[0]
           vg_name=line.split()[2]
           if vg_name:
               if "None" in vg_name:
                   pv=pv.strip()
                   pv_list.append(pv)

       
       
       return pv_list
    
# }}}
def is_vg_in_vgda(pv, vgid, exit=True):# {{{
    """ Checks if the  VG is part of the vgda 
    :pv     : The Physical Volume name. e.g. pv10
    :vgid     : The Volume group name. .e.g 00c76b0700004c000000014b7c82d722
    :quit:   : Exit on error, specifically unix_cmd error

    : example 
    : my_vg = is_vg_in_vgda("hdisk0", "rootvg")
    :returns: bool
    """
    unix_cmd=('/usr/sbin/readvgda -q {} '.format(pv))

    p = subprocess.Popen(unix_cmd,\
            shell=True,
            bufsize=98192,
            stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()

    is_vg = False 

#     print unix_cmd
   
    if rc!=0:
       if quit:
           amd.err_msg("Unable to execute command:", unix_cmd,  exit_code=1)
    
    elif rc==0:
       for line in p.stdout:
           if line:
               if "VGID" in line: 
                   if vgid in line: 
                       is_vg=True
                       return is_vg
    return is_vg
    
# }}}





# MAIN
if __name__ == "__main__":
    print "\n# Printing all PVs"
    print get_all_pv()
    print "\n# Printing all PVs with a PVID"
    print get_all_pvid_pv()
    print "\n# Printing all rootvg PVs"
    print get_all_root_pv()
    print "\n# Printing all FREE PVs"
    print get_all_free_pv()
    print "\n# Checkinf if VG is in readvgda. For testing on s230 only"
#     is_vg_in_vgda('hdisk0', 'rootvg')
    print is_vg_in_vgda('hdisk12', '00c76b0700004c000000014b7c82d722')
    print is_vg_in_vgda('hdisk12', '00c76b0700004c000000014b7c82d722T')
