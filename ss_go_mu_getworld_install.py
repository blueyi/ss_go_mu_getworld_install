#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import platform
import subprocess
import os
import sys


def welcome_print(msg):
    print('*' * 70)
    print('     <<< ' + msg + ' >>>')
    print('Thanks for the new shadowsocks node you shared to GetWorld.in Group!')
    print('Welcome you join our QQ group(484729827) for more support information!')
    print('*' * 70)

welcome_print('Installing shadowsocks server of GetWorld.in')


apt_list = ['ubuntu', 'debian']
rpm_list = ['fedora', 'centos']
sys_distribution = platform.linux_distribution()[0].lower()
# print(sys_distribution)


def is_list_in_str(tlist, tstr):
    for item in tlist:
        if item in tstr:
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
        print_to_file('<<< ' + tcall_cmd + '>>> run failed!')
        sys.exit(1)


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
    run_cmd('service redis-server restart')


def find_str(tstr, file):
    with open(file, 'r') as text:
        for line in text:
            line = line.lower()
            if tstr in line:
                return True


# install ss-go-mu-getworld
def ss_go_install():
    ss_local_path = '/usr/ss_getworld/'
    ss_remote_path = 'https://gitlab.com/getworld/ss_go_mu_getworld_server/raw/master/mu'
    config_remote_path = 'https://gitlab.com/getworld/ss_go_mu_getworld_server/raw/master/config.conf'
    down_file_name = 'ss_go_getworld'
    if os.path.exists(ss_local_path):
        run_cmd('rm -rf ' + ss_local_path)

    run_cmd('mkdir -p ' + ss_local_path)
    run_cmd('wget -c -O ' + ss_local_path + down_file_name + ' ' + ss_remote_path)
    run_cmd('wget -c -N -P ' + ss_local_path + ' ' + config_remote_path)
    if find_str('sign in', ss_local_path + 'config.conf') or os.path.getsize(ss_local_path + down_file_name) / 1000 < 2000:
        first_run_fail("You don't have the permission to connect to GetWorld.in group!\n"
                       "Please contact getworld@qq.com")


ss_go_install()


# auto start
def supervisor_install():
    depend_install('supervisor')
    supervisor_url = 'https://gitlab.com/getworld/ss_go_mu_getworld_server/raw/master/ssserver.conf'
    down_cmd = ''
    if dis_cmd == 'apt':
        ubuntu_su_conf_path = '/etc/supervisor/conf.d/'
        if not os.path.exists(ubuntu_su_conf_path):
            run_cmd('mkdir -p ' + ubuntu_su_conf_path)
        if os.path.isfile(ubuntu_su_conf_path + 'ssserver.conf'):
            run_cmd('rm -f ' + ubuntu_su_conf_path + 'ssserver.conf')
        down_cmd = 'wget -c -N -P ' + ubuntu_su_conf_path + ' ' + supervisor_url
        run_cmd('service supervisor restart')
    elif dis_cmd == 'yum':
        centos_su_conf_path = '/etc/supervisord.d/'
        if not os.path.exists(centos_su_conf_path):
            run_cmd('mkdir -p ' + centos_su_conf_path)
        if os.path.isfile(centos_su_conf_path + 'ssserver.ini'):
            run_cmd('rm -f ' + centos_su_conf_path + 'ssserver.ini')
        down_cmd = 'wget -c -P ' + centos_su_conf_path + ' ' + '-O ' + 'ssserver.ini' + ' ' + supervisor_url
        run_cmd('systemctl start supervisord.service')
        run_cmd('systemctl enable supervisord.service')

    run_cmd(down_cmd)
    run_cmd('supervisorctl reload')

supervisor_install()

error_log.close()

welcome_print('Install Success!')
