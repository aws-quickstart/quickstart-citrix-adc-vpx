import os
from barbarika.helpers import waitfor
from barbarika.aws import send_response, get_subnet_address
from barbarika.citrixadc import CitrixADC


current_aws_region = os.environ['AWS_DEFAULT_REGION']


def lambda_handler(event, context):
    fail_reason = None
    print("event: {}".format(str(event)))
    request_type = event['RequestType']
    response_status = 'FAILED'
    response_data = {}
    try:
        if request_type == 'Create':
            user_password = event['ResourceProperties']['ADCCustomPassword']
            primary_nsip = event['ResourceProperties']['PrimaryADCPrivateNSIP']
            primary_vip = event['ResourceProperties']['PrimaryADCPrivateVIP']
            primary_vip_subnet = event['ResourceProperties']['PrimaryADCVIPPublicSubnetID']

            secondary_nsip = event['ResourceProperties']['SecondaryADCPrivateNSIP']
            secondary_vip = event['ResourceProperties']['SecondaryADCPrivateVIP']
            optional_lbvserver = True if event['ResourceProperties']['LBVserverRequired'] == 'No' else False

            primary = CitrixADC(nsip=primary_nsip,
                                nsuser="nsroot", nspass=user_password)
            secondary = CitrixADC(
                nsip=secondary_nsip, nsuser="nsroot", nspass=user_password)

            primary.add_hanode(
                id=1, ipaddress=secondary_nsip, incmode=True)
            waitfor(30, reason='secondary VPX password to get synced to that of primary')
            secondary.add_hanode(
                id=1, ipaddress=primary_nsip, incmode=True)

            ipset_name = 'qs_ipset'
            lbvserver_name = 'qs_lbvserver'

            primary.add_ipset(name=ipset_name)
            secondary.add_ipset(name=ipset_name)

            subnetmask = get_subnet_address(primary_vip_subnet)[1]
            primary.add_nsip(ip=secondary_vip,
                                netmask=subnetmask, iptype='VIP')

            primary.bind_ipset(name=ipset_name, ipaddress=secondary_vip)
            secondary.bind_ipset(name=ipset_name, ipaddress=secondary_vip)

            primary.add_lbvserver(name=lbvserver_name, servicetype='HTTP',
                                    ipaddress=primary_vip, port=80, ipset=ipset_name)

            if secondary.get_lbvserver(name=lbvserver_name):
                print('SUCCESS: {} and {} configured in HA mode'.format(
                    primary.nsip, secondary.nsip))
            else:
                raise Exception('FAIL: Could not configure {} and {} in HA mode'.format(
                    primary.nsip, secondary.nsip))

            # If lbvserver is optional
            if optional_lbvserver:
                primary.remove_lbvserver(name=lbvserver_name)
            try:
                primary.save_config()
                secondary.save_config()
            except:
                pass # Ignore saving config
            response_status = 'SUCCESS'
        else: # request_type == 'Delete' | 'Update'
            response_status = 'SUCCESS'
    except Exception as e:
        fail_reason = str(e)
        print(fail_reason)
        response_status = 'FAILED'
    finally:
        send_response(event, context, response_status,
                        response_data, fail_reason=fail_reason)
