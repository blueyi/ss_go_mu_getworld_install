#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import platform
import subprocess
import os
import sys


print('*' * 70)
print('Thanks for the new shadowsocks node you shared to GetWorld.in Group!')
print('Welcome you join our QQ group(484729827) for more support information!')
print('*' * 70)


apt_list = ['ubuntu', 'debian']
rpm_list = ['fedora', 'centos']
sys_distribution = platform.linux_distribution()[0].lower()
# print(sys_distribution)


def is_list_in_str(tlist, str):
    for item in tlist:
        if item in str:
            return True
    return False


error_log_file = 'install_err.log'
error_log = open(error_log_file, 'w')


def print_to_file(msg, file_opened=error_log):
    print(msg)
    file_opened.write(str(msg) + '\n')


def first_run_fail(msg):
    print_to_file('System info:')
    for item in platform.uname():
        print_to_file(item)
    print_to_file(msg)
    sys.exit(1)


if os.geteuid() != 0:
    first_run_fail('Please run the script by "root"!')

if platform.uname().machine.lower() != 'x86_64':
    first_run_fail('This script only support x86_64 system, please contact getworld@qq.com')

install_cmd = None
dis_cmd = None
if is_list_in_str(apt_list, sys_distribution):
    install_cmd = 'apt-get install '
    dis_cmd = 'apt'
elif is_list_in_str(rpm_list, sys_distribution):
    install_cmd = 'yum install '
    dis_cmd = 'yum'
else:
    first_run_fail('Your distribution not in supported list, please contact getworld@qq.com')


def run_cmd(cmd, args=' '):
    tcall_cmd = cmd + ' ' + args
    if subprocess.call(tcall_cmd, shell=True) != 0:
        print_to_file('<<<' + tcall_cmd + '>>> run failed!')


def depend_install(soft_list):
    run_cmd(install_cmd, soft_list + ' -y')


# install git
depend_install('git wget')


# install redis
if dis_cmd == 'yum':
    t_cmd = "wget -r --no-parent -A 'epel-release-*.rpm' http://dl.fedoraproject.org/pub/epel/7/x86_64/e/"
    run_cmd(t_cmd)
    t_cmd = "rpm -Uvh dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-*.rpm"
    run_cmd(t_cmd)
    run_cmd('yum update -y')
    depend_install('redis')
    run_cmd('systemctl start redis.service')
    run_cmd('systemctl enable redis.service')
elif dis_cmd == 'apt':
    depend_install('redis-server')
    run_cmd('service redis-server start')


# install ss-go-mu-getworld
def ss_go_install():
    ss_local_path = '/usr/ss_getworld'
    ss_remote_path = 'https://gitlab.com/getworld/ss_go_mu_getworld_server/raw/master/mu'
    config_remote_path = 'https://gitlab.com/getworld/ss_go_mu_getworld_server/raw/master/config.conf'
    run_cmd('mkdir ' + ss_local_path)
    run_cmd('wget -c -P ' + ss_local_path + ' ' + ss_remote_path)
    run_cmd('wget -c -P ' + ss_local_path + ' ' + config_remote_path)




# auto start


error_log.close()