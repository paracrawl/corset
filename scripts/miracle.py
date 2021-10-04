import traceback
import logging
import sys
import argparse
import os
import re
import yaml
import pysolr 
import math 

from util import logging_setup, check_positive
from sacremoses import MosesTokenizer, MosesDetokenizer
from collections import Counter

from nltk import ngrams
#from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords 

import pysolr
from requests.auth import HTTPBasicAuth
#from tempfile import NamedTemporaryFile, gettempdir
from timeit import default_timer

import buildtmx


SOLR_URI = os.environ.get('SOLR_URL')
SOLR_USR = os.environ.get('SOLR_USR')
SOLR_PWD = os.environ.get('SOLR_PWD')


__author__ = "Marta Bañón"
__version__ = "Version 0.1 # 19/04/2021 # Initial release # Marta Bañón"

langnames={
    "da": "danish", 
    "de": "german",
    "el": "greek", 
    "en": "english",
    "es": "spanish",
    "fi": "finnish",    
    "fr": "french",
    "hu": "hungarian",
    "it": "italian",    
    "nl": "dutch",
    "no": "norwegian", 
    "pt": "portuguese",
    "ro": "romanian", 
    "ru": "russian",
    "sl": "slovene", 
    "sv": "swedish"}

#Creating this Similarity class to allow easy "passed-per-reference-like" parameters
class Similarity():
    max_similarity=0
    similarity=0
    
    
def initialization():
    parser = argparse.ArgumentParser(prog=os.path.basename(sys.argv[0]), formatter_class=argparse.ArgumentDefaultsHelpFormatter, description=__doc__)
    parser.add_argument('config', type=argparse.FileType('rt'), default=None, help="Config yaml file")
    
    # Logging group
    groupL = parser.add_argument_group('Logging')
    groupL.add_argument('-q', '--quiet', action='store_true', help='Silent logging mode')
    groupL.add_argument('--debug', action='store_true', help='Debug logging mode')
    groupL.add_argument('--logfile', type=argparse.FileType('w'), default=sys.stderr, help="Store log to a file")
    groupL.add_argument('-v', '--version', action='version', version="%(prog)s " + __version__, help="Show version of this script and exit")

    # Validating & parsing
    # Checking if metadata is specified
    args = parser.parse_args()
    logging_setup(args)  
    
    #Fix logger for pysolr to remove annoying INFO messages
    if logging.getLogger().level == 20:
        logging.getLogger('pysolr').setLevel(logging.WARN)


    
    #Load config from yaml file    
    try:
        config_yaml = yaml.safe_load(args.config)

        if "input" in config_yaml:
            #args.input=config_yaml["input"]
            args.input=open(config_yaml["input"], "rt")
        else:
            logging.error("Missing mandatory 'input' in config file")
            sys.exit(1)
        if "output" in config_yaml:    
            #args.output=config_yaml["output"]
            args.output=open(config_yaml["output"], "w")
        else:
            logging.error("Missing mandatory 'output' in config file")
            sys.exit(1)
        if "sents" in config_yaml:        
            args.sents=config_yaml["sents"]
        else:
            logging.error("Missing mandatory 'sents' in config file")
            sys.exit(1)
        if "collection" in config_yaml:        
            args.collection=config_yaml["collection"]
        else:
            logging.error("Missing mandatory 'collection' in config file")
            sys.exit(1)
        if "lang" in config_yaml:
            args.lang=config_yaml["lang"]
        else:
            logging.error("Missing mandatory 'lang' in config file")
            sys.exit(1)
        if "side" in config_yaml:        
            args.side=config_yaml["side"]
        else:	
            logging.error("Missing mandatory 'side' in config file")
            sys.exit(1)
        if "outformat" in config_yaml:
            args.outformat=config_yaml["outformat"]
        else:
            logging.error("Missing mandatory 'outformat' in config file")
            sys.exit(1)    
        if "lang2" in config_yaml:
            args.lang2=config_yaml["lang2"]
        else:
            logging.error("Missing mandatory 'lang2' in config file")
            sys.exit(1)
        if "side2" in config_yaml:
            args.side2=config_yaml["side2"]
        else:
            logging.error("Missing mandatory 'side2' in config file")                      
            sys.exit(1)
        if "isparallel" in config_yaml:
            args.isparallel=bool(config_yaml["isparallel"])
        else:
            logging.error("Missing mandatory 'isparallel' in config file")
            sys.exit(1)    

            
        try:
            check_positive(args.sents)
        except argparse.ArgumentTypeError:    
            logging.error("Invalid value for sentences: {0}".format(args.sents))
            sys.exit(1)       
        if args.outformat not in ["tsv", "tmx"]:
            logging.error("Wrong outformat: {0} (must be 'tsv' or 'tmx')".format(args.outformat))
            sys.exit(1)    
        '''    
        if args.lang not in langnames:
            logging.error("Unsupported language: {0}".format(args.lang))     
            sys.exit(1)
        '''
        '''    
        if "lang2" in args and args.lang2 not in langnames:
            logging.error("Unsupportd language: {1}".format(args.lang2))
            sys.exit(1)
        '''
        if args.side not in ["src", "trg"]:
            logging.error("Wrong side: {0} (must be 'src' or 'trg')".format(args.side))
            sys.exit(1)
        if "side2" in args and args.side2 not in ["src", "trg"]:
            logging.error("Wrong side: {0} (must be 'src' or 'trg')".format(args.side2))
            sys.exit(1)        


    except:
        logging.error("Error loading config file")        
        #traceback.print_exc()
        sys.exit(1)

    logging.debug("Arguments processed: {}".format(str(args)))

    return args


