from settings import DATABASE_NAME, TABLE_PDF_ZIP, TABLE_PDF_ORIGIN, TABLE_ALL_ORIGIN

DB_NAME = """
CREATE DATABASE {};
""".format(DATABASE_NAME)

DB_NAME_EXIST = """
select * from pg_database where datname='{}';
""".format(DATABASE_NAME)

PDF_SEQ = """
CREATE SEQUENCE if not exists pdf_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 99999999
    CACHE 1;

ALTER SEQUENCE pdf_id_seq OWNER TO postgres;
"""

ORIGIN_SEQ = """
CREATE SEQUENCE if not exists origin_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 99999999
    CACHE 1;

ALTER SEQUENCE origin_id_seq OWNER TO postgres;
"""

ALL_SEQ = """
CREATE SEQUENCE if not exists all_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 99999999
    CACHE 1;

ALTER SEQUENCE all_id_seq OWNER TO postgres;
"""

PDF_ZIP_TABLE = """
CREATE TABLE if not exists {}
(
   	id int NOT NULL,
	file_name varchar NOT NULL, 
	file_dir varchar NOT NULL,
	file_type varchar(5) NOT NULL,
	copy_name varchar NOT NULL,
	target_name varchar NOT NULL,
	target_username varchar NOT NULL,
	start_time timestamp without time zone NOT NULL,
	complete_time timestamp without time zone NOT NULL,
	complete_type boolean NOT NULL,
	remark1 varchar,
	remark2 varchar,
    	PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
);

ALTER TABLE {} OWNER to postgres;
ALTER TABLE {} ALTER column id SET DEFAULT nextval('pdf_id_seq');	
""".format(TABLE_PDF_ZIP, TABLE_PDF_ZIP, TABLE_PDF_ZIP)

PDF_ORIGIN_FILES = """
CREATE TABLE if not exists {}
(
   	id int NOT NULL,
	f_name varchar NOT NULL,
	file_dir varchar NOT NULL,
	s_files_name text NOT NULL, 
	s_files_md5 text NOT NULL,
	s_files_size text NOT NULL,
	s_files_totalsize int,
	remark1 varchar,
	remark2 varchar,
    	PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
);

ALTER TABLE {} OWNER to postgres;
ALTER TABLE {} ALTER column id SET DEFAULT nextval('origin_id_seq');
""".format(TABLE_PDF_ORIGIN, TABLE_PDF_ORIGIN, TABLE_PDF_ORIGIN)

ALL_ORIGIN_FILES = """
CREATE TABLE if not exists {}
(
   	id int NOT NULL,
	f_name varchar NOT NULL,
	file_dir varchar NOT NULL,
	s_files_name text NOT NULL, 
	s_files_md5 text NOT NULL,
	s_files_size text NOT NULL,
	s_files_totalsize int,
	remark1 varchar,
	remark2 varchar,
    	PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
);

ALTER TABLE {} OWNER to postgres;
ALTER TABLE {} ALTER column id SET DEFAULT nextval('all_id_seq');
""".format(TABLE_ALL_ORIGIN, TABLE_ALL_ORIGIN, TABLE_ALL_ORIGIN)

