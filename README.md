# mongodb-zabbix-templates

## Zabbix templates for mongodb monitoring

The main monitoring tasks for us:

1. Watch and notify the support team if mongodb instances is not running or not reachable
2. Watch a basic mongodb and mongos opcounters
3. Watch and notify for Mongodb cluster health: mongos instances, Replicasets health
4. Watch DiskIO counters - it runs well with outstanding third party Iostat-Disk-Utilization-Template (https://github.com/lesovsky/zabbix-extensions/tree/master/files/iostat)
5. Provide easy-to-use and easy-to-understand cluster performance view for staff.

Technically, for fine mongodb performance tuning you need much more information than provides this templates, but its harder to 
collect, store and visualize with Zabbix, and anyway it would be better to use specially designed mongodb tools. 
Google it for more information.

This package contains 3 templates for monitoring mongodb instances (Mongo-DB template), mongos instance (Mongos template) and replicaset health (Mongo-RS Health template).
By customising your hosts configurations with this templates you can monitor lagre mongodb clusters. For us it monitors 12 mongodb servers in sharded 6 big replicasets, 4 instances of small metadata database, config database replicaset, 5 mongos routers and backup server.

## How to install Mongo-DB template

Mongo-DB template is used to collect the basic mongodb server opcounters and notify if the instance is gone.

Server requirements:
Ubuntu 14.04, 16.04 and 18.04 (tested, but should work on any linux, Centos/RHEL 6, 7, Ubuntu 12.04 etc.)
Zabbix server 2.4 - 4.0 (tested, but should work with any Zabbix 2.x)
Latest mongodb-org-tools and mongodb-org-shell linux packages installed (tested with all modern versions of mongodb 3.2, 3.4, 3.6, 4.0)

1. Downoad package from github.
2. Import xml templates to Zabbix server via browser
Configuration -> Templates -> Import template
3. Upload \*.py files to zabbix server, put it to external scrips folder (/usr/lib/zabbix/externalscrips for my server), and
chmod +x mongo\*.py
4. Install on zabbix server required python modules via command line
<pre><code>
sudo pip install pymongo
sudo pip install py-zabbix
</code></pre>
5. Navigate to hosts configuration in zabbix server and add Mongo-DB template to host with mongodb instance.
6. In Macros tab add the following data
<pre><code>
{$MONGODB_HOSTNAME}  IP or DNS name of interface used by mongodb instance
{$MONGODB_USER}  User name
{$MONGODB_PASS}  Password
{$MONGODB_PORT}  Port used by mongodb instance
{$MONGODB_ZABBIX_NAME}  Server hostname, as it registered in zabbix (I use two different interfaces for each mongodb server, mongodb instance is using one, other services including zabbix agent - another).
</code></pre>

In a few minutes it starts to collect data. See the Misc: Data collector in zabbix latest data for easy debug.

For Mongo-DB zabbix graphs go to Monitoring -> Graphs, then select the host with mongodb instance and select Mongo-DB Opcounters and Mongo-DB Network IO graphs. The best way to use this data by your team is to compose special zabbix screens with this graphs with all your servers. How to do this see https://www.zabbix.com/documentation/4.0/manual/config/visualisation/screens

Here is the sample of mongodb zabbix custom screen https://petrushin.org/mongo/mongod_sample.html

## How to install Mongos template

Mongos template is used to collect the basic mongos server opcounters and notify if the instance is gone.

In case you run mongos instance on the same hardware with any mongodb instance and have the same hostname, user and pass Mongos template will use the Macros data from previously configured Mongo-DB template. You have to do only two steps to get Mongos template running.
1. Navigate to hosts configuration in zabbix server and add Mongos template to host with mongos instance.
2. In Macros tab add the following data
<pre><code>{$MONGOS_PORT}  Port used by mongodb instance</code></pre>
In case the mongos instance is running on dedicated hardware or VM you have to add in Macros tab the following data
<pre><code>{$MONGODB_HOSTNAME}  IP or DNS name of interface used by mongodb instance
{$MONGODB_USER}  User name
{$MONGODB_PASS}  Password
{$MONGOS_PORT}  Port used by mongodb instance
{$MONGODB_ZABBIX_NAME}  Server hostname, as it registered in zabbix (I use two different interfaces for each mongodb server, mongodb instance is using one, other services including zabbix agent - another).
</code></pre>

In a few minutes it starts to collect data. See the Mongos Misc: 'Mongos data collector' in zabbix latest data for easy debug.

## How to install Mongo-RS probe template

Mongo-RS probe template is used to watch for replicasets. It watch at entire replicaset, then tries to insert a test record and notify if replicaset or one of replicaset members goes unreachable.
Create new host in zabbix named like replicaset, for example my-rs0, then add Mongo-RS template to this host.
In Macros tab add the Macroses

<pre><code>
{$MONGO_USER}  User
{$MONGO_PASS}  Password
{$RS_NAME} my-rs0
{$RS_STRING} mongo00.domain.com:port,mongo01.domain.com:port,mongo02.domain.com:port
{$RS_ZABBIX_NAME} my-rs0 
</code></pre>

See 'RS data collector' in Mongo Replica Set section in zabbix latest data for debug.

## How to monitor more than one mongodb instance

The easiest way to monitor more than one mongodb instance is to create new host in zabbix then add a MongoDB template with different {$MONGODB_PORT}

## Contacts

Vasily Petrushin
petrushinvs@gmail.com
