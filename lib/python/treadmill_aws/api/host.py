"""Treadmill Host REST API."""
from treadmill import authz

from treadmill_aws import awscontext
from treadmill_aws import hostmanager
from treadmill_aws import cli as aws_cli

class API:
    """Treadmill Host REST API."""

    def __init__(self):

        def create_hosts(hostname, data):
            """Create host."""
            ipa_client = awscontext.GLOBAL.ipaclient
            ec2_conn = awscontext.GLOBAL.ec2

            data['image_id'] = aws_cli.admin.image_id(
                ec2_conn=ec2_conn, sts_conn=False, image=data['image'],
                account=False)
            data['secgroup_id'] = aws_cli.admin.secgroup_id(ec2_conn=ec2_conn,
                secgroup=data['secgroup'])
            data['subnet'] = aws_cli.admin.subnet_id(ec2_conn=ec2_conn,
                subnet=data['subnet'])

            hostmanager.create_host(
                ipa_client=ipa_client,
                ec2_conn=ec2_conn,
                **data)

        def delete_hosts(hostnames):
            """Delete host."""
            ipa_client = awscontext.GLOBAL.ipaclient
            ec2_conn = awscontext.GLOBAL.ec2

            hostmanager.delete_hosts(
                ipa_client=ipa_client,
                ec2_conn=ec2_conn,
                hostnames=hostnames
            )

        def list_hosts(hostnames=None):
            """List hosts."""
            ipa_client = awscontext.GLOBAL.ipaclient

            return hostmanager.find_hosts(
                ipa_client=ipa_client,
                pattern=hostnames
            )

        awscontext.GLOBAL.region_name = 'us-east-1'
        awscontext.GLOBAL.ipa_certs = '/etc/ipa/ca.crt'
        awscontext.GLOBAL.ipa_domain = 'ipa.poc.cloud.ms.com'

        self.create = create_hosts
        self.delete = delete_hosts
        self.list = list_hosts
        self.get = list_hosts


def init(authorizer):
    """Returns module API wrapped with authorizer function."""
    api = API()
    return authz.wrap(api, authorizer)