def get_ngrams(tokenized_sentence, max_order, stop_words):
    #builds ngrams from max_order to 1 for a given sentence
    candidates = {}
    for order in range(max_order, 0, -1):
        candidates[order] = [] #initialize map
        sent_ngrams=list(ngrams(tokenized_sentence, order))
        for candidate in sent_ngrams:        
            if any(token.lower() == token.upper() for token in candidate):
                #if token contains punctuation, we don't want it
                continue
            #if ngram[0].lower() == ngram[0].upper() or ngram[len(ngram)-1].lower() == ngram[len(ngram)-1].upper(): #Starts or ends with punctuation, ignore (the candidate without punct is already a ngram of another order)
            #    continue
            if any(token.lower() not in stop_words for token in candidate): #There is at least a token that is not a stopword
                #glued_candidate = (" ".join(candidate)).lower()
                #glued_candidate = detokenizer.detokenize(candidate)
                candidates[order].append(candidate)
    return candidates
    
def query_solr(solr, side, candidates, rows, start):
    #Queries Solr for a bunch of candidate phrases
    query_array = []
    query_str = " or ".join(side+":"+"\""+c+"\"" for c in candidates)
    #logging.debug(query_str)
    solr_results = solr.search(q=query_str, rows=rows, start=start, sort="custom_score desc")            
    #sentences = build_sentences_array(solr_results, None, None)            
    return solr_results, solr_results.hits
    
def build_sentence(sentence_dict):
    #Builds a tab-separated sentence, given a Solr sentence dict
    sent = [sentence_dict.get("src_url"), sentence_dict.get("trg_url"), sentence_dict.get("src"), sentence_dict.get("trg"), str(sentence_dict.get("custom_score"))]
    return "\t".join(sent)
    
def get_sentence_as_parts(sentence_dict):
    return sentence_dict.get("src_url"), sentence_dict.get("trg_url"), sentence_dict.get("src"), sentence_dict.get("trg"), sentence_dict.get("custom_score")    


def ngrammer(input, max_order, tokenizer, detokenizer, stop_words, col):    
    #given an input stream, extracts all ngrams of order n, n-1, n-2, ..., 1
    all_ngrams = {}
    all_ngrams_freqs = {}
    all_ngrams_sorted = {}
    
    #Initialize map
    for order in range(max_order, 0, -1): 
        all_ngrams[order]=[]           
 
    
    #Read input file extracting n-grams(max_order..1) for each sentence
    for line in input:
        #logging.error(line)
        parts = line.split("\t")
        if len(parts) < col:
            logging.error("Skipping line: {}".format(line))
            continue
        sent = parts[col-1].strip().strip("\n") 
        toks = tokenizer.tokenize(sent, escape=False) #Mosestokenizer
        #toks = word_tokenize(sent) #nltk tokenizer
        sent_ngrams_map = get_ngrams(toks, max_order, stop_words)
        for order in sent_ngrams_map.keys():
            for candidate in sent_ngrams_map[order]:
                all_ngrams[order].append(detokenizer.detokenize(candidate).lower())
            
        
    #"Reduce" the map, counting duplicates (frequency)
    for order in range(max_order, 0, -1):
        all_ngrams_freqs[order] = Counter(all_ngrams[order]).most_common()
        for ngram in all_ngrams_freqs[order]:            
            freq = ngram[1]
            score = order * freq
            try:
                all_ngrams_sorted[score].append(ngram[0])
            except:
                all_ngrams_sorted[score] = [ngram[0]]        
     
    return all_ngrams_sorted           
    

