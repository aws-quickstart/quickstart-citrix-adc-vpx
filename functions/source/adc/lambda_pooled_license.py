import os
from barbarika.helpers import waitfor
from barbarika.aws import send_response
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
            nsip = event['ResourceProperties']['ADCPrivateNSIP']

            adm_ip = event['ResourceProperties']['ADMIP']
            licensing_mode = event['ResourceProperties']['LicensingMode']
            bandwidth = event['ResourceProperties']['Bandwidth']
            pooled_edition = event['ResourceProperties']['PooledEdition']
            platform = event['ResourceProperties']['Platform']
            cpu_edition = event['ResourceProperties']['VCPUEdition']

            adc = CitrixADC(nsip=nsip,
                            nsuser="nsroot", nspass=user_password)

            adc.add_licenseserver(adm_ip)

            adc.allocate_pooled_license(
                licensing_mode, bandwidth, pooled_edition, platform, cpu_edition)
            try:
                adc.save_config()
            except:
                pass # ignore saving config
            adc.reboot(warm=True)
            waitfor(200, reason="Warm rebooting {} ".format(adc.nsip))

            # Validate license
            adc.validate_pooled_license(
                licensing_mode, bandwidth, pooled_edition, platform, cpu_edition)

            try:
                adc.save_config()
            except:
                pass # ignore saving config
            response_status = 'SUCCESS'
        else:  # request_type == 'Delete' | 'Update'
            response_status = 'SUCCESS'
    except Exception as e:
        fail_reason = str(e)
        print(fail_reason)
        response_status = 'FAILED'
    finally:
        send_response(event, context, response_status,
                      response_data, fail_reason=fail_reason)
