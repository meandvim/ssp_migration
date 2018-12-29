#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This module provided AIX Networking Metro related information:

    It contains the following main sections: 
        get_net_adapters
            -Returns a list of all the network adapters on the system
        get_ip
            -Returns the ip addr cofigured on an adapter

        get_all_ips
            -Returns all the IP Addreses configured on the system. 
                - Ip alieases are ignored

        get_all_aliases
            -Returns all the IP Alieases configured on the system. 

        get_def_routes
            -Returns all the Default Gateways configured on the sytem """


import subprocess
import sys
import socket
sys.path.append("/usr/local/rootbin/Pythonlib/")
import amdisplay
from am_logging import pfn
amd=amdisplay.AmDisplay()


def get_net_adapters(state,quit=True):# {{{
    """Retrieves all the network adapters of the state : adapter_state
    :state: The state of the adapter [D,A,S]
       D  for the Defined state
       A  for the Available state
       S  for the Stopped state

     
    :verbose:   Show what is going on
    :quit:      Suppresses output 
    :: TODO
    :returns: list : [en0, en1, enN]

    Examples: 
    get_net_adapters("A")
    get_net_adapters("S")

    """

    adapter_list=[]
    opt1 = " -S {} -F name -Cc if".format(state)
    unix_cmd=("/usr/sbin/lsdev"\
            "{}"\
            ).format(opt1)
    
    
    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
        # Unix_cmd has failed
    if rc!=0:
       if quit:
          amd.err_msg("Unable to retrieve network_adapter list", exit_code=1)
       return False
    
        # Unix_cmd executed successfully
    elif rc==0:
       for line in p.stdout:
           # Ignoring lo0
           if "lo0" not in line:
              adapter_list.append(line.strip())
    
    return adapter_list
    # }}}

def get_ip(adapter, v=False,  quit=True):# {{{
    """Retrieves the IP address of an adapter
    :adapter:   The network adapter  
    :v:   Show what is going on
    :quit:      Suppresses output 
    :returns: str: ip address

    :examples: 
      ip_addr = get_ip(adapter)

     ##   lsattr -F "value" -a "netaddr"  -El   en0
    """
    if v >= 2:
        logging.info("Start of: # {}".format(inspect.stack()[0][3]))

    ip_addr=False
    opt1 = " -F \"value\" -a \"netaddr\" -El {}".format(adapter)
    unix_cmd=("/usr/sbin/lsattr"\
            "{}"\
            ).format(opt1)
    
    if v >= 2: 
        logging.info("unix_cmd is # {} #".format(unix_cmd))# FOR Debugging
    
    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
        # Unix_cmd has failed
    if rc!=0:
       if quit:
          amd.err_msg("Unable to retrieve the IP address", exit_code=1)
       return False
    
        # Unix_cmd executed successfully
    elif rc==0:
       for line in p.stdout:
              ip_addr=(line.strip())
    
    return ip_addr
    # }}}
def get_all_ips(v=False,  quit=True):# {{{
    """Retrieves all the ip addresses configured on the system. 
    The IP aliases will not be retrieved
    :v:   Show what is going on
    :quit:      Suppresses output 
    :returns: str: ip address
     ##   lsattr -F "value" -a "netaddr"  -El   en0

    :examples: 
       ip_addrs_current = am_aix_networking.get_all_ips()
    """

    ip_addr_list=[]

    adapter_list=get_net_adapters("A")
    for adapter in  adapter_list:
      ip_addr = get_ip(adapter)
      ip_addr_list.append(ip_addr)
    
    return ip_addr_list
    # }}}

def get_alias(adapter, verbose=False, silent=False, quit=True):# {{{
    """Retrieves the IP ALIAS address of an adapter
    :adapter:   The network adapter  
    :verbose:   Show what is going on
    :quit:      Suppresses output 
    :returns: str: alias ip address

    ##       lsattr  -F "attribute:value" -a "alias4" -El en2
    """

    alias=False
    opt1 = " -F \"value\" -a \"alias4\" -El {}".format(adapter)
    unix_cmd=("/usr/sbin/lsattr"\
            "{}"\
            ).format(opt1)
    
    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
        # Unix_cmd has failed
    if rc!=0:
       if quit:
          amd.err_msg("Unable to retrieve the IP alias address", exit_code=1)
       return False
    
        # Unix_cmd executed successfully
    elif rc==0:
       for line in p.stdout:
           if  line.strip():
               alias=line.split(",")[0].strip()
    return alias
    # }}}
def get_all_aliases(v=False,  quit=True):# {{{
    """Retrieves all the IP Aliases configured on the system. 
    :v:   Show what is going on
    :quit:      Suppresses output 
    :returns: str: ip address
     ##   lsattr -F "value" -a "netaddr"  -El   en0

    :examples: 
       ip_addrs_current = am_aix_networking.get_all_ips()
    """

    ip_alias_list=[]

    adapter_list=get_net_adapters("A")
    for adapter in  adapter_list:
      ip_alias = get_alias(adapter)
      if ip_alias:
         ip_alias_list.append(ip_alias)

    
    return ip_alias_list
    # }}}

def get_default_routes(verbose=False, silent=False,  quit=True):# {{{
    """Retrieves the default routes
    :verbose:   Show what is going on
    :quit:      Suppresses output 
    :returns: list: default routes

    ##     /usr/bin/netstat -nra
    """

    opt1 = " -nra "
    unix_cmd=("/usr/bin/netstat"\
            "{}"\
            ).format(opt1)
  
    routes_list=[]
    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
        # Unix_cmd has failed
    if rc!=0:
       if quit:
          amd.err_msg("Unable to retrieve a default Gateway", exit_code=1)
       return False
    
        # Unix_cmd executed successfully
    elif rc==0:
       for line in p.stdout:
           if  "default" in line:
               line=line.strip()
               route=line.split()[1]
               try:
                  socket.inet_aton(route)
                  routes_list.append(route)
               except socket.error:
                  amd.err_msg("invalid Gateway:",route, exit_code=1)
    return routes_list
    # }}}

