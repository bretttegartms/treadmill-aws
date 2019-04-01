"""Treadmill AWS instance CLI

Create, delete and manage configurations of AWS instances.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import gzip
import io
import logging
import random

import click

from treadmill import cli
from treadmill import context
from treadmill import dnsutils
from treadmill import restclient

from treadmill_aws import cli as aws_cli


_LOGGER = logging.getLogger(__name__)

_EXCEPTIONS = []
_EXCEPTIONS.extend(restclient.CLI_REST_EXCEPTIONS)

_ON_EXCEPTIONS = cli.handle_exceptions(_EXCEPTIONS)

_REST_PATH = '/aws-instance/'


def init():  # pylint: disable=R0912
    """Configures application monitor"""
    formatter = cli.make_formatter('aws_instance')
    ctx = {}

    @click.group()
    @click.option('--api', help='API url to use.',
                  metavar='URL',
                  type=cli.LIST,
                  envvar='TREADMILL_AWSINSTANCE_API')
    @click.option('--cell', required=True,
                  envvar='TREADMILL_CELL',
                  callback=cli.handle_context_opt,
                  expose_value=False)
    @click.option('--srvrec', help='API srv record.',
                  envvar='TREADMILL_AWSINSTANCE_API_SRVREC')
    def instance_group(api, srvrec):
        """Manage Treadmill app monitor configuration"""
        ctx['api'] = api
        if not ctx['api']:
            ctx['api'] = []

        if srvrec:
            result = dnsutils.srv(srvrec, None)
            for host, port, _p, _w in result:
                ctx['api'].append('http://{}:{}'.format(host, port))

    @instance_group.command()
    @click.argument('hostname')
    @_ON_EXCEPTIONS
    def configure(hostname):
        """Configure AWS instance."""
        restapi = ctx['api']
        url = _REST_PATH + hostname
        instance_entry = restclient.get(restapi, url)
        cli.out(formatter(instance_entry.json()))

    @instance_group.command(name='list')
    @_ON_EXCEPTIONS
    def _list():
        """List AWS instances."""
        restapi = ctx['api']
        url = _REST_PATH
        response = restclient.get(ctx['api'], url)
        cli.out(formatter(response.json()))

    @instance_group.command()
    @click.argument('hostname', nargs=1, required=True)
    @_ON_EXCEPTIONS
    def delete(hostname):
        """Delete AWS instance"""
        restapi = ctx['api']
        url = _REST_PATH + hostname
        restclient.delete(restapi, url)

    @instance_group.command(name='create')
    @click.option(
        '--image',
        type=aws_cli.IMAGE,
        help='Base image.'
    )
    @click.option(
        '--image-account',
        help='AWS image account.',
    )
    @click.option(
        '--domain',
        help='IPA Domain',
    )
    @click.option(
        '--secgroup',
        type=aws_cli.SECGROUP,
        help='Security group'
    )
    @click.option(
        '--subnet',
        type=aws_cli.SUBNET,
        help='Subnet'
    )
    @click.option(
        '--role',
        default='generic',
        help='Instance Role'
    )
    @click.option(
        '--key',
        help='SSH key'
    )
    @click.option(
        '--size',
        default='t2.small',
        help='Instance EC2 size'
    )
    @click.option(
        '--count',
        default=1,
        type=int,
        help='Number of instances'
    )
    @click.option(
        '--disk-size',
        default='10G',
        help='Root parition size, e.g. 100G',
        callback=aws_cli.convert_disk_size_to_int
    )
    @click.option(
        '--instance-profile',
        default='treadmill-node',
        help='Instance profile'
    )
    @click.option(
        '--hostgroup',
        multiple=True,
        help='IPA hostgroup memberships',
    )
    @click.option(
        '--instance-vars',
        type=cli.DICT,
        help='Instance variables in the format foo=bar,baz=qux'
    )
    @click.option(
        '--hostname',
        required=True,
        help='Shortname or Pattern, e.g. PATTERN-{time}',
    )
    @click.option(
        '--ip-address',
        help='IP address',
    )
    @click.option(
        '--eni',
        help='Elastic Network ID; e.g. eni-xxxxxxxx',
    )
    @click.option(
        '--spot',
        is_flag=True,
        help='Request a spot instance',
    )
    @_ON_EXCEPTIONS
    def create(count, disk_size, domain, eni, hostgroup, hostname, image,
               image_account, instance_profile, ip_address, key, role,
               secgroup, size, spot, subnet, instance_vars):
        """Create instance"""
        admin_srv = context.GLOBAL.admin.server()
        admin_cell = context.GLOBAL.admin.cell()
        cell = context.GLOBAL.cell
        cell_data = admin_cell.get(cell)['data']
        restapi = ctx['api']

        payload = {
            'count': count,
            'disk': disk_size or cell_data['disk-size'],
            'domain': domain or cell_data['realm'],
            'eni': eni,
            'hostgroups': hostgroup or cell_data['hostgroups'],
            'hostname': hostname,
            'image': image or cell_data['image'],
            'instance_profile': instance_profile or cell_data['instance_profile'],
            'instance_vars': instance_vars,
            'ip_address': ip_address,
            'key': key,
            'role': role,
            'secgroup': secgroup or cell_data['secgroup'],
            'instance_type': size or cell_data['size'],
            'spot': spot,
            'subnet': subnet or random.choice(cell_data['subnets'])
        }

        url = _REST_PATH + hostname
        response = restclient.post(restapi, url, payload=payload)
        cli.out(response.json())

    del delete
    del _list
    del configure
    del create

    return instance_group
