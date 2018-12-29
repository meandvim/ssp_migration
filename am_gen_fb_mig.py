#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" This module is used generate: node_firstboot_lpar file
    It should only be used for migrating pursposes and not for provisioning
It has the following main sections:
    - IP configuration 
    - IP alias configuration 
    - IP default route configuration 

    - hostname
    - nostart 
    - syssdumpdev
    - date
    - boot_list
    - boot_image

    -It relies on "compile_ini" module for IP configuration
Todo:
    Compile  LVM Stings
"""

import sys
sys.path.append("/usr/local/rootbin/Pythonlib/")
import am_comp_ini as inif


# Temp

fb_file=False
ini_file=False


# fb_file="test_fb.sh"
# ini_file="/space/node_ini_s230en0"


# ATOMIC
def write_header(fb_file,ini_file,verbose=False):# {{{
   """Writing the header 
   :returns: bool

   """
   line=""
   line+="#!/usr/bin/ksh \n\n"

   with open(fb_file,'w') as f:
         f.write(line)
   f.close()
# }}}
def write_variables(fb_file,ini_file,verbose=False):# {{{
   """Defining the variables
   :returns: TODO

   """
   line=""
   # SSH 
   line+="### Variable definitions \n"
   line+="SSH_PUBKEY_ROOT_CSM='ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDuYQMctF6lye53LGWNwcR/Q+lmag1cIpi1xDzos+vpsryPeGO0qD9CGxcZQ9KhexHs/0UG5QxDrIIPPpR+SU89XQtxLCpNzDzdyRoU4bnIy1c07jsM2TQjmAAwu8AYmeqR4Z1S60Cgd2gv80PWp+ImzEpCODJoI7oc6np86wsUtlccU6Md398CHDQKlGd3LamebSl/5T/WWusl3qQJMKl0YbjKyeRzBLYpx0JQzWA0HLYYJo575er+RBWDwQDr6RqomUmvmMAZDcUNtFJvmz/SC5AZRVETSa1aRkkGrd2v64WV+xB/293mI+wAUWRMzGk7FXKTtUjZ1ToSa75pT0q1 root@aix00p04'"
   line+="\n"
   line+="SSH_PUBKEY_ROOT_GLOBAL_NIM_1='ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC+3Qunr9JaugqEyYHgU8gpQd1oLikrOP/qfDnOxCBxUIaN93JTge/YEpmqrYd+i9LBQEvsOuVKxleF51tbcVfouxXPhWQzGIq6BdcF3FVIw1s3cpbweNi1KAksIYsvUHqvuUhQxjErEXhm/I6JwD/Cq4vmMVcBfjAyOXyfAQAOKZsaKxPytA13mgXyaoTlXZHOrjjvK4WNXf1RVld8ET7gHApiKUIe1fZApv8YpR75l8eCsMieBZSNRIKQc4aLOtn/0rTthedbFYhGWX0Erhhav8PZc6meKJNvcqdBKauqFd+yFaWROftBOLd0yiDLPtGxUkRvmCp/Gd7KIjxzzDUj root@i666en0'"
   line+="\n\n"


   line+="#\n"
   line+="# Dump Device\n"
   line+="#\n"
   line+="DUMP_PRI='/dev/lg_dumplv'\n"
   line+="DUMP_SEC='/dev/sysdumpnull'\n"
   line+="DUMP_DIR='/cpdump'\n"

   line+="\n"

   line+="BOOT_LIST='hdisk0'\n\n"



   with open(fb_file,'a') as f:
         f.write(line)
   f.close()
   if verbose:
       print " #-> Writing the global variable section:"
# }}}
def redirect_output(fb_file,ini_file,verbose=False):# {{{
   """Redirects the output to: /etc/fb_date
   :returns: TODO

   """
   line=""
   line+="#\n"
   line+="# Redirecting the output and create a log file\n"
   line+="#\n"
   line+="exec 1>/etc/${0##*/}.log \n"
   line+="exec 2>&1 \n\n"

   with open(fb_file,'a') as f:
         f.write(line)
   f.close()


   if verbose:
       print " #-> Redirecting the output to /etc/fb_node:"
# }}}


def write_ssh_inject(fb_file,ini_file,verbose=False):# {{{
   """Injecting the global nim_1 ssh key
   :returns: none

   """

   # retrieving the root home directory
   root_home = inif.get_root_homedir(ini_file)

   line=""
   line+='\necho "### Attempting to inject the  global NIM ssh key"\n'
   line+="#\n"
   line+="# SSH INJECTION \n"
   line+="#\n"

   line+='ssh_auth_key_file="{}/.ssh/authorized_keys2"\n\n'.format(root_home)
   line+='if /usr/bin/grep -Fxq "${SSH_PUBKEY_ROOT_GLOBAL_NIM_1}"  "${ssh_auth_key_file}"\n'
   line+='then\n'
   line+='  echo "The ssh key exists, nothing to do"\n'
   line+='else\n'
   line+='  #  Inject ssh \n'
   line+='  echo "I am injecting the ssh key"\n'
   line+='  echo "${SSH_PUBKEY_ROOT_GLOBAL_NIM_1}"  >>  "${ssh_auth_key_file}"\n'
   line+='fi\n'
   line+="\n"


   with open(fb_file,'a') as f:
         f.write(line)
   f.close()

   if verbose:
       print " #-> Writing the ssh injection section:"

# }}}

def write_ip_configuration(fb_file,ini_file,verbose=False):# {{{
   """Writing the IP configuration
   :returns: none

   """
   line="\n### IP configuration\n"
   line+='\necho "### Starting the IP configuration"\n'
   ip_string=inif.compile_ip_string(ini_file,verbose=False)
   line+=ip_string
   line+="\n"

   with open(fb_file,'a') as f:
         f.write(line)
   f.close()

   if verbose:
       print " #-> Writing the IP configuration section:"
   
# }}}
def write_alias_configuration(fb_file,ini_file,verbose=False):# {{{
   """Writing the IP Alias configuration
   :returns: none

   """
   line="\n### IP ALIAS configuration\n"
   line+='\necho "### Starting the IP ALIAS configuration"\n'
   line+=inif.compile_ip_alias_string(ini_file,verbose=False)
   line+="\n"

   with open(fb_file,'a') as f:
         f.write(line)
   f.close()


   if verbose:
       print " #-> Writing the IP Alias section:"
# }}}
def write_default_route(fb_file,ini_file,verbose=False):# {{{
   """Writing the default route
   :returns: none

   """
   line="\n### Default route configuration\n"
   line+='\necho "### Starting the GATEWAY configuration"\n'
   line+=inif.compile_default_route_string(ini_file,verbose=False)
   line+="\n"

   with open(fb_file,'a') as f:
         f.write(line)
   f.close()

   if verbose:
       print " #-> Writing the IP Gateway section:"

# }}}
def write_date(fb_file,ini_file,verbose=False):# {{{
   """Writing the date
   :returns: none

   """

   line="\n### Date configuration\n"
   line+='\necho "### Starting the DATE configuration"\n'
   line+="stopsrc -s xntpd >/dev/null 2>&1 \n"
   line+="ntpdate timeserver.mgi.de \n"
   line+="startsrc -s xntpd >/dev/null 2>&1 \n"

   line+="\n"

   with open(fb_file,'a') as f:
         f.write(line)
   f.close()
# }}}
def write_bootlist(fb_file,ini_file,verbose=False):# {{{
   """Writing the  bootlist
   :returns: none

   """

   line="\n### Bootlist configuration\n"
   line+='\necho "### Starting the BOOTLIST configuration"\n'
   line+="bootlist -m normal $BOOT_LIST  2>&1 \n"
   line+="\n"

   with open(fb_file,'a') as f:
         f.write(line)
   f.close()

   if verbose:
       print " #-> Writing the Bootlist section:"
# }}}
def write_bootimage(fb_file,ini_file,verbose=False):# {{{
   """Writing the bootimage
   :returns: none

   """

   line="\n### Bootimage configuration\n"
   line+='\necho "### Writing the BOOTLIST" \n'
   line+="bosboot -a -d $BOOT_LIST 2>&1 \n "
   line+="\n"

   with open(fb_file,'a') as f:
         f.write(line)
   f.close()
# }}}
def write_nostart(fb_file,ini_file,verbose=False):# {{{
   """Writing the /etc/nostart file
   :returns:bool

   """

   line="\n### Creating the /etc/nostart file\n"
   line+='\necho "### Creating the /etc/nostart file" \n'
   line+="/usr/bin/touch /etc/nostart 2>&1 \n "
   line+="\n"

   with open(fb_file,'a') as f:
         f.write(line)
   f.close()
# }}}
# COMPOSITION

def generate_fb_file(fb_file,ini_file,verbose=False):# {{{
   """It generates the firstboot file to be used after the migration

   :fb_file: the first_boot file
   """
   write_header(fb_file)
   write_variables(fb_file)
   redirect_output(fb_file)
   write_ssh_inject(fb_file)
   write_ip_configuration(fb_file)
   write_alias_configuration(fb_file)
   write_default_route(fb_file)
   write_date(fb_file)
   write_bootlist(fb_file)
   write_bootimage(fb_file)
   write_nostart(fb_file)
# }}}
def main(fb_file,ini_file,verbose=False):# {{{
   """It generates the firstboot file to be used after the migration
    :fb_file: The full path of the firstboot file to be generated
      It performs the following actions
        - write_header(fb_file)
        - write_variables(fb_file)
        - redirect_output(fb_file)
        - write_ssh_inject(fb_file)
        - write_ip_configuration(fb_file)
        - write_alias_configuration(fb_file)
        - write_default_route(fb_file)
        - write_date(fb_file)
        - write_bootlist(fb_file)
   """
   if verbose:
       print "# Generating the fb script: {}".format(fb_file)

   write_header(fb_file,ini_file,verbose=verbose)
   write_variables(fb_file,ini_file,verbose=verbose)
   redirect_output(fb_file,ini_file,verbose=verbose)
   write_ssh_inject(fb_file,ini_file,verbose=verbose)
   write_ip_configuration(fb_file,ini_file,verbose=verbose)
   write_alias_configuration(fb_file,ini_file,verbose=verbose)
   write_default_route(fb_file,ini_file,verbose=verbose)
   write_date(fb_file,ini_file,verbose=verbose)
   write_bootlist(fb_file,ini_file,verbose=verbose)
   write_bootimage(fb_file,ini_file,verbose=verbose)
   write_nostart(fb_file,ini_file,verbose=verbose)
# }}}
if __name__ == "__main__":

   if not fb_file:
       print "This module is NOT intended as a script"
   else:
       main(fb_file, ini_file,verbose=False)
       print "fb_script generated: {}".format(fb_file)
