#!/usr/bin/env python
#
# This file is part of Shinken.
#
# Shinken is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Shinken is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Shinken.  If not, see <http://www.gnu.org/licenses/>.

"""
This program get hosts informations from running arbiter daemon and 
get service dependencies definition from config pack flat files then
dump services dependencies according to the config files to a json
that can be loaded in hot_dependencies_arbiter module.

servicedependencies file in pack use template host_name that will be
matched in hosts 'use' directive to apply those servicedependency
definition to hosts.

"""


import os, sys, optparse, cPickle
import shinken.daemons.arbiterdaemon
from shinken.arbiterlink import ArbiterLink
from shinken.http_client import HTTPExceptions 
from shinken.log import logger
from shinken.objects.config import Config

# Try to load json (2.5 and higer) or simplejson if failed (python2.4)
try:
    import json
except ImportError:
    # For old Python version, load simple json
    try:
        import simplejson as json
    except ImportError:
        raise SystemExit("Error: you need the json or simplejson module "
                         "for this script")


sat_types = ['arbiter', 'scheduler', 'poller', 'reactionner',
             'receiver', 'broker']

VERSION = '0.2'

class ShinkenAdmin():

    def __init__(self):
        self.arb = None 
        self.conf = None

    def do_connect(self):
        '''
        Connect to an arbiter daemon
        Syntax: connect [host]:[port]
        Ex: for Connecting to server, port 7770
        > connect server:7770
        Ex: connect to localhost, port 7770
        > connect
        '''
        addr = 'localhost'
        port = '7770'
    
        print "Connection to %s:%s" % (addr, port)
        ArbiterLink.use_ssl = False
        self.arb = ArbiterLink({'arbiter_name': 'arbiter-master', 'address': addr, 'port': port})
        self.arb.fill_default()
        self.arb.pythonize()
        self.arb.update_infos()
        if self.arb.reachable:
            print "Connection OK"
        else:
            sys.exit("Connection to the arbiter get a problem")
    
    def getconf(self):
        '''
        Get the data in the arbiter for a table and some properties
        like hosts  host_name realm
        '''
        files = ['/etc/shinken/packs/oracle-forms/servicedependency.cfg']
        conf = Config()
        conf.read_config_silent = 1
        svcdep_buf = conf.read_config(files)
        svc_dep = conf.read_config_buf(svcdep_buf)['servicedependency']
    
        properties = [ 'host_name','use','act_depend_of']
        hosts = self.arb.get_objects_properties('hosts', properties)

        return (hosts, svc_dep)

    def load_host_mapping(self):
        '''
        Make tuples mapping service dependencies. Return a list of tuples 
        and need hosts and service dependencies parameter.
        '''
        # Get needed conf
        hosts, svc_dep = self.getconf()
        print "Hosts:", hosts
        print "Service Dep:", svc_dep

        r = []
        # Search for host matching "use" template
        for dep in svc_dep:
            # Get host_name and dependent_host_name field from servicedependency
            # config file in packs. Usually values are host's pack template.
            parent_host_name = dep['host_name']
            try:
                dependent_host_name = dep['dependent_host_name']
            except KeyError:
                dependent_host_name = parent_host_name

            # Construct dependencies tuples
            for host in hosts:
                for parent_svc in dep['service_description']:
                    parent_svc_tuples = [ ('service', host[0]+","+parent_svc) for host_name in parent_host_name if host_name in host[1] ]
                for dependent_svc in dep['dependent_service_description']:
                    dependent_svc_tuples = [ ('service', host[0]+","+dependent_svc) for host_name in dependent_host_name if host_name in host[1] ]
                for tuple in parent_svc_tuples:
                    r.append( (tuple, dependent_svc_tuples[parent_svc_tuples.index(tuple)]) )

        return r

    def main(self, output_file):
        self.do_connect()
        r = self.load_host_mapping()

        # Write ouput file
        jsonmappingfile = open(output_file, 'w')
        try:
            json.dump(r, jsonmappingfile)
        finally:
            jsonmappingfile.close()


if __name__ == "__main__":
    parser = optparse.OptionParser(
        version="Shinken service hot dependency according to packs (or custom) definition to json mapping %s" % VERSION)
    parser.add_option("-o", "--output", dest='output_file',
                      default='/tmp/shinken_service_dependency:mapping.json',
                      help="Path of the generated json mapping file.")
    parser.add_option('-v', '--verbose', action='store_true', dest='verbose', help='More verbosity. Used to debug')

    opts, args = parser.parse_args()
    if args:
        parser.error("does not take any positional arguments")

    ShinkenAdmin().main(**vars(opts))
