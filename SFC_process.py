import algorithms
import openstack_setting as opset
from request import Request
from operator import attrgetter
import time


class VNF_Group(object):
    '''Define VNF attrivbute and methods'''

    def __init__(self, request, name, image_name):
        self.req = request
        self.name = name
        self.vnf_group = {}
        self.nova = opset.openstack_auth()
        self.image_name = image_name
        self.lifetime_factor = -1
        self.deadline = {}
        self.count = {}

    def get_vnf_group(self):
        self.vnf_group = algorithms.ILP_packing(self.req.resource, opset.find_flavor_list(self.nova))

    def vnf_deployment(self, vnf_group={}):

        if vnf_group == {}:
            vnf_group = self.vnf_group


        self.get_lifetime_factor()

        for flavor_id, vm_number in vnf_group.items():
            if vm_number > 0:
                vmtoresume_list = [vm.id for vm in opset.find_server_list(self.nova) if vm.status == 'SUSPENDED' and vm.flavor['id'] == flavor_id]
                if vm_number <= len(vmtoresume_list):
                    for j in range(vm_number):
                        opset.resume_vm(self.nova, vmtoresume_list[j])
                        self.count[vmtoresume_list[j]] = -1
                else:
                    flavor = opset.get_flavor(self.nova, flavor_id)
                    image = opset.get_image(self.nova, self.image_name)
                    opset.create_vm(vm_name=self.name+'_'+flavor.name,
                                    flavor=flavor,
                                    image=image,
                                    nova_client=self.nova,
                                    count=vm_number-len(vmtoresume_list))
                    if len(vmtoresume_list) != 0:
                        for resumeid in vmtoresume_list:
                            opset.resume_vm(self.nova, resumeid)
                            self.count[resumeid] = -1


        self.init_count()
        self.get_deadline()


                # to guarantee all VMs have been successfully created
                #time.sleep(0.5*vm_number)

    def get_lifetime_factor(self):
        buy = 5
        rental = 1
        delta = buy/rental
        self.lifetime_factor = int(delta)


    def get_deadline(self):
        self.get_lifetime_factor()
        vm_id_list = opset.get_newServerID_list(self.nova, opset.vmID_deadline_list)

        if vm_id_list:
            for id in vm_id_list:
                if self.lifetime_factor != -1:
                    self.deadline[id] = algorithms.ski_rental(self.lifetime_factor)


    def init_count(self):

        vm_id_list = opset.get_newServerID_list(self.nova, opset.vmID_count_list)
        if vm_id_list:
            for id in vm_id_list:
                self.count[id] = -1





    def update_count(self):
        vm_list = opset.find_server_list(self.nova)
        for vm in vm_list:
            if vm.status == 'SUSPENDED':
                self.count[vm.id] += 1


    def scaling(self, request):

        if not request.resource.equal(self.req.resource):
            self.update_depolyment(request)

        self.req = request

        vmID_list = [vm.id for vm in opset.find_server_list(self.nova) if vm.status == 'SUSPENDED']
        #print(vmID_list)
        for vmID in vmID_list:
            if self.count[vmID] >= self.deadline[vmID]:
                opset.remove_vm(self.nova, vmID)
                del self.count[vmID]
                del self.deadline[vmID]
                # need to add 'remove router' function


    def update_depolyment(self, request):

        flavor_list = opset.find_flavor_list(self.nova)
        new_vnf_group = algorithms.ILP_packing(request.resource, flavor_list)
        update_vnf_group = {}
        for key in new_vnf_group.keys():
            update_vnf_group[key] = new_vnf_group[key] - self.vnf_group[key]
        #print(update_vnf_group)
        self.vnf_group = new_vnf_group
        vnfGroup_to_deploy = {}
        vnfGroup_to_suspend = {}
        for key, value in update_vnf_group.items():
            if update_vnf_group[key] > 0:
                vnfGroup_to_deploy[key] = value
            elif update_vnf_group[key] < 0:
                vnfGroup_to_suspend[key] = -1 * value

        if vnfGroup_to_deploy != {}:
            self.vnf_deployment(vnfGroup_to_deploy)

        suspendErr_flag = 1
        while suspendErr_flag:
            vmtosuspend_list = []
            try:
                if vnfGroup_to_suspend != {}:
                    for flavor_id, vm_num in vnfGroup_to_suspend.items():
                        vm_list = [vm for vm in opset.find_server_list(self.nova) if vm.flavor['id'] == flavor_id and vm.status == 'ACTIVE']
                        vm_list = sorted(vm_list, key=attrgetter('id'))
                        for i in range(vm_num):
                            vmtosuspend_list.append(vm_list[i].id)
            except IndexError:
                time.sleep(3)
            else:
                for id in vmtosuspend_list:

                    opset.suspend_vm(self.nova, id)

                time.sleep(5)
                suspendErr_flag = 0

        self.update_count()

    def get_count(self):
        return self.count







if __name__ == '__main__':


    request1 = Request()
    request1.resource.set_resource(vcpu=4, ram=4, disk=10)
    vnf_test1 = VNF_Group(request1, name='test1', image_name='cirros')
    vnf_test1.get_vnf_group()
    vnf_test1.vnf_deployment()

    print('*' * 20)
    print(vnf_test1.get_count())
    print('*' * 20)

''''
    time.sleep(5)
    request2 = Request(2, 2, 10)
    vnf_test1.scaling(request2)
    print('*' * 20)
    print(vnf_test1.get_count())
    print(vnf_test1.deadline)
    print('*' * 20)
    input()

    time.sleep(5)
    request3 = Request(4, 4, 20)
    vnf_test1.scaling(request3)
    print('*' * 20)
    print(vnf_test1.get_count())
    print(vnf_test1.deadline)
    print('*' * 20)
    input()

    for n in range(5):
        time.sleep(5)
        request4 = Request(2, 2, 10)
        vnf_test1.scaling(request4)

        print('*' * 20)
        print(vnf_test1.get_count())
        print(vnf_test1.deadline)
        print('*' * 20)



        end_flag = int(input('input 0 for ending the program: '))
'''





