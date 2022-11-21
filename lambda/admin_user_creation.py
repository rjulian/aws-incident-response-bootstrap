import json
import boto3


def handler(event, _):
    """Simple example handler for analyzing a CreateUser API call."""
    print(f"Incoming request: {json.dumps(event)}")

    event_payload = json.loads(event["Records"][0]["body"])

    user_name = event_payload["detail"]["responseElements"]["user"].get("userName")

    iam_client = boto3.client("iam")

    user_policies = iam_client.list_attached_user_policies(UserName=user_name)

    for policy in user_policies["AttachedPolicies"]:
        if "administrator" in policy["PolicyName"].downcase:
            print("Alert! Administrator Policy has been attached to user.")
