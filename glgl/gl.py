import os
import struct
import atexit
from datetime import datetime
from time import sleep
import argparse
import json
import re
import numpy as np
import signal
import sys
import socket
import time
import pkg_resources
from glgl.hash import deterministic_hash

class gl(object):

    def __init__(self, config, oneshot=False):
        self.config = config
        self.tcp = Tcp(config['timeout'])
        if not self.tcp.open(config['ip'], config['port']):
            print('TCP connection error')
            print('IP address {}, Port {}'.format(config['ip'], config['port']))
            sys.exit(1)
        if oneshot:
            return

        self.initial_setting()
        self.read_settings(config['dump_input'])

        self.config_hash = deterministic_hash(config, 6)
        print('Run hash is {}.'.format(self.config_hash))
        config_json = open(config['path'] + self.config_hash + ".json", "w")
        json.dump(config, config_json, indent = 4)
        config_json.close()

        config_json = open(pkg_resources.resource_filename('glgl', 'data') + '/' + self.config_hash + ".json", "w")
        json.dump(config, config_json, indent = 4)
        config_json.close()


        if 'mysql' in config['output']:
            import pymysql.cursors
            conn = pymysql.connect(**config['mysql']['login'])
            self.cursor = conn.cursor()
            self.cursor.execute("CREATE DATABASE IF NOT EXISTS " + config['mysql']['name'])
            self.cursor.execute("USE " + config['mysql']['name'])
            table_name = config['mysql']['table_name'] if 'table_name' in config['mysql'] else 'data'
            if table_name == 'hash':
                table_name = self.config_hash
            create_table_query = 'CREATE TABLE IF NOT EXISTS {} (id INT AUTO_INCREMENT, time TIMESTAMP not null default CURRENT_TIMESTAMP,'.format(table_name)
            for name in self.names:
                create_table_query += (name+' FLOAT,')
            create_table_query += 'hash VARCHAR(6), log_time TIMESTAMP, PRIMARY KEY (id))'
            self.cursor.execute(create_table_query)
            insert_query = 'INSERT INTO ' + table_name + '(log_time, '
            for name in self.names:
                insert_query += (name + ', ')
            self.insert_query = insert_query + 'hash) VALUES (' + ('%s,'*(self.n_channels+2))[:-1] + ')'

    def __del__(self):
        self.tcp.close()


    def loop(self):
        while True:
            now = datetime.now()
            date = now.strftime("%Y%m%d")

            msg = self.tcp.send_read_command('MEAS:OUTP:ONE?')
            try:
                data = np.array(struct.unpack_from('>{}h'.format(self.n_channels), msg, 8)) * self.conv_factors
            except:
                sleep(0.1)
                continue

            if 'csv' in self.config['output']:
                if self.config['csv']['time_format'] == 'timestamp':
                    time_str = str(int(now.timestamp()))
                elif self.config['csv']['time_format'] == 'datetime':
                    time_str = now.strftime("%Y-%m-%d %H:%M:%S.%f")
                else:
                    time_str = now.strftime(self.config['csv']['time_format'])
                outfilename = self.get_outfilename(self.config, self.config_hash, date)
                # File existance check
                delim = self.config['csv']['delimiter']
                commentout_string = self.config['csv']['commentout_string']
                if not os.path.isfile(outfilename):
                    with open(outfilename, mode='a') as f:
                        f.write(commentout_string+'time')
                        for name in self.names:
                            f.write(delim + name)
                        f.write('\n')
                with open(outfilename, mode='a') as f:
                    f.write(time_str)
                    for d in data:
                        f.write(delim+"{:>5.6f}".format(d))
                    f.write('\n')

            if 'mysql' in self.config['output']:
                try:
                    self.cursor.execute(self.insert_query, tuple([now.strftime("%Y-%m-%d %H:%M:%S.%f")] + data.tolist() + [self.config_hash]))
                except:
                    sleep(0.1)
                    continue
                
            sleep(self.config['sampling_time'])


    def oneshot_command(self, cmd):
        if '?' in cmd:
            msg = self.tcp.send_read_command(cmd)
            print(msg)
        else:
            self.tcp.send_command(cmd)
        return


    def initial_setting(self):

        tcp = self.tcp
        config = self.config
        self.max_n_channels = int(tcp.send_read_command(":INFO:CH?")[len(':INFO:CH?'):])
        self.names = []

        for i_channel in range(self.max_n_channels):
            ich = str(i_channel+1)

            if ich not in config['channels']:
                if "default" not in config['channels']:
                    print('Channel {} or default are not set. Turn off.'.format(ich))
                    tcp.send_command(':AMP:CH{}:INP OFF'.format(ich))
                    continue
                else:
                    c = config['channels']['default']
            else:
                c = config['channels'][ich]



            if 'input' not in c:
                print('Channel {} input is not set or invalid. Turn off.'.format(ich))
                tcp.send_command(':AMP:CH{}:INP OFF'.format(ich))
                continue

            temp_options = ['TCK', 'TCJ', 'TCT', 'TCR', 'TCE', 'TCB', 'TCS', 'TCN', 'TCW', 'PT100', 'JPT100', 'PT1000']
            if 'DC' == c['input']:
                if 'name' in c:
                    tcp.send_command(':ANN:CH{} {}'.format(ich, c['name']))
                    self.names.append(c['name'])
                else:
                    self.names.append('ch' + ich)

                tcp.send_command(':AMP:CH{}:INP DC'.format(ich))
                options = ['20MV', '50MV', '100MV', '200MV', '500MV', '1V', '2V', '5V', '10V', '20V', '50V', '100V', '1-5V']
                if ('range' in c) and (c['range'] in options):
                    tcp.send_command(':AMP:CH{}:RANG {}'.format(ich, c['range']))
                else:
                    print('Channel {} range is not set or invalid. Set 10V'.format(ich))
                    tcp.send_command(':AMP:CH{}:RANG {}'.format(ich, '10V'))
                if ('filter' in c) and c['filter'] in ['off', 'OFF', 2, 5, 10, 20, 40]:
                    tcp.send_command(':AMP:CH{}:FILT {}'.format(ich, c['filter']))
                else:
                    tcp.send_command(':AMP:CH{}:FILT {}'.format(ich, 'OFF'))

            elif c['input'] in temp_options:
                if 'name' in c:
                    tcp.send_command(':ANN:CH{} {}'.format(ich, c['name']))
                    self.names.append(c['name'])
                else:
                    self.names.append('ch' + ich)
                tcp.send_command(':AMP:CH{}:INP TEMP'.format(ich))
                tcp.send_command(':AMP:CH{}:TEMPI {}'.format(ich, c['input']))

                options = ['100', '500', '2000']
                if ('range' in c) and (c['range'] in options):
                    tcp.send_command(':AMP:CH{}:TEMPR {}'.format(ich, c['range']))
                else:
                    print('Channel {} range is not set or invalid. Set 2000 (degree)'.format(ich))
                    tcp.send_command(':AMP:CH{}:TEMPR {}'.format(ich, '2000'))

                if ('filter' in c) and c['filter'] in ['off', 'OFF', 2, 5, 10, 20, 40]:
                    tcp.send_command(':AMP:CH{}:FILT {}'.format(ich, c['filter']))
                else:
                    tcp.send_command(':AMP:CH{}:FILT {}'.format(ich, 'OFF'))

            elif 'OFF' == c['input']:
                tcp.send_command(':AMP:CH{}:INP OFF'.format(ich))

            else:
                print('Channel {} input {} is not supported. Turn off.'.format(ich, c['input']))
                tcp.send_command(':AMP:CH{}:INP OFF'.format(ich))

            if 'cmd' in c:
                tcp.send_command(c['cmd'])
                if self.tcp.send_read_command(":AMP:CH{}?".format(ich)).split(';')[0].split(' ')[1] == 'OFF':
                    continue

                if 'name' in c:
                    tcp.send_command(':ANN:CH{} {}'.format(ich, c['name']))
                    self.names.append(c['name'])
                else:
                    self.names.append('ch' + ich)

            self.names = [n.replace(' ', '_') for n in self.names]
            if len(self.names) != len(set(self.names)):
                print('Error: channel names should be unique.')
                sys.exit(1)
            self.n_channels = len(self.names)

        return


    def read_settings(self, dump=False):
        tcp = self.tcp
        binary_conversion_factors = []
        dcranges = dict(zip([ '20MV', '50MV','100MV', '200MV', '500MV',  '1V', '2V', '5V', '10V', '20V', '50V', '100V', '1-5V'],
                            [1000000, 400000, 200000,  100000,   40000, 20000,10000, 4000,  2000,  1000,   400,    200,   4000]))
        for i_channel in range(self.max_n_channels):
            ich = str(i_channel+1)
            msg = tcp.send_read_command(":AMP:CH{}?".format(ich))
            # message format
            # ":AMP:CH1:INP TEMP;TEMPI TCT;TEMPR 2000;RANG NONE;FILT 10;ATEMP NONE;VOLT NONE;POWF NONE;SUBS NONE;CO2CAL NONE;TYP M"
            sp = msg.split(';')
            if 'TEMP' == sp[0].split(' ')[1]:
                if '2000' == sp[2].split(' ')[1]:
                    binary_conversion_factors.append(1./10)
                elif '500' == sp[2].split(' ')[1]:
                    binary_conversion_factors.append(1./40)
                elif '200' == sp[2].split(' ')[1]:
                    binary_conversion_factors.append(1./100)
                elif '100' == sp[2].split(' ')[1]:
                    binary_conversion_factors.append(1./200)
                else:
                    binary_conversion_factors.append(1.)
            elif 'DC' == sp[0].split(' ')[1]:
                if sp[3].split(' ')[1] in dcranges:
                    binary_conversion_factors.append(1./dcranges[sp[3].split(' ')[1]])
                else:
                    binary_conversion_factors.append(1.)
            else:
                pass  # OFF

            if dump:
                print(msg)

        self.conv_factors = np.array(binary_conversion_factors)
        return 


    def add_log(self, log:str):
        logfile = pkg_resources.resource_filename('glgl','data') + '/glgl.log'
        with open(logfile, mode='a') as f:
            now = datetime.now()
            f.write(now.strftime("[%Y-%m-%d %H:%M:%S] "))
            f.write(log)
            f.write('\n')
        return


    def show_log():
        logfile = pkg_resources.resource_filename('glgl','data') + '/glgl.log'
        with open(logfile, 'r', encoding='utf-8') as f:
            text = f.read()
        print(text)
        return

    def get_outfilename(self, config, config_hash, date):

        outfilename = ''
        c = 0
        while c < len(config['csv']['naming']):
            if config['csv']['naming'][c:c+4] == 'head':
                outfilename += config['csv']['file_header']
                c += 4
            elif config['csv']['naming'][c:c+4] == 'date':
                outfilename += date
                c += 4
            elif config['csv']['naming'][c:c+4] == 'hash':
                outfilename += config_hash
                c += 4
            elif config['csv']['naming'][c:c+4] == 'host':
                outfilename += socket.gethostname()
                c += 4
            else:
                outfilename += config['csv']['naming'][c]
                c += 1

        outfilename = config['path'] + outfilename
        return outfilename


