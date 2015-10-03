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
from requests import Request,Session,Response
import json
import constants
import sys
import os
import auth
import utils
from cloudify.exceptions import NonRecoverableError
from cloudify import ctx
from cloudify.decorators import operation

@operation
def creation_validation(**_):
    for property_key in constants.VNET_REQUIRED_PROPERTIES:
        _validate_node_properties(property_key, ctx.node.properties)


@operation
#vnet:
def create_vnet(**_):
    if ctx.node.properties['use_external_resource']
        if not resource_group:
            raise NonRecoverableError(
                'External resource, but the supplied '
                'resource group does not exist in the account.')
                sys.exit(1)
        else
            ctx.instance.runtime_properties['existing_resource_group_name']
    else
        for property_key in constants.VNET_REQUIRED_PROPERTIES:
            _validate_node_properties(property_key, ctx.node.properties)
        vm_name=ctx.node.properties['vm_name']
        RANDOM_SUFFIX_VALUE = utils.random_suffix_generator()
        resource_group_name = vm_name+'_resource_group'+RANDOM_SUFFIX_VALUE
        vnet_name = vm_name+'_vnet'
        location = ctx.node.properties['location']
        subscription_id = ctx.node.properties['subscription_id']
        
        credentials='Bearer '+ auth.get_token_from_client_credentials()
        
        headers = {"Content-Type": "application/json", "Authorization": credentials}
        
        vnet_url = constants.azure_url+'/subscriptions/'+subscription_id+'/resourceGroups/'+resource_group_name+'/providers/microsoft.network/virtualNetworks/'+vnet_name+'?api-version='+constants.api_version
        ctx.logger.info("Checking availability of virtual network: " + vnet_name)
    
        if 1:
            try:
                ctx.logger.info("Creating new virtual network: " + vnet_name)
        
                vnet_params=json.dumps({"name":vnet_name, "location": location,"properties": {"addressSpace": {"addressPrefixes": constants.vnet_address_prefixes},"subnets": [{"name": constants.subnet_name, "properties": {"addressPrefix": constants.address_prefix}}]}})
                response_vnet = requests.put(url=vnet_url, data=vnet_params, headers=headers)
                print response_vnet.text
            except:
                ctx.logger.info("Virtual Network " + vnet_name + "could not be created.")
                sys.exit(1)
        else:
            ctx.logger.info("Virtual Network" + vnet_name + "has already been provisioned by another user.")
     
    
    @operation
    def delete_vnet(**_):
        vm_name=ctx.node.properties['vm_name']
        vnet_name = vm_name+'_vnet'
        resource_group_name = vm_name+'_resource_group'
        subscription_id = ctx.node.properties['subscription_id']
        
        credentials='Bearer '+ auth.get_token_from_client_credentials()
        
        headers = {"Content-Type": "application/json", "Authorization": credentials}
        
        ctx.logger.info("Checking availability of virtual network: " + vnet_name)
        if 1:
            try:
                ctx.logger.info("Deleting the virtual network: " + vnet_name)
                vnet_url = constants.azure_url+'/subscriptions/'+subscription_id+'/resourceGroups/'+resource_group_name+'/providers/microsoft.network/virtualNetworks/'+vnet_name+'?api-version='+constants.api_version
                response_vnet = requests.delete(url=vnet_url,headers=headers)
                print response_vnet.text
    
            except:
                ctx.logger.info("Virtual Network " + vnet_name + " could not be deleted.")
            sys.exit(1)
        else:
            ctx.logger.info("Virtual Network " + vnet_name + " does not exist.")


def _validate_node_properties(key, ctx_node_properties):
    if key not in ctx_node_properties:
        raise NonRecoverableError('{0} is a required input. Unable to create.'.format(key))
