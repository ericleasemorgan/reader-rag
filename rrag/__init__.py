'''A retrieval-augmented generation (RAG) system applied against Distant Reader study carrels'''

# Eric Lease Morgan <emorgan@nd.edu>
# (c) Infomotions, LLC; distributed under a GNU Public License

# June      2, 2026 - first investigations
# June     11, 2026 - added bunches o' stuff in previous days; made Reformatter work
# November 17, 2026 - adjusted search to use a threshold as well as VEC_DISTANCE_COSINE
# November 20, 2026 - adjusting search some more; Happy birthday to me!


# configure prompts
PROMPTELABORATE = 'Answer the question "%s", and use only the following as the source of the answer: %s'
PROMPTSUMMARIZE = 'Summarize: %s. Respond in plain text only, no markdown formatting.'
PROMPTSYSTEM    = 'You are %s, and you respond in %s.'

# configure models
LLM      = 'glm-5.2:cloud'
EMBEDDER = 'locusai/multi-qa-minilm-l6-cos-v1'

# configure file names
CACHEDCARREL    = 'cached-carrel.txt'
CACHEDLENGTH    = 'cached-length.txt'
CACHEDPERSONA   = 'cached-persona.txt'
CACHEDQUERY     = 'cached-query.txt'
CACHEDQUESTION  = 'cached-question.txt'
CACHEDSENTENCES = 'cached-sentences.txt'
CACHEDPROMPT    = 'system-prompt.txt'
CACHEDTYPE      = 'cached-type.txt'
CACHEDRESULTS   = 'cached-results.csv'
DATABASE        = 'sentences.db'
INDEXJSON       = 'index.json'
LENGTHS         = 'lengths.txt'
PERSONAS        = 'personas.txt'
LIBRARY         = 'localLibrary'

# other
RRAGCACHE = 'cache'

# require
from json                     import load
from math                     import exp
from natsort                  import natsorted
from ollama                   import embed, generate
from os.path                  import dirname
from pandas                   import DataFrame, read_csv, read_sql_query
from pathlib                  import Path
from rdr                      import configuration, ETC
from scipy.signal             import argrelextrema
from sklearn.metrics.pairwise import cosine_similarity
from sqlite_vec               import load as vecload
from sqlite3                  import connect
from typing                   import List
import numpy                  as     np
from struct                   import pack

# initialize
cwd     = Path( dirname( __file__ ) )
library = configuration ( LIBRARY )


class Settings :

	def __init__( self ) : return( None )

	def set( self, type, value ) :
	
		if type == 'persona' :
			with open( cwd/RRAGCACHE/CACHEDPERSONA, 'w' ) as handle : handle.write( value )

		if type == 'length' :
			with open( cwd/RRAGCACHE/CACHEDLENGTH, 'w' ) as handle : handle.write( value )

	def get( self, type ) :
	
		if type == 'persona' :
			with open( cwd/RRAGCACHE/CACHEDPERSONA ) as handle : content = handle.read().rstrip()
		
		elif type == 'length' :
			with open( cwd/RRAGCACHE/CACHEDLENGTH ) as handle : content = handle.read().rstrip()
				
		elif type == 'carrel' :
			with open( cwd/RRAGCACHE/CACHEDCARREL ) as handle : content = handle.read()
				
		elif type == 'type' :
			with open( cwd/RRAGCACHE/CACHEDTYPE ) as handle : content = handle.read()
				
		elif type == 'query' :
			with open( cwd/RRAGCACHE/CACHEDQUERY ) as handle : content = handle.read()
				
		elif type == 'results' :
			content = read_csv( cwd/RRAGCACHE/CACHEDRESULTS )
				
		return( content )
		
			
class Summarizer :

	def __init__( self ) : return( None )

	def summarize( self ) : 
	
		# initialize
		sentences  = Citations().to_sentences()
		paragraphs = ' '.join( sentences )
		prompt     = PROMPTSUMMARIZE % ( paragraphs )
		system     = PROMPTSYSTEM % ( Settings().get( 'persona' ), Settings().get( 'length' ) )
		
		# do the work, get the response, and done
		result   = generate( LLM, prompt, system=system )
		response = result[ 'response' ]
		return( response  )


