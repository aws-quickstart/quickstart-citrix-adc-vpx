import json
import time
import ipaddress


def waitfor(seconds=2, reason=None):
    if reason is not None:
        print('Waiting for {} seconds. Reason: {}'.format(seconds, reason))
    else:
        print('Waiting for {} seconds'.format(seconds))
    time.sleep(seconds)


# def to_json(data):
#     return codecs.encode(json.dumps(data))

def to_json(data, indent=2):
    return json.dumps(data, indent=indent)


def from_json(data):
    return json.loads(data)


def get_gateway_ip(cidr):
    return [str(ip) for ip in ipaddress.IPv4Network(cidr)][1]


def cidr_to_netmask(cidr):
    return (str(ipaddress.IPv4Network(cidr).network_address), str(ipaddress.IPv4Network(cidr).netmask))
