#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""This module provided AIX INFRASTRUCURE Metro related information:

    It contains the following main sections: 
        is_ssh_reachable
        is_ping_reachable 
        is_up

            """


import os
import subprocess
import sys
import socket
sys.path.append("/usr/local/rootbin/Pythonlib/")
from am_logging import pfn
import amdisplay
amd=amdisplay.AmDisplay()



# TODO

def is_ping_reachabe(hostname,silent=False, verbose=False): # {{{
    """Checking if a host is reachable over ping"""

    pfn(verbose=verbose)

    if silent:
        response = os.system("ping -c 1 > /dev/null " + hostname)
    else:
        response = os.system("ping -c 1 " + hostname)
    if response == 0:
      return True
    else:
      return False

# }}}
def is_ssh_accesible(host, user="root", verbose=False, quit=False ): # {{{
    """Checking if a host is accessible over ssh"""

    unix_cmd=("ssh "\
            " {}@"\
            "{}"\
            " exit"\
            ).format(user, host)
    
    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
        # Unix_cmd has failed
    if rc!=0:
        return False
    
        # Unix_cmd executed successfully
    elif rc==0:
       if verbose:
         amd.ok_msg("   >> Host:",host,"is reachable over ssh")
       return True

# }}}