class Elaborate :

	def __init__( self ) : return( None )

	def elaborate( self, request ) : 
	
		# initialize
		sentences  = Citations().to_sentences()
		paragraphs = ' '.join( sentences )
		prompt     = PROMPTELABORATE % ( request, paragraphs )
		system     = PROMPTSYSTEM % ( Settings().get( 'persona' ), Settings().get( 'length' ) )
		
		# do the work, get the response, and done
		result   = generate( LLM, prompt, system=system )
		response = result[ 'response' ]
		return( response  )


class Cacher :

	def __init__( self ) : return( None )
	
	def cache( self, type, content ) :
	
		if type == 'results' : 
			with open( cwd/RRAGCACHE/CACHEDRESULTS, 'w' ) as handle : handle.write( content.to_csv( index = False ) )

		elif type == 'carrel' : 
			with open( cwd/RRAGCACHE/CACHEDCARREL, 'w' ) as handle : handle.write( content )

		elif type == 'query' : 
			with open( cwd/RRAGCACHE/CACHEDQUERY, 'w' ) as handle : handle.write( content )

		elif type == 'type' : 
			with open( cwd/RRAGCACHE/CACHEDTYPE, 'w' ) as handle : handle.write( content )


class Matcher : 

	def __init__( self ) : return( None )

	def match( self, carrel, query ) :
			
		# configure
		LIMIT    = 128
		TEMPLATE = "SELECT s.title AS titles, s.idx, s.sentence AS sentences, rank AS 'scores' FROM indx JOIN sentences s ON s.id = indx.rowid WHERE indx MATCH '##QUERY##' ORDER BY rank LIMIT ##LIMIT##"
		
		# initialize
		database   = configuration( LIBRARY )/carrel/ETC/DATABASE
		connection = connect( database )
				
		# build sql, search, and sort
		sql   = TEMPLATE.replace( '##QUERY##', query ).replace( '##LIMIT##', str( LIMIT ) )
		items = read_sql_query( sql, connection )
		items = items.sort_values( [ 'titles', 'idx' ] )

		# cache and done
		Cacher().cache( 'results', items)
		Cacher().cache( 'carrel', carrel )
		Cacher().cache( 'query', query )
		Cacher().cache( 'type', 'match' )
		return( items )


