#! /usr/bin/env python
# -*- coding: utf-8 -*-
import platform
import subprocess
import os
import sys
import MySQLdb
import socket
import fcntl
import struct


def welcome_print(msg):
    print('*' * 70)
    print('     <<< ' + msg + ' >>>')
    print('Thanks for the new shadowsocks node you shared to GetWorld.in Group!')
    print('Welcome you join our QQ group(484729827) for more support information!')
    print('*' * 70)

welcome_print('Installing shadowsocks server of GetWorld.in')


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
# depend_install('git wget ' + mysqldb_dep_name)


def epel_url(ver_num=7, mac='x86_64'):
    if ver_num < 7:
        if mac == 'i686':
            mac = 'i386'
            url = 'dl.fedoraproject.org/pub/epel/' + str(ver_num) + '/' + mac + '/'
        else:
            url = 'dl.fedoraproject.org/pub/epel/' + str(ver_num) + '/' + mac + '/' 
    else:
        url = 'dl.fedoraproject.org/pub/epel/' + str(ver_num) + '/' \
                + mac + '/e/'
    return url


def centos_ver():
    t_os_ver_num = 7
    tout = run_cmd('cat /etc/centos-release ')
    tlist = tout.split()
    for word in tlist:
        if word[0].isdigit():
            t_os_ver_num = int(word[0])
    return t_os_ver_num
 

def centos6_install_redis():
    if os.path.exists('redis-2.8.4'):
        run_cmd('rm -rf redis-*')
    depend_install('gcc make tcl')
    redis_v284_url = 'http://download.redis.io/releases/redis-2.8.4.tar.gz'
    run_cmd('wget -c ' + redis_v284_url)
    run_cmd('tar -zxvf redis-2.8.4.tar.gz')
    os.chdir('redis-2.8.4')
    run_cmd('make && make install')
    redis_conf_url = 'https://bitbucket.org/getworld/ss_go_mu_getworld_server/raw/master/redis.conf'
    redis_init_url = 'https://bitbucket.org/getworld/ss_go_mu_getworld_server/raw/master/redis'
    run_cmd('wget -O /etc/redis.conf ' + redis_conf_url)
    run_cmd('wget -O /etc/init.d/redis ' + redis_init_url)
    run_cmd('chmod +x /etc/init.d/redis')
    run_cmd('chkconfig redis on')
    run_cmd('service redis start')
    os.chdir('..')
    run_cmd('rm -rf redis-*')


# install redis
if dis_cmd == 'yum':
    if 'centos' in sys_distribution:
        os_ver_num = centos_ver()
        machine = platform.machine()
        if os_ver_num < 7:
            centos6_install_redis()
        else:
            tepel = epel_url(os_ver_num, machine)
            output = run_cmd(package_query_cmd("epel-release-*"))
            if 'epel' not in output.__str__():
                t_cmd = "wget -r --no-parent -A 'epel-release-*.rpm' http://" + tepel
                run_cmd(t_cmd)
                t_cmd = "rpm -Uvh " + tepel + "epel-release-*.rpm"
                run_cmd(t_cmd)
                run_cmd('rm -rf dl.fedoraproject.org')
            run_cmd('yum update -y')
            depend_install('redis')
            run_cmd('service redis restart')
            run_cmd('chkconfig redis on')
    else:
        run_cmd('yum update -y')
        depend_install('redis')
        run_cmd('systemctl start redis.service')
        run_cmd('systemctl enable redis.service')
elif dis_cmd == 'apt':
    depend_install('redis-server')
    run_cmd('service redis-server restart')


def find_str(tstr, tfile):
    with open(tfile, 'r') as text:
        for tline in text:
            if tstr in tline.lower():
                return True


# install ss-go-mu-getworld
def ss_go_install():
    ss_remote_path = ''
    ss_local_path = '/usr/ss_getworld/'
    if platform.machine().lower() == 'x86_64':
        ss_remote_path = 'https://bitbucket.org/getworld/ss_go_mu_getworld_server/raw/master/mu_x64'
    else:
        ss_remote_path = 'https://bitbucket.org/getworld/ss_go_mu_getworld_server/raw/master/mu_x86'
    config_remote_path = 'https://bitbucket.org/getworld/ss_go_mu_getworld_server/raw/master/config.conf'
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


