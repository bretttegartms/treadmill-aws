"""AWS specific treadmill garbage collector
"""

import logging

from treadmill import admin
from treadmill import context
from treadmill_aws.awscontext import GLOBAL

_LOGGER = logging.getLogger(__name__)
_ACCOUNT = 'ms-aws-test' 


class LDAP:
    """LDAP garbage collection"""
    @staticmethod
    def list():
        """List LDAP server records that are not valid ec2 instances"""
        _LOGGER.info('fetched server list from LDAP')
        client = admin.Server(context.GLOBAL.ldap.conn)
        return {host.get("_id") for host in client.list({})}

    @staticmethod
    def delete(hostname):
        """Delete a LDAP server record"""
        _LOGGER.info('removing %s from LDAP', hostname)
        admin.Server(context.GLOBAL.ldap.conn).delete(hostname)


class IPA:
    """IPA garbage collection"""
    @staticmethod
    def list():
        """List IPA server records that are not valid ec2 instances"""
        _LOGGER.info('fetched server list from IPA')
        return set(GLOBAL.ipaclient.get_hosts(nshostlocation=_ACCOUNT))

    @staticmethod
    def delete(hostname):
        """Delete an IPA server"""
        _LOGGER.info('removing %s from IPA', hostname)
        GLOBAL.ipaclient.unenroll_host(hostname=hostname)

        
class DNS_A:
    """DNS A record garbage collection"""
    @staticmethod
    def list():
        """List A records that do not have a matching host"""
        _LOGGER.info('Fetched DNS list from IPA')
        # Fetch list of A records from IPA
        result = self.ipaclient.search_dns_record()
        if result.get('error'):
            raise Exception(result.get('error'))

        all_records = result['result']['result']
        current = set()
        for rec in all_records:
            if 'arecord' not in rec:
                continue

            a_rec_name = rec['idnsname'][0]
            continue
            for a_rec in rec['arecord']:
                print(a_rec)
                
                try:
                    socket.gethostbyname(host)
                except socket.error:
                    _LOGGER.info(
                        'Stale record - host does not exist: %s',
                        a_rec_name
                    )
                    current.add((a_rec_name, a_rec))
                    continue

                # skip records that do not belong to the cell.
                host = host.rstrip('.')
                if host not in self.servers:
                    _LOGGER.debug('Skip non-cell record: %s',
                                  a_rec_name)
                    continue

                current.add((a_rec_name, a_rec))

        return current


    @staticmethod
    def delete(hostname):
        """Delete an IPA server"""
        _LOGGER.info('removing %s from IPA', hostname)
        # Delete records matching hostname
        shortname = hostname.slice('.')[0]
        GLOBAL.ipaclient.delete_dns_record(record_type="A", record_name=shortname, )



__all__ = (
    'LDAP',
    'IPA',
    'DNS'
)
