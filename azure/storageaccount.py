########
# Copyright (c) 2015 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.

# Built-in Imports
import requests
import json
import constants
import utils
import sys
from cloudify.exceptions import NonRecoverableError
from azure import WindowsAzureConflictError
from azure import WindowsAzureMissingResourceError
from cloudify import ctx
from cloudify.decorators import operation

@operation
def storage_account_creation_validation(**_):
    storage_account_name = ctx.node.properties['vm_name']+'_storage_account'
    if storage_account_name in [storage_account_name for sa in utils.list_all_storage_accounts()]:
        ctx.logger.info("Storage account: " + storage_account_name + " successfully created.")
    else:
        ctx.logger.info("Storage Account " + storage_account_name + " creation validation failed..")
        sys.exit(1)


@operation
def create_storage_account(**_):
    location = ctx.node.properties['location']
    for property_key in constants.STORAGE_ACCOUNT_REQUIRED_PROPERTIES:
        utils.validate_node_property(property_key, ctx.node.properties)
    storage_account_name = ctx.node.properties['vm_name']+'_storage_account'
    resource_group_name = ctx.node.properties['vm_name']+'_resource_group'
    subscription_id = ctx.node.properties['subscription_id']
    ctx.logger.info("Checking availability of storage account: " + storage_account_name)
    if storage_account_name not in [storage_account_name for sa in utils.list_all_storage_accounts()]:
        try:
            ctx.logger.info("Creating new storage account: " + storage_account_name)
            storage_account_url= constants.azure_url+'/subscriptions/'+subscription_id+'/resourceGroups/'+resource_group_name+'/providers/Microsoft.Storage/storageAccounts/'+storage_account_name+'?api-version='+constants.api_version
            storage_account_params=json.dumps({"properties": {"accountType": constants.storage_account_type,}, "location": location})
            response_sa = requests.put(url=storage_account_url, data=storage_account_params, headers=constants.headers)
            print response_sa.text
        except WindowsAzureConflictError:
            ctx.logger.info("Storage Account " + storage_account_name + "could not be created.")
            sys.exit(1)
    else:
        ctx.logger.info("Storage Account " + storage_account_name + "has already been provisioned by another user.")


@operation
def delete_storage_account(**_):
    storage_account_name = ctx.node.properties['vm_name']+'_storage_account'
    resource_group_name = ctx.node.properties['vm_name']+'_resource_group'
    subscription_id = ctx.node.properties['subscription_id']
    ctx.logger.info("Deleting Storage Account"+storage_account_name)
    if storage_account_name in [storage_account_name for sa in utils.list_all_storage_account()]:
        try:
            storage_account_url='https://management.azure.com/subscriptions/'+subscription_id+'/resourceGroups/'+resource_group_name+'/providers/Microsoft.Storage/storageAccounts/'+storage_account_name+'?api-version='+constants.api_version
            response_sa = requests.delete(url=storage_account_url,headers=constants.headers)
            print response_sa.text

        except WindowsAzureMissingResourceError:
            ctx.logger.info("Storage Account " + storage_account_name + " could not be deleted.")
            sys.exit(1)
    else:
        ctx.logger.info("Storage Account " + storage_account_name + " does not exist.")


def _list_all_storage_accounts(**_):
    resource_group_name = ctx.node.properties['vm_name']+'_resource_group'
    subscription_id = ctx.node.properties['subscription_id']
    list_storage_accounts_url=constants.azure_url+'/subscriptions/'+subscription_id+'/resourceGroups/'+resource_group_name+'/providers/Microsoft.Storage/storageAccounts?api-version='+constants.api_version
    list_sa = requests.get(url=list_storage_accounts_url, headers = constants.headers)
    print list_sa.text
