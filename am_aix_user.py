#!/usr/bin/env python
# -*- coding: utf-8 -*-


# For AIX
# Metro Info#{{{
# ----------------------------------------------------------------------------
#
# NAME:         am_user_pwd.py
#
# Purpose:      List user properties for AIX/Linux, It used pwd and grp
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




import pwd
import grp
import amdisplay
import am_aix_hostname
import os.path
import subprocess



amd = amdisplay.AmDisplay()
amh = am_aix_hostname.am_aix_hostname()

# CLASSES
class am_aix_user(object):# {{{
    """
     - compile_mk_user_file_path()

     - is_mk_user_file() # Check if 

     - are_uncommented_entries() # checks if there are any 
              uncommented entries in the user file

     - is_user_commented("user") # Checks if there already is and 
             commented user entry in the file

     - add_mk_user_entry("user","group", "id", "IM")

     - del_mk_user_entry("user")

     - add_user()

     - rm_user()

    """
    make_user_path = "/usr/local/rootbin/USERS/"

    def __init__(self):
        """TODO: Not used at the moment. """

# Prerequisites/Checks
    def compile_mk_user_file_path(self,verbose=False):# {{{

        """Compiling the make_user file path
        :returns:str:make_user_file_path
        """
        self.verbose = verbose
        hostname_prefix = amh.get_prefix()
        make_user_path=self.make_user_path \
                + "make_users." \
                + hostname_prefix\
                + "en0"

        if verbose:
            amd.ok_msg("Compiling the user configuration file path")
        return make_user_path
       # }}}
    def compile_mk_user_argument(self,verbose=False):# {{{

        """Compiling the make_user argument: e.g.: i333en0
        :returns:str:make_user_argument
        """
        self.verbose = verbose
        hostname_prefix = amh.get_prefix()
        make_user_argument = hostname_prefix + "en0"

        if verbose:
            amd.ok_msg("Compiling make_user_argument")
        return make_user_argument
       # }}}
    def is_make_user_sh(self,verbose=False):# {{{
        """Check if the /usr/local/rootbin/USERS/make_users.sh exists
        :returns:bool 
        """
        self.verbose = verbose
        file_name = "/usr/local/rootbin/USERS/make_users.sh"
        
        if os.path.isfile(file_name):
            if verbose:
                amd.ok_msg("User creation script in place")
            return True
        else:
            amd.err_msg("Inexistent file: make_user.sh ",\
                file_name, \
                call_admins=True, 
                exit_code=5)
            return False
       # }}}
    def is_mk_user_file(self,verbose=False):# {{{
        """Check if the /usr/local/rootbin/USERS/make_users.{prefix}en0 file\
                exist
        :returns:bool 
        """
        self.verbose = verbose
        file_name = self.compile_mk_user_file_path()
        
        if os.path.isfile(file_name):
            if verbose:
                amd.ok_msg("User configuration file in place.")
            return True
        else:
            amd.err_msg("Missing user configuration file:",\
                file_name, \
                call_admins=True, 
                exit_code=5)
            return False
       # }}}
    def are_uncommented_entries(self,verbose=False):# {{{
        """TODO: Determining if there are uncommented entries into make_user file
        :returns: bool
        """




        self.verbose = verbose
        file_name = self.compile_mk_user_file_path()
        with open(file_name,'r') as f:
            lines = f.readlines()
        f.close

        header = "#</MAKE_USERS_HEAD>"
        all_lines_nr = len(lines)

        # Checking to see if there are more than 1 Header  entries
        header_entries = 0
        for line in lines:
            if line.startswith(header):
                header_entries += 1
        if header_entries > 1:
            amd.err_msg("Invalid make_user file. Multiple header entries",\
            call_admins=True,\
            exit_code=5)
            

       
        # Determining the user index line number: first line after the header
            # user_index_line_nr
        line_nr = 0
        for line in lines:
            line_nr += 1
            if line.startswith(header):
                user_index_line_nr = line_nr
       

        # Checking to see if there are uncommented entries in the user section.
            # User section starts afte the header
        no_uncommented_lines = 0
        while user_index_line_nr <= all_lines_nr -1 :
            #  If line is empty, ignore it
            if lines[user_index_line_nr] in ['\n', '\r\n']:
                pass
            else:
                #  If line is commented, ignore it
                if lines[user_index_line_nr].startswith("#"):
                    pass
    #                  print lines[user_index_line_nr].strip()
                #  If line is uncommented, raise Exception
                else:
                   amd.err_msg("Unsuported use case: ")
                   amd.err_msg("Uncommented entries in the user section",\
                            "of the make_users file",\
                            call_admins = True,\
                            exit_code = 6)
            user_index_line_nr += 1
        
        if verbose:
            if not no_uncommented_lines:
                amd.ok_msg("There are no uncommented entries in the user conf. file")


