# Autovacuum Failures and it's Resolution

* Note: Including end to end testing , scripts checked into the Repo and monitoring queries also demonstrated below. I'd also recommend to check OS level utilizations like Memory and CPU while I work through causation and resolution for autovacuum, additional to the below steps. Out of the monitoring tools I have used in past , I chose pgadmin to Query the database status for this instance. However, pganalyze, PRTG , grafana and prometheus can give me an historic insight for the table dba_sanchit.test2 in terms of it's DML activities, Resource utilizations. 

# Create the necessary Schema
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
```

# Calling the script load-data.py to load mock data into the table, and Stress the Autovacuum Process.
       -- Add Updates/Deletes to overwhelm the autovacuum. Autovacuum gets triggered due to the necessity of cleaning up the Bloat/dead tuples based on the autovacuum_analyze_scale_factor or autovacuum_vacuum_scale_factor.
       -- I monitored that looking into the dead tuples and other stats into the pg_stat_user_tables.
           Output from pg_stat_activity table:
```

-- Loading initial data into this postgres DB
sanchitshah@Sanchits-MacBook-Pro autovacuum % python3 load-data.py 
Table: test2, Dead Tuples: 0, Last Autovacuum: 2025-02-07 00:38:14.318330+00:00
Table: test2, Dead Tuples: 0, Last Autovacuum: 2025-02-07 00:38:14.318330+00:00


-- View of the Database
postgres=# select pid,wait_event, wait_event_type,now() - query_start, query from pg_stat_activity where state='active';
-[ RECORD 1 ]---+--------------------------------------------------------------------------------------------------------------
pid             | 885
wait_event      | 
wait_event_type | 
?column?        | 00:00:00
query           | select pid,wait_event, wait_event_type,now() - query_start, query from pg_stat_activity where state='active';
-[ RECORD 2 ]---+--------------------------------------------------------------------------------------------------------------
pid             | 945
wait_event      | VacuumDelay
wait_event_type | Timeout
?column?        | 00:02:38.288354
query           | autovacuum: VACUUM ANALYZE dba_sanchit.test2

-- Parallely when the Load-data script continues to Update more records.
postgres=# select pid,wait_event, wait_event_type,now() - query_start, query from pg_stat_activity where state='active';
-[ RECORD 1 ]---+--------------------------------------------------------------------------------------------------------------
pid             | 885
wait_event      | 
wait_event_type | 
?column?        | 00:00:00
query           | select pid,wait_event, wait_event_type,now() - query_start, query from pg_stat_activity where state='active';
-[ RECORD 2 ]---+--------------------------------------------------------------------------------------------------------------
pid             | 938
wait_event      | DataFileRead
wait_event_type | IO
?column?        | 00:00:05.507834
query           |                                                                                                              +
                |         UPDATE dba_sanchit.test2                                                                             +
                |         SET address = 'r3jr243fnoiwe3fc9843we84iu43rtnkj34jbhtbjh43hjbtb34jbtbjh43jht34'                     +
                |         WHERE id % 10 = 0

-- Stressing the Database which shows the autovacuum is running but not able to keep up to reduce the Table Bloat for dba_sanchit.test2 table.

postgres=# select * from pg_stat_user_tables where relname = 'test2';
-[ RECORD 1 ]-------+------------------------------
relid               | 16457
schemaname          | dba_sanchit
relname             | test2
seq_scan            | 179
last_seq_scan       | 2025-02-07 00:18:56.934704+00
seq_tup_read        | 3384000000
idx_scan            | 0
last_idx_scan       | 
idx_tup_fetch       | 0
n_tup_ins           | 20000000
n_tup_upd           | 90000000
n_tup_del           | 1000000
n_tup_hot_upd       | 44109233
n_tup_newpage_upd   | 45890767
n_live_tup          | 18784945
n_dead_tup          | 38444612
n_mod_since_analyze | 15000000
n_ins_since_vacuum  | 0
last_vacuum         | 
last_autovacuum     | 2025-02-07 00:16:18.468271+00
last_analyze        | 
last_autoanalyze    | 2025-02-07 00:16:20.21195+00
vacuum_count        | 0
autovacuum_count    | 3
analyze_count       | 0
autoanalyze_count   | 3

