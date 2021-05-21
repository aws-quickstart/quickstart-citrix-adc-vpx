import os
from barbarika.aws import send_response, get_latest_citrixadc_ami


def lambda_handler(event, context):
    current_aws_region = os.environ["AWS_DEFAULT_REGION"]
    fail_reason = None
    print("event: {}".format(str(event)))
    request_type = event["RequestType"]
    response_status = "FAILED"
    response_data = {}
    try:
        if request_type == "Create":
            adc_version = event["ResourceProperties"]["ADCVersion"]
            adc_product = event["ResourceProperties"]["ADCProduct"]

            response_data["LatestADCAMI"] = latestami = get_latest_citrixadc_ami(adc_version, adc_product)
            print(f"Latest ADC AMI is {latestami} for Region:{current_aws_region}, ADCVersion:{adc_version} and ADCProduct:{adc_product}")
            response_status = "SUCCESS"
        else:  # request_type == 'Delete' | 'Update'
            response_status = "SUCCESS"
    except Exception as e:
        fail_reason = str(e)
        print(fail_reason)
        response_status = "FAILED"
    finally:
        send_response(event, context, response_status, response_data, fail_reason=fail_reason)


if __name__ == "__main__":
    adc_version = "12.1"
    adc_product = "Citrix ADC VPX - Customer Licensed"
    print(get_latest_citrixadc_ami(adc_version, adc_product))
