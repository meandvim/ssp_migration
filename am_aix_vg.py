#!/usr/bin/env python
# -*- coding: utf-8 -*-


""" This module is used to retrieve VG Volume Group information
It contains the following main sections
    get_all_vg
        - Returns a list of all the Volume Groups
    get_all_active_vg
        - Returns a list of all the active VG names
    get_all_non_rootvg_vg
        - Returns a list of all VG names which are not rootvg
    get_all_active_non_rootvg_vg
        - Returns a list of all the active VG names which are not rootvg
    is_vg(vg_name)
        - returns bool: checks if a vg exists
Example:
import am_aix_vg
pv_lit=get_all_vg()

Todo:
"""
import sys
import subprocess
sys.path.append("/usr/local/rootbin/Pythonlib/")
from am_logging  import pfn
from amdisplay import AmDisplay
amd=AmDisplay()

def get_all_vg():# {{{
    """Returns a list of all VG names
    :returns: list: vg_name
    """
    unix_cmd=("/usr/sbin/lsvg")
    
    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
   
    vg_list=[]
    if rc!=0:
       return False
    
    elif rc==0:
       for line in p.stdout:
           vg=line.split()[0]
           if vg:
               vg=vg.strip()
               vg_list.append(vg)
    
       return vg_list
    
# }}}
def get_all_active_vg():# {{{
    """Returns a list of all the active VG names
    :returns: list: vg_name
    """
    unix_cmd=("/usr/sbin/lsvg -o ")
    
    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
   
    vg_list=[]
    if rc!=0:
       return False
    
    elif rc==0:
       for line in p.stdout:
           vg=line.split()[0]
           if vg:
               vg=vg.strip()
               vg_list.append(vg)
    
       return vg_list
    
# }}}
def get_all_non_rootvg_vg():# {{{
    """Returns a list of all VG names which are not rootvg
    :returns: list: vg_name
    """
    unix_cmd=("/usr/sbin/lsvg")
    
    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
   
    vg_list=[]
    if rc!=0:
       return False
    
    elif rc==0:
       for line in p.stdout:
           vg=line.split()[0]
           if vg:
               if 'rootvg' not in vg:
                   vg=vg.strip()
                   vg_list.append(vg)
    
       return vg_list
    
# }}}
def get_all_active_non_rootvg_vg():# {{{
    """Returns a list of all the active VG names which are not rootvg
    :returns: list: vg_name
    """
    unix_cmd=("/usr/sbin/lsvg -o ")
    
    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
   
    vg_list=[]
    if rc!=0:
       return False
    
    elif rc==0:
       for line in p.stdout:
           vg=line.split()[0]
           if vg:
               if 'rootvg' not in vg:
                   vg=vg.strip()
                   vg_list.append(vg)
    
       return vg_list
    
# }}}

def is_vg(vg_name):# {{{
    """Determines if a VG exists or not
    :returns: bool
    """
    unix_cmd=("/usr/sbin/lsvg {} ").format(vg_name)
    
    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
   
    vg_list=[]
    if rc!=0:
       return False
    
    elif rc==0:
       return True
    
# }}}

def import_vg(vg,major,pv,verbose=False, q=True, activate=True):
    """Imports a Volume Group from a PV

    :vg:    The vg name: e.g. VGS230BASE 
    :major: The major number used for importing the vg. e.g. 100
    :pv:    The Phisical Volume name used to import the VG e.g. hdisk12 
    :v:      Verbosity, show what is going on
    :q:      Quit on erorr: True
    :returns: bools
    :cmd:   importvg -V 100 -y  VGS230BASE hdisk5

    : examples   import_vg("VGS230BASE", "100", "hdisk12")
                 import_vg("VGS230BASE", "100", "hdisk12", verbose=2)

    :Todo:  Implement other importvg specific flags
    """
    pfn(verbose)
    if verbose:
       amd.info_cyan_msg("Starting to import the Volume Group")

    unix_cmd=("/usr/sbin/importvg "\
            " -V {} "\
            " -y {}"\
            "  {}"\
            ).format(major,vg, pv)
    
    if verbose >= 2:
        print "Debugging:unix_cmd is:{}:".format(unix_cmd)	# FOR Debugging
    
    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
        # Unix_cmd has failed
    if rc!=0:
        if q:
            amd.err_msg("Unable to import the vg:", vg, exit_code=1)
        else:
            if v:
                amd.err_msg("Unable to import the vg:", vg,)
        return False
    
    
        # Unix_cmd executed successfully
    elif rc==0:
        if verbose >= 2:
            amd.ok_msg("VG has been successfully imported:")
        return True
    


if __name__ == "__main__":
    print "\n# Printing all VGs"
    print get_all_vg()
    print "\n# Printing all Active VGs"
    print get_all_active_vg()
    print "\n# Printing all Non rootvg VGs"
    print get_all_non_rootvg_vg()
    print "\n# Printing all Active Non rootvg VGs"
    print get_all_active_non_rootvg_vg()
    print "\n# Checking if a VG exits"
    print is_vg("rootvg")
    
    #print "\n# Importing the vg"
    #print "\n\n VEEERRRBOSE"
    #import_vg("VGS230BASE", "100", "hdisk12", verbose=2)

    #print "\n\n SILENT"
    #print import_vg("VGS230BASE", "100", "hdisk12", q=False, verbose=2)
