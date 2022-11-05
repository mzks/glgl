#! /usr/bin/env python

import os
import sys
import signal
import argparse
import json
import re
import numpy as np
import shutil
import pkg_resources
from glgl.gl import gl


def sig_handler(signum, frame) -> None:
    sys.exit(1)

def main():

    parser = argparse.ArgumentParser(description='glgl command')
    parser.add_argument('-c', '--config', default='default_config', help='Config json file name')
    parser.add_argument('-g', '--generate_config', action='store_true', help='Generate config example')
    parser.add_argument('-i', '--ip', default=None, help='GL840 IP address')
    parser.add_argument('-r', '--port', default=8023, type=int, help='GL840 port')
    parser.add_argument('-t', '--sampling_time', default=-1., help='Sampling time interval to collect data (sec.)', type=float)
    parser.add_argument('-o', '--output', default='default', choices=['default', 'csv', 'mysql', 'both'],
                        help='Output style (file or database)')
    parser.add_argument('-p', '--path', default='default', help='File output path')
    parser.add_argument('-d', '--dump', action='store_true', help='Show input channels information')
    parser.add_argument('-n', '--naming', default='default',
                        help='File naming style e.g., date-hash-id.csv etc.')
    parser.add_argument('-f', '--file_header', default='default', help='File header')
    parser.add_argument('-z', '--delimiter', default='default', help='Delimiter for csv output')
    parser.add_argument('-b', '--booked', default=None, help='Find configure file booked.')
    parser.add_argument('-s', '--stored', action='store_true', help='Use the previous configuration stored')
    parser.add_argument('-q', '--quit', action='store_true', help='Kill all running glgl')
    parser.add_argument('-x', '--execute', default=None, help='One-shot execute command (i.e., -x ":AMP:CH1?")')
    parser.add_argument('-v', '--version', action='store_true')

    args = parser.parse_args()
    version = '0.1.0'
    if args.version:
        print('glgl version : ' + version)
        return

    if args.quit:
        import psutil
        pids = psutil.pids()
        self_pid = os.getpid()
        for pid in pids:
            if pid == self_pid:
                continue
            try:
                p = psutil.Process(pid)
                cmd = ''.join(p.cmdline())
                if (cmd.find('glgl') != -1) & (cmd.find('glgl-q') == -1):
                    p.kill()
                    add_log('Killed PID: ' + str(pid))
            except:
                pass
        return
        if args.log:
            gl.show_log()
        return

    if args.booked != None:
        config_filename = pkg_resources.resource_filename('glgl', 'data') + '/' + args.booked + '.json'
        if os.path.exists(config_filename):
            shutil.copyfile(config_filename, './'+args.booked+'.json')
        else:
            print(args.booked + '.json does not exist. Nothing to do.')
        return

    if args.generate_config:
        config_filename = pkg_resources.resource_filename('glgl', 'data') + '/default_config.json'
        if os.path.exists('./custom_config.json'):
            print('custom_config.json exists in this directory. Nothing to do.')
            return
        shutil.copyfile(config_filename, './custom_config.json')
        return

    if args.config == 'default_config':
        config_filename = pkg_resources.resource_filename('glgl', 'data') + '/default_config.json'
    else:
        config_filename = pkg_resources.resource_filename('glgl', 'data') + '/' + args.config
        if os.path.exists(config_filename):
            pass
        else:
            config_filename = args.config

    if args.stored:
        config_filename = pkg_resources.resource_filename('glgl', 'data') + '/.previous_config.json'
        if os.path.exists(config_filename):
            pass
        else:
            config_filename = pkg_resources.resource_filename('glgl', 'data') + '/default_config.json'

    print('Use config ' + config_filename)

    config = read_jsonc(config_filename)

    if args.ip != None:
        config['ip'] = args.ip
    if args.port != None:
        config['port'] = args.port
    if args.sampling_time > 0.:
        config['sampling_time'] = args.sampling_time
    if args.path != 'default':
        config['path'] = args.path
    if config['path'][-1] != '/':
        config['path'] = config['path'] + '/'
    if args.dump == True:
        config['dump_input'] = True


    if args.output != 'default':
        config['output'] = args.output

    if args.file_header != 'default':
        config['csv']['file_header'] = args.file_header
    if args.naming != 'default':
        config['csv']['naming'] = args.naming
    if args.delimiter == 'space':
        config['csv']['delimiter'] = ' '
    elif args.delimiter != 'default':
        config['csv']['delimiter'] = args.delimiter

    filename = pkg_resources.resource_filename('glgl', 'data') + '/.previous_config.json'
    config_json = open(filename, "w")
    json.dump(config, config_json, indent=4)
    config_json.close()

    g = gl(config)

    if args.execute:
        g.oneshot_command(args.execute)
        return


    signal.signal(signal.SIGTERM, sig_handler)
    try:
        g.loop()
    finally:
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        del g
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        
    return


def read_jsonc(filepath: str):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    re_text = re.sub(r'/\*[\s\S]*?\*/|//.*', '', text)
    json_obj = json.loads(re_text)
    return json_obj


if __name__ == '__main__':
    main()
