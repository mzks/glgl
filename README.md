# glgl

Monitor Graphtec GL840 data logger via ethernet

## Features
 - easy install
 - store data in csv and/or mysql 
 - json configure, overwritable with arguments


## Install
```
python -m pip install git+https://github.com/mzks/glgl.git
```
For pyenv user, `pyenv shims` might be required.

## Usage

`glgl` command is available.
The data logging start with the following command,
```
glgl --ip 192.168.0.1
```
Your GL840 IP address should be used instead of `192.168.0.1`
All channel will be set as DC input and its range 10V as a default.
In this command, csv file and json file will be created at the current direcory like `data-20221105-bs664s.csv` and `bs664s.json`.
The csv naming style is configurable (see later).
The `bs664s` is a deterministic hash generated with all config options.
Files with different configurations are saved with deferent names.
The used config json file is saved in the path and stored.
If you miss the configure file, you can regenerate with the command `glgl -s bs664s`.

If you want to set channel configurations, edit config json file.
`glgl -g` generates example config json file.
Then, run `glgl -c your_config.json`.

The script can kill `glgl -q` command even it run with nohup.

If you want directly to execute command without continues logging, use `-x` option.
This option doesn't touch GL840 configuration, just run the command.

This script corrects the data in each `sampling_time` (seconds) + processing offset.
The `sampling_time` is set in the json config or `-t` option.
The processing offset is usually about 1 second.
The more frequent data collection would be develop for future.

### Command line options
These command line option will overwrite config option.
```
glgl -h
usage: glgl [-h] [-c CONFIG] [-g] [-i IP] [-r PORT] [-t SAMPLING_TIME] [-o OUTPUT] [-p PATH] [-d] [-n NAMING] [-f FILE_HEADER]
            [-z DELIMITER] [-b BOOKED] [-s] [-q] [-x EXECUTE] [-v]

glgl command

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Config json file name
  -g, --generate_config
                        Generate config example
  -i IP, --ip IP        GL840 IP address
  -r PORT, --port PORT  GL840 port
  -t SAMPLING_TIME, --sampling_time SAMPLING_TIME
                        Sampling time interval to collect data (sec.)
  -o OUTPUT, --output OUTPUT
                        Output style (csv or mysql), i.e., -o csv,mysql
  -p PATH, --path PATH  File output path
  -d, --dump            Show input channels information
  -n NAMING, --naming NAMING
                        File naming style e.g., date-hash-id.csv etc.
  -f FILE_HEADER, --file_header FILE_HEADER
                        File header
  -z DELIMITER, --delimiter DELIMITER
                        Delimiter for csv output
  -b BOOKED, --booked hash
                        Find configure file booked.
  -s, --stored          Use the previous configuration stored
  -l, --log             List the hashes of the previous runs
  -q, --quit            Kill all running glgl
  -x EXECUTE, --execute EXECUTE
                        One-shot execute command (i.e., -x ":AMP:CH1?")
  -v, --version
```

### Config json file

`glgl -g` generate template config `example_config.json` in a current directory.
The parameters are written in the config json (commentable with //) file.
```
// default_config.json
// glgl
{
    // Connection settings
    "ip": "10.241.47.98",
    "port": 8023,
    "timeout": 1, // sec.
    "sampling_time": 0.2, // time interval to take data (sec.)
    "dump_input": false, // show channel settings
    "output": ["csv", "mysql"], // Output format
    "path": "./", // path to save your text data and configurations

    //// Configurations for formats to save file
    "csv": {
        // File naming style. available keywords: head, date, hash, id, host
        "naming": "head-date-hash.csv",
        // File header. It will be used when you include "head" in your "naming"
        "file_header": "data",
        // Time column format (datetime, timestamp or strftime format (for example, "%H:%M:%S")
        "time_format" : "datetime",
        // Delimiter // default ',' generates CSV format
        "delimiter": ",",
        // Additional string is put on the header
        "commentout_string": ""
    },

    //// Mysql Database configuration
    // 'login' configurations are used in arguments of pymysql.connect()
    "mysql":{
        "login":{
            "host": "127.0.0.1",
            "port": 3306,
            "user": "root",
            "passwd": "password",
            "autocommit": true},
            "name": "glgl", // database name
            "table_name": "data"
    },

    //// configurations for each channels
    "channels":{
        "default":{ // if "n" is not defined, this setting will be used.
            "input": "DC",
            "range": "10V"
        },
        "1":{ // CH1
            // name : channel name used for csv header
            "name": "ch1",
            "input": "TCT", // TC-T thermocouple input
            // available: [TCK, TCJ, TCT, TCR, TCE, TCB, TCS, TCN, TCW, PT100, JPT100, PT1000]
            "range": "2000", // temperature range, available: [100, 500, 2000]
            "filter": 10 // filter, "off" or integer 2, 5, 10, 20, 40
        },
        "2":{ // CH2
            "name": "ch2",
            "input": "DC", // DC voltage input
            "range": "5V", // DC input range
            // available: 20/50/100/200/500(MV) /1/2/5/10/20/(V)/ 1-5(V)
            "filter": "off"
        },

        // ... 

        "19":{
            "name": "ch19",
            "input": "DC",
            "range": "1-5V"
        }
        // "20" is not defined here, then "default setting will be used for CH20
    }
}
```
Then, `glgl -c your_config_file.json`

### CSV file format
The `config['channels']["1"]["name"]` in the configure json is used as the column name of channel 1.
```
time,ch1,ch2,ch3,ch4,ch5,ch6,ch7,ch8,ch9,ch10,ch11,ch12,ch13,ch14,ch15,ch16,ch17,ch18,ch19,ch20
2022-11-05 22:35:19.812601,0.114000,0.162000,16.382000,16.382500,16.382500,16.382500,16.382500,16.382500,16.382500,16.382000,1.162500,0.063000,0.019500,0.009000,0.004000,0.001500,0.000500,0.000000,-0.001000,-0.001000
2022-11-05 22:35:21.029717,0.114000,0.162000,16.382000,16.382500,16.382500,16.382500,16.382500,16.382500,16.382500,16.382000,1.162500,0.063000,0.019500,0.009000,0.004000,0.001500,0.000500,0.000000,-0.001000,-0.001000
2022-11-05 22:35:22.248694,0.114000,0.162000,16.382000,16.382500,16.382500,16.382500,16.382500,16.382500,16.382500,16.382000,1.162500,0.063000,0.019500,0.009000,0.004000,0.001500,0.000500,0.000000,-0.001000,-0.001000
```
If you want to read with pandas, use `df = pd.read_csv('yourfile.csv', parse_dates=[0])`.

### mysql format
In the config,
```
    "mysql":{
        "login":{
            "host": "127.0.0.1",
            "port": 3306,
            "user": "root",
            "passwd": "password",
            "autocommit": true},
            "name": "glgl", // database name
            "table_name": "data"
    }
```
,the `"name"` and `"table_name"` are used as database name and table name.
If the `table_name` is `"hash"`, the config deterministic hash will be used for the table name.

