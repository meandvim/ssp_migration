#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" REFACTOR, REFACTOR, REFACTOR
This module is used to accommodate the standard way of managing FSs/VGs/
of the AIX Metro Team. 
In the future, it should be migrated to LVM API"""



# For AIX
# Metro Info#{{{
# ----------------------------------------------------------------------------
#
# NAME:         am_aix_lvm.py
#
# Purpose:      AIX LVM/Filesytem Module:
#       - Retrieve FS ownership
#       - Retrieve FS size: 
#       - Retrieve FS persmissions
#       
#
# Parameter:    see -h
#
# ----------------------------------------------------------------------------
#
# Author:       aldo@metrosystems.net
#
# Date:    08.05.2018  
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
#  08.05.2018 v 1.00/history:
# 
#			  08.05.2018 v 1.0.0/Fist version
#
# ----------------------------------------------------------------------------
#
# ToDo:         Further tasks
#
# ----------------------------------------------------------------------------
#
#}}}




import os
from os import stat
import subprocess
import am_aix_hostname
from pwd import getpwuid
import sys
import time

sys.path.append("/usr/local/rootbin/Pythonlib")
import am_aix_hostname
import amdisplay

amxh = am_aix_hostname.am_aix_sap_hostname()
# Refactoring
class Am_Aix_Lvm:# {{{
    """General AIX LVM methods. 
    Not to be confused iwth Am_Aix_Make_Lvm with is for make_lvm
    - is_aix_lvm
    - get_vgs
    - compile_vg_name
    - is_compiled_name_in_vg_list

    - is_lv
    - make_lvm
    """

    def __init__(self):
        """General purpuse AMGI AIX LVM operations
        - is_aix_lvm()
        - get_vgs()
        - get_vgs_free

        - compile_vg_name(type="BASE")
        - is_mirror_pool()
        - mk_lvm()
        """

    amd=amdisplay.AmDisplay()
    def is_aix_lvm(self, verbose = False):# {{{
        """Checking to see if aixlvm is used:
        :returns: bool """
        self.verbose=verbose

        unix_cmd=("lsvg")
        
        if self.verbose == 2:
            print "Debugging:unix_cmd is:{}:".format(unix_cmd)	# FOR Debugging
        
        p = subprocess.Popen(unix_cmd,\
                shell=True, stdout=subprocess.PIPE,\
                stderr=subprocess.STDOUT)
        rc = p.wait()
        
        
            # Unix_cmd has failed
        if rc!=0:
           return False
        
            # Unix_cmd executed successfully
        elif rc==0:
            return True
        # }}}
    def get_vgs(self, verbose = False):# {{{
        """Retrieving the list of VGs
        :returns: list: vgs_list or bool  """
        self.verbose=verbose

        vgs_list = []
        unix_cmd=("lsvg")
        
        if self.verbose == 2:
            print "Debugging:unix_cmd is:{}:".format(unix_cmd)	# FOR Debugging
        
        p = subprocess.Popen(unix_cmd,\
                shell=True, stdout=subprocess.PIPE,\
                stderr=subprocess.STDOUT)
        rc = p.wait()
        
        
            # Unix_cmd has failed
        if rc!=0:
           return False
        
            # Unix_cmd executed successfully
        elif rc==0:
            for line in p.stdout:
                vgs_list.append(line.strip())

            return vgs_list
        # }}}
    def compile_vg_name(self, vg_type="BASE"):# {{{
        """Compiling the VG name:  e.g VGS055BASE or  VGS055DBn
        :vg_type: str: BASE OR DB
        :returns: str: vg_name
        """
        self.vg_type = vg_type

        # Checking if vg_type is BASE OR DB
        if  ("BASE" not in self.vg_type) and ("DB" not in self.vg_type):

            self.amd.err_msg("Unsupported use case.",\
                "Use only BASE or DB for volume groups",\
                exit_code = 15)
        # Determining the cluster vg_type : S, I, G, H


        amh = am_aix_hostname.am_aix_hostname()
        cluster_type = amh.get_cluster_type()
        numerical_prefix = amh.get_numerical_prefix()

    
        vg_name = "VG" + \
                cluster_type + \
                numerical_prefix + \
                self.vg_type

        return vg_name

        # }}}
    def is_compiled_name_in_vg_list(self,vg_type="BASE"):# {{{
        """Determines if a compiled name is part of the existing vgs list
        :returns: bool 
        """

        self.vg_type = vg_type
        vg_list = self.get_vgs()
        compiled_vg_name = self.compile_vg_name(vg_type=self.vg_type)
        print vg_list
        print compiled_vg_name
        if compiled_vg_name in vg_list:
            return True
        else:
            return False
        # }}}

    def is_lv(self, lv_name, verbose=False):# {{{
        """Check if lv exists

        :lv_name: The name of Logical Volume. e.g "lyceus"
        :returns: BOOL
        """
        self.lv_name = lv_name
        self.verbose = verbose

        unix_cmd=("lslv"\
                " {}"\
                ).format(lv_name)
        
        if self.verbose == 2:
            print "Debugging:unix_cmd is:{}:".format(unix_cmd)	# FOR Debugging
        
        p = subprocess.Popen(unix_cmd,\
                shell=True, stdout=subprocess.PIPE,\
                stderr=subprocess.STDOUT)
        rc = p.wait()
        
        
            # Unix_cmd has failed
        if rc!=0:
           #  The LV does not exist
           return False
       
            # Unix_cmd executed successfully
        elif rc==0:
           #  The LV exists
           return True
        # }}}
    def is_fs(self, fs_path, verbose=False):# {{{
        """Check if fs  exists

        :fs_path: The path of the FS: e.g."/syslink/lyceus"
        :returns: BOOL
        """
        self.fs_path = fs_path
        self.verbose = verbose

        unix_cmd=("lsfs"\
                " {}"\
                ).format(fs_path)
        
        if self.verbose == 2:
            print "Debugging:unix_cmd is:{}:".format(unix_cmd)	# FOR Debugging
        
        p = subprocess.Popen(unix_cmd,\
                shell=True, stdout=subprocess.PIPE,\
                stderr=subprocess.STDOUT)
        rc = p.wait()
        
        
            # Unix_cmd has failed
        if rc!=0:
           #  The LV does not exist
           return False
       
            # Unix_cmd executed successfully
        elif rc==0:
           #  The LV exists
           return True
        # }}}
    def is_fs_mounted(self, fs_path, verbose=False):# {{{
        """Check if fs is mounted. 

        :fs_path: The path of the FS: e.g."/syslink/lyceus"
        :returns: BOOL
        """
        self.fs_path = fs_path
        self.verbose = verbose

        return os.path.ismount(fs_path)

        # }}}

    def mount_fs(self, fs_path, verbose=False): # {{{
        """Check if fs is mounted. 

        :fs_path: The path of the FS: e.g."/syslink/lyceus"
        :returns: BOOL
        """
        self.fs_path = fs_path
        self.verbose = verbose

        unix_cmd=("/usr/sbin/mount "\
                "{}"\
                ).format(fs_path)
        
        if self.verbose == 2:
            print "Debugging:unix_cmd is:{}:".format(unix_cmd)	# FOR Debugging
        
        p = subprocess.Popen(unix_cmd,\
                shell=True, stdout=subprocess.PIPE,\
                stderr=subprocess.STDOUT)
        rc = p.wait()
        
        
            # Unix_cmd has failed
        if rc!=0:
           return False
        
            # Unix_cmd executed successfully
        elif rc==0:
           return True

        # }}}
    def umount_fs(self, fs_path, verbose=False): # {{{
        """Check if fs is mounted. 

        :fs_path: The path of the FS: e.g."/syslink/lyceus"
        :returns: BOOL
        """
        self.fs_path = fs_path
        self.verbose = verbose

        unix_cmd=("/usr/sbin/umount "\
                " -f "\
                "{}"\
                ).format(fs_path)
        
        if self.verbose == 2:
            print "Debugging:unix_cmd is:{}:".format(unix_cmd)	# FOR Debugging
        
        p = subprocess.Popen(unix_cmd,\
                shell=True, stdout=subprocess.PIPE,\
                stderr=subprocess.STDOUT)
        rc = p.wait()
        
       


            # Unix_cmd has failed
        if rc!=0:
           return False
        
            # Unix_cmd executed successfully
        elif rc==0:
           time.sleep(2)
           if verbose:
               self.amd.ok_msg("FS successfully unmounted:",\
                       fs_path)
           return True

        # }}}

    # Creating a LV# {{{
    def mk_lvm(self, 
            lv_name,\
            fs_type="jfs2",\
            copies=2,\
            vg="rootvg",\
            nr_lp=8,\
            verbose = False):
        """Standard AIX mklv method

        :lv_name: The name of the Logical Volume. e.g. lyceus
        :fs_type: LV type. jfs2 default
        :copies: The nr. of PP allocated for each LP
        :vg: The VG where LV will be created. Default is root
        :nr_lp: Number of Logical Partitions to be created
        :returns: bool

        """
        self.name = lv_name
        self.fs_type = fs_type
        self.copies = copies
        self.vg = vg
        self.nr_lp = nr_lp
        if not self.is_lv(lv_name):
            # create the lv
            # Unix CMD is
            # /usr/sbin/mklv -y 'lyceus' -t'jfs2' -c'2' rootvg 8

            unix_cmd=("/usr/sbin/mklv "\
                    " -y {} "\
                    " -t {}"\
                    " -c {}"\
                    " {}"\
                    " {}"\
                    ).format(lv_name,\
                            fs_type,\
                            copies,\
                            vg,\
                            nr_lp)
            
            if verbose == 2:
                print "Debugging:unix_cmd is:{}:".format(unix_cmd)	# FOR Debugging
            
            p = subprocess.Popen(unix_cmd,\
                    shell=True, stdout=subprocess.PIPE,\
                    stderr=subprocess.STDOUT)
            rc = p.wait()
            
            
                # Unix_cmd has failed
            if rc!=0:
                self.amd.err_msg("Unable to create Logical Volume",\
                        lv_name,\
                        call_admins = True,
                        exit_code = 7)
            
                # Unix_cmd executed successfully
            elif rc==0:
                self.amd.ok_msg("The LV:",\
                        lv_name,\
                        ": has been successfully created.")
                return True
            
        # LV exists: Nothing to do
        else:
            if verbose:
                self.amd.info_msg("The Logical Volume:",\
                        lv_name,\
                        ": exists. Nothing to do")
# }}}
    # Creating a FS# {{{
    def mk_fs(self, 
            lv_name,\
            mount_point,\
            fs_type = "jfs2",\
            agblksize = "4096", \
            permissions = "rw", \
            verbose = False):
        """Standard AIX mklv method

        :lv_name: The name of the Logical Volume. e.g. lyceus
        :mount_point: The FS name/mount_point. eg. /syslink/lyceus
        :fs_type: LV type. jfs2 default
        :agblksize: The block size, default 4096
        :permissions: the FS premissions
        :returns: bool

        """
        self.lv_name = lv_name # The name of the device -d
        self.fs_type = fs_type #  The FS type: default = jfs2
        self.mount_point = mount_point # The mountpoint of the FS
        self.permissions = permissions  # FS permissions [ro|rw]

        if  not self.is_fs(mount_point):
            # create the FS
            # UNIX CMD for FS creation
            # /usr/sbin/crfs -v jfs2 -d'lyceus' -m'/syslink/lyceus'\
            #   -A''`locale yesstr | awk -F: '{print $1}'`'' -p'r# {{{
                        # }}}

            unix_cmd=("/usr/sbin/crfs"\
                    " -d {}"\
                    " -v {} "\
                    " -m {}"\
                    " -p {}"\
                    " -a agblksize={}"\
                    ).format(lv_name,\
                            fs_type,\
                            mount_point,\
                            permissions,\
                            agblksize)
            
            if verbose:
                print "Debugging:unix_cmd is:{}:".format(unix_cmd)	# FOR Debugging
            
            p = subprocess.Popen(unix_cmd,\
                    shell=True, stdout=subprocess.PIPE,\
                    stderr=subprocess.STDOUT)
            rc = p.wait()
            
            
                # Unix_cmd has failed
            if rc!=0:
                self.amd.err_msg("Unable to create the Filesystem",\
                        mount_point,\
                        call_admins = True,
                        exit_code = 8)
            
                # Unix_cmd executed successfully
            elif rc==0:
                self.amd.ok_msg("The Filesystem:",\
                        mount_point,\
                        ": has been successfully created.")
                try:
                    self.mount_fs(mount_point)
                except Exception as e:
                    amd.err_msg("Unable to mount the FS:",\
                            mount_point,\
                            call_admins = True,\
                            exit_code = 9)
                else:
                    return True
            
        # FS exists: Nothing to do
        else:
            if verbose:
                self.amd.info_msg("The Filesystem:",\
                        mount_point,\
                        ": exists. Nothing to do")
# }}}
    # Removing a FS# {{{
    def rm_fs(self, 
            mount_point,\
            verbose = False):
        """Removing an AIX  Filesystem

        :mount_point: The FS name/mount_point. eg. /syslink/lyceus
        :returns: bool
        """
        self.mount_point = mount_point # The mountpoint of the FS

        # check if FS exists
        if  self.is_fs(mount_point):

            # Check if the FS exists and it is mounted
            if self.is_fs_mounted(mount_point):
                if not  self.umount_fs(mount_point, verbose=True):
                    self.amd.err_msg("Unable to unmount FS:",\
                            mount_point,\
                            call_admins = True,\
                            exit_code = 10)





            # remove the FS
            # /usr/sbin/rmfs /syslink/lyceus
            unix_cmd=("/usr/sbin/rmfs"\
                    "  -r "\
                    "  {}"\
                    ).format(mount_point)
            
            if verbose == 2:
                print "Debugging:unix_cmd is:{}:".format(unix_cmd)	# FOR Debugging
            
            p = subprocess.Popen(unix_cmd,\
                    shell=True, stdout=subprocess.PIPE,\
                    stderr=subprocess.STDOUT)
            rc = p.wait()
            
            
                # Unix_cmd has failed
            if rc!=0:
                self.amd.err_msg("Unable to remove the Filesystem",\
                        mount_point,\
                        call_admins = True,
                        exit_code = 8)
            
                # Unix_cmd executed successfully
            elif rc==0:
                self.amd.ok_msg("The Filesystem:",\
                        mount_point,\
                        ": has been successfully removed.")
                return True
            
        # Inexistent: Nothing to do
        else:
            if verbose:
                self.amd.info_msg("Inexistent Filesystem:",\
                        mount_point,": Nothing to do")
# }}}




# End of class: Am_Aix_Lvm
#}}}



# _Refactoring 



class Am_Aix_Fs(object):# {{{

    """Retrieving AIX FS information
    is_fs
    get_owner
    get_group_owner
    get_user_group_owner
    """

    def __init__(self, filename):
        self.filename = filename
        
        # _var = private 


    def is_fs(self):
        self._is_fs = os.path.ismount(self.filename)
        return self._is_fs


    def get_owner(self):
        if self.is_fs():
            self._owner =  getpwuid(stat(self.filename).st_uid).pw_name
            return self._owner


    def get_group_owner(self):
        if self.is_fs():
            self._group_owner =  getpwuid(stat(self.filename).st_gid).pw_name
            return self._group_owner


    def get_user_group_owner(self):
        if self.is_fs():
            self._user_group_list = []
            self._user_group_list.append(self.get_owner())
            self._user_group_list.append(self.get_group_owner())
            return self._user_group_list

    # }}}
    class Am_Aix_Make_Lvm():# {{{
        """Standard Metro AIX LVM operations"""
        def __init__(self,\
                make_lvm_basedir="/home/root/bin/LVM/", \
                make_lvm_executable="make_lvm",\
                make_lvm_input_file_prefix="make_lvm.input_",\
                verbose=False):

            """ TODO: Determine what you want to instantiate """
            self.make_lvm_basedir = make_lvm_basedir
            self.make_lvm_executable = make_lvm_executable
            self.make_lvm_input_file_prefix = make_lvm_input_file_prefix
            self.verbose = verbose

            # Instantiate an amaxh object of am_aix_hostname
            self.amxh = am_aix_hostname.am_aix_sap_hostname()
            self.prefix = self.amxh.get_prefix()   # e.g. s030

            self.lvm_input_file_name = self.make_lvm_input_file_prefix + \
                    self.prefix
            self.lvm_input_file_path = self.make_lvm_basedir + \
                        self.lvm_input_file_name

            # Instantiate an amdisplay object
            self.amd = amdisplay.AmDisplay()
            
            
        
        def compile_mkale_lvm_argument(self,verbose=False):# {{{

            """Compiling the make_lvm argument: e.g.: i333en0
            :returns:str:make_lvm_argument
            """
            self.verbose = verbose
            hostname_prefix = amh.get_prefix()
            make_lvm_argument = hostname_prefix.upper()

            if verbose:
                amd.ok_msg("Compiling make_lvm_argument")
            return make_lvm_argument
           # }}}
        def get_input_file_full_path(self):# {{{
            """Compiling the make_lmv.input_xNNN full path"""
            return self.lvm_input_file_path
# }}}
        def is_make_lvm_script(self):# {{{
            """Checking if /home/rot/bin/LVM/make_lvm script exists
            :returns: bool """
            file = self.make_lvm_executable
            if os.path.isfile(file):
               amd.ok_msg("make_lvm configuration file in place.")
               return True
            else:
               self.amd.err_msg("The file",\
                       file, \
                       "does not exist",\
                       call_admins = True,\
                       exit_code = 14)
            return False
         # }}}
        def is_make_lvm_base_dir(self):# {{{
            """Checking if /home/root/bin/LVM/ directory exists
            returns bool"""
            
            dir =  self.make_lvm_basedir
            if os.path.isdir(dir):
                return True
            else:
                self.amd.err_msg("The directory",\
                        dir, \
                        "does not exist",\
                        call_admins = True,\
                        exit_code = 13)
                return False
            # }}}
        def is_lvm_input_file(self, verbose=False):# {{{
            """Determines if the make_lvm.input_xNN exists 
            returns bool"""
            self.verbose = verbose
            file = self.get_input_file_full_path()

            if os.path.isfile(file):
                amd.ok_msg("make_lvm configuration file in place.")
                return True 
            else:
                print self.get_input_file_full_path()
                self.amd.err_msg("The file ",\
                        file,\
                        "does not exist",\
                        call_admins=True,\
                        exit_code = 14)
                return False
# }}}
            
        def are_uncommented_entries(self,verbose=False):# {{{
            """TODO: Determining if there are uncommented entries into make_user file
            :returns: bool
            """

            self.verbose = verbose
            file_name = self.get_input_file_full_path()
            with open(file_name,'r') as f:
                lines = f.readlines()
            f.close

            header = "#BEGIN"
            all_lines_nr = len(lines)

           
            # Determining the user index line number: first line after the header
                # user_index_line_nr
            line_nr = 0
            for line in lines:
                line_nr += 1
                if line.startswith(header):
                    user_index_line_nr = line_nr
           

            # Checking to see if there are uncommented entries in the\
            # VG section.
                # VG section starts afte the header
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
                       amd.err_msg("Uncommented entries in the VG section",\
                                "of the make_lvm.input file",\
                                call_admins = True,\
                                exit_code = 6)
                user_index_line_nr += 1
            
            if verbose:
                if not no_uncommented_lines:
                    amd.ok_msg("There are no uncommented entries",\
                            " in the LVM conf. file")


# }}}

    def add_make_lvm_entry(self, verbose=False):# {{{

        """Adding configuration line in the male_lvm file used
        to create a new Fs

       #FS:FS:VGKUERZEL:LVNAME:PP_ANZAHL:MOUNTPUNKT:BOOTOPT(yes=true,no=false),NBPI
       FS:FS:VGI333BASE:i333log             :22   :/i333/log                :y
        
        :returns: bool
        """

        
        self.verbose = verbose
        file = self.lvm_input_file_name

        # Checking if lvm_entry_line already exists
        #  TODO
        with open(file,'a') as f:
           f.write(lvm_entry_line + "\n")
        f.close() 

        if verbose:
           amd.ok_msg("Successfully added FS entry in the conf. file")

# }}}
    def rm_make_lvm_entry(self,  verbose=False):# {{{

        """Adding configuration line in the make_lvm file used
        to create a new FS

        :returns: bool
        """

        self.verbose = verbose
        file = self.lvm_input_file_name

        # Removing the user entry line
        pattern_to_remove = lvm_entry_line
        f = open(file,"r+")
        lines = f.readlines()
        f.seek(0)
        for line in lines:
            if pattern_to_remove not in line:
                f.write(line)
        f.truncate()
        f.close()


        if verbose:
           amd.ok_msg("Successfully removed LVM/FSline",\
                   "from the conf. file")

# }}}
             
    def do_aix_make_lvm_prereq(self, verbose=False):# {{{
        self.verbose =  verbose
        ammakelvm = Am_Aix_Make_Lvm()
        """Performing Standard Metro AIX user prerequisites
        - is_lvm_input_file()
        - is_make_lvm_script()
        - are_uncommented_entries()
        verbose: spew verbose output """

        amd.info_msg("    Performing general  AIX make_lvm prerequisites.")
        ammakelvm.is_lvm_input_file(verbose=verbose)
        ammakelvm.is_make_lvm_script(verbose=verbose)
        ammakelvm.compile_mk_user_argument(verbose=verbose)
        ammakelvm.are_uncommented_entries(verbose=verbose)


# }}}


    def add_fs(self, make_lvm_entry, verbose=False):# {{{
        """Adding the user present in the make_user_file """
        self.verbose = verbose
        self.make_lvm_entry = make_lvm_entry


        # YOU ARE HERE
        # Doing the standard make_lvm prerequisites: 
        self.do_aix_user_prereq(verbose=verbose)

        # Generating the argument for make_lvm argument e.g. S055
        make_lvm_argument = self.compile_mk_user_argument()
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



# }}}



# FUNCTIONS
def do_aix_make_lvm_prereq(verbose=False):# {{{
    ammakelvm = Am_Aix_Make_Lvm()
    """Performing Standard Metro AIX user prerequisites
    - is_lvm_input_file()
    - is_make_lvm_script()
    - are_uncommented_entries()
    verbose: spew verbose output """

    amd.info_msg("    Performing general  AIX make_lvm prerequisites.")
    ammakelvm.is_lvm_input_file()
    ammakelvm.is_make_lvm_script()
    ammakelvm.are_uncommented_entries()


# }}}



# TODO: 
# DONE # Check if duplicate entries in the lvm 
# DONE # Add lvm entry
# DONE # Remove lvm entry
# Execute make_lvm






    