# }}}

    def do_aix_user_prereq(self, verbose=False):# {{{
        amux = am_aix_user()
        """Performing Standar Metro AIX user prerequisites
        -is_mk_user_file()
        -are_uncommented_entries()
        -is_commented_user_entry()
        verbose: spew verbose output """
    
        if verbose:
            amd.info_msg("    Performing general AIX username prerequisites.")
        self.compile_mk_user_file_path(verbose=verbose)
        self.is_make_user_sh(verbose=verbose)
        self.is_mk_user_file(verbose=verbose)
        self.are_uncommented_entries(verbose=verbose)
        self.check_duplicate_user_entries(verbose=verbose)
    #     amux.is_user_commented("lyceus", verbose=verbose)
    # }}}


# TODO
    def check_duplicate_user_entries(self ,verbose=True):# {{{
        """Checking if the user is already commented in the config. file
        :returns:bool 
        """
        self.verbose = verbose

        file_name = self.compile_mk_user_file_path()
        with open(file_name,'r') as f:
            lines = f.readlines()
        f.close

        header = "#</MAKE_USERS_HEAD>"
        all_lines_nr = len(lines)
       
        # Determining the user index line number: first line after the header
         # user_index_line_nr
            #  I no longer need to check if there are multiple header entries, 
            #    it is taken care of by: are_uncommented_entries()




# }}}
    def is_user_commented(self,user,verbose=True):# {{{
        """Checking if the user is already commented in the config. file
        :returns:bool 
        """
        self.user = user # The user to be cheked 
        self.verbose = verbose

        file_name = self.compile_mk_user_file_path()
        with open(file_name,'r') as f:
            lines = f.readlines()
        f.close

        header = "#</MAKE_USERS_HEAD>"
        all_lines_nr = len(lines)
       
        # Determining the user index line number: first line after the header
         # user_index_line_nr
            #  I no longer need to check if there are multiple header entries, 
            #    it is taken care of by: are_uncommented_entries()
        line_nr = 0
        for line in lines:
            line_nr += 1
            if line.startswith(header):
                user_index_line_nr = line_nr
#                 print user_index_line_nr # FOR TESTING
       

        # Checking to see if there are uncommented entries in the user section.
            # User section starts afte the header
        exiting_commented_user = False
        while user_index_line_nr <= all_lines_nr -1 :
#             print user_index_line_nr    #  For Testing
            #  If line is empty, ignore it
            if lines[user_index_line_nr] in ['\n', '\r\n']:
                pass
            else:
                if self.user in line:
                    if lines[user_index_line_nr].startswith("#"):
                        amd.err_msg("Unsupported use case")
                        amd.err_msg("User already defined in the conf. file: ",\
                              user,\
                              call_admins = True,\
                              exit_code = 7)
                        
            user_index_line_nr += 1

        if verbose:
            if not exiting_commented_user:
               amd.ok_msg("There are no previously defined user entries for:",\
                     user)


# }}}
# _TODO

# USER OPERATIONS (Hardcodded for lyceus)
    def add_mk_user_entry(self, user_entry_line, verbose=False):# {{{

        """Adding configuration line in the make_user file used
        to create a new user

        AIX header format
         1. USER --> Keyword to assign line as user definitionr-line
         2. UNAME --> Name of User ( e.g.  u0122708 || u1900000 || m0004711   )
         3. GROUPS --> Comma separated Groupnames. First group is the primary
            all following are secondary groups.
         4. E_MAIL --> E-Mail-Adress of User (gecos: ford.prefect@mgi.de)
         5. ENV_FILE-file --> Name of environment-file ( dev.env || dummy  )
         6. UID --> AIX-uid for the user
         7. ALT_HOME --> alternate home-directory posible entries:
               a) if not set (/$USER_HOME/$UNAME)
               b) /space --> sets home-directory to /space/$UNAME
               c) /space/prod/ --> sets home-directory to /space/prod
         8. IM_TICKET --> number of HPSC-ticket for reference in /etc/mgi_users
        
        :returns: bool
        """

        self.user_entry_line = user_entry_line
        self.verbose = verbose
        file = self.compile_mk_user_file_path()

        # Checking if user_entry_line already exists
        #  TODO
        with open(file,'a') as f:
           f.write(user_entry_line + "\n")
        f.close() 

        if verbose:
           amd.ok_msg("Successfully added user entry in the conf. file")

