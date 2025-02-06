# Autovacuum Failures and it's Resolution

# Create the necessary Schema, and load initial data into the table. 
```
postgres@b702cd26cd8b:/$ psql 
psql (17.2 (Debian 17.2-1.pgdg120+1))
Type "help" for help.

postgres=# \dn
      List of schemas
  Name  |       Owner       
--------+-------------------
 public | pg_database_owner
(1 row)

postgres=# create schema dba_sanchit; 
CREATE SCHEMA

-- Create the table and load initial data. 
postgres=# create table dba_sanchit.test(id bigint, name varchar(255), address text ); 
CREATE TABLE

postgres=# insert into dba_sanchit.test select g as id, md5(random()::text) as name, md5(random()::text) as address from generate_series(1,1000000)g;
INSERT 0 1000000
postgres=# \dt+ dba_sanchit.test 
                                     List of relations
   Schema    | Name | Type  |  Owner   | Persistence | Access method |  Size  | Description 
-------------+------+-------+----------+-------------+---------------+--------+-------------
 dba_sanchit | test | table | postgres | permanent   | heap          | 104 MB | 
(1 row)

-- Add Updates/Deletes to overwhelm the autovacuum. Autovacuum gets triggered due to the necessity of cleaning up the Bloat/dead tuples based on the autovacuum_analyze_scale_factor or autovacuum_vacuum_scale_factor. I monitored that looking into the dead tuples and other stats into the pg_stat_user_tables.

