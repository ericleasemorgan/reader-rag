#!/usr/bin/env python

# morphadorn.py - given a TEI file, mark-up sentences complete with words, lemmas, and parts-of-speech

# Eric Lease Morgan <eric_morgan@infomotions.com>
# November 24, 2018 - first cut but took all day to write
# December  1, 2018 - added lemma and pos to punctuation; added identifiers; on a plane to Oslo
# June     12, 2026 - migrating to the Reader, sort of
# [Date]        - optimized for speed using spacy.pipe and native lxml XSLT

# configure
MODEL    = 'en_core_web_sm'
ENCODING = 'UTF-8'
STYLE    = './etc/add-id.xsl'
MAX      = 1600000

# require
from lxml import etree
import spacy
import sys

# sanity check
if len( sys.argv ) != 2 :
	sys.stderr.write( 'Usage: ' + sys.argv[ 0 ] + " <file>\n" )
	exit()

# initialize
file = sys.argv[ 1 ] 
tei = etree.parse( file )

# initialize XSLT transformation natively to avoid os.system and temporary files
xslt = etree.parse( STYLE )
transform = etree.XSLT( xslt )

# load spacy and disable unnecessary pipeline components for speed
nlp = spacy.load( MODEL, disable=['ner', 'tagger', 'lemmatizer', 'attribute_ruler'] )
nlp.max_length = MAX

sys.stderr.write( file + '\n' )

# get paragraphs and lines, defaulting to empty string if text is None
paragraphs = tei.xpath( '//body//p | //body//l' )
texts = [ p.text if p.text else '' for p in paragraphs ]

# process all paragraphs in a batch using nlp.pipe for maximum speed
for paragraph, document in zip( paragraphs, nlp.pipe( texts, batch_size=100 ) ) :

	# re-initialize
	paragraph.text = ''
	
	# process each sentence in the given paragraph
	for sentence in document.sents :

		# add subelement and set text
		s        = etree.SubElement( paragraph, 's' )
		s.text   = sentence.text
					
# apply xslt, write directly to the original file, and done
result = transform( tei )
with open( file, 'wb' ) as f :
    f.write( etree.tostring( result, xml_declaration=True, encoding=ENCODING, pretty_print=True ) )

exit()