# }}}
    def rm_mk_user_entry(self, user_entry_line, verbose=False):# {{{

        """Adding configuration line in the make_user file used
        to create a new user

        AIX header format
         1. USER --> Keyword to assign line as user definitionr-line
         2. UNAME --> Name of User ( e.g.  u0122708 || u1900000 || m0004711   )
         3. GROUPS --> Comma separated Groupnames. First group is the primary
            all following are secondary groups.
         4. E_MAIL --> E-Mail-Adress of User (gecos: ford.prefect@mgi.de)
         5. ENV_FILE-file --> Name of environment-file ( dev.env || dummy  )
         6. UID --> AIX-uid for the user
         7. ALT_HOME --> alternate home-directory posible entries:
               a) if not set (/$USER_HOME/$UNAME)
               b) /space --> sets home-directory to /space/$UNAME
               c) /space/prod/ --> sets home-directory to /space/prod
         8. IM_TICKET --> number of HPSC-ticket for reference in /etc/mgi_users
        
        :returns: bool
        """

        self.user_entry_line = user_entry_line
        self.verbose = verbose
        file = self.compile_mk_user_file_path()

        # Removing the user entry line
        pattern_to_remove = user_entry_line
        f = open(file,"r+")
        lines = f.readlines()
        f.seek(0)
        for line in lines:
            if pattern_to_remove not in line:
                f.write(line)
        f.truncate()
        f.close()


        if verbose:
           amd.ok_msg("Successfully removed the user entry line",\
                   "from the conf. file")

# }}}

    def add_group(self, group_name, group_id, verbose=False):# {{{
        """Adding groups """
        self.verbose = verbose
        self.group_name = group_name
        self.group_id = group_id
        
        # Running mkgroup
        unix_cmd=("mkgroup" \
                " -a id={0}"
                " {1} " \
                ).format(group_id,group_name)
       

        if verbose == 2:
            print "Debugging:unix_cmd is:{}:".format(unix_cmd)	# FOR Debugging
        
        p = subprocess.Popen(unix_cmd,\
                shell=True, stdout=subprocess.PIPE,\
                stderr=subprocess.STDOUT)
        rc = p.wait()
        
        
            # Unix_cmd has failed
        if rc!=0:
            if verbose:
                for line in p.stdout:
                    print line
            amd.err_msg("Unable to create group:",\
                    group_name,\
                    call_adm = True,\
                    exit_code = 8)

            # Unix_cmd executed successfully
        elif rc==0:
            if verbose:
                amd.ok_msg("Group successfully  created:",\
                        group_name)
        # }}}
    def rm_group(self, group_name, verbose=False):# {{{
        """Removing a group """
        self.verbose = verbose
        self.group_name = group_name
        
        # Running mkgroup
        unix_cmd=("rmgroup" \
                " {0} " \
                ).format(group_name)
       

        if verbose == 2:
            print "Debugging:unix_cmd is:{}:".format(unix_cmd)	# FOR Debugging
        
        p = subprocess.Popen(unix_cmd,\
                shell=True, stdout=subprocess.PIPE,\
                stderr=subprocess.STDOUT)
        rc = p.wait()
        
        
            # Unix_cmd has failed
        if rc!=0:
            if verbose:
                for line in p.stdout:
                    print line
            amd.err_msg("Unable to remove group:",\
                    group_name,\
                    call_adm = True,\
                    exit_code = 8)

            # Unix_cmd executed successfully
        elif rc==0:
            if verbose:
                amd.ok_msg("Group successfully removed:",\
                        group_name)
        # }}}

    def add_user(self, user_name, verbose=False):# {{{
        """Adding the user present in the make_user_file """
        self.verbose = verbose
        self.user_name = user_name


        # Doing the standard user prerequisites 
        self.do_aix_user_prereq(verbose=verbose)

        # Generating the argument for make_users.sh e.g. s055en0
        user_conf_file_argument = self.compile_mk_user_argument()

        # Adding user entry into user config file: 
        user_entry_line = ("USER:lyceus:lyceus,sapsys,dba"\
                ":metrosystemsrobuk-sapbasisadministration@metrosystems.net:"\
                "dummy:80400::IM00009999")
        self.add_mk_user_entry(user_entry_line, verbose = verbose)
        
        # Running make_users.sh 
        # The next line is suboptimal:\
                # I need to discuss this with my colleaugues to find a better\
                # approch the existing script required relativ paths
        unix_cmd=("cd /usr/local/rootbin/USERS; ./make_users.sh" \
                " {0} " \
                ).format(user_conf_file_argument)
       

        if verbose == 2:
            print "Debugging:unix_cmd is:{}:".format(unix_cmd)	# FOR Debugging
        
        p = subprocess.Popen(unix_cmd,\
                shell=True, stdout=subprocess.PIPE,\
                stderr=subprocess.STDOUT)
        rc = p.wait()
        
        
            # Unix_cmd has failed
        if rc!=0:
            for line in p.stdout:
                print line
            amd.err_msg("Unable to create user Lyceus",\
                    call_adm = True,\
                    exit_code = 8)

            # Unix_cmd executed successfully
        elif rc==0:
