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

import os
from subprocess import Popen, PIPE
from optparse import OptionParser


VERSION = '0.9'

class check_SydelUnivers:

    def __init__(self, connect, username, password):
        self.connect = connect
        self.username = username
        self.password = password

    def do_connect(self, method="sqlplus"):
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
        connection = { 'sqlplus' : self.sqlplus_session() }
        try:
            res = connection[method]
            return res
        except KeyError:
            sys.exit('Wrong connection method')
    
    def sqlplus_session(self, OHOME=os.getenv('ORACLE_HOME')):
            c = self.username+'/'+self.password+'@'+self.connect
            try:
                session = Popen([OHOME+'/bin/sqlplus', c], stdin=PIPE, stdout=PIPE, stderr=PIPE)
                print "Connection OK"
                return session
            except (OSError, ValueError) as err:
                sys.exit("Connection got a problem : %s" % err.strerror)
    
    def get_alarmes(self, session):
        '''
        Get Sydel Univers alarmes relatives to user provided in argument
        '''
    
        output_format = 'column LIB_ALA FORMAT A35\n'
        get_alarmes = 'SELECT a.COD_ALA, a.LIB_ALA, a.NIV_ALA, h.DAT_CREA_ALA FROM devdbsud.SU_ALA a, devdbsud.SU_ALA_HIS h WHERE a.cod_ala=h.cod_ala and h.etat_ala != \'TERM\' and instr(a.lst_ope,\';SYDEL;\')>0 order by dat_crea_ala;'
    
        stdout, stderr = session.communicate(input=output_format + get_alarmes)
        
        lines = stdout.splitlines()
    
        # 14 is the number of meaningless lines.
        nb_alarmes = len(lines)-14
        alarmes = [ lines.pop(i) for i in range(12, len(lines)-2) ]
    
        return (alarmes, nb_alarmes)
    
    def main(self):
        session = self.do_connect()
        alarmes, nb_alarmes = self.get_alarmes(session)
        print "We got %d alarmes" % nb_alarmes


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option('-c', '--connect', dest='connect', help='Connect string to Sydel Univers Oracle Database. See your tnsnames.ora')
    parser.add_option('-u', '--username', dest='username', help='Oracle user to connect at database')
    parser.add_option('-p', '--password', dest='password', help='Oracle password')

    opts, args = parser.parse_args()

    if args:
        parser.error("does not take any positional arguments")
    
    check_SydelUnivers(**vars(opts)).main()
