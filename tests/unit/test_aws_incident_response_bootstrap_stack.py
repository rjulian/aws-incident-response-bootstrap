import aws_cdk as core
import aws_cdk.assertions as assertions

from aws_incident_response_bootstrap.aws_incident_response_bootstrap_stack import AwsIncidentResponseBootstrapStack

# example tests. To run these tests, uncomment this file along with the example
# resource in aws_incident_response_bootstrap/aws_incident_response_bootstrap_stack.py
def test_guardduty_created():
    app = core.App()
    stack = AwsIncidentResponseBootstrapStack(app, "aws-incident-response-bootstrap")
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties("AWS::GuardDuty::Detector", {
        "Enable": True
    })

def test_sns_created():
    app = core.App()
    stack = AwsIncidentResponseBootstrapStack(app, "aws-incident-response-bootstrap")
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties("AWS::SNS::Topic", {
        "DisplayName": "GuardDuty Alerting Topic"
    })

    template.has_resource_properties("AWS::SNS::Subscription", {
        "Protocol": "email"
    })

def test_eventbridge_rule_and_target_created():
    app = core.App()
    stack = AwsIncidentResponseBootstrapStack(app, "aws-incident-response-bootstrap")
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties("AWS::Events::Rule", {
        "State": "ENABLED",
    })

def test_securityhub_created():
    app = core.App()
    stack = AwsIncidentResponseBootstrapStack(app, "aws-incident-response-bootstrap")
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties("AWS::SecurityHub::Hub", {
    })
