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


`glgl -g` generate template config `custom_config.json` in a current directory.
The parameters are written in the config json file as comments.

