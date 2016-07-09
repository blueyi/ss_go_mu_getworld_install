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


def del_self():
    run_cmd('rm -f ' + sys.argv[0])
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


error_log_file = 'install_err.log'
error_log = open(error_log_file, 'w')


def print_to_file(msg, file_opened=error_log):
    print(msg)
    file_opened.write(str(msg) + '\n')


def run_cmd(cmd, args=' '):
    tcall_cmd = cmd + ' ' + args
    p = subprocess.Popen(tcall_cmd, shell=True, stdout=subprocess.PIPE)
    toutput = p.communicate()[0]
    if p.returncode != 0 and ('grep' not in tcall_cmd):
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

if platform.uname().machine.lower() != 'x86_64':
    first_run_fail('This script only support x86_64 system, please contact getworld@qq.com')


install_cmd = None
dis_cmd = None
if is_list_in_str(apt_list, sys_distribution):
    install_cmd = 'apt-get install '
    dis_cmd = 'apt'
    run_cmd('apt-get update -y')
elif is_list_in_str(rpm_list, sys_distribution):
    install_cmd = 'yum install '
    dis_cmd = 'yum'
    run_cmd('yum update -y')
else:
    first_run_fail('Your distribution not in supported list, please contact getworld@qq.com')


def package_query_cmd(soft):
    package_query_str = ''
    if dis_cmd == 'apt':
        package_query_str = "dpkg --get-selections | grep '\\b" + soft + "\\s*install'"
    elif dis_cmd == 'yum':
        package_query_str = "rpm -qa | grep '" + soft + "'"
    return package_query_str


def depend_install(soft_list):
    for soft in soft_list.split():
        toutput = run_cmd(package_query_cmd(soft))
        if soft in toutput.__str__():
            print(soft,  '-- You have installed!')
            continue
        run_cmd(install_cmd, soft + ' -y')


# install git
depend_install('git wget')


def epel_url():
    os_ver_num = '7'
    tout = run_cmd('cat /etc/centos-release ')
    tlist = tout.split()
    for word in tlist:
        if word[0].isdigit():
            os_ver_num = str(word[0])
    url = 'dl.fedoraproject.org/pub/epel/' + os_ver_num + '/' \
          + platform.machine() + '/e/'
    return url


# install redis
if dis_cmd == 'yum':
    if 'centos' in sys_distribution:
        tepel = epel_url()
        output = run_cmd(package_query_cmd("epel-release-*"))
        if 'epel' not in output.__str__():
            t_cmd = "wget -r --no-parent -A 'epel-release-*.rpm' http://" + tepel
            run_cmd(t_cmd)
            t_cmd = "rpm -Uvh " + tepel + "epel-release-*.rpm"
            run_cmd(t_cmd)
            run_cmd('rm -rf dl.fedoraproject.org')
        run_cmd('rm -rf dl.fedoraproject.org')
    run_cmd('yum update -y')
    depend_install('redis')
    run_cmd('systemctl start redis.service')
    run_cmd('systemctl enable redis.service')
elif dis_cmd == 'apt':
    depend_install('redis-server')
    run_cmd('service redis-server restart')


def find_str(tstr, tfile):
    with open(tfile, 'r') as text:
        for line in text:
            if tstr in line.lower():
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
    run_cmd('chmod a+x ' + ss_local_path + down_file_name)


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
        down_cmd = 'wget -c -O ' + centos_su_conf_path + 'ssserver.ini' + ' ' + supervisor_url
        run_cmd('systemctl start supervisord.service')
        run_cmd('systemctl enable supervisord.service')

    run_cmd(down_cmd)
    run_cmd('supervisorctl reload')

supervisor_install()

error_log.close()

is_del_err_file = True
with open(error_log_file, 'r') as err:
    for line in err:
        if len(line) != 0:
            is_del_err_file = False

if is_del_err_file:
    run_cmd('rm -f ' + error_log_file)

welcome_print('Install Success!')
del_self()