#             if verbose:
            amd.ok_msg("User succesfully created: ", user_name)
        # }}}
    def rm_user(self, user_name, verbose=False):# {{{
        """Removing the user_name"""
        self.verbose = verbose
        self.user_name = user_name


##        # Doing the standard user prerequisites if verbose: 
##        self.do_aix_user_prereq(verbose=verbose)
##
##        # Generating the argument for make_users.sh e.g. s055en0
##        user_conf_file_argument = self.compile_mk_user_argument()
##
##        # Adding user entrly into user config file: 
##        user_entry_line = ("USER:lyceus:lyceus,sapsys,dba"\
##                ":metrosystemsrobuk-sapbasisadministration@metrosystems.net:"\
##                "dummy:80400::IM00009999")
##        self.add_mk_user_entry(user_entry_line, verbose = verbose)
##        

        # Removing the user
        unix_cmd=("rmuser " \
                " {0} " \
                ).format(user_name)

        if verbose == 2:
            print "Debugging:unix_cmd is:{}:".format(unix_cmd)	# FOR Debugging
        
        p = subprocess.Popen(unix_cmd,\
                shell=True, stdout=subprocess.PIPE,\
                stderr=subprocess.STDOUT)
        rc = p.wait()
        
            # Unix_cmd has failed
        if rc!=0:
            for line in p.stdout:
                print line
            amd.err_msg("Unable to remove  user Lyceus",\
                    call_adm = True,\
                    exit_code = 11)

            # Unix_cmd executed successfully
        elif rc==0:
            amd.ok_msg("User succesfully removed: ", user_name)
        # }}}


    def list_user(self, user_name, verbose=False):# {{{
        """Listing user info"""
        self.verbose = verbose
        self.user_name = user_name

        # Loading user info into a list
        self.do_aix_user_prereq(verbose=verbose)

        unix_cmd=("lsuser -f -a groups shell home"\
                " {}"\
                ).format(user_name)
        
        if  verbose == 2:
            print "Debugging:unix_cmd is:{}:".format(unix_cmd)	# FOR Debugging
        
        p = subprocess.Popen(unix_cmd,\
                shell=True, stdout=subprocess.PIPE,\
                stderr=subprocess.STDOUT)
        rc = p.wait()
        
            # Unix_cmd has failed
        if rc!=0:
            amd.err_msg("Unable to retrieve user information",\
                    call_admins = True)
            output_list = p.stdout.readlines()
            pass
        
            # Unix_cmd executed successfully
        elif rc==0:
            
            output_list = p.stdout.readlines()
            for i in output_list:
                print i.strip()

        # }}}
    def list_fs_ownership(self, filesystem, verbose=False):# {{{
        """List Filesytem Ownership"""
        self.verbose = verbose
        self.filesystem = filesystem


        unix_cmd=("lsuser -f -a groups shell home"\
                " {}"\
                ).format(user_name)
        
        if  verbose == 2:
            print "Debugging:unix_cmd is:{}:".format(unix_cmd)	# FOR Debugging
        
        p = subprocess.Popen(unix_cmd,\
                shell=True, stdout=subprocess.PIPE,\
                stderr=subprocess.STDOUT)
        rc = p.wait()
        
            # Unix_cmd has failed
        if rc!=0:
            amd.err_msg("Unable to retrieve user information",\
                    call_admins = True)
            output_list = p.stdout.readlines()
            pass
        
            # Unix_cmd executed successfully
        elif rc==0:
            
            output_list = p.stdout.readlines()
            for i in output_list:
                print i.strip()

        # }}}



# }}}


# FUNCTIONS
def do_aix_user_prereq(verbose=False):# {{{
    amux = am_aix_user()
    """Performing Standard Metro AIX user prerequisites
    -is_mk_user_file()
    -are_uncommented_entries()
    -is_commented_user_entry()
    verbose: spew verbose output """

    amd.info_msg("    Performing general AIX username prerequisites.")
    amux.compile_mk_user_file_path(verbose=True)
    amux.is_mk_user_file(verbose=True)
    amux.are_uncommented_entries(verbose=True)
    amux.check_duplicate_user_entries(verbose=True)
#     amux.is_user_commented("lyceus", verbose=True)
# }}}

def test_add_mk_user_entry():# {{{
    """Staring the user operations section
    """
    amd.info_msg("    Starting the user operation section")
    amux = am_aix_user()
    amux.add_mk_user_entry("USER:oraji3:staff:METROSYSTEMS-ROBUK-SAP1-ADMINISTRATION@metrosystems.net:dummy:80201:/home:IM00009999",verbose=True)
# }}}

# HERE IT GOES        
if __name__ == "__main__":    
    do_aix_user_prereq(verbose=True)
    test_add_mk_user_entry()
 


