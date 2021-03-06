# The *mdmanager.py* script
This document describes the usage of the python script `mdmanager.py`,
which is used in all training modules belonging to the 'ingestion of metadata', i.e. from [01.b Generate metadata](01.b-generate-metadata.md) to [04.b Upload metadata](04.b-upload-metadata.md).

## Environment
Ubuntu 14.04 server with the following system packages:

```sh
sudo apt-get install git
sudo apt-get install python-setuptools python-dev build-essential
sudo apt-get install enchant
sudo easy_install pip
```

## Prerequisites

### 1. Python
To run the script you need Python 2.7.

### 2. The source code
The python script [mdmanager.py](mdmanager.py) comes with the training material.Please download the repository and change in the working directory ```B2FIND-Training``` :
```sh
git clone https://github.com/EUDAT-Training/B2FIND-Training.git
cd B2FIND-Training
```

The script requires several modules listed in the file `requirements.txt`, which need to be installed first by

```sh
pip install -r requirements.txt
```
Maybe you need sudo rights to install all needed packages.

Check with
```sh
pip freeze 
```
whether all packages have been installed correctly.

 > Note: If you use different python compilers you need to make sure that pip is linked to the one you would like to use. If not linked correctly you will receive errors as:
 ```sh
 Requirement already satisfied (use --upgrade to upgrade): dublincore in /home/xxx/anaconda2/lib/python2.7/site-packages
```
> In this case you have to add this path to your Python path by
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

Description
===========
Management of metadata, comprising
- Generation of formated XML records from raw metadata sets
- Harvesting of XML files from a data provider endpoint
- Mapping of specially formated XML to a target JSON schema
- Validation of mapped JSON records as compatible with target schema
- Uploading of JSON records to B2FIND or another CKAN instance
....
```
In the following subsections we discuss the usage of the several options in more detail.

### General options
The 'global' options are listed after the ```Description``` directly under ```Options``` :

```sh
Options
=======
--help, -h              show this help message and exit
--verbose, -v           increase output verbosity (e.g., -vv is more than -v)
--outdir=PATH, -d PATH  The relative root directory in which all harvested and
                        processed files will be saved. The converting and the
                        uploading processes work with the files from this dir.
                        (default is 'oaidata')
--community=STRING, -c STRING
                        community or project, for which metadata are
                        harvested, processed, stored and uploaded. This
                        'label' is used through the whole metadata life cycle.
--mdsubset=STRING       Subset of metadata to be harvested (by default 'None')
                        and subdirectory of harvested and processed metadata
                        (by default 'SET_1'
--mdprefix=STRING       Metadata schema of harvested meta data (default is the
                        OAI mdprefix 'oai_dc')
```

We want to emphasize here the cross-process option *community* specifying the community or the project which 'owns' the metadata. This parameter is employed by all modes of the script and used to tie the different steps of preparing and uploading metadata together, which are executed by running the script in its different [processing modes](#processingModes).
In this repository we will take you through all these steps along *use cases*, whereby the name of the treated use case will be employed as the parameter *community*.

The options *mdsubset* and *mdprefix* influence especially the harvesting and mapping procedures. So they determine not only the OAI parameters *set* and *mdprefix*, but as well the path where harvested files are stored and where the mapping and upload process expect the files to be processed. 

### Operation modes for single and multiple sources

In the following sections the sample use cases will employ both of these operation modes and we will hint at how to set parameters and how they influence the behaviour.

#### Single Source

```sh
Single Source Operation Mode
----------------------------
Use the source option if you want to ingest from only ONE source.

--source=URL or PATH, -s URL or PATH
                        In 'generation mode' a PATH to raw metadata given as
                        spreadsheets or in 'harvest mode' an URL to a data
                        provider you want to harvest metadata records from.
```

#### Multiple Sources

```sh
Multiple Sources Operation Mode
-------------------------------
Use the list option if you want to ingest from multiple sources via the
requests specified in the list file.

--list=FILE, -l FILE    list of harvest sources and requests (default is
                        ./harvest_list)
```

**Excercise** Inspect the file *harvest_list* for the general formatting of such a file.

### <a name="processingModes">Processing modes</a>
Depending on the processing step you want to perform, the script *mdmanager.py* can be executed in different modes by using the option `-m | --mode`,
and provides procedures for the whole ingestion workflow how to come from unstructured metadata to entries in the discovery portal (own CKAN or B2FIND instance).

Please refer to the table below for all possible modes, their meaning and the related training module :

Mode | Explanation | Associated training module |
------|-------------------|---------------------|
g | Generation of formated XML records from raw metadata sets | [01 MD Generation ](01.b-generate-metadata.md) |
h | Harvesting of XML files from a data provider endpoint | [02.b MD Harvester ](02.b-OAI-harvester.md) |
m | Mapping of specially formated XML to a target JSON schema | [03.a MD Mapping ](03.a-map-metadata.md) |
v | Validation of mapped JSON records as compatible with target schema | [03.b MD Validation ](03.b-validate-metadata.md) | 
u | Uploading of JSON records to B2FIND or another CKAN instance |  [04.b MD Uploader ](04.b-upload-metadata.md) |

#### <a name="modeGeneration"> Generation mode </a>
This means using mode option `--mode g` and is linked to the module [ 01.b Generate metadata](01.b-generate-metadata.md)
```sh
------------------
These options will be required to generate formatted metadata sets (by default
DublinCore XML files) from 'raw' spreadsheet data that resides in the PATH
given by SOURCE.

--delimiter=STRING      Delimiter, which seperates the fields and associated
                        values in the datasets (lines) of the spreadsheets,
                        can be 'comma' (default) or 'tab'
```

#### Harvesting mode
This means using mode option `--mode h` and is linked to the module [02.b Configure your harvester](02.b-configure-OAI-harvester.md)
```sh
Harvest Options
---------------
These options will be required to harvest metadata records from a data
provider (by default via OAI-PMH from the URL given by SOURCE).

--verb=STRING           Verbs or requests defined in OAI-PMH, can be
                        ListRecords (default) or ListIdentifers
--fromdate=DATE         Filter harvested files by date (Format: YYYY-MM-DD).
```

#### Mapping mode
This means using mode option `--mode m` and is linked to the module [ 03.a Map metadata](03.a-map-metadata.md)
```sh
Mapping Options
---------------
These options will be required to map metadata records formatted in a
supported metadata format to JSON records formatted in a common target schema.
(by default XML records are mapped onto the B2FIND schema, compatable to be
uploaded to a CKAN repository.

--subset=STRING         Subdirectory of meta data records to be mapped. By
                        default this is the same as the the term given by
                        option '--mdsubset'.
--mdschema=STRING       Metadata format and schema of harvested meta data
                        records to be mapped. By default this is the same as
                        the term given by option '--mdprefix'.
```

#### Upload mode
This means using mode option `--mode u` and is linked to the module [04.b Upload metadata](04.b-upload-metadata.md)

```sh
Upload Options
--------------
These options will be required to upload an dataset to a CKAN database.

--iphost=IP, -i IP      IP adress of B2FIND portal (CKAN instance)
--auth=STRING           Authentification for CKAN APIs (API key, by default
                        taken from file $HOME/.netrc)
```

### Information and support

For any further information and documentation please look at the [README.md](README.md) file or send an email to *widmann@dkrz.de*.
