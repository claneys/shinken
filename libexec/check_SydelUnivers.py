#!/usr/bin/env python
############################## check_snmp_load #################
# Version : 0.9
# Date : Oct 29 2013
# Author  : Romain Forlot ( rforlot[At] yahoo [dot] com )
# Help : http://blog.claneys.com
# Licence : GPL - http://www.fsf.org/licenses/gpl.txt
#################################################################
#
# Help : ./check_SydelUnivers -c <connect_string> -u <database_username> -p <database_username_password> -w <warning threshold>
#
# This plugin check alarms triggered for a specific user and return them. There are no critical threshold since SU handle 
# that state.

import os, re, sys

# You'll need to install this module : easy_install cx_Oracle
# Prior to be able to install it, you must install python-devel package
# relative to your GNU/linux distro
import cx_Oracle

from subprocess import Popen, PIPE
from optparse import OptionParser

OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3

VERSION = '0.9'

class check_SydelUnivers():

    def __init__(self, connect, username, password, warning, su_username):
        self.connect = connect
        self.username = username
        self.password = password
        self.su_username = su_username
        self.get_alarms_request = 'SELECT a.COD_ALA, a.LIB_ALA, a.NIV_ALA, h.DAT_CREA_ALA FROM %s.SU_ALA a, %s.SU_ALA_HIS h WHERE a.cod_ala=h.cod_ala and h.etat_ala != \'TERM\' and instr(a.lst_ope,\';SYDEL;\')>0 order by dat_crea_ala' % (self.username, self.username)
        self.tables = [ 'SU_ALA', 'SU_ALA_HIS' ]
        # End with one of the self.tables value
        self.is_synonyms_exist = 'SELECT COUNT(*) FROM all_objects WHERE object_type like \'SYNONYM\' and owner = \'%s\' and object_name = ' % self.username.upper()
        self.create_synonyms = 'create synonym %s.SU_ALA for %s.' % (self.username, self.su_username)
        # Thresholds. We don't have critical threshold since
        # SU handled criticity.
        self.warn = warning

    def do_connect(self, method="cx_Oracle"):
        '''
        Initialize sqlplus connection to
        the oracle database.
        method : support only oracle by now, using sqlplus.
        OHOME : ORACLE_HOME, default: retrieve ORACLE_HOME environment variable.
        user : user used to connect
        password : password of user
        base : name of database to connect to. With an Oracle DB it is the connect string
        '''
    
        # Connection selection dictionnary
        # Only sqlplus for now.
        connection = { 'cx_Oracle' : self.cx_Oracle() }
        try:
            res = connection[method]
            return res
        except KeyError:
            sys.exit('Wrong connection method')
    
    def cx_Oracle(self):
            c = self.username+'/'+self.password+'@'+self.connect
            try:
                session = cx_Oracle.connect(c)
                return session
            except (OSError, ValueError) as err:
                sys.exit("Connection got a problem : %s" % err.strerror)
    
    def get_alarms(self, session):
        '''
        Get Sydel Univers alarms relatives to user provided in argument
        session : session object connected to the database.
        '''

        cursor = session.cursor()
        try:
            cursor.execute(self.get_alarms_request)
        except cx_Oracle.DatabaseError as e:
            if str(e).startswith('ORA-00942'):
                print('%s\nMissing Synonym from Oracle username for your user: %s\nUse option -s.' % (e, self.username))
                exit(1)
            else:
                print e

        alarms = cursor.fetchall()

        return alarms

    def set_synonyms(self, session):
        cursor = session.cursor()
        for table in self.tables:
            request_exist = self.is_synonyms_exist + "'%s'" % table
            cursor.execute(request_exist)
            if cursor.fetchone()[0] == 1:
                print 'Synonyms for %s table already created.' % table
            else:
                request_create = self.create_synonyms + table
                cursor.execute(request_create)
                cursor.execute(request_exist)
                if cursor.fetchone()[0] == 1:
                    print 'Synonyms for %s table created.' % table
                else:
                    print 'Problem at creation...'
                    exit(1)
                                

    def process_alarms(self, alarms):
        '''
        Search for critical alarms, then format ouput for 
        Shinken/nagios.
        alarms : list of tuples of alarms.
        '''

        nb_alarms = len(alarms)
        is_critical = False

        exit_code = OK
        output = "You got %d alarm(s)" % nb_alarms
        perfdata = "| Alarmes_SU=%d;%d;;; " % (nb_alarms, self.warn)
        long_output = ""

        if nb_alarms == 0:
            return ("OK %s %s"% (output, perfdata), exit_code)

        for alarm in alarms:
            if alarm[2] == 1:
                exit_code = CRITICAL
                long_output += "CRITICAL: " + alarm[1] + " since " + str(alarm[3].date()) + " at " + str(alarm[3].time()) + "\n"
            else:
                if exit_code != CRITICAL:
                    exit_code = WARNING
                long_output += "WARNING: " + alarm[1] + " since " + str(alarm[3].date()) + " at " + str(alarm[3].time()) + "\n"

        return (output+perfdata+long_output, exit_code)

    def main(self):
        session = self.do_connect()
        if self.su_username:
            self.set_synonyms(session)
        else:
            alarms = self.get_alarms(session)
            check_results = self.process_alarms(alarms)

            print check_results[0]
            exit(check_results[1])

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option('-c', '--connect', dest='connect', help='Connect string to Sydel Univers Oracle Database. See your tnsnames.ora')
    parser.add_option('-u', '--username', dest='username', help='Oracle user to connect at database')
    parser.add_option('-p', '--password', dest='password', help='Oracle password')
    parser.add_option('-w', '--warning', dest='warning', type=int, default=1, help='Warning threshold triggered if there are more than this threshold. Default: 1')
    parser.add_option('-s', '--su-username', dest='su_username', help='This will create the tables synonym for your user.\nEnter the SU username.')

    opts, args = parser.parse_args()

    if args:
        parser.error("does not take any positional arguments")
    
    check_SydelUnivers(**vars(opts)).main()
