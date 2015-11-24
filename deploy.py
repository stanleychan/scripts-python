#!/usr/bin/env python

import pexpect
import os
import subprocess
import time

GIT_ADDRESS = 'http://localhost:3000/XLV5/pem.git'
SERVER_ADDRESS = 'root@10.251.196.224'
PASSWORD = None
FILE_W = None

def get_sevpasswd():
    global PASSWORD
    file = open('./.srv_passwd', 'r')
    try:
        PASSWORD = file.readline()
    finally:
        file.close()
        print PASSWORD
        print 'HHH'
        return PASSWORD

def init_log():
    global FILE_W
    FILE_W = open('./.deploy_log', 'a')

def close_log():
    global FILE_W
    try:
        logging(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
        FILE_W.close()
    except NameEroor:
        print 'FILE_W does not exist'
    
def logging(msg):
    global FILE_W
    try:
        FILE_W.write(msg+'\n')
    finally:
        pass

def perform_cmd(*popen_args, **kwargs):
    """Run command with arguments and return its output as a byte string.
    Backported from Python 2.7."""
    process = subprocess.Popen(stdout=subprocess.PIPE, *popen_args, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode:
        command = kwargs.get('args')
        if command is None:
            command = popen_args[0]
        error = subprocess.CalledProcessError(retcode, command)
        error.output = output
        raise error
    return output

def get_latest_code(git_path):
    if os.path.exists('pem_base'):
        os.chdir('./pem_base')
        perform_cmd(['git', 'pull'])
        os.chdir('..')
    else:
        perform_cmd(['git', 'clone', git_path, './pem_base'])

#    if os.path.exists('pem'):
#        perform_cmd(['rm', './pem', '-rf'])

    perform_cmd(['cp', 'pem_base', 'pem', '-rf'])
    perform_cmd(['rm', './pem/.git', '-rf'])

    print 'compress code'
    perform_cmd(['tar', 'czf', 'pem.tar.gz', './pem'])
    print "Compress process finished"
    logging('get the lastest code for git repository and compressed it')

def ssh_cmd(passwd, cmd):
    ret = -1
    ssh = pexpect.spawn('ssh %s "%s"' % (SERVER_ADDRESS, cmd))
    try:
        i = ssh.expect(['password:', 'continue connecting (yes/no)?'], timeout=100)
        if i == 0:
            ssh.sendline(passwd)
            print "expect2"
        elif i == 1:
            ssh.sendline('yes\n')
            ssh.expect('password:')
            ssh.sendline(passwd)
            r = ssh.read()
            print r
    except pexpect.EOF:
        ssh.close()
        ret = 0

    except pexpect.TIMEOUT:
        print 'TIMEOUT'
        ret = -1
    return ret

def ssh_scp():
    pass

def backup_server_code():
    global PASSWORD
    ssh_cmd(PASSWORD, 'cd /var/www && tar czf pem_online.tar.gz pem')
    logging('backup online code successfully')

def update_server_code():
    path = SERVER_ADDRESS + ':/var/www'
    perform_cmd(['scp', 'pem.tar.gz', path])

    global PASSWORD
    ssh_cmd(PASSWORD, 'cd /var/www && tar xzf pem_bak.tar.gz')
    logging('deploy code successfully')
    return
   

def deploy(git_path):
    init_log()
    get_sevpasswd()
    get_latest_code(git_path)
    backup_server_code()
    update_server_code()
    close_log()



### main function
if __name__ == '__main__':
    deploy(GIT_ADDRESS)