class Hybridizer : 

	def __init__( self ) : return( None )

	# hybrid; combined full text and semantic search
	def search( self, carrel, query ):
	
		# configure
		MODEL           = 'locusai/multi-qa-minilm-l6-cos-v1'
		LIBRARY         = 'localLibrary'
		SELECTFULLTEXT  = "SELECT  s.id, s.title, s.idx, s.sentence FROM indx JOIN sentences s ON s.id = indx.rowid WHERE indx MATCH ? ORDER BY rank LIMIT ?"
		SELECTSEMANTICS = "SELECT  s.id, s.title, s.idx, s.sentence, e.distance FROM (SELECT  sentence_id, distance FROM embeddings WHERE embedding MATCH ? ORDER BY distance LIMIT ?) e JOIN    sentences s ON s.id = e.sentence_id ORDER BY e.distance"
		DATABASE       = 'sentences.db'
		LIMIT          = 128
		RECALL         = 256
		K_RRF          = 60
		RELATIVE_DROP  = 0.20
		COLUMNS        = [ 'titles', 'idx', 'sentences', 'scores' ]
	
		# update
		self.query = query

		# initialize
		database = configuration( LIBRARY ) / carrel / ETC / DATABASE
	
		# connect and load the vec0 extension
		connection = connect( database )
		connection.enable_load_extension( True )
		vecload( connection )
	
		# full text search
		try :
			fts_results = connection.execute( SELECTFULLTEXT, [ query, RECALL ] ).fetchall()
		except Exception as e:
			stderr.write( f"  FTS5 search failed: {e}\n" )
			fts_results = []
	
		# vectorize the query
		try :
			query = embed( model=MODEL, input=query ).model_dump( mode='json' )[ 'embeddings' ][ 0 ]
			query = pack( "%sf" % len( query ), *query )
		except Exception as e : exit( f"Error generating embedding: {e}" )
	
		# semantic search
		knn_results = connection.execute( SELECTSEMANTICS, [ query, RECALL ] ).fetchall()
	
		# close
		connection.close()
	
		# create a list of all the sentences
		sentences = {}
		for row in knn_results:
			sid, title, idx, sentence, distance = row
			sentences[ sid ] = ( title, idx, sentence )
	
		for row in fts_results:
			sid, title, idx, sentence = row
			if sid not in sentences: sentences[ sid ] = ( title, idx, sentence )
	
		# accumulate RRF scores
		rrf_scores = {}
	
		for rank, row in enumerate( knn_results, 1 ):
			sid = row[ 0 ]
			rrf_scores[ sid ] = rrf_scores.get( sid, 0.0 ) + 1.0 / ( K_RRF + rank )
	
		for rank, row in enumerate( fts_results,1 ):
			sid = row[ 0 ]
			rrf_scores[ sid ] = rrf_scores.get( sid, 0.0 ) + 1.0 / ( K_RRF + rank )
	
		# determine which result sources contributed each ID
		knn_ids = set( row[ 0 ] for row in knn_results )
		fts_ids = set( row[ 0 ] for row in fts_results )
	
		# =============================================
		# Sort by fused score (descending), apply hard
		# limit, then apply relative elbow detection to
		# truncate at the point where scores drop off
		# by more than RELATIVE_DROP from the previous
		# result's score.
		# =============================================
		sorted_fused = sorted( rrf_scores.items(), key=lambda x: -x[ 1 ] )[ :LIMIT ]
	
		fused = []
		for i, ( sid, score ) in enumerate( sorted_fused ):
			if i == 0 : fused.append( ( sid, score ) )
			else:
				prev_score = sorted_fused[ i - 1 ][ 1 ]
				score_gap = prev_score - score
	
				# calculate relative drop as a fraction of the previous score
				if prev_score > 0 : relative_drop = score_gap / prev_score
				else              : relative_drop = 0
	
				if relative_drop > RELATIVE_DROP : break
	
				fused.append( ( sid, score ) )
	
		# =============================================
		# PART 4: Display results
		# =============================================
	
		if not fused: print( "No results found." )
		else:
		
			items = []
			for rank, ( sid, score ) in enumerate( fused, 1 ):
			
				title, idx, sentence = sentences[ sid ]
				items.append( [ title, idx, sentence, score ] )
				
			items = DataFrame( items, columns=COLUMNS )
			items = items.sort_values( [ 'titles', 'idx' ] )
	
			# cache and done
			Cacher().cache( 'results', items )
			Cacher().cache( 'carrel', carrel )
			Cacher().cache( 'query', self.query )
			Cacher().cache( 'type', 'hybrid' )
			return( items )