def split_in_batches(all_ngrams_sorted, group_scores, blocksize):
    #Splits the ngrams in "blocks" of blocksize , to avoid the "maxBooleanClauses" issue
    group = {}
    for score in group_scores:
        group[score] =  []
        if len(all_ngrams_sorted[score]) < blocksize:
            group[score].append(all_ngrams_sorted[score])
        else:   
            block = 0
            while block*blocksize < len(all_ngrams_sorted[score]):
                group[score].append(all_ngrams_sorted[score][block*blocksize:block*blocksize+blocksize])
                block = block+1
    return group      


def get_results_for_group(solr, scoring_group, status, indexes, desired_sentences, spg, side, sim):
    #Given a scoring group (i.e. regular_group or emergency_group),
    #a status array,
    #and a indexes array,
    #queries solr to extract sentences  
    
    page= 0
    indexes_len  = len(indexes) #Manually doing this to avoid reading the set every time
    while indexes_len < desired_sentences and any(s != 0 for s in status.values()): #Indexes list is not full yet, and there are still groups to be queried
        logging.debug("********* Page {0} starts ***********".format(page))
        #pending: list of score groups that are true
        pending_groups_this_round = list(filter(lambda x: status[x]!=0, status))    
        logging.debug("Status: {0}".format(status))
        logging.debug("Pending groups this round: {0}".format(pending_groups_this_round))

        for group in pending_groups_this_round:
            logging.debug("******** Group {0} starts ********".format(group))
            #Looping through active groups (status != 0)
            if indexes_len  >= desired_sentences:
                #We are done!
                return
           
            blocks_in_group = len(scoring_group[group])    
            booster = status[group]    
            pagesize = spg * booster 
            rows = pagesize // blocks_in_group
            
            blocks_next_round = [] #Keep here blocks for next round, removing those fully explored
        
            for block_index in range(0, blocks_in_group):   
                logging.debug("******* Block {1} from group {0} starts *********".format(group, block_index))
                block = scoring_group[group][block_index]
                logging.debug("Block index: {0} ".format(block_index))
                logging.debug("Block: {0}".format(block))               

                logging.debug("Querying for {0} sentences (base: {4}, booster: {5}, blocks: {7} ) from group {1} (block {6}), starting in {2} (page {3})".format(rows, group , page*rows, page, spg, booster, block_index, blocks_in_group))                

                solr_sentences, matches = query_solr(solr, side, block, rows, page*rows)
                logging.debug("Retrieved {0} sentences for group {1}, block {3} (total: {2})".format(len(solr_sentences), group, matches, block_index))
                for candidate_sent in solr_sentences:
                    if candidate_sent.get('id') not in indexes:
                        #logging.debug("Added candidate: {0}".format(candidate_sent.get("id")))
                        indexes_len = indexes_len + 1 #Update length by hand
                        indexes.add(candidate_sent.get('id'))
                        sim.similarity = sim.similarity+group
                        if args.outformat=="tmx":
                            url1, url2, sent1, sent2, custom_score = get_sentence_as_parts(candidate_sent)
                            buildtmx.write_line(args.output, args.lang, args.lang2, url1,  url2, sent1, sent2, custom_score)
                        else:   
                            args.output.write(build_sentence(candidate_sent)+"\n")
                            
                    #else:
                        #logging.debug("Candidate {0} already existing.".format(candidate_sent.get("id")))
                    #logging.debug("Indexes: {0}".format(len(indexes)))
                    if indexes_len >= desired_sentences:
                        logging.debug("Alredy retrieved {0} sentences, bye!".format(indexes_len))
                        return
                if len(solr_sentences) < rows:
                    #Solr returned less sentences than the amount requested -> there are no more results for this block
                    logging.debug("Block {0} from group {1} is fully explored".format(block_index, group))
                else:
                    blocks_next_round.append(block)

            if len(blocks_next_round) == 0:
                #No blocks in this group were added for next round
                logging.debug("Group {0} is fully explored".format(group))
                status[group] = 0 #This group is fully explored
            else:
                #Replace with tne new group, without the fully explored blocks
                scoring_group[group] = blocks_next_round
                    
        page=page+1        
    
    return   
        
    
