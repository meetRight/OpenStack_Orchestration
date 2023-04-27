from openstack import connection

def openstack_connection():
    conn = connection.Connection(
        region_name='RegionOne',
        auth=dict(
            auth_url='http://192.168.210.110/identity',
            username='admin',
            password='password',
            project_id='e47b5904270d4b8a9644bc0fdb8aef6a',
            user_domain_id='default'),
        compute_api_version='2',
        identity_interface='public')

    return conn

def list_endpoints(conn):
    print("List Endpoints:")

    for endpoint in conn.identity.endpoints():
        print(endpoint)

def list_servers(conn):
    print('List Servers ')
    servers = conn.compute.servers(details=False, all_projects=True)

    for server in servers:
        if len(server.name.split('-')) == 4:
            server_type = server.name.split('-')[3].lower()
            if server_type == 'udm':
                print(server.name)

def start_server(conn, server_name):    
    Server = conn.compute.find_server(server_name)
    
    if Server.status == 'ACTIVE':
        print("The Server is ACTIVE")
    else:
        print("Start Server "+ server_name)
        conn.compute.start_server(Server)


if __name__ == '__main__':
    
    try:
        conn=openstack_connection()
    except:
        print('-------Connection Failed--------')
    
    start_server(conn, server_name='slice-1293-2313-UDM')