"""Helper functions."""

from treadmill_aws import ec2client
from treadmill_aws import metadata


def image_id(ec2_conn, image, account, image_tag=None):
    """Resolve CLI image arguments to image id."""
    if not account:
        account = 'self'

    if image:
        return ec2client.get_image(ec2_conn,
                                   owners=[account],
                                   **image)['ImageId']

    # Return newest image with matching tags
    if image_tag:
        images = ec2client.list_images(ec2_conn=ec2_conn,
                                       owners=[account],
                                       tags=image_tag,
                                       **image)['ImageId']
        return images.pop()

    if metadata.image_id():
        image = {'ids': [metadata.image_id()]}
        return ec2client.get_image(ec2_conn,
                                   owners=[account],
                                   **image)['ImageId']


def subnet_id(ec2_conn, subnet):
    """Resolve subnet CLI arguments to subnet id."""
    if not subnet and metadata.subnet_id():
        subnet = {'ids': [metadata.subnet_id()]}
    return ec2client.get_subnet(ec2_conn, **subnet)['SubnetId']


def secgroup_id(ec2_conn, secgroup):
    """Resolve secgroup id from secgroup CLI arguments."""
    if not secgroup and metadata.secgroup_id():
        secgroup = {'ids': [metadata.secgroup_id()]}
    return ec2client.get_secgroup(ec2_conn, **secgroup)['GroupId']
