#!/usr/bin/env python3
#encoding: UTF-8

__author__ = "Marta Bañón (mbanon)"
# Please, don't delete the previous descriptions. Just add new version description at the end.
__version__ = "0.1 # 01/03/2021 # Parallel text to SOLR converter and uploader # mbanon"

import os
import sys
import json
import argparse
import traceback
import logging
import gzip
import timeit
import base64

import urllib.request 

from pathlib import Path
from util import logging_setup

def initialization():
    # Getting arguments and options with argparse
    # Initialization of the argparse class
    parser = argparse.ArgumentParser(prog=os.path.basename(sys.argv[0]), formatter_class=argparse.RawDescriptionHelpFormatter, description=__doc__)

    # Mandatory parameters
    ## Input file. Can be std input stream.
    parser.add_argument('input',  help="Corpus file (optionally gzipped).")
    

    #Options group
    groupO = parser.add_argument_group('options')

    groupO.add_argument('-c', '--collection', type=str, help="Solr collection url", required=True)  
    groupO.add_argument("-p", "--prefix", type=str, help="Prefix for Solr identifiers", required=True)  
    groupO.add_argument('-b', '--blocksize',  type=int, default=5000, help="Amount of documents to upload to Solr at once")
    # Output file.
    #groupO.add_argument('-o', '--output', type=argparse.FileType('wb+'), default=None, help="File in Solr-ready format")
 
    groupO.add_argument('--liteformat',  action='store_true', help='True when the TSV comes is 5 column long.') 
    groupO.add_argument('-u', '--user', type=str, help="Solr user")
    groupO.add_argument('-w', '--password', type=str, help="Solr password")
      
    # Logging group
    groupL = parser.add_argument_group('logging')
    groupL.add_argument('-q', '--quiet', action='store_true', help='Silent logging mode')
    groupL.add_argument('--debug', action='store_true', help='Debug logging mode')
    groupL.add_argument('--logfile', type=argparse.FileType('a'), default=sys.stderr, help="Store log to a file")

    # Validating & parsing
    args = parser.parse_args()
    logging_setup(args)

    # Extra-checks for args here
    inputFile=Path(args.input)
    if inputFile.is_file():
        if inputFile.match("*.gz"):
            f=gzip.open(str(inputFile.resolve()),mode='rt')
        else:
            f=inputFile.open()
        args.input=f
    #else:
    #    logging.error("Provided input file does not exist")
    #    exit(1)    
    return args

class Sentence():
       
    def __init__(self, id, src_url, trg_url, src, trg, custom_score):
        self.id = id
        self.src_url = src_url
        self.trg_url = trg_url
        self.src = src
        self.trg = trg
        #self.bicleaner_score = bicleaner_score
        #self.badjuju_score = badjuju_score
        #self.priority = priority
        self.custom_score = custom_score
        self.tags = []
        #future: tags
        
    def to_dict(self):          
        d=dict()
        d['id'] = self.id
        d['src_url'] = self.src_url
        d['trg_url'] = self.trg_url
        d['src'] = self.src
        d['trg'] = self.trg
        #d['bicleaner_score'] = self.bicleaner_score
        #d['badjuju_score'] = self.badjuju_score
        #d['priority'] = self.priority
        d['custom_score'] = self.custom_score
        return d

    def to_json(self):
        d = self.to_dict()
        #return json.dumps(d)
        return json.JSONEncoder().encode(d)
        
  
def uploadToSolr(documents, collection, username, password):  
    #print(documents)
    #return
    solr_url = "{}/update/json?commit=true".format(collection)
    parsed_url = urllib.parse.urlparse(solr_url)


    req = urllib.request.Request(url=parsed_url.geturl(), data=documents,  headers = {"Content-Type": "application/json"})

    if username!=None and password!=None:
        credentials = ('%s:%s' % (username, password))
        encoded_credentials = base64.b64encode(credentials.encode('ascii'))
        req.add_header('Authorization', 'Basic %s' % encoded_credentials.decode("ascii"))
  
    with urllib.request.urlopen(req) as f:
        resp=f.read()
    logging.info (resp)
    return
  

def processLine(line, prefix, counter, liteformat):
    parts = line.split("\t")
    if liteformat and  len(parts) < 5:
        logging.warning("Missing fields in sentence:  ")
        logging.warning(line+"\n")
        return
    if not liteformat and len(parts) < 8:    
        logging.warning("Missing fields in sentence:  ")
        logging.warning(line+"\n")
        return

    document_id = "{}.{}".format(prefix,str(counter))   
    if liteformat:
        return (Sentence(document_id, parts[0], parts[1], parts[2], parts[3], parts[4]).to_dict())
    else:        
        return(Sentence(document_id, parts[0], parts[1], parts[2], parts[3], parts[7]).to_dict())    


def get_domain(url):
    if "//" in url:
        parts = url.split("//")
        protocol = parts[0]
        parts_2 = parts[1].split("/")
        domain = parts_2[0]
        if ":" in domain:
            return(protocol+"//"+domain.split(":")[0])
        else:
            return(protocol+"//"+domain)
    else:
        domain = url.split("/")[0]
        if ":" in domain:
            return (domain.split(":")[0])
        else:            
            return(domain)
        

def main(args):
    counter = 1
    document_batch = []
    #if (args.user!=None or args.password!=None):
        #password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        #domain = get_domain(args.collection)
        #password_mgr.add_password(None, domain, args.user, args.password)
        #handler = urllib.request.HTTPBasicAuthHandler(password_mgr)

    for line in args.input:
        proc_line = processLine(line.strip(), args.prefix, counter, args.liteformat)
        if proc_line == None:
            continue
        document_batch.append(proc_line)
        if (counter%args.blocksize==0):
            json_data = json.dumps(document_batch)
            data = json_data.encode("utf-8")
            uploadToSolr(data, args.collection, args.user, args.password)
            document_batch = []
        counter += 1    
    if (document_batch != []):
        json_data = json.dumps(document_batch)
        data = json_data.encode("utf-8")
        uploadToSolr(data, args.collection, args.user, args.password)
      
      
if __name__ == '__main__':
    try:
        logging_setup()
        args = initialization() # Parsing parameters
        logging_setup(args)
        start_time = timeit.default_timer()
        main(args)  # Running main program
        end_time = timeit.default_timer()
        logging.info("Program finished. Elapsed time: {}".format(end_time - start_time))
    except json.decoder.JSONDecodeError:
        tb = traceback.format_exc()
        logging.error(tb)
        logging.error("Input file is not parseable")
    except urllib.error.URLError:
        tb = traceback.format_exc()
        logging.error(tb)
        logging.error("Wrong Solr url")
    except Exception as ex:
        tb = traceback.format_exc()
        logging.error(tb)
        sys.exit(1)

      

   


    

