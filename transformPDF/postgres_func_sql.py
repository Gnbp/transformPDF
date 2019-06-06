INSERT_SQL_PDF = """ 
CREATE OR REPLACE FUNCTION pdf_insert_function (
    pdf_table_name varchar,
    pfeildname text[],
    f_name varchar,
    f_dir varchar,
    f_type varchar,
    t_uname varchar,
    c_name varchar,
    t_name varchar,
    s_time numeric,
    c_time numeric,
    c_type boolean,
    r_mark1 varchar,
    r_mark2 varchar,
    origin_table_name varchar DEFAULT '',
    ofeildame text[] DEFAULT '{ }',
    of_name varchar DEFAULT '',
    of_dir varchar DEFAULT '',
    o_names text DEFAULT '',
    o_md5s text DEFAULT '',
    o_size text DEFAULT '',
    oallsize numeric DEFAULT 0,
    o_remark1 text DEFAULT ''
    ) RETURNS VOID AS $$
DECLARE
    pdf_sql text;
    origin_sql text;
BEGIN
    IF origin_table_name <> '' THEN
    origin_sql:=origin_insert_function($14,$15,$16,$17,$18,$19,$20,$21,$22);
    END IF;
    pdf_sql:='INSERT INTO '
        ||quote_ident(pdf_table_name)
        ||'('
        ||array_to_string(pfeildname,',')
        ||') values('
        ||f_name ||','
        ||f_dir  ||','
        ||f_type ||','
        ||t_uname||','
        ||c_name ||','
        ||t_name ||',to_timestamp('
        ||s_time ||'),to_timestamp('
        ||c_time ||'),'
        ||c_type ||','
        ||r_mark1||','
        ||r_mark2
        ||')';
    execute pdf_sql;
    
END;
$$ language plpgsql;
"""


INSERT_SQL_ORIGIN = """ 
CREATE OR REPLACE FUNCTION origin_insert_function (
    origintablename varchar,
    originfieldname text[],
    ofa_name varchar,
    ofa_dir varchar,
    origin_names text,
    origin_md5s text,
    origin_size text,
    oallsizes numeric,
    origin_remark text
    ) RETURNS VOID AS $$
DECLARE
    ex_sql text;
BEGIN
    ex_sql:='INSERT INTO '
        ||quote_ident(origintablename)
        ||'('
        ||array_to_string(originfieldname,',')
        ||') values('
        ||ofa_name    ||','
        ||ofa_dir     ||','
        ||origin_names||','
        ||origin_md5s ||','
        ||origin_size ||','
        ||oallsizes   ||','
        ||origin_remark
        ||')';
    execute ex_sql;
    
END;
$$ language plpgsql;
"""


UPDATE_SQL_PDF = """ 
CREATE OR REPLACE FUNCTION pdf_update_function (
    pdf_table_name varchar,
    pfeildname text[],
    f_name varchar,
    f_dir varchar,
    f_type varchar,
    t_uname varchar,
    c_name varchar,
    t_name varchar,
    s_time numeric,
    c_time numeric,
    c_type boolean,
    r_mark1 varchar,
    r_mark2 varchar,
    origin_table_name varchar DEFAULT '',
    ofeildame text[] DEFAULT '{ }',
    of_name varchar DEFAULT '',
    of_dir varchar DEFAULT '',
    o_names text DEFAULT '',
    o_md5s text DEFAULT '',
    o_size text DEFAULT '',
    oallsize numeric DEFAULT 0,
    o_remark1 text DEFAULT ''
    ) RETURNS VOID AS $$
DECLARE
    update_sql text;
    origin_sql text;
BEGIN
    IF origin_table_name <> '' THEN
    origin_sql:=origin_insert_function($14,$15,$16,$17,$18,$19,$20,$21,$22);
    END IF;
    update_sql:='UPDATE '
        ||quote_ident(pdf_table_name)
        ||' SET complete_type='||c_type||',copy_name='||c_name||',target_name='||t_name||',start_time=to_timestamp('||s_time ||'),complete_time=to_timestamp('||c_time||') WHERE file_name='
        ||f_name;
    execute update_sql;
END;
$$ language plpgsql;
"""

FILE_OBJ_EXIST = """ 
CREATE OR REPLACE FUNCTION query_obj_exist (
    objtablename varchar,
    objfieldname varchar,
    obj_dir varchar,
    obj_type varchar,
    out obj_complete_type boolean
    ) AS $$
DECLARE
    ex_sql text;
BEGIN
    ex_sql:='SELECT '
        ||objfieldname||' FROM '
        ||quote_ident(objtablename)
        ||' WHERE file_dir='
        ||obj_dir     ||'AND file_type='
        ||obj_type;
    execute ex_sql into obj_complete_type ;
    
END;
$$ language plpgsql;
"""
DROP_INSERT_FUNCTION_SQL = "DROP function if exists pdf_insert_function(varchar,text[],varchar,varchar,varchar,varchar,varchar,varchar,numeric,numeric,boolean,varchar,varchar,varchar,text[],varchar,varchar,text,text,text,numeric,text)"
DROP_ORIGIN_FUNCTION_SQL = "DROP function if exists origin_insert_function(varchar,text[],varchar,varchar,text,text,text,numeric,text)"
DROP_UPDATE_FUNCTION_SQL = "DROP function if exists pdf_update_function(varchar,text[],varchar,varchar,varchar,varchar,varchar,varchar,numeric,numeric,boolean,varchar,varchar,varchar,text[],varchar,varchar,text,text,text,numeric,text)"
DROP_EXIST_FUNCTION_SQL = "DROP function if exists query_obj_exist(varchar,varchar,varchar,varchar)"