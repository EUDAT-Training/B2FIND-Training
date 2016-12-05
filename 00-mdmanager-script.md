# The *mdmanager.py* script
This document describes the usage of the python script `mdmanager.py`,
which is used in all training modules belonging to the 'ingestion of metadata', i.e. from [01] to [04].

## Environment
Ubuntu 14.04 server

## Prerequisites

### 1. Python
To run the script you need Python 2.7 or later.

### 2. The source code
The python script [mdmanager.py](mdmanager.py) comes with this training material.

Additionally the script requires several modules listed in the file `requirements.txt`, which need to be installed first by

```sh
pip install -r requirments.txt
```
 > Note: If you use different python compilers you need to make sure that pip is linked to the one you would like to use. If not linked correctly you will receive an error:
 ```sh
 Requirement already satisfied (use --upgrade to upgrade): dublincore in /home/xxx/anaconda2/lib/python2.7/site-packages
```
> you have to add this path to your Python path by
```sh
 export PYTHONPATH=$PYTHONPATH:/home/xxx/anaconda2/lib/python2.7/site-packages/
```

## Usage
To get an overview about the functionality of the script enter
```sh
$ ./mdmanager.py -h
Usage
=====
  mdmanager.py [options]
....
```

In the following subsections we discuss the usage of the options and modes in more detail.

### Processing modes and general option
The script *mdmanager.py* can be executed in different modes by using the option `-m | --mode`,
and provides procedures for the whole ingestion workflow how to come from unstructured metadata to entries in the discovery portal (own CKAN or B2FIND instance).

Please refer to the table below for all possible modes, their meaning and the related training module :

Mode | Explanation | Associated training module |
------|-------------------|---------------------|
g | Generation of formated XML records from raw metadata sets | [01 MD Generation ](01.b-generate-metadata.md) |
h | Harvesting of XML files from a data provider endpoint | [02.b MD Harvester ](02.b-OAI-harvester.md) |
m | Mapping of specially formated XML to a target JSON schema | [03.a MD Mapping ](03.a-map-metadata.md) |
v | Validation of mapped JSON records as compatible with target schema | [03.b MD Validation ](03.b-validate-metadata.md) | 
u | Uploading of JSON records to B2FIND or another CKAN instance |  [04.b MD Uploader ](04.b-upload-metadata.md) |

Beside this processing mode option there are other 'global' options as shown in the top part of the help output:

```sh
Options
=======
--help, -h              show this help message and exit
--verbose, -v           increase output verbosity (e.g., -vv is more than -v)
--mode=PROCESSINGMODE, -m PROCESSINGMODE
                        This specifies the processing mode. Supported modes
                        are (g)enerating, (h)arvesting, (m)apping,
                        (v)alidating, and (u)ploading.
--community=STRING, -c STRING
                        community or project where metadata are originated.
...
```

We want to emphasize here the cross-process option `community` specifying the community or the project which 'owns' the metadata.
This is related to the *use cases* through which we guide you through the tutorial. 

### Single and multiple source requests

#### Multiple Sources

```sh
Request for Multiple Sources
----------------------------
This is the default operation mode and performs ingestion from a list of
sources.

--list=FILE, -l FILE    list of requests to several sources (default is
                        ./harvest_list)
```

#### Single Source
```sh
Request for a Single Source
---------------------------
Use the options '-s | --source SOURCE if you want to ingest from only ONE
source.

--source=STRING, -s STRING
                        Source of metadata to be processed. In generation mode
                        this is the path to the raw metadata and in harvesting
                        mode this is the URL endpoint from which records are
                        harvested from (e.g. the OAI-URL)
```

In this case the other options, which depend on the excecuted processing mode and are explained below, must be as well explicitly specified.

### Processing mode specific options

#### Generation and Harvesting mode

```sh
Generate and Harvest Options
----------------------------
These options are required to generate or harvest metadata from the specified
sources.

--verb=STRING           Specifiers of the procesing request. In generation
                        mode this is the delimiter of the source (e.g.
                        'comma'(default) or 'tab' and in harvesting mode this
                        is a 'verb' supported by OAI-PMH ( e.g. ListRecords
                        (default) or ListIdentifers)
--mdsubset=STRING       Subset of the processed data meta data (for OAI-PMH
                        harvesting the OAI subset, if availbale)
--mdprefix=STRING       Meta data schema of the source (for OAI-PMH harvesting
                        the OAI metadata prefix
--fromdate=DATE         filter metadata to be processed by date (Format: YYYY-
                        MM-DD).
--target_mdschema=STRING
                        (Optional) Meta data schema of the target
```

#### Upload mode

```sh
Upload Options
--------------
These options will be required to upload an dataset to a CKAN database.

--iphost=IP, -i IP      IP adress of B2FIND portal (CKAN instance)
--auth=STRING           Authentification for CKAN APIs (API key, by default
                        taken from file $HOME/.netrc)
--handle_check=CREDENTIALFILE
                        check and generate handles corresponding to the
                        settings in the CREDENDIALFILE
--ckan_check=BOOLEAN    check existence and checksum of records in CKAN
                        database during upload
```

### Information and support

```sh
For any further information and documentation please look at the README.md
file or send an email to widmann@dkrz.de.
```
