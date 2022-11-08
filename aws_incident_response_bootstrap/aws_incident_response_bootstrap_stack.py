"""CDK Stack to set up basic incident response infrastructure."""
from aws_cdk import Stack, aws_guardduty, aws_sns, aws_events, aws_events_targets, aws_cloudwatch, aws_securityhub
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

        guardduty_topic = aws_sns.Topic(
            self,
            "GuardDutyTopic",
            display_name="GuardDuty Alerting Topic",
        )

        # Modify this if you'd rather do an HTTP integration (think Slack or a custom app)
        aws_sns.Subscription(
            self,
            "EmailSubscription",
            topic=guardduty_topic,
            endpoint="example@example.com",
            protocol=aws_sns.SubscriptionProtocol.EMAIL,
        )

        # Rule that alerts on a GuardDuty finding over a severity 5, target associated with rule creation.
        aws_events.Rule(
            self,
            "GuardDutyRule",
            targets=[aws_events_targets.SnsTopic(guardduty_topic)],
            event_pattern=aws_events.EventPattern(
                source=["aws.guardduty"],
                detail_type=["GuardDuty Finding"],
                detail={
                    "severity": [
                        5,
                        5.0,
                        5.1,
                        5.2,
                        5.3,
                        5.4,
                        5.5,
                        5.6,
                        5.7,
                        5.8,
                        5.9,
                        6,
                        6.0,
                        6.1,
                        6.2,
                        6.3,
                        6.4,
                        6.5,
                        6.6,
                        6.7,
                        6.8,
                        6.9,
                        7,
                        7.0,
                        7.1,
                        7.2,
                        7.3,
                        7.4,
                        7.5,
                        7.6,
                        7.7,
                        7.8,
                        7.9,
                        8,
                        8.0,
                        8.1,
                        8.2,
                        8.3,
                        8.4,
                        8.5,
                        8.6,
                        8.7,
                        8.8,
                        8.9,
                    ]
                },
            ),
        )

        aws_cloudwatch.CfnAnomalyDetector(
            self,
            "LambdaInvocationAnomalyDetector",
            metric_name="Invocations",
            namespace="AWS/Lambda",
            stat="Sum",
        )

        # You may know some conditions and alarms you want to set about resources in your environment that should trigger security responses.
        # As a sensible placeholder, we'll respond to lambda errors.
        aws_cloudwatch.CfnAlarm(
            self,
            "LambdaInvocationsAnomaly",
            alarm_name="Lambda Invocations Anomaly",
            alarm_actions=[guardduty_topic.topic_arn],
            alarm_description="Alert when invocations are out of bands.",
            comparison_operator="LessThanLowerOrGreaterThanUpperThreshold",
            threshold_metric_id="ad1",
            evaluation_periods=1,
            treat_missing_data="breaching",
            metrics=[
                aws_cloudwatch.CfnAlarm.MetricDataQueryProperty(
                    expression="ANOMALY_DETECTION_BAND(m1, 2)", id="ad1"
                ),
                aws_cloudwatch.CfnAlarm.MetricDataQueryProperty(
                    id="m1",
                    metric_stat=aws_cloudwatch.CfnAlarm.MetricStatProperty(
                        metric=aws_cloudwatch.CfnAlarm.MetricProperty(
                            metric_name="Invocations", namespace="AWS/Lambda"
                        ),
                        period=86400,
                        stat="Sum",
                    ),
                ),
            ],
        )

        aws_securityhub.CfnHub(self, "SecurityHub")
