#!/usr/bin/python
#

from __future__ import print_function

import logging
logging.basicConfig(level = logging.ERROR)

import sys, getopt
from pyzabbix import ZabbixMetric, ZabbixSender

from pymongo import MongoClient
from pymongo import ReadPreference
import time

ZBHOST = 'localhost'
ZBPORT = 10051

try:
  opts, args = getopt.getopt(sys.argv[1:],"c:n:r:u:s:")
except getopt.GetoptError:
  print ('mongod-rs-probe.py -c <connection string> -n <hostname in zabbix> -u <user> -s <secret pass> -r <replicaSet>')
  sys.exit(2)

for opt, arg in opts:
  if opt == '-c':
    mongostr = arg
  elif opt == '-n':
    zbhost = arg
  elif opt == '-r':
    replicaSet = arg
  elif opt == '-u':
    muser = arg
  elif opt == '-s':
    mpass = arg

inserted = 0
connected = 0
deleted = 0
mread = 0
warn = 0

def report_and_exit():
	packet = [
		ZabbixMetric(zbhost, 'rs.insert', inserted),
		ZabbixMetric(zbhost, 'rs.read', mread),
		ZabbixMetric(zbhost, 'rs.delete', deleted),
		ZabbixMetric(zbhost, 'rs.connect', connected),
		ZabbixMetric(zbhost, 'rs.warn', warn),
	]
	# print (warn)
	result = ZabbixSender(zabbix_port = ZBPORT, zabbix_server = ZBHOST).send(packet)
	#print (result)
	exit()


def rs_status(rs_):
#	print (rs_.admin.read_preference)
	wwarn = 0
	if len(rs_.nodes) < 2:
		print ('RS '+replicaSet+' status: ERROR')
		print ('Online nodes:', [i for i in rs_.nodes])
		wwarn = 1
	else:
		res = rs_.admin.command("replSetGetStatus")
#  		print (res)
#		print (rs_.nodes)
#		print ('ok:', int(res['ok']))
                for i in res['members']:
			print ('name:', i['name'], 'state:', int(i['state']), i['stateStr'], 'health:', int(i['health']))
			if int(i['health']) != 1 or int(i['state']) == 5:
				wwarn = 1
		if wwarn == 1:
			print ('RS', replicaSet, 'status: WARN!')
		else:
			print ('RS', replicaSet, 'status: OK!')
	return wwarn

#print ('Connecting '+mongostr+'?replicaSet='+replicaSet+'...')
print ('Replicaset:', replicaSet)

try:
  rs = MongoClient('mongodb://'+muser+':'+mpass+'@'+mongostr+'/admin?replicaSet='+replicaSet, readPreference='secondaryPreferred',
	serverSelectionTimeoutMS=5000, connectTimeoutMS=5000)
except Exception as e:
  print ('Can\'t connect to replicaset '+mongostr+'?replicaSet='+replicaSet)
  print ("ERROR:", e)
  report_and_exit()

connected = 1
#print ('Connected!')
#print (rs);

sequence = int (time.time() * 1000)
#print ('Inserting new seq ' + str(sequence)+'...')
msg = { 'sequence': sequence }
try:
  if replicaSet == 'configReplSet':
	_id = rs['admin']['rw-test'].insert_one(msg).inserted_id
  else:
	_id = rs['rw-test']['rw-test'].insert_one(msg).inserted_id
except Exception as e:
#  print (type(e))
#  print (e)
  print ('Replicaset '+replicaSet+" write ERROR:", e)
  rs_status(rs)
  report_and_exit()

inserted = 1
#print ('Sequence inserted')
if replicaSet == 'configReplSet':
	rw_test_seq = rs['admin']['rw-test'].find_one({"_id": _id})
else:
	rw_test_seq = rs['rw-test']['rw-test'].find_one({"_id": _id})

mread = 1

#print ('Got sequence '+str(rw_test_seq['sequence']))
try:
    if sequence == int(rw_test_seq['sequence']):
        print ('Got right sequence, replicaset '+replicaSet+' UP')
    else:
        print ('Got strange sequence, replicaset '+replicaSet+str(rw_test_seq['sequence']))
except Exception as e:
    print ('Replicaset '+replicaSet+" read ERROR:", e)
    rs_status(rs)
    report_and_exit()


if replicaSet == 'configReplSet':
	rs['admin']['rw-test'].delete_one({"_id": _id})
else:
	rs['rw-test']['rw-test'].delete_one({"_id": _id})
deleted = 1

warn = rs_status(rs)
report_and_exit()

