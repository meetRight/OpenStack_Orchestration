from resource import Resource


class Request():

    def __init__(self, traffic={}):
        """
        :param traffic:流量
        :param resource: 资源
        """
        self.traffic = traffic
        self.resource = Resource()


    def traffic_to_resource(self):
        pass