def main(args):
    '''
    ************* THE SETUP PART ***********
    '''

    time_start = default_timer()
    solr = pysolr.Solr(SOLR_URI+"/"+args.collection, auth=HTTPBasicAuth(SOLR_USR,SOLR_PWD))
    max_order = 8
    blocksize = 200
    
    tokenizer = MosesTokenizer(args.lang) 
    detokenizer = MosesDetokenizer(args.lang)
    

    if args.lang not in langnames:
        stop_words=[]
    else:                        
        try:        
            stop_words = set(stopwords.words(langnames[args.lang]))
        except LookupError as e:
            #whoops, no stopwords downloaded, try again:
            import nltk
            nltk.download('stopwords')
            stop_words = set(stopwords.words(langnames[args.lang]))
            
    
    #If input text is parallel:
    if args.isparallel:
        tokenizer2=MosesTokenizer(args.lang2)
        detokenizer2=MosesDetokenizer(args.lang2)
        if args.lang2 not in langnames:
            stop_words2=[]
        else:    
            stop_words2=set(stopwords.words(langnames[args.lang2]))
  
    if args.outformat=="tmx":
        buildtmx.write_header(args.output)           
        
    '''
    ************** THE NGRAMS PART ***************
    '''
    
    #Get ngrams sorted by score (score = ngram_order * frequency)
    all_ngrams_sorted = ngrammer(args.input, max_order, tokenizer, detokenizer, stop_words, col=1)
    
    if len(all_ngrams_sorted) == 0:
        logging.error("No ngrams found.")
        sys.exit(1)
    
    if args.isparallel:
        args.input.seek(0)
        all_ngrams_sorted2 = ngrammer(args.input, max_order, tokenizer2, detokenizer2, stop_words2, col=2)
   

    #get list of scores, sorted desc (higher scores first)
    scores = list(all_ngrams_sorted.keys())
    scores.sort(reverse=True)
    if args.isparallel:
        scores2 = list(all_ngrams_sorted2.keys())
        scores2.sort(reverse=True)

            
    #display size of groups    
    for score in scores:
        logging.debug("Group {0} --> {1} candidates".format(score, len(all_ngrams_sorted[score])))
    if args.isparallel:
        for score in scores2:
            logging.debug("Group {0} --> {1} candidates".format(score, len(all_ngrams_sorted2[score])))

 
    #Segmenting score groups:
    #Top 25% scores: x4
    #25%-50% scores: x2
    #50%-75% scores: x1
    #Bottom 25% scores: emergency group (not queried until all others fully explored)
 
    twentyfivepercent = len(scores) // 4
    if twentyfivepercent==0:
        twentyfivepercent=1
    first_group_scores = scores[0:twentyfivepercent]
    second_group_scores = scores[twentyfivepercent:twentyfivepercent*2]
    third_group_scores = scores[twentyfivepercent*2:twentyfivepercent*3]
    emergency_group_scores = scores[twentyfivepercent*3:]    
    
    if args.isparallel:
        twentyfivepercent2 = len(scores2) // 4
        first_group_scores2 = scores2[0:twentyfivepercent2]
        second_group_scores2 = scores2[twentyfivepercent2:twentyfivepercent2*2]
        third_group_scores2 = scores2[twentyfivepercent2*2:twentyfivepercent2*3]
        emergency_group_scores2 = scores2[twentyfivepercent2*3:]
    

    '''
    logging.debug("Scores: {0}".format(scores))    
    logging.debug("First group scores: {0}".format(first_group_scores))
    logging.debug("Second group scores: {0}".format(second_group_scores))
    logging.debug("Third group scores: {0}".format(third_group_scores))
    logging.debug("Emergency group is score {0}.".format(emergency_group_scores))
    '''
    
    regular_group_scores = []
    regular_group_scores.extend(first_group_scores)
    regular_group_scores.extend(second_group_scores)
    regular_group_scores.extend(third_group_scores)
    
    if args.isparallel:
        regular_group_scores2 = []
        regular_group_scores2.extend(first_group_scores2)
        regular_group_scores2.extend(second_group_scores2)
        regular_group_scores2.extend(third_group_scores2)


    regular_group = split_in_batches(all_ngrams_sorted, regular_group_scores, blocksize)
    emergency_group = split_in_batches(all_ngrams_sorted, emergency_group_scores, blocksize)

    if args.isparallel:        
        regular_group2 = split_in_batches(all_ngrams_sorted2, regular_group_scores2, blocksize)
        emergency_group2 = split_in_batches(all_ngrams_sorted2, emergency_group_scores2, blocksize)

   
    
    logging.debug("******** regular **********")
    for k in regular_group.keys():
        logging.debug("{0} --> {1}".format(k, len(regular_group[k])))
    logging.debug("********* emergency *********")
    for k in emergency_group.keys():
        logging.debug("{0} --> {1}".format(k, len(emergency_group[k])))
    logging.debug("******************")        
    
    
    if args.isparallel:
        logging.debug("******** regular 2 **********")
        for k in regular_group2.keys():
            logging.debug("{0} --> {1}".format(k, len(regular_group2[k])))
        logging.debug("********* emergency 2 *********")
        for k in emergency_group2.keys():
            logging.debug("{0} --> {1}".format(k, len(emergency_group2[k])))
        logging.debug("******************")  
    
    
    ngrams_time = default_timer() - time_start    
    logging.info("Extracted ngrams in {0:.2f} s".format(ngrams_time))
    

    '''
    ************ THE SOLR PART ****************
    '''


    #status: keeps track of retrieved sents per scoring group
    status = {}
    for score in regular_group_scores:
        if score in first_group_scores:
            status[score] = 4
        elif score in second_group_scores:
            status[score] = 2    
        elif score in third_group_scores:
            status[score] = 1
        else:        
            status[score] = 0  #0: Don't query for this score anymore. Other value: booster            
    emergency_status = {}
    for score in emergency_group_scores:
        emergency_status[score] = 1
        
    if args.isparallel:
        status2 = {}
        for score in regular_group_scores2:
            if score in first_group_scores2:
                status2[score] = 4
            elif score in second_group_scores2:
                status2[score] = 2
            elif score in third_group_scores2:
                status2[score] = 1
            else:
                status2[score] = 0  #0: Don't query for this score anymore. Other value: booster            
        emergency_status2 = {}
        for score in emergency_group_scores2:
            emergency_status2[score] = 1


    #spg: sentences per group (base value. Boosted x4 for first group, x2 for second group)
    #In case of parallel input, args.sents is divided by 2 (half for src, half for trg)
    if args.isparallel:
        spg = math.ceil((args.sents/2)/len(regular_group_scores))
        spg2 = math.ceil((args.sents/2)/len(regular_group_scores2))
    else:
        spg = math.ceil(args.sents/len(regular_group_scores))               

    #Max similarity: Theorical best case, in which all sentences are from first 25% group
    sim = Similarity()
    #accum = 0
    if args.isparallel:
        for s in first_group_scores:
            sim.max_similarity = sim.max_similarity+(4*spg*s)
            #accum = accum + 4*spg
            #if accum >= args.sents/2:
            #    break
        for s in first_group_scores2:
            sim.max_similarity = sim.max_similarity+(4*spg2*s)    
            #accum = accum + 4*spg2
            #if accum >= args.sents:
            #    break
    else:
        for s in first_group_scores:
            sim.max_similarity = sim.max_similarity+(4*spg*s)
            #accum = accum + 4*spg
            #if accum >= args.sents:
            #    break
            


            
    #indexes: keeps track of which sentences were included in the output
    indexes = set()
    if args.isparallel:
        get_results_for_group(solr, regular_group, status, indexes, args.sents/2, spg, args.side, sim)
        get_results_for_group(solr, regular_group2, status2, indexes, args.sents, spg2, args.side2, sim) #not dividing sents/2 because we want to reach the total in this iteration
    else:
        get_results_for_group(solr, regular_group, status, indexes, args.sents, spg, args.side, sim) 


    #All done with the regular group, let's see if we need the emergency group:
    if len(indexes) < args.sents:
        if args.isparallel:
            spg = int((args.sents/2)/len(emergency_group_scores))
            spg2= int((args.sents/2)/len(emergency_group_scores2))
            get_results_for_group(solr, emergency_group, emergency_status, indexes, args.sents/2, spg, args.side, sim)            
            get_results_for_group(solr, emergency_group2, emergency_status2, indexes, args.sents, spg2, args.side2, sim)
        else:
            spg = int(args.sents / len(emergency_group_scores))
            get_results_for_group(solr, emergency_group, emergency_status, indexes, args.sents, spg, args.side, sim)
            
    solr_time = default_timer() - time_start - ngrams_time    
    logging.info("Queried solr in {0:.2f} s".format(solr_time))
    
    if args.outformat == "tmx":
        buildtmx.write_footer(args.output)


    '''
    ********* STATS ***********
    '''
    logging.info("Max. similarity: {0}".format(sim.max_similarity))
    logging.info("Similarity: {0} ({1:.2f}%)".format(sim.similarity, sim.similarity*100/(sim.max_similarity)))

    

    '''
    ************ DESPEDIDA Y CIERRE ************
    '''    
    total_time = default_timer() - time_start    
    logging.info("Elapsed time {0:.2f} s".format(total_time))
    

if __name__ == '__main__':
    try:
        logging_setup()
        args = initialization() # Parsing parameters
        main(args)  # Running main program
    except Exception as ex:
        tb = traceback.format_exc()
        logging.error(tb)
        sys.exit(1)
