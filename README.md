A script to spawn an EC2 instance from an AMI, and update a domain hosted on Route53 to reflect the IP Address of the spawned instance (without the use of Elastic IPs).

Used to provide a VPN endpoint for my development/analysis/"untrusted" virtual network which is not active all the time, so no point keeping the endpoint running.

Requires the AWS Python .

You will need to create an IAM user for the script to run as, probably with something like the following "Allow" permissions:

```
"Action": [
                "ec2:DescribeInstanceStatus",
                "ec2:DescribeInstances",
                "ec2:DescribeNetworkInterfaces",
                "ec2:StartInstances",
                "ec2:RunInstances",
                "ec2:StopInstances",
                "ec2:CreateTags",
                "ec2:TerminateInstances"
            ],
```

```
            "Action": [
                "route53:ChangeResourceRecordSets",
                "route53:ListHostedZones",
                "route53:ListResourceRecordSets",
                "route53:GetChange"
            ],
```