postgres=# select now();
-[ RECORD 1 ]----------------------
now | 2025-02-07 00:19:20.068404+00


postgres=# select pid,wait_event, wait_event_type,now() - query_start, query from pg_stat_activity where state='active';
-[ RECORD 1 ]---+--------------------------------------------------------------------------------------------------------------
pid             | 885
wait_event      | 
wait_event_type | 
?column?        | 00:00:00
query           | select pid,wait_event, wait_event_type,now() - query_start, query from pg_stat_activity where state='active';
-[ RECORD 2 ]---+--------------------------------------------------------------------------------------------------------------
pid             | 938
wait_event      | WALWriteLock
wait_event_type | LWLock
?column?        | 00:00:05.224525
query           |                                                                                                              +
                |         UPDATE dba_sanchit.test2                                                                             +
                |         SET address = 'r3jr243fnoiwe3fc9843we84iu43rtnkj34jbhtbjh43hjbtb34jbtbjh43jht34'                     +
                |         WHERE id % 10 = 0
-[ RECORD 3 ]---+--------------------------------------------------------------------------------------------------------------
pid             | 977
wait_event      | WalWrite
wait_event_type | IO
?column?        | 00:00:44.346847
query           | autovacuum: VACUUM ANALYZE dba_sanchit.test2

-- Reissuing
postgres=# select pid,wait_event, wait_event_type,now() - query_start, query from pg_stat_activity where state='active';
-[ RECORD 1 ]---+--------------------------------------------------------------------------------------------------------------
pid             | 885
wait_event      | 
wait_event_type | 
?column?        | 00:00:00
query           | select pid,wait_event, wait_event_type,now() - query_start, query from pg_stat_activity where state='active';
-[ RECORD 2 ]---+--------------------------------------------------------------------------------------------------------------
pid             | 938
wait_event      | DataFileRead
wait_event_type | IO
?column?        | 00:00:06.333736
query           |                                                                                                              +
                |         UPDATE dba_sanchit.test2                                                                             +
                |         SET address = 'r3jr243fnoiwe3fc9843we84iu43rtnkj34jbhtbjh43hjbtb34jbtbjh43jht34'                     +
                |         WHERE id % 10 = 0
-[ RECORD 3 ]---+--------------------------------------------------------------------------------------------------------------
pid             | 977
wait_event      | WalSync
wait_event_type | IO
?column?        | 00:01:08.798002
query           | autovacuum: VACUUM ANALYZE dba_sanchit.test2


```

# Review the Current Database Config - To Reconfigure postgres parameters to resolve the problem. 

Current Configs:
```
postgres=# select name, setting from pg_settings where name ilike '%autovacuum%';
                 name                  |  setting  
---------------------------------------+-----------
 autovacuum                            | on
 autovacuum_analyze_scale_factor       | 0.1
 autovacuum_analyze_threshold          | 50
 autovacuum_freeze_max_age             | 200000000
 autovacuum_max_workers                | 3
 autovacuum_multixact_freeze_max_age   | 400000000
 autovacuum_naptime                    | 60
 autovacuum_vacuum_cost_delay          | 2
 autovacuum_vacuum_cost_limit          | -1
 autovacuum_vacuum_insert_scale_factor | 0.2
 autovacuum_vacuum_insert_threshold    | 1000
 autovacuum_vacuum_scale_factor        | 0.2
 autovacuum_vacuum_threshold           | 50
 autovacuum_work_mem                   | -1
 log_autovacuum_min_duration           | 600000
(15 rows)

