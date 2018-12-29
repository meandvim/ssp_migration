#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This module updates the AME values in node_conf_lpar,
    It is usually called by the am_premig.py module
    ToDO
    Execution: 
    actions: 
        - Disable the AME:
            LPAR_AME_FACTOR      => '1.4', -> LPAR_AME_FACTOR      => '1',
            LPAR_MEM_DES         => '45312', = node_conf_file 
            if  LPAR_MEM_MAX < LPAR_MEM_DES   => 'current + 10G',
        """



import fileinput
import os.path
import sys
sys.path.append("/usr/local/rootbin/Pythonlib/")
import am_comp_ini as inif

def replace_ame(node_conf_file, ame_key, ame_value,verbose=False):# {{{
    """Replacing the AME values for SAP

    :ame_key: The name of the ame property to change. e.g. LPAR_MEM_DES
    :ame_value: The value of the AME config:  e.g 1024
    """

    for line in fileinput.FileInput(node_conf_file, inplace=1):
        if ame_key in line:
           if  line.startswith(ame_key):
              old_ame_key_value= line.split("'")[1]
              line = line.replace(old_ame_key_value, ame_value)
        print str.strip(line)
# }}}

def disable_ame(node_conf_file, ini_file, verbose=False):
    """Replacing the VLANA value

    :vlan_name: The name of the vlan: VLANA or VLANB for SAP
    :vlan_value: kvalue: int: 198 or 
    """
   

    #  Retrieving the AME values
    ame = inif.get_ame_factor(ini_file)
    max_mem = inif.get_ame_max_memory(ini_file)
    target_mem = inif.get_ame_target_memory(ini_file)


    # BUILDING THE DICTIONARY 
    mem_dict={}
    mem_dict.update({'LPAR_AME_FACTOR':'0'})
    mem_dict.update({'LPAR_MEM_DES':target_mem})
    mem_dict.update({'LPAR_MEM_MAX':max_mem})

   
    # Modifying the node_conf file
    # If NO AME it value is: "-": in lparstat -i -> am_node_ini

      # LIVE AME = ACTIVE
    if "-" not in ame:
       if verbose:
           print "# Updating the AME values for: {}".format(node_conf_file)

       for mem_key,mem_value in mem_dict.items():
           replace_ame(node_conf_file, mem_key, mem_value)
           if verbose:
               print " #-> Changing: {} to {}".format(mem_key, mem_value)

      # LIVE AME = DEACTIVATED
    else:
       replace_ame(node_conf_file, 'LPAR_AME_FACTOR', '0')
       if verbose:
           print "# LIVE AME is disabled, disabling it in: {}".\
                format(node_conf_file)
           print " #-> Changing LPAR_AME_FACTOR to: 0 "
 


# MAIN
def main(node_conf_file, ini_file, verbose=False):
    """Perform all the AME related changes to the node_conf_file

    :node_conf_file: The file where the vlan values are changed
    :ini_file:       The live configuration file 
    :verbose:        Show what is going on
    :returns: TODO

    """
    # Disabling the AME factor in ame_conf
    disable_ame(node_conf_file, ini_file, verbose=verbose)





if __name__ == "__main__":
    print "I should be configuring AME"
    main(node_conf_file)