class Searcher :

    def __init__( self ) :
        self.query = None
        return( None )

    def search( self, carrel, query ) :

        # configure
        CANDIDATE_POOL = 200      # larger pool from vector DB for reranking
        TOP_K          = 64       # final results after reranking and filtering
        MIN_THRESHOLD  = 0.15     # absolute minimum cosine similarity (0–1 scale)
        CONTEXT_WINDOW = 1        # number of adjacent sentences to include on each side
        COLUMNS        = [ 'titles', 'idx', 'sentences', 'scores' ]

        # SQL: retrieve a candidate pool from vector search
        SELECT = (
            "SELECT s.id, s.title, s.idx, s.sentence, e.distance "
            "FROM (SELECT sentence_id, distance FROM embeddings "
            "      WHERE embedding MATCH ? AND k = ? "
            "      ORDER BY distance) e "
            "JOIN sentences s ON s.id = e.sentence_id"
        )

        # SQL: retrieve a specific sentence by title+idx (for context expansion)
        SELECT_CONTEXT = (
            "SELECT id, sentence FROM sentences "
            "WHERE title = ? AND idx = ?"
        )

        # update
        self.query = query

        # initialize database
        database = connect( library/carrel/ETC/DATABASE, check_same_thread=False )
        database.enable_load_extension( True )
        vecload( database )

        # --- 1. QUERY EXPANSION ---
        # Generate paraphrases using the LLM, then embed all variations
        expanded_queries = self._expand_query( query )

        # Embed the original query and all paraphrases
        all_queries = [ query ] + expanded_queries
        embeddings_list = []
        for q in all_queries:
            vec = embed( model=EMBEDDER, input=q ).model_dump( mode='json' )[ 'embeddings' ][ 0 ]
            embeddings_list.append( vec )

        # Average the embeddings to create a single enriched query vector
        query_vec = np.mean( embeddings_list, axis=0 ).tolist()

        # --- 2. VECTOR SEARCH (candidate pool) ---
        records = database.execute(
            SELECT, [ self.serialize( query_vec ), CANDIDATE_POOL ]
        ).fetchall()

        if not records:
            items = DataFrame( [], columns=COLUMNS )
            Cacher().cache( 'results', items )
            Cacher().cache( 'carrel', carrel )
            Cacher().cache( 'query', self.query )
            Cacher().cache( 'type', 'semantic' )
            return( items )

        # --- 3. RERANK IN PYTHON (exact cosine similarity) ---
        # sqlite-vec distance is an approximation; recompute exact similarity
        query_array = np.array( query_vec ).reshape( 1, -1 )

        items = []
        for record in records :
            sid      = record[ 0 ]
            title    = record[ 1 ]
            idx      = record[ 2 ]
            sentence = record[ 3 ]

            # Re-embed the retrieved sentence for exact comparison
            # (Alternatively, pre-store embeddings — but re-embedding is exact)
            sentence_vec = embed(
                model=EMBEDDER, input=sentence
            ).model_dump( mode='json' )[ 'embeddings' ][ 0 ]
            sentence_array = np.array( sentence_vec ).reshape( 1, -1 )

            # Cosine similarity (1.0 = identical, 0.0 = unrelated)
            similarity = cosine_similarity( query_array, sentence_array )[ 0 ][ 0 ]

            items.append( [ title, idx, sentence, similarity ] )

        # --- 4. ADAPTIVE SCORE CUTOFF ---
        # Sort by similarity descending
        items.sort( key=lambda x: x[ 3 ], reverse=True )

        # Find the natural drop-off point in the score distribution
        cutoff_idx = self._find_score_dropoff( items )

        # Apply both the adaptive cutoff and the absolute minimum threshold
        filtered = []
        for i, item in enumerate( items ):
            if i >= cutoff_idx and item[ 3 ] < MIN_THRESHOLD:
                break
            if item[ 3 ] < MIN_THRESHOLD:
                break
            filtered.append( item )

        # --- 5. DEDUPLICATE near-identical sentences ---
        filtered = self._deduplicate( filtered )

        # --- 6. CONTEXT EXPANSION ---
        # Include adjacent sentences to improve passage-level recall
        if CONTEXT_WINDOW > 0:
            filtered = self._expand_context(
                filtered, database, SELECT_CONTEXT, CONTEXT_WINDOW
            )

        # --- 7. FINAL TRIM AND SORT ---
        filtered = filtered[ :TOP_K ]
        items = DataFrame( filtered, columns=COLUMNS )
        items = items.sort_values( [ 'titles', 'idx' ] )

        # cache and done
        Cacher().cache( 'results', items )
        Cacher().cache( 'carrel', carrel )
        Cacher().cache( 'query', self.query )
        Cacher().cache( 'type', 'semantic' )
        return( items )


    def serialize( self, vector: List[float] ) -> bytes :
        '''Serialize a list of floats into a compact "raw bytes" format'''
        from struct import pack
        return pack( "%sf" % len( vector ), *vector )


    def _expand_query( self, query: str, n_paraphrases: int = 2 ) -> List[str]:
        '''Generate paraphrases of the query using the LLM to broaden semantic coverage.'''
        prompt = (
            f'Rephrase the following question in {n_paraphrases} different ways. '
            f'Each rephrasing should use different vocabulary but preserve the same meaning. '
            f'Output one rephrasing per line, nothing else.\n\nQuestion: {query}'
        )
        try:
            response = generate( model=LLM, prompt=prompt )
            lines = response[ 'response' ].strip().split( '\n' )
            # Clean up: remove numbering, extra whitespace, empty lines
            paraphrases = [
                line.strip().lstrip( '0123456789.-) ' )
                for line in lines
                if line.strip()
            ]
            return paraphrases[ :n_paraphrases ]
        except Exception:
            # If LLM fails, fall back to no expansion
            return []


    def _find_score_dropoff( self, items: List[list] ) -> int:
        '''
        Find the index where similarity scores naturally drop off.
        Uses the largest gap between consecutive scores as the cutoff.
        '''
        if len( items ) < 3:
            return len( items )

        scores = [ item[ 3 ] for item in items ]
        max_gap = 0
        cutoff_idx = len( items )

        for i in range( 1, len( scores ) ):
            gap = scores[ i - 1 ] - scores[ i ]
            if gap > max_gap:
                max_gap = gap
                cutoff_idx = i

        return cutoff_idx


    def _deduplicate(
        self, items: List[list], similarity_threshold: float = 0.85
    ) -> List[list]:
        '''Remove near-duplicate sentences using word-set overlap (Jaccard similarity).'''
        seen = []
        result = []
        for item in items:
            sentence = item[ 2 ].lower()
            is_dup = False
            for prev in seen:
                words_a = set( sentence.split() )
                words_b = set( prev.split() )
                if words_a and words_b:
                    overlap = len( words_a & words_b ) / len( words_a | words_b )
                    if overlap > similarity_threshold:
                        is_dup = True
                        break
            if not is_dup:
                seen.append( sentence )
                result.append( item )
        return result


    def _expand_context(
        self,
        items: List[list],
        database,
        select_context_sql: str,
        window: int
    ) -> List[list]:
        '''
        For each matched sentence, include adjacent sentences (by idx)
        to improve passage-level recall.
        '''
        expanded = []
        seen_ids = set()

        for item in items:
            title    = item[ 0 ]
            idx      = item[ 1 ]
            sentence = item[ 2 ]
            score    = item[ 3 ]

            # Try to parse idx as integer for arithmetic
            try:
                idx_int = int( idx )
            except ( ValueError, TypeError ):
                # If idx is not numeric, skip context expansion for this item
                expanded.append( item )
                continue

            # Add surrounding sentences
            for offset in range( -window, window + 1 ):
                adj_idx = idx_int + offset
                key = ( title, adj_idx )

                if key in seen_ids:
                    continue

                seen_ids.add( key )

                if offset == 0:
                    # Original matched sentence with its score
                    expanded.append( [ title, str( adj_idx ), sentence, score ] )
                else:
                    # Fetch adjacent sentence from database
                    row = database.execute(
                        select_context_sql, [ title, str( adj_idx ) ]
                    ).fetchone()
                    if row:
                        adj_sentence = row[ 1 ]
                        # Adjacent sentences get a decayed score
                        decayed_score = score * ( 1.0 / ( 1.0 + abs( offset ) ) )
                        expanded.append(
                            [ title, str( adj_idx ), adj_sentence, decayed_score ]
                        )

        return expanded


