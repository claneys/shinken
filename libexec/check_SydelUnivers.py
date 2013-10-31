#!/usr/bin/env python
############################## check_snmp_load #################
# Version : 0.9
# Date : Oct 29 2013
# Author  : Romain Forlot ( rforlot[At] yahoo [dot] com )
# Help : http://blog.claneys.com
# Licence : GPL - http://www.fsf.org/licenses/gpl.txt
#################################################################
#
# Help : ./check_SydelUnivers
#

import os, re

# You'll need to install this module : easy_install cx_Oracle
# Prior to be able to install it, you must install python-devel package
# relative to your GNU/linux distro
import cx_Oracle

from subprocess import Popen, PIPE
from optparse import OptionParser


VERSION = '0.9'

class check_SydelUnivers:

    def __init__(self, connect, username, password):
        self.connect = connect
        self.username = username
        self.password = password
        self.get_alarmes_request = 'SELECT a.COD_ALA, a.LIB_ALA, a.NIV_ALA, h.DAT_CREA_ALA FROM devdbsud.SU_ALA a, devdbsud.SU_ALA_HIS h WHERE a.cod_ala=h.cod_ala and h.etat_ala != \'TERM\' and instr(a.lst_ope,\';SYDEL;\')>0 order by dat_crea_ala'
        # Thresholds. We don't have critical threshold since
        # SU handled criticity.
        self.warn = 1

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
                print "Connection OK"
                return session
            except (OSError, ValueError) as err:
                sys.exit("Connection got a problem : %s" % err.strerror)
    
    def get_alarmes(self, session):
        '''
        Get Sydel Univers alarmes relatives to user provided in argument
        session : session object connected to the database.
        '''

        cursor = session.cursor()
        cursor.execute(self.get_alarmes_request)

        alarmes = cursor.fetchall()

        return alarmes

    def process_alarmes(self, alarmes):
        '''
        Search for critical alarmes, then format them for 
        Shinken/nagios.
        alarmes : list of tuples of alarmes.
        '''

        nb_alarmes = len(alarmes)
        is_critical = False

        exit_code = 0
        output = "We got %d alarme(s)" % nb_alarmes
        perfdata = "| Alarmes_SU=%d;%d;;;" % (nb_alarmes, self.warn)
        long_output = ""

        if nb_alarmes == 0:
            return ("OK"+output+perfdata, exit_code)

        for alarme in alarmes:
            if alarme[2] == 1:
                exit_code = 2
                long_output += "CRITICAL: " + alarme[1] + " since " + str(alarme[3].date()) + " at " + str(alarme[3].time())
            else:
                exit_code = 1
                long_output += "WARNING: " + alarme[1] + " since " + str(alarme[3].date()) + " at " + str(alarme[3].time())

        return (output+perfdata+long_output, exit_code)

    def main(self):
        session = self.do_connect()
        alarmes = self.get_alarmes(session)
        check_results = self.process_alarmes(alarmes)

        print check_results[0]
        exit(check_results[1])

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option('-c', '--connect', dest='connect', help='Connect string to Sydel Univers Oracle Database. See your tnsnames.ora')
    parser.add_option('-u', '--username', dest='username', help='Oracle user to connect at database')
    parser.add_option('-p', '--password', dest='password', help='Oracle password')

    opts, args = parser.parse_args()

    if args:
        parser.error("does not take any positional arguments")
    
    check_SydelUnivers(**vars(opts)).main()
