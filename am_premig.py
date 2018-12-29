#!/usr/bin/env python
# -*- coding: utf-8 -*-

"Simple wrapper module for premigration activities"


import os

import sys
sys.path.append("/usr/local/rootbin/Pythonlib/")
import am_gen_fb_mig
import am_update_sap_node_conf_ame as sap_ame
import am_update_sap_node_conf_vlan as sap_vlan


def gen_fb(fb_file,
        ini_file,
        verbose=False):

    """

    :fb_file:   The first_boot file name  used for migration
                This file will be generated so it is manatory
                the path exists

    :ini_file:  The ini_file path used to retrieve the configuration     
    :node_conf_file:    The node_conf_lpar file path 
    :verbose:   Show what is going on
    :returns: bool

    """

    # Generating the First_BOOT
    am_gen_fb_mig.main(fb_file, ini_file,verbose=verbose)



def main(fb_file,
        ini_file,
        node_conf_file,
        verbose=False):

    """TODO: Docstring for main.

    :fb_file:   The first_boot file name  used for migration
                This file will be generated so it is manatory
                the path exists

    :ini_file:  The ini_file path used to retrieve the configuration     
    :node_conf_file:    The node_conf_lpar file path 
    :verbose:   Show what is going on
    :returns: TODO

    """
    # File/path prereq
    fb_path = os.path.dirname(fb_file)
    if fb_path and not os.path.isdir(fb_path):
        print "# ERROR: Inexitent path for the fb_file: {}".format(fb_file)
        sys.exit(1)

    if not os.path.isfile(ini_file):
        print "# ERROR: Inexitent file: {}".format(ini_file)
        sys.exit(1)

    if not os.path.isfile(node_conf_file):
        print "# ERROR: Inexitent file: {}".format(node_conf_file)
        sys.exit(1)



    # Generating the First_BOOT
    am_gen_fb_mig.main(fb_file, ini_file,verbose=verbose)
    


    # Updating the vlan Values inside node_conf_file
    sap_vlan.main(node_conf_file,verbose=verbose)


    # Updating the AME values inside node_conf_file
    sap_ame.main(node_conf_file, ini_file,verbose=verbose)

    






if __name__ == "__main__":
    print "This module is not inteded to run as a script"