class Citations :

	def __init__( self ) : return( None )
	
	def to_sentences( self ) :
			
		# initialize; get the previously cached results
		items = Settings().get( 'results' )

		# create a list of sentences and done
		sentences = []
		for index, row in items.iterrows() : sentences.append( row[ 'sentences' ] )
		return( sentences )

			
	def to_citations( self, format ) :
					
		# initialize; get the previously cached results
		items  = Settings().get( 'results' )
		carrel = Settings().get( 'carrel' )
		
		# create a list of items sorted by the number of times they were cited
		items = items.groupby( [ 'titles' ], as_index=False )[ 'sentences' ].count()
		items = items.sort_values( 'sentences', ascending=False )
		items = [ row.tolist() for index, row in items.iterrows() ]	
				
		# process each item; transform the list of items into a list of pseudo-citations
		citations = []
		with open ( library/carrel/INDEXJSON ) as handle : bibliographics = load( handle )		
		for item in items :
		
			# parse
			id    = item[ 0 ]
			count = item[ 1 ]
						
			# loop through all bhe bibliogrpahics; ought to be a dictionary, not a list
			for bibliographic in bibliographics :
				
				# match
				if str( bibliographic[ 'id' ] ) == str( id ) :
					
					# parse, update, and break
					author    = bibliographic[ 'author' ]
					title     = bibliographic[ 'title' ]
					date      = bibliographic[ 'date' ]
					summary   = bibliographic[ 'summary' ]
					keywords  = bibliographic[ 'keywords' ]
					extension = bibliographic[ 'extension' ]
					citations.append( { 'id':id, 'author':author, 'title': title, 'date':date, 'summary':summary, 'keywords':keywords, 'extension':extension, 'count':count } )
					break
					
		# convert to a data frame
		citations = DataFrame( citations )
		
		# branch and done
		if   format == 'json' : return( citations.to_json( orient='records' ) )
		elif format == 'tsv'  : return( citations.to_csv( sep='\t', header=False, index=False ) )
		elif format == 'csv'  : return( citations.to_csv( index=False ) )


