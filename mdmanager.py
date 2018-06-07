#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

"""mdmanager.py
  Management of metadata 

Copyright (c) 2016 Heinrich Widmann (DKRZ) Licensed under AGPLv3.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import os, optparse, sys, glob
import time, datetime
import simplejson as json

import logging
logger = logging.getLogger()
import traceback

# 
PY2 = sys.version_info[0] == 2
if PY2:
    from urllib import quote
    from urllib2 import urlopen, Request
    from urllib2 import HTTPError,URLError
else:
    from urllib import parse
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError,URLError


import socket
from itertools import tee 

##import classes from B2FIND modules
from generating import Generator
from harvesting import Harvester
from mapping import Mapper

# needed for Harvester class:
import sickle as SickleClass
from sickle.oaiexceptions import NoRecordsMatch
from requests.exceptions import ConnectionError
import lxml.etree as etree
import uuid, hashlib

# needed for MAPPER :
from pyparsing import *
import Levenshtein as lvs
import iso639
import codecs
import re
import xml.etree.ElementTree as ET
import io

# needed for UPLOADER class:
from collections import OrderedDict

def setup_custom_logger(name,verbose):
    log_format='%(levelname)s :  %(message)s'
    log_level=logging.CRITICAL
    if verbose == 1 :
        log_format='%(levelname)s in  %(module)s\t%(funcName)s\t%(lineno)s : %(message)s'
        log_level=logging.ERROR
    elif  verbose == 2 :
        log_format='%(levelname)s in %(module)s\t%(funcName)s\t%(lineno)s : %(message)s'
        log_level=logging.WARNING
    elif verbose == 3 :
        log_format='%(levelname)s at %(asctime)s in L %(lineno)s : %(message)s'
        log_level=logging.INFO
    elif verbose > 3 :
        log_format='%(levelname)s at %(asctime)s %(msecs)d in L %(lineno)s : %(message)s'
        log_level=logging.DEBUG


    formatter = logging.Formatter(fmt=log_format)

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger.setLevel(log_level)
    logger.addHandler(handler)
    return logger


class CKAN_CLIENT(object):

    """
    ### CKAN_CLIENT - class
    # Provides methods to call a CKAN API request via urllib2
    #
    # Parameters:
    # -----------
    # (URL)     iphost  - URL to CKAN database
    # (string)  auth    - Authentication key for API requests
    #
    # Return Values:
    # --------------
    # 1. CKAN_CLIENT object
    #
    # Public Methods:
    # ---------------
    # .action (action, jsondata) - call the api <action>
    #
    # Usage:
    # ------

    # create CKAN object                       
    CKAN = CKAN_CLIENT(iphost,auth)

    # call action api:
    CKAN.action('package_create',{"name":"testdata", "title":"empty test object"})
    """

    def __init__ (self, ip_host, api_key):
            self.ip_host = ip_host
            self.api_key = api_key
            self.logger = logging.getLogger()
        
    def validate_actionname(self,action):
        return True
        
        
    def action(self, action, data={}):
        ## action (action, jsondata) - method
            # Call the api action <action> with the <jsondata> on the CKAN instance which was defined by iphost
            # parameter of CKAN_CLIENT.
            #
            # Parameters:
            # -----------
            # (string)  action  - Action name of the API v3 of CKAN
            # (dict)    data    - Dictionary with json data
            #
            # Return Values:
            # --------------
            # (dict)    response dictionary of CKAN
            
            if (not self.validate_actionname(action)):
                    print('[ERROR] Action name '+ str(action) +' is not defined in CKAN_CLIENT!')
            else:
                    return self.__action_api(action, data)
                
    def __action_api (self, action, data_dict):
        # Make the HTTP request for data set generation.
        response=''
        rvalue = 0
        api_url = "http://{host}/api/rest".format(host=self.ip_host)
        action_url = "{apiurl}/dataset".format(apiurl=api_url)	# default for 'package_create'

        # "package_delete_all", "package_activate_all" and "member_create" are special actions
        # which are not supported by APIv3 of CKAN
        # special cases:
        if (action == "package_activate_all"):
            if data_dict['group']:
                    data = self.action('member_list',{"id" : data_dict['group'], "object_type":"package"})
            else:
                    data = self.action('package_list',{})

            print('Total number of datasets: ' + str(len(data['result'])))
            for dataset in data['result']:
                    logging.info('\tTry to activate object: ' + str(dataset))
                    self.action('package_update',{"name" : dataset[0], "state":"active"})

            return True
        elif (action == "package_delete_all"):
            if (data_dict['group']):
                data = self.action('member_list',{"id" : data_dict['group'], "object_type":"package"})
            elif (data_dict['list']):
                data['result'] = data_dict['list']
            else:
                data = self.action('package_list',{})
            pcount = 0
            print('Total number of datasets: ' + str(len(data['result'])))
            #self.action('bulk_update_delete',{"datasets" : data['result'], "id":"enes"})
            for dataset in data['result']:
                pcount += 1
                print('\tTry to delete object (' + str(pcount) + ' of ' + str(len(data['result'])) + '): ' + str(dataset))
                print('\t', (self.action('package_update',{"name" : dataset[0], "state":"delete"}))['success'])

            return True
        elif (action == "member_create" or action == "organization_member_create"):
            api_url = "http://{host}/api/action".format(host=self.ip_host)
            action_url = "{apiurl}/{action}".format(apiurl=api_url,action=action)

            ds_id = data_dict['id']

            if (data_dict['id'] == None):
                            ds_id = (self.action('package_show',{"id" : data_dict['name']}))['id']

            member_dict = {
                    "id": data_dict['group'],
                    "object": ds_id,
                    "object_type": "package", 
                    "capacity" : "public"
            }

            data_dict	= member_dict
        # normal case:
        else:
            action_url = "http://{host}/api/3/action/{action}".format(host=self.ip_host,action=action)

        # make json data in conformity with URL standards
        try:
            if PY2 :
                data_string = quote(json.dumps(data_dict))##.encode("utf-8") ## HEW-D 160810 , encoding="latin-1" ))##HEW-D .decode(encoding)
            else :
                data_string = parse.quote(json.dumps(data_dict)).encode(encoding) ## HEW-D 160810 , encoding="latin-1" ))##HEW-D .decode(encoding)
        except Exception as err :
            logging.critical('%s while building url data' % err)

        ###HEW-D data_string = unicode(urllib.quote(json.dumps(data_dict)), errors='replace')

        logging.debug('\t|-- Action %s\n\t|-- Calling %s\n\t|-- Data %s ' % (action,action_url,data_dict))	
        ##HEW-Tlogging.debug('\t|-- Object %s ' % data_dict)	
        try:
            request = Request(action_url,data_string)
            self.logger.debug('request %s' % request)            
            if (self.api_key): request.add_header('Authorization', self.api_key)
            self.logger.debug('api_key %s....' % self.api_key)
            if PY2 :
                response = urlopen(request)
            else :
                response = urlopen(request)                
            self.logger.debug('response %s' % response)            
        except HTTPError as e:
            self.logger.error('%s : The server %s couldn\'t fulfill the action %s.' % (e,self.ip_host,action))
            if ( e.code == 403 ):
                logging.error('Access forbidden, maybe the API key is not valid?')
                ## exit(e.code)
            elif ( e.code == 409 and action == 'package_create'):
                self.logger.info('\tMaybe the dataset already exists => try to update the package')
                self.action('package_update',data_dict)
            elif ( e.code == 409):
                self.logger.debug('\tMaybe you have a parameter error?')
                return {"success" : False}
            elif ( e.code == 500):
                self.logger.critical('\tInternal server error')
                return {"success" : False}
        except URLError as e:
            self.logger.critical('\tURLError %s : %s' % (e,e.reason))
            return {"success" : False}
        except Exception as e:
            self.logger.critical('\t%s' % e)
            return {"success" : False}
        else :
            out = json.loads(response.read())
            self.logger.debug('out %s' % out)
            assert response.code >= 200
            return out

##HEW-D        try:
##HEW-D            request = urllib2.Request(action_url)
##HEW-D            if (self.api_key): request.add_header('Authorization', self.api_key)
##HEW-D            response = urllib2.urlopen(request,data_string)
##HEW-D        except HTTPError as e:
##HEW-D            logging.debug('\tHTTPError %s : The server %s couldn\'t fulfill the action %s.' % (e.code,self.ip_host,action))
##HEW-D            if ( e.code == 403 ):
##HEW-D                logging.error('\tAccess forbidden, maybe the API key is not valid?')
##HEW-D                exit(e.code)
##HEW-D            elif ( e.code == 409 and action == 'package_create'):
##HEW-D                logging.debug('\tMaybe the dataset already exists => try to update the package')
##HEW-D                self.action('package_update',data_dict)
##HEW-D                ##HEW-D return {"success" : False}
##HEW-D            elif ( e.code == 409):
##HEW-D                logging.debug('\tMaybe you have a parameter error?')
##HEW-D                return {"success" : False}
##HEW-D            elif ( e.code == 500):
##HEW-D                logging.error('\tInternal server error')
##HEW-D                exit(e.code)
##HEW-D        except URLError as e:
##HEW-D            logging.error('\tURLError %s : %s' % (e,e.reason))
##HEW-D            exit('%s' % e.reason)
##HEW-D        else :
##HEW-D            out = json.loads(response.read())
##HEW-D            assert response.code >= 200
##HEW-D            return out

class UPLOADER (object):

    """
    ### UPLOADER - class
    # Uploads JSON files to CKAN portal and provides more methods for checking a dataset
    #
    # Parameters:
    # -----------
    # 1. (CKAN_CLIENT object)   CKAN - object of the CKAN_CLIENT class
    #
    # Return Values:
    # --------------
    # 1. UPLOADER object
    #
    # Public Methods:
    # ---------------
    # .check_dataset(dsname,checksum)   - Compare the checksum of the dataset <dsname> with <checksum> 
    # .check_url(url)           - Checks and validates a url via urllib module
    # .delete(dsname,dsstatus)  - Deletes a dataset from a CKAN portal
    # .get_packages(community)  - Gets the details of all packages from a community in CKAN and store those in <UPLOADER.package_list>
    # .upload(dsname, dsstatus,
    #   community, jsondata)    - Uploads a dataset to a CKAN portal
    # .check(jsondata)       - Validates the fields in the <jsondata> by using B2FIND standard
    #
    # Usage:
    # ------

    # create UPLOADER object:
    UP = UPLOADER(CKAN,OUT)

    # VALIDATE JSON DATA
    if (not UP.check(jsondata)):
        print "Dataset is broken or does not pass the B2FIND standard"

    # CHECK DATASET IN CKAN
    ckanstatus = UP.check_dataset(dsname,checksum)

    # UPLOAD DATASET TO CKAN
    upload = UP.upload(dsname,ckanstatus,community,jsondata)
    if (upload == 1):
        print('Creation of record succeed')
    elif (upload == 2):
        print('Update of record succeed')
    else:
        print('Upload of record failed')
    """
    
    def __init__(self, CKAN):
        self.logger = logging.getLogger()
        self.CKAN = CKAN
        
        self.package_list = dict()
        # B2FIND metadata fields
        self.b2findfields = list()
        self.b2findfields = [
                   "title","notes","tags","url","DOI","PID","Checksum","Rights","Discipline","author","Publisher","PublicationYear","PublicationTimestamp","Language","TemporalCoverage","SpatialCoverage","spatial","Format","Contact","MetadataAccess","oai_set","oai_identifier","fulltext"]
        self.ckandeffields = ["author","title","notes","tags","url"]

    def json2ckan(self, jsondata):
        ## json2ckan(UPLOADER object, json data) - method
        ##  converts flat JSON structure to CKAN JSON record with extra fields
        logging.debug('    | Adapt default fields for upload to CKAN')
        for key in self.ckandeffields :
            if key not in jsondata:
                logging.debug('[WARNING] : CKAN default key %s does not exist' % key)
            else:
                logging.debug('    | -- %-25s ' % key)
                if key in  ["author"] :
                    jsondata[key]=';'.join(list(jsondata[key]))
                elif key in ["title","notes"] :
                    jsondata[key]='\n'.join(list(jsondata[key]))##.encode("iso-8859-1") ### !!! encode to display e.g. 'Umlauts' corectly

        jsondata['extras']=list()
        logging.debug('    | Adapt extra fields for upload to CKAN')
        for key in set(self.b2findfields) - set(self.ckandeffields) :
            if key in jsondata :
                logging.debug('    | -- %-25s ' % key)
                if key in ['Contact','Format','Language','Publisher','PublicationYear','Checksum']:
                    value=';'.join(jsondata[key])
                elif key in ['oai_set','oai_identifier']: ### ,'fulltext']
                    if isinstance(jsondata[key],list) or isinstance(jsondata[key],set) : 
                        value=jsondata[key][-1]      
                else:
                    value=jsondata[key]
                jsondata['extras'].append({
                     "key" : key,
                     "value" : value
                })
                del jsondata[key]
            else:
                logging.debug('[WARNING] : No data for key %s ' % key)

        return jsondata

    def check(self, jsondata):
        ## check(UPLOADER object, json data) - method
        # Checks the jsondata and returns the correct ones
        #
        # Parameters:
        # -----------
        # 1. (dict)    jsondata - json dictionary with metadata fields with B2FIND standard
        #
        # Return Values:
        # --------------
        # 1. (dict)   
        # Raise errors:
        # -------------
        #               0 - critical error occured
        #               1 - non-critical error occured
        #               2 - no error occured    
    
        errmsg = ''
        
        ## check mandatory fields ...
        mandFields=['title','url','oai_identifier']
        for field in mandFields :
            if field not in jsondata: ##  or jsondata[field] == ''):
                raise Exception("The mandatory field '%s' is missing" % field)
        ##HEW-D elif ('url' in jsondata and not self.check_url(jsondata['url'])):
        ##HEW-D     errmsg = "'url': The source url is broken"
        ##HEW-D     if(status > 1): status = 1  # set status
            
        # ... OAI Set
        if('oai_set' in jsondata and ';' in  jsondata['oai_set']):
            jsondata['oai_set'] = jsondata['oai_set'].split(';')[-1] 
            
        # shrink field fulltext
        if('fulltext' in jsondata):
            ##raise Exception("'fulltext': Too big ( %d bytes, %d len)" % (sys.getsizeof(jsondata['fulltext']),len(jsondata['fulltext'])))
            encoding='utf-8'
            encoded = u' '.join([x.strip() for x in jsondata['fulltext'] if x is not None]).encode(encoding)[:32000]
            encoded=re.sub('\s+',' ',encoded)
            jsondata['fulltext']=encoded.decode(encoding, 'ignore')

        if 'PublicationYear' in jsondata :
            try:
                datetime.datetime.strptime(jsondata['PublicationYear'][0], '%Y')
            except (ValueError,TypeError) as e:
                raise Exception("Error %s : Key %s value %s has incorrect data format, should be YYYY" % (e,'PublicationYear',jsondata['PublicationYear']))
                # delete this field from the jsondata:
                del jsondata['PublicationYear']
                
        # check Date-Times for consistency with UTC format
        dt_keys=['PublicationTimestamp', 'TemporalCoverage:BeginDate', 'TemporalCoverage:EndDate']
        for key in dt_keys:
            if key in jsondata :
                try:
                    datetime.datetime.strptime(jsondata[key], '%Y-%m-%d'+'T'+'%H:%M:%S'+'Z')
                except ValueError:
                    raise Exception("Value %s of key %s has incorrect data format, should be YYYY-MM-DDThh:mm:ssZ" % (jsondata[key],key))
                    del jsondata[key] # delete this field from the jsondata

        return jsondata

    def upload(self, ds, dsstatus, community, jsondata):
        ## upload (UPLOADER object, dsname, dsstatus, community, jsondata) - method
        # Uploads a dataset <jsondata> with name <dsname> as a member of <community> to CKAN. 
        #   <dsstatus> describes the state of the package and is 'new', 'changed', 'unchanged' or 'unknown'.         #   In the case of a 'new' or 'unknown' package this method will call the API 'package_create' 
        #   and in the case of a 'changed' package the API 'package_update'. 
        #   Nothing happens if the state is 'unchanged'
        #
        # Parameters:
        # -----------
        # 1. (string)   dsname - Name of the dataset
        # 2. (string)   dsstatus - Status of the dataset: can be 'new', 'changed', 'unchanged' or 'unknown'.
        #                           See also .check_dataset()
        # 3. (string)   dsname - A B2FIND community in CKAN
        # 4. (dict)     jsondata - Metadata fields of the dataset in JSON format
        #
        # Return Values:
        # --------------
        # 1. (integer)  upload result:
        #               0 - critical error occured
        #               1 - no error occured, uploaded with 'package_create'
        #               2 - no error occured, uploaded with 'package_update'
    
        rvalue = 0
        
        # add some general CKAN specific fields to dictionary:
        jsondata["name"] = ds.lower()
        jsondata["state"]='active'
        jsondata["groups"]=[{ "name" : community }]
##HEW- changed!!!!
        jsondata["owner_org"]="eudat" ##HEW!!! "eudat"

        # if the dataset checked as 'new' so it is not in ckan package_list then create it with package_create:
        if (dsstatus == 'new' or dsstatus == 'unknown') :
            logging.debug('\t - Try to create dataset %s' % ds)
            
            results = self.CKAN.action('package_create',jsondata)
            if (results and results['success']):
                rvalue = 1
            else:
                logging.debug('\t - Creation failed. Try to update instead.')
                results = self.CKAN.action('package_update',jsondata)
                if (results and results['success']):
                    rvalue = 2
                else:
                    rvalue = 0
        
        # if the dsstatus is 'changed' then update it with package_update:
        elif (dsstatus == 'changed'):
            logging.debug('\t - Try to update dataset %s' % ds)
            
            results = self.CKAN.action('package_update',jsondata)
            if (results and results['success']):
                rvalue = 2
            else:
                logging.debug('\t - Update failed. Try to create instead.')
                results = self.CKAN.action('package_create',jsondata)
                if (results and results['success']):
                    rvalue = 1
                else:
                    rvalue = 0
           
        return rvalue

def main():
    global TimeStart
    TimeStart = time.time()

    # check the version from svn:
    global ManagerVersion
    ManagerVersion = '2.0'

    # parse command line options and arguments:
    modes=['g','generate','h','harvest','c','convert','m','map','v','validate','o','oaiconvert','u','upload','h-c','c-u','h-u', 'h-d', 'd','delete']
    p = options_parser(modes)
    global options
    options,arguments = p.parse_args()
    
    # check option 'mode' and generate process list:
    (mode, pstat) = pstat_init(p,modes,options.mode,options.source,options.iphost)
    
    # make jobdir
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    jid = os.getpid()

    ## logger
    logger = setup_custom_logger('root',options.verbose)

    # print out general info:
    ##HEW-Dprint('\n|- Version:  \t%s' % ManagerVersion)
    print('|- Run mode:   \t%s' % pstat['short'][mode])
    logging.debug('Process ID:\t%s' % str(jid))
    logging.debug('Processing status:\t')
    for key in pstat['status']:
        logging.debug(" %s\t%s" % (key, pstat['status'][key]))
    # check options:

    if ( pstat['status']['u'] == 'tbd'):
    
        # checking given options:
        if (options.iphost):
          if (not options.auth):
             from os.path import expanduser
             home = expanduser("~")
             if(not os.path.isfile(home+'/.netrc')):
                logging.critical('[CRITICAL] Can not access job host authentification file %s/.netrc ' % home )
                exit()
             f = open(home+'/.netrc','r')
             lines=f.read().splitlines()
             f.close()

             l = 0
             for host in lines:
                if(options.iphost == host.split()[0]):
                   options.auth = host.split()[1]
                   break
             logging.debug(
                'NOTE : For upload mode write access to %s by API key must be allowed' % options.iphost
             )
             if (not options.auth):
                logging.critical('[CRITICAL] API key is neither given by option --auth nor can retrieved from %s/.netrc' % home )
                exit()
        else:
            logging.critical(
                "\033[1m [CRITICAL] " +
                    "For upload mode valid URL of CKAN instance (option -i) and API key (--auth) must be given" + "\033[0;0m"
            )
            sys.exit(-1)
            
    ## START PROCESSING:
    print ("|- Start : \t%s\n" % now)
    logging.info("Loop over processes and related requests :\n")
    logging.info('|- <Process> started : %s' % "<Time>")
    logging.info(' |- Joblist: %s' % "<Filename of request list>")
    logging.info('   |# %-15s : %-30s \n\t|- %-10s |@ %-10s |' % ('<ReqNo.>','<Request description>','<Status>','<Time>'))



    try:
        # start the process:
        process(options,pstat)
        exit()
    except Exception as e:
        logging.critical("[CRITICAL] Program is aborted because of a critical error! Description:")
        logging.critical("%s" % traceback.format_exc())
        exit()
    finally:
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        logging.info("\nEnd :\t\t%s" % now)


def process(options,pstat):
    ## process (options,pstat) - function
    # Starts processing as specified in pstat['tbd'] and 
    #  according the request list given bey the options
    #
    # Parameters:
    # -----------
    # 1. options (OptionsParser object)
    # 2. pstat   (process status dict)  
    #
    
    # set single or multi mode:
    mode = None
    procOptions=['community','source','verb','mdprefix','mdsubset','target_mdschema']
    if(options.source):
        mode = 'single'
        ##HEW Not used in training
        options.target_mdschema=None
        mandParams=['community','verb','mdprefix'] # mandatory processing params
        for param in mandParams :
            if not getattr(options,param) :
                logger.critical("Processing parameter %s is required in single mode" % param)
                sys.exit(-1)
        reqlist=[[
                options.community,
                options.source,
                options.verb,
                options.mdprefix,
                options.mdsubset,
                options.target_mdschema
            ]]
    elif(options.list):
        if (pstat['status']['g'] == 'tbd'):
            logger.critical("  Processing parameter [ --source | -s SOURCE ] is required in generation mode")
            sys.exit(-1)
        mode = 'multi'
        logger.debug(' |- Joblist:  \t%s' % options.list)
        ## HEW set options.target_mdschema to NONE for Training
        options.target_mdschema=None
        reqlist=parse_list_file('harvest',options.list, options.community,options.mdsubset,options.mdprefix,options.target_mdschema)

    ## check job request (processing) options
    for opt in procOptions :
        if hasattr(options,opt) : logger.debug(' |- %s:\t%s' % (opt.upper(),getattr(options,opt)))

    ## GENERATION mode:    
    if (pstat['status']['g'] == 'tbd'):
        GEN = Generator(pstat,options.outdir)
        process_generate(GEN,reqlist)
        
    ## HARVESTING mode:    
    if (pstat['status']['h'] == 'tbd'):
        ### print('\n|- Harvesting started : %s' % time.strftime("%Y-%m-%d %H:%M:%S"))
        HV = Harvester(pstat,options.outdir,options.fromdate)
        process_harvest(HV,reqlist)
        
    ## MAPPINING - Mode:  
    if (pstat['status']['m'] == 'tbd'):
        print('\n|- Mapping started : %s' % time.strftime("%Y-%m-%d %H:%M:%S"))
        MP = Mapper(options.outdir,options.fromdate)
        process_map(MP,reqlist)

    ## VALIDATOR - Mode:  
    if (pstat['status']['v'] == 'tbd'):
        print('\n|- Validating started : %s' % time.strftime("%Y-%m-%d %H:%M:%S"))
        MP = Mapper()
        process_validate(MP,reqlist)

    ## UPLOADING - Mode:  
    if (pstat['status']['u'] == 'tbd'):
            # create CKAN object                       
            CKAN = CKAN_CLIENT(options.iphost,options.auth)
            UP = UPLOADER(CKAN)
            logging.info('\n|- Uploading started : %s' % time.strftime("%Y-%m-%d %H:%M:%S"))
            logging.info(' |- Host:  \t%s' % CKAN.ip_host )
            # start the process uploading:
            process_upload(UP,reqlist,options)

def process_generate(GEN, rlist):
    ## process_generate (GENERATOR object, rlist) - function
    # Generate metadata per request.
    #
    # Parameters:
    # -----------
    # (object)  GEN   - instance of class Generator
    # (list)    rlist - list of request lists 
    #
    # Return Values:
    # --------------
    # None
    ir=0
    for request in rlist:
        ir+=1
        genstart = time.time()
        logging.info('   |# %-4d : %-30s \n\t|- %-10s |@ %-10s |' % (ir,request,'Started',time.strftime("%H:%M:%S")))
        results = GEN.generate(request)
    
        if (results == -1):
            logging.error("Couldn't generate metadata according request %s" % request)

        gentime=time.time()-genstart

def process_harvest(HV, rlist):
    ## process_harvest (Harvester object, rlist) - function
    # Harvests per request.
    #
    # Parameters:
    # -----------
    # (object)  HV    - instance of class Harvester
    # (list)    rlist - list of request lists 
    #
    # Return Values:
    # --------------
    # None
    ir=0
    for request in rlist:
        ir+=1
        harveststart = time.time()
        logging.info('   |# %-4d : %-30s \n\t|- %-10s |@ %-10s |' % (ir,request,'Started',time.strftime("%H:%M:%S")))
        results = HV.harvest(request)
    
        if (results == -1):
            logging.critical("Couldn't harvest from %s" % request)

        harvesttime=time.time()-harveststart

def process_map(MP, rlist):
    ## process_map (Mapper object, rlist) - function
    # Maps per request.
    #
    # Parameters:
    # -----------
    # (object)  Mapper - object from the class Mapper
    # (list)    rlist - list of requests 
    #
    # Return Values:
    # --------------
    # None
    ir=0
    for request in rlist:
        ir+=1
        cstart = time.time()
        
        if len(request) > 4:
            path=os.path.abspath('oaidata/'+request[0]+'-'+request[3]+'/'+request[4])
        else:
            path=os.path.abspath('oaidata/'+request[0]+'-'+request[3]+'/SET')
             
        if (len(request) > 5 and request[5]):            
            target=request[5]
        else:
            target=None

        results = MP.map(request)

        ctime=time.time()-cstart
        results['time'] = ctime
        
def process_validate(MP, rlist):
    ## process_validate (Mapper object, rlist) - function
    # Validates per request.
    #
    # Parameters:
    # -----------
    # (object)  VALIDATOR - object from the class Mapper
    # (list)    rlist - list of request lists 
    #
    # Return Values:
    # --------------
    # None
    ir=0
    for request in rlist:
        ir+=1
        cstart = time.time()
        
        if len(request) > 4:
            path=os.path.abspath('oaidata/'+request[0]+'-'+os.path.basename(request[3])+'/'+request[4])
        else:
            path=os.path.abspath('oaidata/'+request[0]+'-'+request[3]+'/SET_1')

        outfile='%s/%s' % (path,'validation.stat')

        if (len(request) > 5 and request[5]):            
            target=request[5]
        else:
            target=None

        logging.info('   |# %-4d : %-10s\t%-20s\t--> %-30s \n\t|- %-10s |@ %-10s |' % (ir,request[0],request[3:5],outfile,'Started',time.strftime("%H:%M:%S")))

        results = MP.validate(request[0],request[3],path,target)

        ctime=time.time()-cstart
        results['time'] = ctime
        
def process_oaiconvert(MP, rlist):

    ir=0
    for request in rlist:
        ir+=1
        logging.info('   |# %-4d : %-10s\t%-20s --> %-10s\n\t|- %-10s |@ %-10s |' % (ir,request[0],request[2:5],request[5],'Started',time.strftime("%H:%M:%S")))
        rcstart = time.time()
        
        results = MP.oaiconvert(request[0],request[3],os.path.abspath(request[2]+'/'+request[4]),request[5])

        rctime=time.time()-rcstart
        results['time'] = rctime
        
        # save stats:
        MP.OUT.save_stats(request[0]+'-' + request[3],request[4],'o',results)


def process_upload(UP, rlist, options):
    ##HEW-D-ec credentials,ec = None,None

    def print_extra(key,jsondata):
        for v in jsondata['extras']:
            if v['key'] == key:
                print(' Key : %s | Value : %s |' % (v['key'],v['value']))
 

    ###HEW-D disabled for Training create credentials and handle cleint if required
    options.handle_check=False  ###HEW-D disabled for Training
    if (options.handle_check):
          try:
              cred = PIDClientCredentials.load_from_JSON('credentials_11098')
          except Exception as err:
              logging.critical("[CRITICAL %s ] : Could not create credentials from credstore %s" % (err,options.handle_check))
              ##p.print_help()
              sys.exit(-1)
          else:
              logging.debug("Create EUDATHandleClient instance")
              client = EUDATHandleClient.instantiate_with_credentials(cred)

    CKAN = UP.CKAN
    last_community = ''
    package_list = dict()

    ir=0
    mdschemas={
        "ddi" : "ddi:codebook:2_5 http://www.ddialliance.org/Specification/DDI-Codebook/2.5/XMLSchema/codebook.xsd",
        "oai_ddi" : "http://www.icpsr.umich.edu/DDI/Version1-2-2.xsd",
        "marcxml" : "http://www.loc.gov/MARC21/slim http://www.loc.gov/standards",
        "iso" : "http://www.isotc211.org/2005/gmd/metadataEntity.xsd",        
        "oai_dc" : "http://www.openarchives.org/OAI/2.0/oai_dc.xsd",
        "oai_qdc" : "http://pandata.org/pmh/oai_qdc.xsd",
        "cmdi" : "http://catalog.clarin.eu/ds/ComponentRegistry/rest/registry/profiles/clarin.eu:cr1:p_1369752611610/xsd",
        "json" : "http://json-schema.org/latest/json-schema-core.html",
        "fgdc" : "No specification for fgdc available",
        "hdcp2" : "No specification for hdcp2 available"
        }
    for request in rlist:
        ir+=1
        logging.info('   |# %-4d : %-10s\t%-20s \n\t|- %-10s |@ %-10s |' % (ir,request[0],request[2:5],'Started',time.strftime("%H:%M:%S")))
        community, source = request[0:2]
        mdprefix = request[3]

        if len(request) > 4:
            subset = request[4]
        else:
            subset = 'SET'
        
        results = {
            'count':0,
            'ecount':0,
            'tcount':0,
            'time':0
        }

        try:
            ckangroup=CKAN.action('group_list')
            if community not in ckangroup['result'] :
                logger.critical('Can not found community %s' % community)
                sys.exit(-1)
        except Exception as err:
            logging.critical("%s : Can not show CKAN group %s" % (err,community))
            sys.exit()
            
        if 'success' not in ckangroup and ckangroup['success'] != True :
            logging.critical(" CKAN group %s does not exist" % community)
            sys.exit()

        print ('|- Community %s\n |- MD prefix %s\n |- Subset %s\n' % (community,mdprefix,subset))

        path=os.path.abspath('oaidata/'+request[0]+'-'+request[3]+'/'+subset)

        if not os.path.exists(path):
            logging.critical('The directory "%s" does not exist! No files for uploading are found!' % path)
            
            # save stats:
            ##UP.OUT.save_stats(community+'-'+mdprefix,subset,'u',results)
            
            continue
        
        logging.debug('    |   | %-4s | %-40s |\n    |%s|' % ('#','id',"-" * 53))
        ##HEW : For Training no ckan_check
        options.ckan_check = 'False'
        if (last_community != community and options.ckan_check == 'True'):
            last_community = community
            UP.get_packages(community)
        
        uploadstart = time.time()
        
        # find all .json files in dir/json:
        files = filter(lambda x: x.endswith('.json'), os.listdir(path+'/json'))
        
        results['tcount'] = len(files)
        
        scount = 0
        fcount = 0
        oldperc = 0
        for filename in files:
            ## counter and progress bar
            fcount+=1
            if (fcount<scount): continue
            perc=int(fcount*100/int(len(files)))
            bartags=perc/5
            if perc%10 == 0 and perc != oldperc :
                oldperc=perc
                print("\t[%-20s] %d / %d%%\r" % ('='*bartags, fcount, perc ))
                sys.stdout.flush()

            jsondata = dict()
            pathfname= path+'/json/'+filename
            if ( os.path.getsize(pathfname) > 0 ):
                with open(pathfname, 'r') as f:
                    try:
                        jsondata=json.loads(f.read())
                    except:
                        logging.error('    | [ERROR] Cannot load the json file %s' % path+'/json/'+filename)
                        results['ecount'] += 1
                        continue
            else:
                results['ecount'] += 1
                continue

            # get dataset id (CKAN name) from filename (a uuid generated identifier):
            ds_id = os.path.splitext(filename)[0]
            
            logging.info('    | u | %-4d | %-40s |' % (fcount,ds_id))

            # get OAI identifier from json data extra field 'oai_identifier':
            if 'oai_identifier' not in jsondata :
                jsondata['oai_identifier'] = [ds_id]

            oai_id = jsondata['oai_identifier'][0]
            logging.debug("        |-> identifier: %s\n" % (oai_id))
            
            ### CHECK JSON DATA for upload
            jsondata=UP.check(jsondata)

            ### ADD SOME EXTRA FIELDS TO JSON DATA:
            #  generate get record request for field MetaDataAccess:
            if (mdprefix == 'json'):
               reqpre = source + '/dataset/'
               mdaccess = reqpre + oai_id
            else:
               reqpre = source + '?verb=GetRecord&metadataPrefix=' + mdprefix
               mdaccess = reqpre + '&identifier=' + oai_id
            index1 = mdaccess

            # exceptions for some communities:
            if (community == 'clarin' and oai_id.startswith('mi_')):
                mdaccess = 'http://www.meertens.knaw.nl/oai/oai_server.php?verb=GetRecord&metadataPrefix=cmdi&identifier=http://hdl.handle.net/10744/' + oai_id
            elif (community == 'sdl'):
                mdaccess =reqpre+'&identifier=oai::record/'+oai_id

            ###HEW!!! if (field.split('.')[0] == 'extras'): # append extras field
            ###HEW!!!        self.add_unique_to_dict_list(newds['extras'], field.split('.')[1], value)

            ## Move all CKAN extra fields to the list jsondata['extras']
            
            jsondata['MetaDataAccess']=mdaccess

            jsondata=UP.json2ckan(jsondata)
##            # determine checksum of json record and append
##            try:
##                checksum=hashlib.md5(unicode(json.dumps(jsondata))).hexdigest()
##                checksum=hashlib.md5(json.dumps(jsondata)).hexdigest()
##            except UnicodeEncodeError:
##                logging.error('        |-> [ERROR] Unicode encoding failed during md checksum determination')
##                checksum=None
##            except Exception as err:
##                logging.error('        |-> [ERROR] %s' % err)
##                checksum=None
##            else:
##                jsondata['version'] = checksum
            jsondata['version'] = None
            jsondata['owner_org'] = options.ckan_organization
                
            # Set the tag ManagerVersion:
            jsondata['extras'].append({
                      "key" : "ManagerVersion",
                      "value" : ManagerVersion
                     })
            
            ### CHECK STATE OF DATASET IN CKAN AND HANDLE SERVER:
            # status of data set
            dsstatus="unknown"
     
            # check against handle server
            handlestatus="unknown"
            checksum2=None
            if (options.handle_check):
                try:
                    ##HEW-D pid = "11098/eudat-jmd_" + ds_id ##HEW?? 
                    pid = cred.get_prefix() + '/eudat-jmd_' + ds_id 
                    rec = client.retrieve_handle_record_json(pid)
                    checksum2 = client.get_value_from_handle(pid, "CHECKSUM",rec)
                    ManagerVersion2 = client.get_value_from_handle(pid, "JMDVERSION",rec)
                    B2findHost = client.get_value_from_handle(pid,"B2FINDHOST",rec)
                except Exception as err:
                    logging.error("[CRITICAL : %s] in client.get_value_from_handle" % err )
                else:
                    logging.debug("Got checksum2 %s, ManagerVersion2 %s and B2findHost %s from PID %s" % (checksum2,ManagerVersion2,B2findHost,pid))
                if (checksum2 == None):
                    logging.debug("        |-> Can not access pid %s to get checksum" % pid)
                    handlestatus="new"
                elif ( checksum == checksum2) and ( ManagerVersion2 == ManagerVersion ) and ( B2findHost == options.iphost ) :
                    logging.debug("        |-> checksum, ManagerVersion and B2FIND host of pid %s not changed" % (pid))
                    handlestatus="unchanged"
                else:
                    logging.debug("        |-> checksum, ManagerVersion or B2FIND host of pid %s changed" % (pid))
                    handlestatus="changed"
                dsstatus=handlestatus

            # check against CKAN database
            ckanstatus = 'unknown'                  
            if (options.ckan_check == 'True'):
                ckanstatus=UP.check_dataset(ds_id,checksum)
                if (dsstatus == 'unknown'):
                    dsstatus = ckanstatus

            upload = 0
            # depending on status of handle upload record to B2FIND 
            logging.debug('        |-> Dataset is [%s]' % (dsstatus))
            if ( dsstatus == "unchanged") : # no action required
                logging.info('        |-> %s' % ('No upload required'))
            else:
                upload = UP.upload(ds_id,dsstatus,community,jsondata)
                if (upload == 1):
                    logging.info('        |-> Creation of %s record succeed' % dsstatus )
                elif (upload == 2):
                    logging.info('        |-> Update of %s record succeed' % dsstatus )
                    upload=1
                else:
                    logging.error('        |-> Upload of %s record %s failed ' % (dsstatus, ds_id ))
                    logging.error('        |-> JSON data :\n\t %s ' % json.dumps(jsondata, indent=2))
                    sys.exit()

            # update PID in handle server                           
            if (options.handle_check):
                if (handlestatus == "unchanged"):
                    logging.info("        |-> No action required for %s" % pid)
                else:
                    if (upload >= 1): # new or changed record
                        ckands='http://b2find.eudat.eu/dataset/'+ds_id
                        if (handlestatus == "new"): # Create new PID
                            logging.info("        |-> Create a new handle %s with checksum %s" % (pid,checksum))
                            try:
                                npid = client.register_handle(pid, ckands, checksum, None, True ) ## , additional_URLs=None, overwrite=False, **extratypes)
                            except (HandleAuthenticationError,HandleSyntaxError) as err :
                                logging.critical("[CRITICAL : %s] in client.register_handle" % err )
                            except Exception as err:
                                logging.critical("[CRITICAL : %s] in client.register_handle" % err )
                                sys.exit()
                            else:
                                logging.debug(" New handle %s with checksum %s created" % (pid,checksum))
                        else: # PID changed => update URL and checksum
                            logging.info("        |-> Update handle %s with changed checksum %s" % (pid,checksum))
                            try:
                                client.modify_handle_value(pid,URL=ckands) ##HEW-T !!! as long as URLs not all updated !!
                                client.modify_handle_value(pid,CHECKSUM=checksum)
                            except (HandleAuthenticationError,HandleNotFoundException,HandleSyntaxError) as err :
                                logging.critical("[CRITICAL : %s] client.modify_handle_value %s" % (err,pid))
                            except Exception as err:
                                logging.critical("[CRITICAL : %s]  client.modify_handle_value %s" % (err,pid))
                                sys.exit()
                            else:
                                logging.debug(" Modified JMDVERSION, COMMUNITY or B2FINDHOST of handle %s " % pid)

                    try: # update PID entries in all cases (except handle status is 'unchanged'
                        client.modify_handle_value(pid, JMDVERSION=ManagerVersion)
                        client.modify_handle_value(pid, COMMUNITY=community)
                        client.modify_handle_value(pid, SUBSET=subset)
                        client.modify_handle_value(pid, B2FINDHOST=options.iphost)
                        client.modify_handle_value(pid, IS_METADATA=True)
                        client.modify_handle_value(pid, MD_SCHEMA=mdschemas[mdprefix])
                        client.modify_handle_value(pid, MD_STATUS='B2FIND_uploaded')
                    except (HandleAuthenticationError,HandleNotFoundException,HandleSyntaxError) as err :
                        logging.critical("[CRITICAL : %s] in client.modify_handle_value of pid %s" % (err,pid))
                    except Exception as err:
                        logging.critical("[CRITICAL : %s] in client.modify_handle_value of %s" % (err,pid))
                        sys.exit()
                    else:
                        logging.debug(" Modified JMDVERSION, COMMUNITY or B2FINDHOST of handle %s " % pid)

            results['count'] +=  upload
            
        uploadtime=time.time()-uploadstart
        results['time'] = uploadtime
        logging.info(
                '   \n\t|- %-10s |@ %-10s |\n\t| Provided | Uploaded | Failed |\n\t| %8d | %6d | %6d |' 
                % ( 'Finished',time.strftime("%H:%M:%S"),
                    results['tcount'],
                    fcount,
                    results['ecount']
                ))
        
        # save stats:
        ##HEW-DDD UP.OUT.save_stats(community+'-'+mdprefix,subset,'u',results)

def parse_list_file(process,filename,community=None,subset=None,mdprefix=None,target_mdschema=None):
    if(not os.path.isfile(filename)):
        logging.critical('[CRITICAL] Can not access job list file %s ' % filename)
        exit()
    else:
        file = open(filename, 'r')
        lines=file.read().splitlines()
        file.close

    # processing loop over ingestion requests
    inside_comment = False
    reqlist = []

    logging.debug(' Arguments given to parse_list_file:\n\tcommunity:\t%s\n\tmdprefix:\t%s\n\tsubset:\t%s\n\ttarget_mdschema:\t%s' % (community,mdprefix,subset,target_mdschema))


    l = 0
    for request in lines:
        logging.debug(' Request in %s : %s' % (filename,request))
    
        l += 1
        
        # recognize multi-lines-comments (starts with '<#' and ends with '>'):
        if (request.startswith('<#')):
            inside_comment = True
            continue

        if ((request.startswith('>') or request.endswith('>')) and (inside_comment == True)):
            inside_comment = False
            continue
        
        # ignore comments and empty lines
        if(request == '') or ( request.startswith('#')) or (inside_comment == True):
            continue
       
        # sort out lines that don't match given community
        if((community != None) and ( not request.startswith(community))):
            continue

        # sort out lines that don't match given mdprefix
        if (mdprefix != None):
            if ( not request.split()[3] == mdprefix) :
              continue

        # sort out lines that don't match given subset
        if (subset != None):
            if len(request.split()) < 5 :
               continue
            elif ( not request.split()[4] == subset ) and (not ( subset.endswith('*') and request.split()[4].startswith(subset.translate(None, '*')))) :
              continue

##        if (target_mdschema != None):
##            request+=' '+target_mdschema  

        reqlist.append(request.split())
        
    if len(reqlist) == 0:
        logging.critical(' No matching request found in %s' % filename)
        exit()
 
    return reqlist

def options_parser(modes):
    
    p = optparse.OptionParser(
        description = '''Description                                                              
===========                                                                           
 Management of metadata, comprising                                      
      - Generation of formated XML records from raw metadata sets \n\t                           
      - Harvesting of XML files from a data provider endpoint \n\t                           
      - Mapping of specially formated XML to a target JSON schema \n\t                             
      - Validation of mapped JSON records as compatible with target schema \n\t
      - Uploading of JSON records to B2FIND or another CKAN instance \n\t
''',
        formatter = optparse.TitledHelpFormatter(),
        prog = 'mdmanager.py',
        epilog='For any further information and documentation please look at the README.md file or send an email to widmann@dkrz.de.'
    )
        
    p.add_option('-v', '--verbose', action="count",
                        help="increase output verbosity (e.g., -vv is more than -v)", default=False)

    p.add_option('--outdir', '-d', help="The relative root directory in which all harvested and processed files will be saved. The converting and the uploading processes work with the files from this dir. (default is 'oaidata')",default='oaidata', metavar='PATH') 
    p.add_option('--community', '-c', help="community or project, for which metadata are harvested, processed, stored and uploaded. This 'label' is used through the whole metadata life cycle.", default='', metavar='STRING')
    ##HEW-D really needed (for Training) ???  
    p.add_option('--mdsubset', help="Subset of metadata to be harvested (by default 'None') and subdirectory of harvested and processed metadata (by default 'SET_1'",default=None, metavar='STRING')
    p.add_option('--mdprefix', help="Metadata schema of harvested meta data (default is the OAI mdprefix 'oai_dc')",default=None, metavar='STRING')
    group_single = optparse.OptionGroup(p, "Single Source Operation Mode","Use the source option if you want to ingest from only ONE source.")
    group_single.add_option('--source', '-s', help="In 'generation mode' a PATH to raw metadata given as spreadsheets or in 'harvest mode' an URL to a data provider you want to harvest metadata records from.",default=None,metavar='URL or PATH')    
    group_multi = optparse.OptionGroup(p, "Multiple Sources Operation Mode","Use the list option if you want to ingest from multiple sources via the requests specified in the list file.")
    group_multi.add_option('--list', '-l', help="list of harvest sources and requests (default is ./harvest_list)", default='harvest_list',metavar='FILE')

    group_processmodes = optparse.OptionGroup(p, "Processing modes","The script can be executed in different modes by using the option -m | --mode, and provides procedures for the whole ingestion workflow how to come from unstructured metadata to entries in the discovery portal (own CKAN or B2FIND instance).")
    group_processmodes.add_option('--mode', '-m', metavar='PROCESSINGMODE', help='\nThis specifies the processing mode. Supported modes are (h)arvesting, (m)apping, (v)alidating, and (u)ploading.')

    group_generate = optparse.OptionGroup(p, "Generation Options",
        "These options will be required to generate formatted metadata sets (by default DublinCore XML files) from 'raw' spreadsheet data that resides in the PATH given by SOURCE.")
    group_generate.add_option('--delimiter', help="Delimiter, which seperates the fields and associated values in the datasets (lines) of the spreadsheets, can be 'comma' (default) or 'tab'",default='comma', metavar='STRING')

    group_harvest = optparse.OptionGroup(p, "Harvest Options",
        "These options will be required to harvest metadata records from a data provider (by default via OAI-PMH from the URL given by SOURCE).")
    group_harvest.add_option('--verb', help="Verbs or requests defining the mode of harvesting, can be ListRecords(default) or ListIdentifers if OAI-PMH used or e.g. 'works' if JSON-API is used",default='ListRecords', metavar='STRING')
    group_harvest.add_option('--fromdate', help="Filter harvested files by date (Format: YYYY-MM-DD).", default=None, metavar='DATE')

    group_map = optparse.OptionGroup(p, "Mapping Options",
        "These options will be required to map metadata records formatted in a supported metadata format to JSON records formatted in a common target schema. (by default XML records are mapped onto the B2FIND schema, compatable to be uploaded to a CKAN repository.")
    group_map.add_option('--subset', help="Subdirectory of harvested meta data records to be mapped. By default this is the same as the the term given by option '--mdsubset'.",default=None, metavar='STRING')
    group_map.add_option('--mdschema', help="Metadata format and schema of harvested meta data records to be mapped. By default this is the same as the term given by option '--mdprefix'.",default=None, metavar='STRING')

    ##HEW-D : Not used in Training (yet) !!! group_single.add_option('--target_mdschema', help="Meta data schema of the target",default=None,metavar='STRING')
    
    group_upload = optparse.OptionGroup(p, "Upload Options",
        "These options will be required to upload an dataset to a CKAN database.")
    group_upload.add_option('--iphost', '-i', help="IP adress of B2FIND portal (CKAN instance)", metavar='IP')
    group_upload.add_option('--auth', help="Authentification for CKAN APIs (API key, by default taken from file $HOME/.netrc)",metavar='STRING')
    group_upload.add_option('--ckan_organization', help="CKAN Organization name (by default 'rda')",default='eudat',metavar='STRING')
    ##HEW-D:(Not used yet in the Training) group_upload.add_option('--handle_check', help="check and generate handles of CKAN datasets in handle server and with credentials as specified in given credential file", default=None,metavar='FILE')
    ##HEW-D:(Not used yet in the Training) group_upload.add_option('--ckan_check',help="check existence and checksum against existing datasets in CKAN dattabase",default='False', metavar='BOOLEAN')

    p.add_option_group(group_single)
    p.add_option_group(group_multi)
    p.add_option_group(group_processmodes)
    p.add_option_group(group_generate)
    p.add_option_group(group_harvest)
    p.add_option_group(group_map)
    p.add_option_group(group_upload)
    
    return p

def pstat_init (p,modes,mode,source,iphost):
    if (mode):
        if not(mode in modes):
           print("[ERROR] Mode " + mode + " is not supported")
           sys.exit(-1)
    else: # all processes (default)
        mode = 'h-u'
 
    # initialize status, count and timing of processes
    plist=['g','h','m','v','u','c','o','d']
    pstat = {
        'status' : {},
        'text' : {},
        'short' : {},
     }

    for proc in plist :
        pstat['status'][proc]='no'
        if ( proc in mode):
            pstat['status'][proc]='tbd'
        if (len(mode) == 3) and ( mode[1] == '-'): # multiple mode
            ind=plist.index(mode[0])
            last=plist.index(mode[2])
            while ( ind <= last ):
                pstat['status'][plist[ind]]='tbd'
                ind+=1
        
    if ( mode == 'h-u'):
        pstat['status']['a']='tbd'
        
    if source:
       stext='provider '+source
    else:
       stext='a list of MD providers'
       
    pstat['text']['g']='Generate XML files from raw information' 
    pstat['text']['h']='Harvest XML files from ' + stext 
    pstat['text']['c']='Convert XML to B2FIND JSON'  
    pstat['text']['m']='Map community XML to B2FIND JSON and do semantic mapping'  
    pstat['text']['v']='Validate JSON records against B2FIND schema'  
    pstat['text']['o']='OAI-Convert B2FIND JSON to B2FIND XML'  
    pstat['text']['u']='Upload JSON records as datasets into B2FIND %s' % iphost
    pstat['text']['d']='Delete B2FIND datasets from %s' % iphost
    
    pstat['short']['h-u']='TotalIngestion'
    pstat['short']['g']='Generation'
    pstat['short']['h']='Harvesting'
    pstat['short']['c']='Converting'
    pstat['short']['m']='Mapping'
    pstat['short']['v']='Validating'
    pstat['short']['o']='OAIconverting'
    pstat['short']['u']='Uploading'
    pstat['short']['d']='Deletion'
    
    return (mode, pstat)

def exit_program (OUT, message=''):
    # stop the total time:
    OUT.save_stats('#Start','subset','TotalTime',time.time()-TimeStart)

    # print results with OUT.HTML_print_end() in a .html file:
    OUT.HTML_print_end()

    if (OUT.options.verbose != False):
      logging.debug('For more info open HTML file %s' % OUT.jobdir+'/overview.html')

if __name__ == "__main__":
    main()
