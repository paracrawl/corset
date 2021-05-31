
CREATE SCHEMA dpdb;

CREATE TABLE dpdb.users(
    id serial PRIMARY KEY,
    social_id varchar (200) UNIQUE NOT NULL,    
    name varchar (200) NOT NULL,
    email varchar (200) UNIQUE NOT NULL,
    avatar varchar (200),
    creation_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_admin boolean NOT NULL DEFAULT FALSE,
    is_active boolean NOT NULL DEFAULT TRUE
    );
    
CREATE TABLE dpdb.langs(
    id serial PRIMARY KEY,
    lang_code varchar(5) UNIQUE NOT NULL,
    name varchar (200) NOT NULL,
    is_active boolean NOT NULL DEFAULT TRUE
    );    
  
CREATE TABLE dpdb.tags(
    id serial PRIMARY KEY,
    tag varchar(50) UNIQUE NOT NULL,
    is_active boolean NOT NULL DEFAULT TRUE
    );
 
CREATE TABLE dpdb.status(
    id serial PRIMARY KEY,
    status varchar(50) UNIQUE NOT NULL,
    is_active boolean NOT NULL DEFAULT TRUE
    );
 
CREATE TABLE dpdb.langformats(
    id serial PRIMARY KEY,
    lang_format varchar(50) UNIQUE NOT NULL,
    is_active boolean NOT NULL DEFAULT TRUE
    );
    
CREATE TABLE dpdb.fileformats(
    id serial PRIMARY KEY,
    file_format varchar(50) UNIQUE NOT NULL,
    is_active boolean NOT NULL DEFAULT TRUE
    );        
 
CREATE TABLE dpdb.basecorpora(
    id serial PRIMARY KEY,
    name varchar(200) UNIQUE NOT NULL,
    description varchar(1000),
    source_lang integer NOT NULL REFERENCES dpdb.langs(id),
    target_lang integer NOT NULL REFERENCES dpdb.langs(id),
    sentences integer NOT NULL DEFAULT 0,
    size_mb integer NOT NULL DEFAULT 0,
    solr_collection varchar(500) NOT NULL,
    is_active boolean NOT NULL DEFAULT TRUE,
    is_highlight boolean NOT NULL DEFAULT FALSE 
    );

CREATE TABLE dpdb.querycorpora(
    id serial PRIMARY KEY,
    file_format integer NOT NULL REFERENCES dpdb.fileformats(id),
    lang_format integer NOT NULL REFERENCES dpdb.langformats(id),
    source_lang integer NOT NULL REFERENCES dpdb.langs(id),
    target_lang integer REFERENCES dpdb.langs(id),
    sentences integer NOT NULL DEFAULT 0,
    size_mb integer NOT NULL DEFAULT 0,
    location varchar(1000) NOT NULL,
    is_active boolean NOT NULL DEFAULT TRUE
    );