# modify ss config and add node to db
local_ip = '127.0.0.1'

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        return socket.inet_ntoa(fcntl.ioctl(
                s.fileno(),
                0x8915,
                struct.pack('256s', ifname[:15])
                )[20:24])
    except :
        ips = run_cmd("LANG=C ifconfig | grep \"inet addr\" | grep -v \"127.0.0.1\" | awk -F \":\" '{print $2}' | awk '{print $1}'")
        return ips
    return '127.0.0.1'

net_list = ['eth0', 'venet0:0']
for net_name in net_list:
    realip = get_ip_address(net_name)
    if realip != '127.0.0.1' and len(realip) > 7:
        local_ip = realip
        break


db = MySQLdb.connect(host="sssql.getworld.in",
                     user="ss",
                     passwd="LoveGetWorld2016",
                     db="shadowsocks",
                     charset="utf8")
cur = db.cursor()
cur.execute("SELECT id, server FROM ss_node")
server_dict = {}
for row in cur.fetchall():
    server_dict[row[1]] = row[0]


cur.execute("SELECT `key` FROM mu_key")
mu_key = ''
for row in cur.fetchall():
    mu_key = row[0]


def max_id():
    maxid = 1
    for se in server_dict.items():
        if maxid < se[1]:
            maxid = se[1]
    return maxid

node_id = max_id() + 1


def insert_ip(tnode_id, ip_addr, db_cursor, db_table):
    name = "'" + ip_addr + "'"
    ss_type = '1'
    method = "'aes-128-cfb'"
    cust_method = '1'
    traffic_rate = '1'
    info = "'NULL'"
    status = "'可用'"
    offset = '0'
    sort = str(tnode_id)
    insert_command = "INSERT INTO " + db_table + " VALUES(" + str(tnode_id) + "," + \
            name + "," + ss_type + "," + name + "," + method + "," + cust_method + "," + \
            traffic_rate + "," + info + "," + status + "," + offset + "," + sort + ")"
#    print(insert_command)
    db_cursor.execute(insert_command)


def del_dup_ip(ip_addr, ser_dic, db_cursor, db_table):
    del_cmd = "DELETE FROM " + db_table + " WHERE server=" + "'" + ip_addr + "'"
    if ip_addr in ser_dic:
        db_cursor.execute(del_cmd)

# del_dup_ip(local_ip, server_dict, cur, 'ss_node')
insert_ip(node_id, local_ip, cur, 'ss_node')

db.commit()
cur.close()
db.close()


# modify ss config node id
def replace_str_in_file(otstr, ntstr, tfile):
    sed_cmd = "sed -i 's/" + otstr + "/" + ntstr + "/g' " + tfile
    run_cmd(sed_cmd)


def modify_node_id(tnode_id, config_file):
    old_str = "^node.*"
    new_str = "node " + str(tnode_id)
    replace_str_in_file(old_str, new_str, config_file)


ss_config_file_path = '/usr/ss_getworld/config.conf'

modify_node_id(node_id, ss_config_file_path)


# modify ss config mu key
def modify_mu_key(tmu_key, config_file):
    old_str = "^key.*"
    new_str = "key " + tmu_key
    replace_str_in_file(old_str, new_str, config_file)


modify_mu_key(mu_key, ss_config_file_path)


# supervisord install
def centos6_install_supervisord():
    run_cmd('yum install python-setuptools -y')
    run_cmd('easy_install supervisor')
    down_su_init = 'https://bitbucket.org/getworld/ss_go_mu_getworld_server/raw/master/supervisord'
    down_su_init_cmd = 'wget -O /etc/rc.d/init.d/supervisord ' + down_su_init
    down_su_conf = 'https://bitbucket.org/getworld/ss_go_mu_getworld_server/raw/master/supervisord.conf'
    down_su_conf_cmd = 'wget -O /etc/supervisord.conf ' + down_su_conf
    run_cmd(down_su_init_cmd)
    run_cmd(down_su_conf_cmd)
    run_cmd('chmod 755 /etc/rc.d/init.d/supervisord')
    run_cmd('chkconfig --add supervisord')
    run_cmd('chkconfig supervisord on')


# auto start
def supervisor_install():
    supervisor_url = 'https://bitbucket.org/getworld/ss_go_mu_getworld_server/raw/master/ssserver.conf'
    down_cmd = ''
    supervisor_log_path = '/var/log/supervisor/'
    if not os.path.exists(supervisor_log_path):
        run_cmd('mkdir -p ' + supervisor_log_path)
    if dis_cmd == 'apt':
        depend_install('supervisor')
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
        if centos_ver() < 7:
            centos6_install_supervisord()
            run_cmd('service supervisord restart')
        else:
            depend_install('supervisor')
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
