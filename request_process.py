class Request():

    def __init__(self,vcpus,ram,disk):
        self.resource = Resource(vcpus,ram,disk)


class Resource():

    def __init__(self,vcpus,ram,disk):
        self.vcpus = vcpus
        self.ram = ram
        self.disk = disk

    def equal(self, new_resource):
        if (self.ram == new_resource.ram) and (self.vcpus == new_resource.vcpus) and (self.disk == new_resource.disk):
            return True
        else:
            return False