class Reformatter :

	def __init__( self ) : return( None )

	def reformat( self ) :

		# configure
		PSIZE = 16
		ORDER = 2
		
		# read the cache
		sentences = Citations().to_sentences()
				
		# vectorize and activate similaritites; for longer sentences increase the value of PSIZE
		try : embeddings = embed( model=EMBEDDER, input=sentences ).model_dump( mode='json' )[ 'embeddings' ]
		except Exception as e:
			exit( f"Error creating embeddings: {str(e)}" )
		
		# try to compute similarities
		try               : similarities = self.activate_similarities( cosine_similarity(embeddings), p_size=PSIZE )
		except ValueError : return( None )
			
		# compute minmimas
		minmimas = argrelextrema( similarities, np.less, order=ORDER )
			
		# Get the order number of the sentences which are in splitting points
		splits = [ minmima for minmima in minmimas[ 0 ] ]
			
		# build result
		text = ''
		for index, sentence in enumerate( sentences ) :
		
			# check if sentence is a minima (splitting point)
			if index in splits : text += f'\n\n{sentence} '
			else               : text += f'{sentence} '
	
		# done
		return( text )
		
		
	def activate_similarities( self, similarities:np.array, p_size=10 )->np.array :
		''''Don't really understand what this function does'''
	
		# To create weights for sigmoid function we first have to create space. P_size will determine number of sentences used and the size of weights vector.
		x = np.linspace( -10, 10, p_size )
	
		# Then we need to apply activation function to the created space
		y = np.vectorize(self.rev_sigmoid) 
	
		# Because we only apply activation to p_size number of sentences we have to add zeros to neglect the effect of every additional sentence and to match the length ofvector we will multiply
		activation_weights = np.pad(y(x),(0,similarities.shape[0]-p_size))
	
		# Take each diagonal to the right of the main diagonal
		diagonals = [similarities.diagonal(each) for each in range(0,similarities.shape[0])]
	
		# Pad each diagonal by zeros at the end. Because each diagonal is different length we should pad it with zeros at the end
		diagonals = [np.pad(each, (0,similarities.shape[0]-len(each))) for each in diagonals]
	
		# Stack those diagonals into new matrix
		diagonals = np.stack(diagonals)
	
		# Apply activation weights to each row. Multiply similarities with our activation.
		diagonals = diagonals * activation_weights.reshape(-1,1)
	
		# Calculate the weighted sum of activated similarities
		activated_similarities = np.sum(diagonals, axis=0)
	
		# done
		return( activated_similarities )

	def rev_sigmoid( self, x:float )->float :
		''''Don't understand what this function does'''
		return ( 1 / ( 1 + exp( 0.5*x ) ) )


