#!/usr/bin/python

import boto3
import json
import sys
import time

DNS_ZONE_ID = "zone_id_goes_here"
DNS_CNAME = "vpn.example.com."
EC2_AMI_ID = "ami-123456"
EC2_SEC_GROUP = "sg-123456"
EC2_INSTANCE_SIZE = "t2.nano"
EC2_TAG = "VPN"

ec2 = boto3.client('ec2')
route53 = boto3.client('route53')

# Get VPN Instance, based on tags
response = ec2.describe_instances(
    Filters = [
        {
            'Name': 'tag-value',
            'Values': [ EC2_TAG, ],
        }
    ]
)

existingInstanceId = None

if response['Reservations']:
    for i in response['Reservations']:
        if i['Instances'][0]['State']['Code'] == 16:
            existingInstanceId = i['Instances'][0]['InstanceId']
            break;

if sys.argv[1] == 'start':
    if existingInstanceId is None:
        # Start instance and wait until it's up
        response = ec2.run_instances(
    #        DryRun = True,
            ImageId=EC2_AMI_ID,
            MinCount=1,
            MaxCount=1,
            SecurityGroupIds=[
                EC2_SEC_GROUP,
            ],
            InstanceType=EC2_INSTANCE_SIZE,
        )

        newInstanceId = response['Instances'][0]['InstanceId']
        
        ec2waiter = ec2.get_waiter('instance_running')
        ec2waiter.wait(
            InstanceIds = [
                newInstanceId,
            ],
        )
        
        response = ec2.describe_instances(
            InstanceIds = [ newInstanceId ],
        )
  
        ec2.create_tags(
            Resources = [
                newInstanceId,
            ],
            Tags = [
                {
                   'Key': 'Purpose',
                   'Value': EC2_TAG
                }
            ]
        )

        newInstanceDnsName = response['Reservations'][0]['Instances'][0]['PublicDnsName']

        changeWaiter = route53.get_waiter('resource_record_sets_changed')

        # Update DNS
        response = route53.change_resource_record_sets(
            HostedZoneId = DNS_ZONE_ID,
            ChangeBatch = {

            "Changes": [
                    {
                        "Action": "UPSERT",
                        "ResourceRecordSet": {
                            "Name": DNS_CNAME,
                            "Type": "CNAME",
                            "TTL": 60,
                            "ResourceRecords": [
                                {
                                "Value": newInstanceDnsName
                                },
                            ],
                        },
                    }
                ]
            }
        )

        changeWaiter.wait(Id=response['ChangeInfo']['Id'])

if sys.argv[1] == 'stop':
    if existingInstanceId is not None:
        print("Shall now terminate instance: " + str(existingInstanceId))
        ec2.terminate_instances(
            InstanceIds = [
                    existingInstanceId,
            ]
        )
        #instance.wait_until_stopped()

        response = route53.list_resource_record_sets(
            HostedZoneId = DNS_ZONE_ID,
            StartRecordName = DNS_CNAME,
            StartRecordType = 'CNAME'
        )

        currentDnsValue = response['ResourceRecordSets'][0]['ResourceRecords'][0]['Value']

        response = route53.change_resource_record_sets(
            HostedZoneId = DNS_ZONE_ID,
            ChangeBatch = {

            "Changes": [
                    {
                        "Action": "DELETE",
                        "ResourceRecordSet": {
                            "Name": DNS_CNAME,
                            "Type": "CNAME",
                            "TTL": 60,
                            "ResourceRecords": [
                                {
                                    "Value": currentDnsValue
                                },
                            ],
                        },
                    }
                ]
            }
        )
