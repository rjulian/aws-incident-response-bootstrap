"""CDK Stack to set up basic incident response infrastructure."""
from aws_cdk import (
    Stack,
    aws_guardduty,
)
from constructs import Construct


class AwsIncidentResponseBootstrapStack(Stack):
    """Class defining incident response infrastructure stack."""
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        aws_guardduty.CfnDetector(
            self,
            "GuardDutyDetector",
            enable=True,
            data_sources=aws_guardduty.CfnDetector.CFNDataSourceConfigurationsProperty(

                # Do you use EKS? Why not get some extra alerting from GuardDuty?
                kubernetes=aws_guardduty.CfnDetector.CFNKubernetesConfigurationProperty(
                    audit_logs=aws_guardduty.CfnDetector.CFNKubernetesAuditLogsConfigurationProperty(
                        enable=False
                    )
                ),

                # Want GuardDuty to scan your EBS volumes when it sees malicious activity and alert you about Malware?
                malware_protection=aws_guardduty.CfnDetector.CFNMalwareProtectionConfigurationProperty(
                    scan_ec2_instance_with_findings=aws_guardduty.CfnDetector.CFNScanEc2InstanceWithFindingsConfigurationProperty(
                        ebs_volumes=False
                    )
                ),

                # Let GuardDuty analyze S3 data events and alert you when it sees irrational behavior in S3?
                s3_logs=aws_guardduty.CfnDetector.CFNS3LogsConfigurationProperty(
                    enable=False
                ),
            ),

            # This can be FIFTEEN_MINUTES, ONE_HOUR, SIX_HOURS, depending on how long of a lag you're comfortable with a finding showing up in Eventbridge or S3.
            finding_publishing_frequency="FIFTEEN_MINUTES",
        )
