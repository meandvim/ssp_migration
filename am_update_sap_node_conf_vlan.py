#!/usr/bin/env python
# -*- coding: utf-8 -*-

import fileinput
import os.path
import sys


# For testing:
# node_conf_file="node_conf_s370en0"


# sap_vlan_dic={"VLANA":"198", "VLANB":"1658"}
def replace_vlan(node_conf_file, vlan_name, vlan_value,verbose=False ):
    """Replacing the VLANA value

    :vlan_name: The name of the vlan: VLANA or VLANB for SAP
    :vlan_value: kvalue: int: 198 or 
    """
    for line in fileinput.FileInput(node_conf_file, inplace=1):
        if vlan_name in line:
            old_vlan_value= line.split("'")[1]
            line = line.replace(old_vlan_value, vlan_value)
        print str.strip(line)


def main(node_conf_file,verbose=False):
    """TODO: Docstring for main.
    :node_conf_file: The file where the vlan values are changed
    """
    if not os.path.isfile(node_conf_file):
        print "Inexistent file: {}".format(node_conf_file)
        sys.exit(1)

    if verbose:
        print "# Updating vlan values for: {}".format(node_conf_file)
    sap_vlan_dic={"VLANA":"198", "VLANB":"1658"}
    for vlan_name,vlan_number in sap_vlan_dic.items():
        if verbose:
            print " #-> Changing: {} to {}".format(vlan_name, vlan_number)
        replace_vlan(node_conf_file, vlan_name, vlan_number)

    return 0


if __name__ == "__main__":
    print "I should be Replacing the VLAN values"
    main(node_conf_file)