postgres=# select name, setting from pg_settings where name ilike '%work_mem%';
           name            | setting 
---------------------------+---------
 autovacuum_work_mem       | -1
 logical_decoding_work_mem | 65536
 maintenance_work_mem      | 65536
 work_mem                  | 4096
(4 rows)

postgres=# select name, setting from pg_settings where name ilike '%shared_buffers%';
      name      | setting 
----------------+---------
 shared_buffers | 16384
(1 row)

postgres=# select name, setting from pg_settings where name ilike '%workers%';
                    name                     | setting 
---------------------------------------------+---------
 autovacuum_max_workers                      | 3
 max_logical_replication_workers             | 4
 max_parallel_apply_workers_per_subscription | 2
 max_parallel_maintenance_workers            | 2
 max_parallel_workers                        | 8
 max_parallel_workers_per_gather             | 2
 max_sync_workers_per_subscription           | 2
(7 rows)


```

Modifying Configs: 
```
postgres=# ALTER table dba_sanchit.test2 set ( autovacuum_vacuum_scale_factor = 0.01, autovacuum_analyze_scale_factor = 0.01 , autovacuum_vacuum_cost_delay=0,autovacuum_vacuum_cost_limit=2000); 
ALTER TABLE

```

-- After modifying respective params, the autovacuum speed up the Cleaning of the rows, dead-tuples went down from 38M to 715K in just a matter of 2 seconds which was picked immediately. 
```
postgres=# select * from pg_stat_user_tables where relname = 'test2';
-[ RECORD 1 ]-------+------------------------------
relid               | 16457
schemaname          | dba_sanchit
relname             | test2
seq_scan            | 239
last_seq_scan       | 2025-02-07 00:29:15.86102+00
seq_tup_read        | 4524000000
idx_scan            | 0
last_idx_scan       | 
idx_tup_fetch       | 0
n_tup_ins           | 20000000
n_tup_upd           | 120000000
n_tup_del           | 1000000
n_tup_hot_upd       | 44977355
n_tup_newpage_upd   | 75022645
n_live_tup          | 18983380
n_dead_tup          | 715125
n_mod_since_analyze | 0
n_ins_since_vacuum  | 0
last_vacuum         | 
last_autovacuum     | 2025-02-07 00:29:32.2824+00
last_analyze        | 
last_autoanalyze    | 2025-02-07 00:29:33.409566+00
vacuum_count        | 0
autovacuum_count    | 5
analyze_count       | 0
autoanalyze_count   | 5

postgres=# 

-- After 10 mins to verify if the autovacuum is keeping up

postgres=# select * from pg_stat_user_tables where relname = 'test2';
-[ RECORD 1 ]-------+------------------------------
relid               | 16457
schemaname          | dba_sanchit
relname             | test2
seq_scan            | 263
last_seq_scan       | 2025-02-07 00:35:39.876457+00
seq_tup_read        | 4980000000
idx_scan            | 0
last_idx_scan       | 
idx_tup_fetch       | 0
n_tup_ins           | 35862461
n_tup_upd           | 132000000
n_tup_del           | 1000000
n_tup_hot_upd       | 45768216
n_tup_newpage_upd   | 86231784
n_live_tup          | 40830587
n_dead_tup          | 0
n_mod_since_analyze | 10000000
n_ins_since_vacuum  | 10000000
last_vacuum         | 
last_autovacuum     | 2025-02-07 00:36:26.32304+00
last_analyze        | 
last_autoanalyze    | 2025-02-07 00:35:23.118753+00
vacuum_count        | 0
autovacuum_count    | 12
analyze_count       | 0
autoanalyze_count   | 11

```

# Simultaneously, connected pgdmin to the local Postgres Database server for monitoring Queries 
![Screenshot 2025-02-06 at 5 06 39 PM](https://github.com/user-attachments/assets/1474bd8d-130a-4894-af74-8053e4e3dbed)


