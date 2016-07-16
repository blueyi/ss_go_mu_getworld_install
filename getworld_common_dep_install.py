#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 blueyi <blueyi@blueyi-lubuntu>
#
# Distributed under terms of the MIT license.

import platform
import subprocess
import os
import sys


def del_self():
#    run_cmd('rm -f ' + sys.argv[0])
    pass

apt_list = ['ubuntu', 'debian']
rpm_list = ['fedora', 'centos']
sys_distribution = platform.linux_distribution()[0].lower()
# print(sys_distribution)


def is_list_in_str(tlist, tstr):
    for item in tlist:
        if item in tstr:
            return True
    return False


error_log_file = 'common_install_err.log'
error_log = open(error_log_file, 'w')


def print_to_file(msg, file_opened=error_log):
    print(msg)
    file_opened.write(str(msg) + '\n')


def run_cmd(cmd, args=' ', out=subprocess.PIPE):
    tcall_cmd = cmd + ' ' + args
    p = subprocess.Popen(tcall_cmd, shell=True, stdout=out)
    toutput = p.communicate()[0]
    if p.returncode != 0 and ('grep' not in tcall_cmd):
        if os.geteuid() != 0:
            print_to_file('Please run the script by "root"!')
            sys.exit(1)
        print_to_file('<<< ' + tcall_cmd + '>>> run failed!')
        print("Please contact getworld@qq.com and send install_err.log")
        del_self()
        sys.exit(1)
    return toutput


def first_run_fail(msg):
    print_to_file('System info:')
    for item in platform.uname():
        print_to_file(item)
    print_to_file(msg)
    del_self()
    sys.exit(1)


if os.geteuid() != 0:
    first_run_fail('Please run the script by "root"!')

# if platform.machine().lower() != 'x86_64':
#    first_run_fail('This script only support x86_64 system, please contact getworld@qq.com')


install_cmd = None
dis_cmd = None
mysqldb_dep_name = None
if is_list_in_str(apt_list, sys_distribution):
    install_cmd = 'apt-get install '
    dis_cmd = 'apt'
    run_cmd('apt-get update -y')
    mysqldb_dep_name = 'python-mysqldb'
elif is_list_in_str(rpm_list, sys_distribution):
    install_cmd = 'yum install '
    dis_cmd = 'yum'
    run_cmd('yum update -y')
    mysqldb_dep_name = 'MySQL-python'
else:
    first_run_fail('Your distribution not in supported list, please contact getworld@qq.com')


def package_query_cmd(soft):
    package_query_str = ''
    if dis_cmd == 'apt':
        package_query_str = "dpkg --get-selections | grep '\\b" + soft + "\\s*install'"
    elif dis_cmd == 'yum':
        package_query_str = "rpm -qa | grep '\\b" + soft + "'"
    return package_query_str


def depend_install(soft_list):
    for soft in soft_list.split():
        toutput = run_cmd(package_query_cmd(soft))
        if soft in toutput.__str__():
            print(soft,  '-- You have installed!')
            continue
        run_cmd(install_cmd, soft + ' -y')


# install git
depend_install(mysqldb_dep_name)


ss_install_cmd = "wget --no-check-certificate " \
                 "https://github.com/blueyi/ss_go_mu_getworld_install/raw/master/ss_go_mu_getworld_install_py2.py" \
                 " -O /tmp/ss_getworld_install.py && python /tmp/ss_getworld_install.py"

run_cmd(ss_install_cmd, out=None)

error_log.close()

is_del_err_file = True
with open(error_log_file, 'r') as err:
    for line in err:
        if len(line) != 0:
            is_del_err_file = False

if is_del_err_file:
    run_cmd('rm -f ' + error_log_file)

del_self()