CREATE TABLE dpdb.customcorpora(
    id serial PRIMARY KEY,
    name varchar(200) NOT NULL,
    description varchar(1000),
    file_format integer NOT NULL REFERENCES dpdb.fileformats(id),
    source_lang integer NOT NULL REFERENCES dpdb.langs(id),
    target_lang integer NOT NULL REFERENCES dpdb.langs(id),
    sentences integer NOT NULL DEFAULT 0,
    size_mb integer NOT NULL DEFAULT 0,
    location varchar(1000) NOT NULL,
    solr_collection varchar(500) NOT NULL,
    solr_prefix varchar(100) NOT NULL,
    topics  INT[],
    last_download timestamp,
    num_downloads integer NOT NULL DEFAULT 0,
    is_private boolean NOT NULL DEFAULT TRUE,
    is_active boolean NOT NULL DEFAULT TRUE ,
    is_highlight boolean NOT NULL DEFAULT FALSE ,
    creation_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

CREATE TABLE dpdb.queryrequests(
    id serial PRIMARY KEY,
    owner integer NOT NULL REFERENCES dpdb.users(id),
    name varchar(200) NOT NULL,
    creation_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    base_corpus integer NOT NULL REFERENCES dpdb.basecorpora(id),
    query_corpus integer NOT NULL REFERENCES dpdb.querycorpora(id),
    custom_corpus integer  REFERENCES dpdb.customcorpora(id),
    job varchar(200) UNIQUE NOT NULL,
    status integer NOT NULL REFERENCES dpdb.status(id)
    );

CREATE TABLE dpdb.searchrequests(
    id serial PRIMARY KEY,
    owner integer NOT NULL REFERENCES dpdb.users(id),
    creation_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    base_corpus integer REFERENCES dpdb.basecorpora(id) DEFAULT NULL,
    custom_corpus integer REFERENCES dpdb.customcorpora(id) DEFAULT NULL,
    search_lang integer NOT NULL REFERENCES dpdb.langs(id),
    search_field varchar (50) NOT NULL,
    search_term varchar (200) NOT NULL,
    search_type varchar (50) NOT NULL
    );
    
CREATE UNIQUE INDEX unique_base_search_key ON dpdb.searchrequests (owner, base_corpus, search_lang, search_field, search_term) WHERE custom_corpus IS NULL;
CREATE UNIQUE INDEX unique_custom_search_key  ON dpdb.searchrequests  (owner, custom_corpus, search_lang, search_field, search_term) WHERE base_corpus IS NULL;
    
INSERT INTO dpdb.langs (lang_code, name, is_active) VALUES
    ('en', 'English', 't'),
    ('bg', 'Bulgarian', 'f'),
    ('ca', 'Catalan', 'f'),
    ('cs', 'Czech', 'f'),
    ('da', 'Danish', 'f'),
    ('de', 'German', 't'),    
    ('el', 'Greek', 'f'),
    ('es', 'Spanish', 't'),
    ('et', 'Estonian', 'f'),
    ('eu', 'Basque', 'f'),
    ('fi', 'Finnish', 'f'),
    ('fr', 'French', 't'),
    ('ga', 'Irish', 'f'),
    ('gl', 'Galician', 'f'),
    ('hr', 'Croatian', 'f'),
    ('hu', 'Hungarian', 'f'),
    ('is', 'Icelandic', 'f'),
    ('it', 'Italian', 't'),
    ('lt', 'Lithuanian', 'f'),
    ('lv', 'Latvian', 'f'),
    ('mt', 'Maltese', 'f'),
    ('nb', 'Norwegian (Bokmål)', 'f'),
    ('nl', 'Dutch', 't'),
    ('nn', 'Norwegian (Nynorsk)', 'f'),
    ('no', 'Norwegian','f'),
    ('pl', 'Polish', 'f'),
    ('pt', 'Portuguese', 't'),
    ('ro', 'Romanian', 'f'),
    ('ru', 'Russian','f'),
    ('sk', 'Slovak', 'f'),
    ('sl', 'Slovenian', 'f'),
    ('sv', 'Swedish', 'f');

    
INSERT INTO dpdb.status(status) VALUES
    ('FAILURE'),
    ('PENDING'),
    ('RETRY'),
    ('STARTED'),
    ('SUCCESS');

INSERT INTO dpdb.langformats (lang_format) VALUES
    ('mono'),
    ('parallel');
    
INSERT INTO dpdb.fileformats (file_format) VALUES
    ('tsv'),
    ('tmx');
    
INSERT INTO dpdb.tags (tag) VALUES
    ('General'),
    ('Technical'),
    ('Legal'),
    ('Financial'),
    ('Medical'),
    ('Religion'),
    ('Politics'),
    ('Administrative'),
    ('Subtitles'),
    ('Patents'),
    ('News'),
    ('Books'),
    ('Talks'),
    ('Other');

--INSERT INTO dpdb.basecorpora (name, description, source_lang, target_lang, sentences, size_mb, solr_collection, is_highlight) VALUES
--    ('Paracrawl EN-ES', 'English-Spanish ParaCrawl Corpus release v7.1', 1, 8, 23944238, 3075, 'paracrawl-en-es', 't'),
--    ('Paracrawl EN-PT', 'English-Portuguese ParaCrawl Corpus release v7.1', 1, 27, 10908656, 1384, 'paracrawl-en-pt', 't'),
--    ('Paracrawl EN-DE', 'English-German ParaCrawl Corpus release v7.1', 1, 6, 28198207, 3874, 'paracrawl-en-de', 't'),
--    ('Paracrawl EN-FR', 'English-French ParaCrawl Corpus release v7.1', 1, 12, 31947091, 4268, 'paracrawl-en-fr', 't'),
--    ('Paracrawl EN-NL', 'English-Dutch ParaCrawl Corpus release v7.1', 1, 23, 9321114, 1168, 'paracrawl-en-nl', 't'),
--    ('Paracrawl EN-IT', 'English-Italian ParaCrawl Corpus release v7.1', 1, 18, 13622365, 1745, 'paracrawl-en-it', 't');