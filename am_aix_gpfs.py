#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This module provided AIX GPFS Metro related information:

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
import inspect
sys.path.append("/usr/local/rootbin/Pythonlib/")
from am_logging import pfn 
import amdisplay
amd=amdisplay.AmDisplay()


# TODO
def get_gpfs_manager(verbose=False, silent=False, quit=True):# {{{
    """Retrieves cluster manager
    :verbose:   Show what is going on
    :quit:      Suppresses output 
    :returns:   list: cluster_manager_hostname, cluster_manager_ip

     ##  mmlsmgr -c
        Cluster manager node: 164.139.214.100 (s046serv)
     """
    if verbose >= 2:
        logging.info("Start of: # {}".format(inspect.stack()[0][3]))

    cluster_manager=False

    opt1 = " -Y "
    unix_cmd=("/usr/lpp/mmfs/bin/mmlsmgr "\
        "{}"\
        ).format(opt1)
    
    if verbose >= 2 and not silent:
        logging.info("unix_cmd is # {} #".format(unix_cmd))# FOR Debugging
    
    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
        # Unix_cmd has failed
    if rc!=0:

       # Checking if the output for 6027-1382 to see if : 
       # mmlsmgr: 6027-1382 This node does not belong to a GPFS cluster

       for line in p.stdout:
           if "6027-1382" in line: 
               cluster_manager = None
               amd.info_msg("No cluster manager")
               return cluster_manager   
    
        # Unix_cmd executed successfully
    elif rc==0:
       for line in p.stdout:
           if line:
               if not "HEADER" in line: 
                   if "clusterManager" in line:
                      line = line.strip()
                      cluster_manager=line.split(":")[6]
    
    return cluster_manager
    # }}}
def get_gpfs_nsd_dic(verbose=False, silent=False, quit=True):# {{{
    """Retrieves NSDs 
    :verbose:   Show what is going on
    :quit:      Suppresses output 
    :returns:   dict: NSD List

     ##  mmlsnsd -Y
     """
    if verbose >= 2:
        logging.info("Start of: # {}".format(inspect.stack()[0][3]))

    nsd_dict={}
    nsd = None

    opt1 = " -Y "
    unix_cmd=("/usr/lpp/mmfs/bin/mmlsnsd "\
        "{}"\
        ).format(opt1)
    
    if verbose >= 2 and not silent:
        logging.info("unix_cmd is # {} #".format(unix_cmd))# FOR Debugging
    
    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
        # Unix_cmd has failed
    if rc!=0:

       for line in p.stdout:
           if "6027-1382" in line: 
               amd.info_msg("No cluster manager, No NSD")
               return nsd       # None
    
        # Unix_cmd executed successfully
    elif rc==0:
       for line in p.stdout:
           if line:
               if not "HEADER" in line: 
                   line = line.strip()
                   fs=line.split(":")[6]
                   nsd=line.split(":")[7]
                   nsd_dict[nsd]=fs
    
    return nsd_dict
    # }}}
def get_gpfs_nsd_list(verbose=False, silent=False, quit=True):# {{{
    """Retrieves NSDs 
    :verbose:   Show what is going on
    :quit:      Suppresses output 
    :returns:   list: NSD List :['gpfs1nsd', 'gpfs4nsd']

     ##  mmlsnsd -Y
     """

    nsd_list=[]


    opt1 = " -Y "
    unix_cmd=("/usr/lpp/mmfs/bin/mmlsnsd "\
        "{}"\
        ).format(opt1)

    
    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
        # Unix_cmd has failed
    if rc!=0:
       if quit:
          amd.err_msg("Unable to retrieve the NSDs", exit_code=1)
       return False
    
        # Unix_cmd executed successfully
    elif rc==0:
       for line in p.stdout:
           if line:
               if not "HEADER" in line: 
                   line = line.strip()
                   nsd=line.split(":")[7]
                   if nsd:
                       nsd_list.append(nsd)
    
    return nsd_list
    # }}}
def get_gpfs_mounted_fs_dict(verbose=False, silent=False, quit=True):# {{{
    """Returns dict{} of mounted gpfs fileystems: {'/dev/sap_bzx': '/gpfs'}
    :verbose:   Show what is going on
    :quit:      Suppresses output 
    :returns:   dict: FS,mount_point

     ##  /usr/sbin/mount
     """

    gpfs_dict={}

    unix_cmd=("/usr/sbin/mount ")
    
    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
        # Unix_cmd has failed
    if rc!=0:
       if quit:
          amd.err_msg("Unable to retrieve the mounted gfps FSs ", exit_code=1)
       return False
    
        # Unix_cmd executed successfully
    elif rc==0:
       for line in p.stdout:
           if line:
              if not "mounted" in line: 
                 if not line.startswith("--------"):
                   line = line.strip()
                   fs_type=line.split()[2]
                   if "mmfs" in fs_type:
                     device=line.split()[0]
                     gpfs_fs=line.split()[1]
                     gpfs_dict[device]=gpfs_fs
    
    return gpfs_dict
    # }}}
def get_gpfs_mounted_fs_list(verbose=False, silent=False, quit=True):# {{{
    """Returns list of mounted gpfs fileystems: ['/gpfs']
    :verbose:   Show what is going on
    :quit:      Suppresses output 
    :returns:   dict: FS,mount_point

     ##  /usr/sbin/mount
     """


    gpfs_list=[]

    unix_cmd=("/usr/sbin/mount ")
    
    p = subprocess.Popen(unix_cmd,\
            shell=True, stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT)
    rc = p.wait()
    
        # Unix_cmd has failed
    if rc!=0:
       if quit:
          amd.err_msg("Unable to retrieve the mounted gfps FSs ", exit_code=1)
       return False
    
        # Unix_cmd executed successfully
    elif rc==0:
       for line in p.stdout:
           if line:
              if not "mounted" in line: 
                 if not line.startswith("--------"):
                   line = line.strip()
                   fs_type=line.split()[2]
                   if "mmfs" in fs_type:
                     gpfs_fs=line.split()[1]
                     gpfs_list.append(gpfs_fs)
    
    return gpfs_list
    # }}}
