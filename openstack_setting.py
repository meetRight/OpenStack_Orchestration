import os
import time
from novaclient import client, exceptions
from novaclient.v2.images import GlanceManager
from novaclient.v2.flavors import FlavorManager
from novaclient.v2.servers import ServerManager

vmID_deadline_list = []
vmID_count_list = []


def openstack_auth():
    '''auth configuration'''
    auth_url = "http://192.168.210.110/compute/v2.1"
    username = 'admin'
    password = 'password'
    user_domain_name = 'Default'
    project_name = 'admin'
    project_domain_name = 'Default'
    project_id = 'e47b5904270d4b8a9644bc0fdb8aef6a'

    # 建立nova-client连接
    nova = client.Client(version=2,
                         username=username,
                         password=password,
                         project_id=project_id,
                         user_domain_name=user_domain_name,
                         project_domain_name=project_domain_name,
                         auth_url=auth_url)
    print('-------succeed--------')
    vms = nova.servers.list
    for vm in vms:
        print('vm {}   {}'.format(vm.name(), vm.id()))
    print(nova.servers.list())
    print(nova.flavors.list())
    return nova


def find_flavor_list(nova_client):
    FM = FlavorManager(nova_client)
    return FM.list()


def find_server_list(nova_clinet):
    SM = ServerManager(nova_clinet)
    return SM.list()


def get_flavor(nova_client, flavor_id):
    FM = FlavorManager(nova_client)
    return FM.get(flavor_id)


def get_image(nova_client, name_or_id):
    GM = GlanceManager(nova_client)
    return GM.find_image(name_or_id=name_or_id)


def create_vm(vm_name, flavor, image, nova_client, count):
    try:
        SM = ServerManager(nova_client)
        SM.create(name=vm_name, image=image, flavor=flavor, max_count=count, min_count=count)
    except exceptions.Conflict:
        print("This name has been used ")
        return False
    else:
        return True


def suspend_vm(nova_client,vm_id):
    SM = ServerManager(nova_client)
    SM.suspend(vm_id)


def remove_vm(nova_client, vm_id):
    if vm_id != 'f686bc62-0ff1-4576-a55e-92df18deb8d9':
        SM = ServerManager(nova_client)
        SM.delete(vm_id)


def get_newServerID_list(nova_client, vm_list):
    ''''get id list of existing VMs that are not int vm_list'''

    allvm_list = find_server_list(nova_client)
    vm_id_list = []
    for vm in allvm_list:
        if vm.id not in vm_list:
            vm_id_list.append(vm.id)
            vm_list.append(vm.id)
    return vm_id_list


def resume_vm(nova_client, vm_id):
    SM = ServerManager(nova_client)
    SM.resume(vm_id)


def remove_allvm(nova_client):
    SM = ServerManager(nova_client)
    for vm in SM.list():
        if vm.id != 'f686bc62-0ff1-4576-a55e-92df18deb8d9':
            SM.delete(vm.id)




if __name__ == '__main__':
    print("hello world")
    try:
        nova=openstack_auth()
        fl_list = find_flavor_list(nova)
        # create_vm(vm_name='tony2_server', flavor=fl_list[0], nova_client=nova)

        print('Congratuations')
    except:
        print('-------Failed--------')
