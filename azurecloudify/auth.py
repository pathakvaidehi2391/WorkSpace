
import requests
import json
import time
from cloudify.exceptions import NonRecoverableError
from lockfile import LockFile
from cloudify import ctx, context
import constants
from cloudify.decorators import operation
import os.path


@operation
def generate_token(use_client_file=True, **kwargs):
    ctx.logger.info("In generate_token")
    endpoints, payload = _get_payload_endpoints()
    token, token_expires = _get_token_value_expiry(endpoints, payload)
    ctx.logger.info("In generate_token: token_expires {}".format(token_expires))
    try:
        json_data = {}
        with open(constants.path_to_local_azure_token_file, 'w') as f:
            json_data["auth_token"] = token
            json_data["token_expires"] = token_expires
            f.seek(0)
            f.write(json.dumps(json_data))
            f.close()
    except:
        raise NonRecoverableError("Failures while creating or using {}".format(constants.path_to_local_azure_token_file))

    ctx.instance.runtime_properties[constants.AUTH_TOKEN_VALUE] = token
    ctx.instance.runtime_properties[constants.AUTH_TOKEN_EXPIRY] = token_expires
    return token


def _get_token_value_expiry(endpoints, payload):
    response = requests.post(endpoints, data=payload).json()
    token = response['access_token']
    token_expires = response['expires_on']
    ctx.logger.info("_get_token_value_expiry token is {} ".format(token))
    return token, token_expires


# If client file is used (use_client_file==True), it means that this is during bootstrap
def get_auth_token(use_client_file=True, **kwargs):
    ctx.logger.info("In auth.get_auth_token")
    if use_client_file:
        if constants.AUTH_TOKEN_VALUE in ctx.instance.runtime_properties:
            # If you are here , it means that this is during bootstrap
            ctx.logger.info("In auth.get_auth_token returning token from runtime props")
            ctx.logger.info("In auth.get_auth_token token from runtime props is:{}".format(ctx.instance.runtime_properties[constants.AUTH_TOKEN_VALUE]))
            return ctx.instance.runtime_properties[constants.AUTH_TOKEN_VALUE]

        # Check if token file exists on the client's VM. If so, take the value from it and set it in the runtime
        ctx.logger.info("In auth.get_auth_token checking local azure file path {}".format(constants.path_to_local_azure_token_file))
        if os.path.isfile(constants.path_to_local_azure_token_file):
            # If you are here , it means that this is during bootstrap
            ctx.logger.info("{} exists".format(constants.path_to_local_azure_token_file))
            token, token_expires = get_token_from_client_file()
            ctx.logger.info("get_auth_token expiry is {} ".format(token_expires))
            ctx.instance.runtime_properties[constants.AUTH_TOKEN_VALUE] = token
            ctx.instance.runtime_properties[constants.AUTH_TOKEN_EXPIRY] = token_expires
            ctx.logger.info("get_auth_token token1 is {} ".format(token))
            return token

    # From here, this is not during bootstrap, which also means that this code runs on the manager's VM.
    try:
        ctx.logger.info("In auth.get_auth_token b4 locking {}".format(constants.path_to_azure_conf))
        lock = LockFile(constants.path_to_azure_conf)
        lock.acquire()
        ctx.logger.info("{} is locked".format(lock.path))
        with open(constants.path_to_azure_conf, 'r') as f:
            json_data = json.load(f)
            token_expires = json_data["token_expires"]
            token = json_data["auth_token"]
            ctx.logger.info("get_auth_token token2 is {} ".format(token))
    except:
        raise NonRecoverableError("Failures while locking or using {}".format(constants.path_to_azure_conf))

    ctx.logger.info("In auth.get_auth_token b4 timestamp")
    timestamp = int(time.time())
    ctx.logger.info("In auth.get_auth_token timestamp is {}".format(timestamp))
    ctx.logger.info("In auth.get_auth_token token_expires1 is {}".format(token_expires))
    token_expires = int(token_expires)
    ctx.logger.info("In auth.get_auth_token token_expires2 is {}".format(token_expires))
    if token_expires-timestamp <= 600 or token_expires == 0 or token is None or token == "":
        ctx.logger.info("In auth.get_auth_token token_expires-timestamp {}".format(token_expires-timestamp))
        endpoints, payload = _get_payload_endpoints()
        token, token_expires = _get_token_value_expiry(endpoints, payload)
        ctx.logger.info("get_auth_token token3 is {} ".format(token))
        ctx.logger.info("In auth.get_auth_token b4 opening {}".format(constants.path_to_azure_conf))
        with open(constants.path_to_azure_conf, 'r+') as f:
            json_data = json.load(f)
            json_data["auth_token"] = token
            json_data["token_expires"] = token_expires
            f.seek(0)
            f.write(json.dumps(json_data))
            f.close()
    lock.release()
    ctx.logger.info("{} is released".format(lock.path))
    ctx.logger.info("get_auth_token token4 is {} ".format(token))
    return token


@operation
def set_auth_token(azure_config, **kwargs):
    # This method invoked only during bootstrap (it's a relationship interface)
    ctx.source.instance.runtime_properties[constants.AUTH_TOKEN_VALUE] = ctx.target.instance.runtime_properties[constants.AUTH_TOKEN_VALUE]
    ctx.source.instance.runtime_properties[constants.AUTH_TOKEN_EXPIRY] = ctx.target.instance.runtime_properties[constants.AUTH_TOKEN_EXPIRY]


def _get_payload_endpoints():
    client_id = ctx.node.properties['client_id']
    aad_password = ctx.node.properties['aad_password']
    tenant_id = ctx.node.properties['tenant_id']
    endpoints = constants.login_url+'/'+tenant_id+'/oauth2/token'
    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': aad_password,
        'resource': constants.resource,
    }
    return endpoints, payload


def get_token_from_client_file():
    with open(constants.path_to_local_azure_token_file, 'r') as f:
        json_data = json.load(f)
        token_expires = json_data["token_expires"]
        token = json_data["auth_token"]
        f.close()

    ctx.logger.info("get_token_from_client_file expiry is {} ".format(token_expires))
    return token, token_expires


def get_credentials():
    subscription_id = ctx.node.properties['subscription_id']
    location = ctx.node.properties['location']
    credentials = 'Bearer ' + get_auth_token()
    headers = {"Content-Type": "application/json", "Authorization": credentials}
    return headers, location, subscription_id