class PyDevIo:

    def __init__(self, timeout):
        self.timeout = timeout

    #Open tcp
    def opentcp(self, IP, port):
        return True

    #Close port
    def close(self):
        return True

    #Send command
    def send_command(self, strMsg):
        return True
    
    #Receive
    def read_command(self, timeout):
        return ""
    
    #Transmit and receive commands
    def send_read_command(self, strmsg, timeout):
        return ""

    def read_binary(self, readbytes, timeout):
        msgbuf = bytes(range(0)) # Message buffer
        return msgbuf

BUFFSIZE = 8192

class Tcp(PyDevIo):

    # Constractor
    def __init__(self, timeout):
        super().__init__(timeout)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
        self.sock.settimeout(timeout)                                   #Timeout
        self.timeout = timeout

    # Open socket
    def open(self, IP, port):
        ret = False

        try:
            self.sock.connect((IP, port))
            ret = True
        except Exception as e:
            ret = False
        
        return ret

    # Close socket
    def close(self):
        ret = False

        try:
            self.sock.close()
            ret = True
        except Exception as e:
            ret = False
        
        return ret

    # Send command
    def send_command(self, strmsg):
        ret = False

        try:
            strmsg = strmsg + '\r\n'                #Add a terminator, CR+LF, to transmitted command
            self.sock.send(bytes(strmsg, 'utf-8'))  #Convert to byte type and send
            ret = True
        except Exception as e:
            ret = False

        return ret
    
    # Read command
    def read_command(self, timeout=None):
        if timeout == None:
            timeout = self.timeout
        ret = False
        msgbuf = bytes(range(0))                    # Message buffer

        try:
            start = time.time()                     # Record for timeout
            while True:
                rcv  = self.sock.recv(BUFFSIZE)     # Receive data from the device
                rcv = rcv.strip(b"\r")              # Delete CR in received data
                if b"\n" in rcv:                    # End the loop when LF is received
                    rcv = rcv.strip(b"\n")          # Ignore the terminator CR
                    msgbuf = msgbuf + rcv
                    msgbuf = msgbuf.decode('utf-8')
                    break
                else:
                    msgbuf = msgbuf + rcv
                
                #Timeout processing
                if  time.time() - start > timeout:
                    msgbuf = ""
                    break
        except Exception as e:
            ret = False

        return msgbuf
    
    # send and read commands
    def send_read_command(self, strmsg, timeout=None):
        if timeout == None:
            timeout = self.timeout
        ret = self.send_command(strmsg)
        if ret:
            msgbuf_str = self.read_command(timeout)  #Receive response when command transmission is succeeded
        else:
            msgbuf_str = ""

        return msgbuf_str

    # Read binary
    def read_binary(self, readbytes, timeout=None):
        if timeout == None:
            timeout = self.timeout
        ret = False
        msgbuf = bytes(range(0))                # Message buffer

        try:
            rcv  = self.sock.recv(readbytes)    # Receive data from the device
            rcv = rcv.strip(b"\r")              # Delete CR in received data
            msgbuf = msgbuf + rcv
            
        except Exception as e:
            ret = False

        return msgbuf

