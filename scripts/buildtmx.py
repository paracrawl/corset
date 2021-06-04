"""Build tmx from tab separated file
Usage:
  buildtmx.py LANG1 LANG2 
"""

#Based on: https://github.com/bitextor/biroamer/blob/master/buildtmx.py

from docopt import docopt
from xml.sax.saxutils import escape
import sys
import datetime

tmx_header = """<?xml version="1.0"?>
<tmx version="1.4">
 <header
   adminlang="en"
   srclang="{}"
   o-tmf="PlainText"
   creationtool="buildtmx"
   creationtoolversion="4.0"
   datatype="PlainText"
   segtype="sentence"
   creationdate="{}"
   o-encoding="utf-8">
 </header>
 <body>
"""
 
 
tmx_footer ="  </body>\n</tmx>\n"

tu_template="""    <tu>
      <prop type="custom-score">{}</prop> 
      <tuv xml:lang="{}">
        <prop type="source-document">{}</prop>
        <seg>{}</seg>
      </tuv>
      <tuv xml:lang="{}">
        <prop type="source-document">{}</prop>      
        <seg>{}</seg>
      </tuv>
    </tu>
"""
      
      

def print_tu(lang1, lang2, url1, url2, s1, s2, custom_score):
    global tu_template    
    return tu_template.format(custom_score, lang1, escape(url1), escape(s1), lang2, escape(url2), escape(s2))

def write_header(output):
    global tmx_header
    creationdate = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
    output.write(tmx_header.format("en", creationdate))
    
def write_footer(output):
    global tmx_footer    
    output.write(tmx_footer)

def write_line(output, lang1, lang2, url1, url2,  sent1, sent2, custom_score):
    output.write(print_tu(lang1, lang2, url1, url2, sent1, sent2, custom_score))

def build_tmx_file(input, output, lang1, lang2):
    global tmx_header, tmx_footer
    
        
    creationdate = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
    
    output.write(tmx_header.format("en", creationdate))
    
    for i in input:
        sentences = i.strip().split("\t")
        output.write(print_tu(lang1, lang2, sentences[0], sentences[1]))
    
    output.write(tmx_footer)
    output.close()

