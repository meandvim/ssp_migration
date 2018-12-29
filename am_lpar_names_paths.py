#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os


"""This module is used to retrive hostname related tasks""" 


# FILES
def get_mgi_path():
    """Returns the standard mgi_path: /etc/mgi_config
    :returns: str: "/etc/mgi_config"
    """
    return "/etc/mgi_config"


def get_short_hostname():# {{{
    """Retrieve the short hostname of the lpar. e.g s230en
    :returns:   str: short_hostname e.g. s230en0
    """
    short_hostname = False

    mgi_file=get_mgi_path()
    
    with open(mgi_file,'r') as f:
       for line in f:
           if "Hostname" and "en0" in line:
               short_hostname=line.split()[1]
    f.close()
    return short_hostname
# }}}
def get_hostname():# {{{
    """Retrieve the short hostname of the lpar. e.g s230en
    :returns:   str: short_hostname e.g. s230en0
    """

    hostname = False

    mgi_file=get_mgi_path()
    
    with open(mgi_file,'r') as f:
       for line in f:
           if "Hostname:" and "en0" in line:
               hostname=line.split()[1]
               break
    f.close()
    return hostname
# }}}


def get_nod_ini_path(hostname):# {{{
    """Returns the full path of the /node_ini file. 
    :hostname:  Custom hosname of rhe hostname of the local server: .e.g s230en0
    :returns:   str: node_ini path 

    examples: get_nod_ini_path("s230en0")
    examples: get_nod_ini_path(get_short_hostname()) #hosntame of the local host
    """
    
    if hostname:
        return "/etc/node_ini_{}".format(hostname)
    else:
        return False
# }}}
def get_nod_conf_path(hostname):# {{{
    """Returns the full path of the /node_conf file. 
    :hostname:  Custom hosname of rhe hostname of the local server: .e.g s230en0
    :returns:   str: node_ini path 

    examples: get_nod_ini_path("s230en0")
    examples: get_nod_ini_path(get_short_hostname())
    """
    
    if hostname:
        return "/space/node_conf_{}".format(hostname)
    else:
        return False
# }}}
def get_nod_www_path(hostname):# {{{
    """Returns the full path of the /node_conf file. 
    :hostname:  Custom hosname of rhe hostname of the local server: .e.g s230en0
    :returns:   str: node_ini path 

    examples: get_nod_ini_path("s230en0")
    examples: get_nod_ini_path(get_short_hostname()) #hosntame of the local host
    """
    
    if hostname:
        return "/space/node_conf_{}".format(hostname)
    else:
        return False
# }}}
