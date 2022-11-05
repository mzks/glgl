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

## Usage

`glgl` command is available.
```
glgl -h
usage: glgl [-h] [-c CONFIG] [-g] [-i IP] [-r PORT] [-t SAMPLING_TIME] [-o {default,csv,mysql,both}] [-p PATH] [-d] [-n NAMING]
            [-f FILE_HEADER] [-z DELIMITER] [-b BOOKED] [-s] [-q] [-x EXECUTE] [-v]

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
  -o {default,csv,mysql,both}, --output {default,csv,mysql,both}
                        Output style (file or database)
  -p PATH, --path PATH  File output path
  -d, --dump            Show input channels information
  -n NAMING, --naming NAMING
                        File naming style e.g., date-hash-id.csv etc.
  -f FILE_HEADER, --file_header FILE_HEADER
                        File header
  -z DELIMITER, --delimiter DELIMITER
                        Delimiter for csv output
  -b BOOKED, --booked BOOKED
                        Find configure file booked.
  -s, --stored          Use the previous configuration stored
  -q, --quit            Kill all running glgl
  -x EXECUTE, --execute EXECUTE
                        One-shot execute command (i.e., -x ":AMP:CH1?")
  -v, --version
```


`glgl -g` generate template config `example_config.json` in a current directory.
The parameters are written in the config json file as comments.
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
            // name : channel name used for csv header and sql column name
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
        "3":{
            "name": "ch3",
            "input": "TCK",
            "range": "100"
        },
        "4":{
            "name": "ch4",
            "input": "TCJ",
            "range": "500"
        },
        "5":{
            "name": "ch5",
            "input": "TCR",
            "range": "2000"
        },
        "6":{
            "name": "ch6",
            "input": "TCE",
            "range": "2000"
        },
        "7":{
            "name": "ch7",
            "input": "TCB",
            "range": "2000"
        },
        "8":{
            "name": "ch8",
            "input": "TCS",
            "range": "2000"
        },
        "9":{
            "name": "ch9",
            "input": "TCN",
            "range": "2000"
        },
        "10":{
            "name": "ch10",
            "input": "PT1000",
            "range": "2000"
        },
        "11":{
            "name": "ch11",
            "input": "DC",
            "range": "20MV",
            "filter": 2
        },
        "12":{
            "name": "ch12",
            "input": "DC",
            "range": "20MV"
        },
        "13":{
            "name": "ch13",
            "input": "DC",
            "range": "50MV"
        },
        "14":{
            "name": "ch14",
            "input": "DC",
            "range": "100MV"
        },
        "15":{
            "name": "ch15",
            "input": "DC",
            "range": "200MV"
        },
        "16":{
            "name": "ch16",
            "input": "DC",
            "range": "500MV"
        },
        "17":{
            "name": "ch17",
            "input": "DC",
            "range": "1V"
        },
        "18":{
            "name": "ch18",
            "input": "DC",
            "range": "10V"
        },
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
