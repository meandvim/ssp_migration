#!/usr/bin/env python
# -*- coding: utf-8 -*-



# For AIX

# For AIX
# Metro Info#{{{
# ----------------------------------------------------------------------------
#
# NAME:         amdisplay.py
#
# Purpose:      Displays ok_msg, err_msg, warning, info messages
#
# Parameter:    see -h
#
# ----------------------------------------------------------------------------
#
# Author:       aldo@metrosystems.net
#
# Date:    27.04.2018  
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
#  27.04.2018 v 1.00/history:
# 
#			  27.04.2018 v 1.0.0/Fist version
#
# ----------------------------------------------------------------------------
#
# ToDo:         Further tasks
#
# ----------------------------------------------------------------------------
#
#}}}






import os
import sys
import platform

class AmDisplay(object):# {{{

    """MyHelper class. it contains:
            - ok_msg
            - err_msg
            - info_msg
            - warn_msg
            - crit_msg
            - call_admin
            - local_exit
            """

    # Colors definitions: # {{{
    HEADER = '\033[95m'
    BLUE = '\033[34m'
    GREEN = '\033[92m'
    WHITE = '\033[0m'
    WARNING = '\033[93m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    DEBUG = '\033[94m'
    FAIL = '\033[91m'
    MAGNETA = '\033[35m'
    RED = '\033[91m'
    NC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
# }}}
    
    def __init__(self):
        """TODO: to be defined. """

    def local_exit(self, exit_code, verbose=False):# {{{
       """Exiting the program and sending an exit code
       usage: local_exit(4,verbose=True)
       """
       self.exit_code = exit_code
       if verbose == 3:
           print self.WHITE + \
               "[" + self.DEBUG + \
               "DEBUG" + self.WHITE + \
               "]  " + \
               "Exit code is : " + \
               str(exit_code) + \
               self.WHITE, 

       print "\nExiting...\n"
       sys.exit(exit_code)
# }}}
    def call_admins(self, msg="", verbose=False):# {{{
       """Informing the user that the specified operation requires \
        superuser support. 
       usage: call_admins("message", verbose = False)
       """

       print self.WHITE + \
           "[" + self.YELLOW + \
           "INFO " + self.WHITE + \
           "]  " + \
           "Please contact the system administrators." + \
           self.WHITE 
       self.verbose = verbose
    



# }}}
    def ok_msg(self, msg1, *args ):# {{{
        """ Prints an OK message
        usage: ok_msg("Checking if server:", server, "is reachable")
        """
        self.msg1 = msg1
        self.args = args

        if args:
            # Printing the first message: 
            print self.WHITE + "[" + self.GREEN + "OK" + self.WHITE + "]  " + \
                  msg1 + \
                  self.WHITE, 

            # Printing var length messages
            for var in args:
               print var, 
            print self.NC 

        else:
           print self.WHITE + "[" + self.GREEN + "OK" + self.WHITE + "]  " + \
                msg1 + \
                self.WHITE 
# }}}
    def info2_msg(self, msg1, *args ):# {{{
        """ Prints an OK message
        usage: info_msg("User", user, "is not a member of:", group)
        """
        self.msg1 = msg1
        self.args = args

        if args:
            # Printing the first message: 
            print self.WHITE + "[" + self.YELLOW + "INFO" + self.YELLOW + "]  " + \
                  msg1 + \
                  self.WHITE, 

            # Printing var length messages
            for var in args:
               print var, 
            print self.NC 

        else:
           print self.WHITE + "[" + self.YELLOW + "INFO" + self.YELLOW + "]  " + \
                msg1 + \
                self.WHITE 
# }}}
    def info_green_msg(self, msg1, *args ):# {{{
        """ Prints an OK message
        usage: info_msg("User", user, "is not a member of:", group)
        """
        self.msg1 = msg1
        self.args = args

        if args:
            # Printing the first message: 
            print self.WHITE + "[" + self.GREEN + "INFO" + self.GREEN + "]  " + \
                  msg1 + \
                  self.WHITE, 

            # Printing var length messages
            for var in args:
               print var, 
            print self.NC 

        else:
           print self.WHITE + "[" + self.GREEN + "INFO" + self.GREEN + "]  " + \
                msg1 + \
                self.WHITE 
# }}}
    def stage_msg(self, msg1, *args ):# {{{
        """ Prints an OK message
        usage: info_msg("User", user, "is not a member of:", group)
        """
        self.msg1 = msg1
        self.args = args

        if args:
            # Printing the first message: 
            print self.WHITE + "[" + self.CYAN + "INFO" + self.WHITE + "]  " + \
                  self.CYAN + \
                  msg1 + \
                  self.WHITE, 

            # Printing var length messages
            for var in args:
               print var, 
            print self.NC 

        else:
           print self.WHITE + "[" + self.CYAN + "INFO" + self.WHITE + "]  " + \
                self.CYAN + \
                msg1 + \
                self.WHITE 
# }}}
    def info_cyan_msg(self, msg1, *args ):# {{{
        """ Prints an OK message
        usage: info_msg("User", user, "is not a member of:", group)
        """
        self.msg1 = msg1
        self.args = args

        if args:
            # Printing the first message: 
            print self.WHITE + "[" + self.CYAN + "INFO" + self.WHITE + "]  " + \
                  self.CYAN + \
                  msg1 + \
                  self.WHITE, 

            # Printing var length messages
            for var in args:
               print var, 
            print self.NC 

        else:
           print self.WHITE + "[" + self.CYAN + "INFO" + self.WHITE + "]  " + \
                self.CYAN + \
                msg1 + \
                self.WHITE 
# }}}
    def operation_msg(self, msg1, *args ):# {{{
        """ Prints an OK message
        usage: info_msg("User", user, "is not a member of:", group)
        """
        self.msg1 = msg1
        self.args = args

        if args:
            # Printing the first message: 
            print self.WHITE + "[" + self.MAGNETA + "INFO" + self.WHITE + "]  " + \
                  self.MAGNETA + \
                  msg1 + \
                  self.WHITE, 

            # Printing var length messages
            for var in args:
               print var, 
            print self.NC 

        else:
           print self.WHITE + "[" + self.MAGNETA + "INFO" + self.WHITE + "]  " + \
                self.MAGNETA + \
                msg1 + \
                self.WHITE 
# }}}
    def oper_msg(self, msg1, *args ):# {{{
        """ Prints an OK message
        usage: info_msg("User", user, "is not a member of:", group)
        """
        self.msg1 = msg1
        self.args = args

        if args:
            # Printing the first message: 
            print self.WHITE + "[" + self.MAGNETA + "INFO" + self.WHITE + "]  " + \
                  self.MAGNETA + \
                  msg1 + \
                  self.WHITE, 

            # Printing var length messages
            for var in args:
               print var, 
            print self.NC 

        else:
           print self.WHITE + "[" + self.MAGNETA + "INFO" + self.WHITE + "]  " + \
                self.MAGNETA + \
                msg1 + \
                self.WHITE 
# }}}
    def info_msg(self, msg1, *args ):# {{{
        """ Prints an Info message
        usage: info_msg("User", user, "is not a member of:", group)
        """
        self.msg1 = msg1
        self.args = args

        if args:
            # Printing the first message: 
            print self.WHITE + "[" + self.YELLOW + "INFO" + self.YELLOW + "]  " + \
                  msg1 + \
                  self.WHITE, 

            # Printing var length messages
            for var in args:
               print var, 
            print self.NC 

        else:
           print self.WHITE + "[" + self.YELLOW + "INFO" + self.YELLOW + "]  " + \
                msg1 + \
                self.WHITE 
# }}}
    def refactoring_msg(self, msg1, *args ):# {{{
        """ Prints an refactoring message
        usage: info_msg("User", user, "is not a member of:", group)
        """
        self.msg1 = msg1
        self.args = args

        if args:
            # Printing the first message: 
            print self.WHITE + "[" + self.RED + "REFACTORING" + self.RED + "]  " + \
                  msg1 + \
                  self.WHITE, 

            # Printing var length messages
            for var in args:
               print var, 
            print self.NC 

        else:
           print self.WHITE + "[" + self.RED + "REFACTORING" + self.RED + "]  " + \
                msg1 + \
                self.WHITE 
# }}}
    def debug_msg(self, msg1, *args ):# {{{
        """ Prints a debug messages
        usage: info_msg("User", user, "is not a member of:", group)
        """
        self.msg1 = msg1
        self.args = args

        if args:
            # Printing the first message: 
            print self.WHITE + "[" + self.DEBUG + "DEBUG:" + self.DEBUG + "]  " + \
                  msg1 + \
                  self.WHITE, 

            # Printing var length messages
            for var in args:
               print var, 
            print self.NC 

        else:
           print self.WHITE + "[" + self.DEBUG + "INFO" + self.DEBUG + "]  " + \
                msg1 + \
                self.WHITE 
# }}}
    def err_msg(self, msg1, *args, **kwargs ):# {{{
       """ Prints an custom error message
       usage: err_msg("Unable to raech server", server, call_admins=False,\
exit_code=3, verbose=False)

       *args    : can be: call_admins
       **kwargs : can be: local_exit=rc:    rc = int =  return code
       """

       self.msg1 = msg1 
       self.args = args
       self.kwargs = kwargs

       if args:
          # Printing the first message: 
          print self.WHITE + "[" + self.RED + "ERROR" + self.WHITE + "]  " + \
                msg1 + \
                self.WHITE, 

          # Printing var length messages
          for var in args:
             print var, 
          print self.NC 

       else:
          print self.WHITE + "[" + self.RED + "ERROR" + self.WHITE + "]  " + \
              msg1 + \
              self.WHITE 

        
       # Parsing the kwargs arguments: 
       if "call_admins"   in kwargs.keys():
            if "verbose" in kwargs.keys():
                self.call_admins(kwargs["call_admins"],\
                        verbose = kwargs['verbose'])
            else:
                self.call_admins(kwargs["call_admins"])


       if "exit_code" in kwargs.keys():
            if "verbose" in kwargs.keys():
                self.local_exit(kwargs["exit_code"],\
                        verbose = kwargs['verbose'])
            else:
               self.local_exit(kwargs["exit_code"])

        
# }}}
# }}}


# FQDN/HOSTNAME




        
if __name__ == "__main__":    
    # # MyHelper call# {{{
    amd= AmDisplay()
    print ""
    amd.ok_msg("Displaying sample OK messages")
    amd.ok_msg("Determining the OS type:", "AIX")
    server="lxsrvmgi2"
 
    # am.err_msg("Unable to reach server", server, call_admins=True, exit_code=5)
    amd.ok_msg("Checking if server:", server, "is reachable")
    os_type = "AIX"
    amd.ok_msg("Determining the OS version:", os_type)
    amd.ok_msg("Checking if LVM is in use:", "yes")
    free_space="188"
    amd.ok_msg("Checking free space:", free_space)
    amd.ok_msg("Mounting the remote repositories:", "Done")
    # am.err_msg("Unable to reach server", server, call_admins=True, exit_code=5,verbose=True)
 
    size = 100
    amd.ok_msg("Determining the Memory size:",size)
    # 
    # am.err_msg("Unable to determine hardware architecutre",\
    #         call_admins=True,\
    #         exit_code=8)
    # 
    # am.err_msg()# }}}

    # AmInfra call
     
    amd.ok_msg("Determining the OS release:", "etc")
    amd.ok_msg("Determining the OS arch:", "altceva")
    amd.ok_msg("Determining the OS version:", "blabla")
    print ""
    amd.err_msg("Displaying sample err messages")
    amd.err_msg("Unable to reach server:", "lxsrvmgi")
    amd.err_msg("Printing an error with call admins:",call_admins= True) 
    print ""

    amd.info_msg("Displaying Info messages")
    amd.info_msg("keep learning")
