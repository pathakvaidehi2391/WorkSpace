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
def public_ip_creation_validation(**_):
    public_ip_name = ctx.node.properties['vm_name']+'_pip'
    if public_ip_name in [public_ip_name for pip in _list_all_public_ips()]:
        ctx.logger.info("Public IP: " + public_ip_name + " successfully created.")
    else:
        ctx.logger.info("Public IP" + public_ip_name + " creation validation failed..")
        sys.exit(1)
       
@operation
def create_public_ip(**_):
    vm_name=ctx.node.properties['vm_name']
    public_ip_name=:vm_name+'_pip'
    subscription_id = ctx.node.properties['subscription_id']
    location = ctx.node.properties['location']
    resource_group_name = ctx.node.properties['vm_name']+'_resource_group'
    public_ip_url=constants.azure_url+'/subscriptions/'+subscription_id+'/resourceGroups/'+resource_group_name+'/providers/microsoft.network/publicIPAddresses/'+public_ip_name+'?api-version={api-version}='+constants.api_version
    if public_ip_name not in [public_ip_name for pip in _list_all_public_ips()]:
        try:
            ctx.logger.info("Creating new public ip : " + public_ip_name)
            public_ip_params=json.dumps({
                    "location": location,
                    "name":public_ip_name,
                    "properties": {
                        "publicIPAllocationMethod": "Static",
                        "idleTimeoutInMinutes": 4,
                    }
                }
            )
        except WindowsAzureConflictError:
            ctx.logger.info("Public IP" + public_ip_name + "could not be created.")
        sys.exit(1)
    else:
        ctx.logger.info("Public IP" + public_ip_name + "has already been assigned to another VM")


def delete_public_ip():
    public_ip_name = ctx.node.properties['vm_name']+'_pip'
    subscription_id = ctx.node.properties['subscription_id']
    resource_group_name = ctx.node.properties['vm_name']+'_resource_group'
    if public_ip_name  in [public_ip_name for pip in _list_all_public_ips()]:
        try:
            ctx.logger.info("Deleting Public IP")
            public_ip_url='https://management.azure.com/subscriptions/'+subscription_id+'/resourceGroups/'+resource_group_name+'/providers/microsoft.network/ publicIPAddresses/'+public_ip_name+'?api-version='+constants.api_version
            response_pip = requests.delete(url=public_ip_url,headers=constants.headers)
            print(response_pip.text)
        except WindowsAzureMissingResourceError:
            ctx.logger.info("Public IP " + public_ip_name + " could not be deleted.")
        sys.exit(1)
    else:
        ctx.logger.info("Public IP " + public_ip_name + " does not exist.")


def _list_all_public_ips(**_):
    resource_group_name = ctx.node.properties['vm_name']+'_resource_group'
    subscription_id = ctx.node.properties['subscription_id']
    list_public_ips_url=constants.azure_url+'/subscriptions/'+subscription_id+'/resourceGroups/'+resource_group_name+'/providers/microsoft.network/publicIPAddresses?api-version='+constants.api_version
    list_public_ips = requests.get(url=list_public_ips_url, headers = constants.headers)
    print list_public_ips.text
    #public_ips_list= #extract public_ips
    #return public_ips_list