"""Treadmill AWS Instance REST api.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import flask
import flask_restplus as restplus
from flask_restplus import fields

from treadmill import webutils


def init(api, cors, impl):
    """Configures REST handlers for AWS instance resource."""

    namespace = webutils.namespace(
        api, 'aws-instance', 'AWS Instance REST operations'
    )

    model = {
        'Hostname': fields.String(description='Hostname'),
        'Id': fields.String(description='EC2 ID'),
        'Arch': fields.String(description='Architecture'),
        'Image': fields.String(description='Image ID'),
        'Type': fields.String(description='Instance Type'),
        'Key': fields.String(description='SSH Key'),
        'Launch': fields.String(description='Launch Time'),
        'Status': fields.String(description='Status'),
        'Vpc': fields.String(description='VPC ID'),
        'Subnet': fields.String(description='Subnet'),
        'Tags': fields.String(description='Instance Tags'),
    }

    aws_instance_model = api.model(
        'AWSInstance', model
    )

    aws_instance_create_model = api.model('AWSCreateInstance', {
        'instance': fields.String(
            description='Instance ID of the instance created.'
        )
    })

    aws_instance_list_model = api.model('AWSListInstance', {
        'hostnames': fields.String(
            description='Hostname of the instance found.'
        )
    })

    resource_fields = {
        'tags': fields.Raw(description='Tags k/v dictionary'),
        'name': fields.String(description='Resource name'),
        'ids': fields.List(fields.String, description='List of resource ids')
    }

    aws_instance_req_model = api.model('AWSInstanceRequest', {
        'image': fields.Nested(resource_fields, description='Image'),
        'image_account': fields.String(description='Image account.'),
        'userdata': fields.List(fields.String, description='User data.'),
        'profile': fields.String(description='Instance profile.'),
        'secgroup': fields.Nested(resource_fields, description='AWS secgroup'),
        'subnet': fields.Nested(resource_fields, description='AWS subnet'),
        'key': fields.String(description='Instance ssh key.'),
    })

    match_parser = api.parser()

    @namespace.route(
        '/',
    )
    class _InstanceResourceList(restplus.Resource):
        """Treadmill Instance resource"""

        @webutils.get_api(api, cors,
                          marshal=api.marshal_list_with,
                          resp_model=aws_instance_list_model,
                          parser=match_parser)
        def get(self):
            """Returns list of instances."""
            return impl.list()

    @namespace.route('/<instance>')
    @api.doc(params={'instance': 'Instance Hostname or EC2 ID'})
    class _InstanceResource(restplus.Resource):
        """TreadmillAWS Instance resource."""

        @webutils.get_api(api, cors,
                          marshal=api.marshal_with,
                          resp_model=aws_instance_model)
        def get(self, instance):
            """Return instance configuration."""
            return impl.get(instance)

        @webutils.post_api(api, cors,
                           req_model=aws_instance_req_model,
                           resp_model=aws_instance_create_model)
        def post(self, instance):
            """Creates instance."""
            return impl.create(instance, flask.request.json)

        @webutils.delete_api(api, cors)
        def delete(self, instance):
            """Deletes instance."""
            return impl.delete(instance)
