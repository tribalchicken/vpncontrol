A script to spawn an EC2 instance from an AMI, and update a domain hosted on Route53 to reflect the IP Address of the spawned instance (without the use of Elastic IPs).

Used to provide a VPN endpoint for my development/analysis/"untrusted" virtual network which is not active all the time, so no point keeping the endpoint running.

Requires the AWS Python API