#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" This module is used to retrieve the root user configuration
It contains the following main sections
    get_homedir
        - Returns the rootvg homedir
Example:
import am_aix_root
root_home=get_root_home()

Todo:
"""

# For AIX

# For AIX
# Metro Info#{{{
# ----------------------------------------------------------------------------
#
# NAME:         am_aix_root.py
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
# Date:    12.10.2018  
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
#  12.10.2018 v 1.00/history:
# 
#			  12.10.2018 v 1.0.0/Fist version
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



def get_root_home():# {{{
    """Return a string containig the root home directory
    :returns: str:  root home e.g. /home/root
    """
    unix_cmd=("lsuser -C -a home root")
    
    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
   
    if rc!=0:
       return False
    
    elif rc==0:
       for line in p.stdout:
           if not line.startswith("#"):
               line = line.strip()
               root_home = line.split(":")[1]
               if root_home:
                   return root_home
               else:
                   return False
    
# }}}





# MAIN
if __name__ == "__main__":
    print "\n# Retrieving the root_home"
    print get_root_home()
