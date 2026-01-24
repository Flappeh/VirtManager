import requests
import sys
import urllib3
import asyncio

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


VCENTER_HOST = "https://vcenter.ict.lab"
VCENTER_USER = "iko@vsphere.local"
VCENTER_PASS = "P@ssw0rd"

class VCenterUtils:
    def __init__(self, host: str, user: str, pwd: str):
        self.host = host
        self.user = user
        self.password = pwd
        self.session: requests.Session = self.create_session()
        self.auth_token = ""
        
    def create_session(self):
        session = requests.Session()
        return session

    def get_vcenter_session(self):
        try:
            rsp = self.session.post(
                url=f"{self.host}/api/session",
                auth=(self.user,self.password),
                verify=False
            )
            if rsp.status_code == 201:
                self.auth_token = rsp.text.replace('"', '')
            else:
                print("Error getting vCenter Session")
                sys.exit()
        
        except Exception as e:
            print(f"Error {e}")
            sys.exit()

    def get_vcenter_cluster_list(self):
        try:
            data = self.request_vcenter_resource('/api/vcenter/cluster')
            for i in data:
                print(i)
        except Exception as e:
            print(f"Error occured : {e}")

    def get_vcenter_datacenter_list(self):
        try:
            data = self.request_vcenter_resource('/api/vcenter/datacenter')
            for i in data:
                print(i)
        except Exception as e:
            print(f"Error occured : {e}")

    def get_vcenter_vm_list(self):
        try:
            data = self.request_vcenter_resource('/api/vcenter/vm')
            for i in data:
                print(i)
        except Exception as e:
            print(f"Error occured : {e}")

    def get_vcenter_datastore_list(self):
        try:
            data = self.request_vcenter_resource('/api/vcenter/datastore')
            for i in data:
                print(i)
        except Exception as e:
            print(f"Error occured : {e}")

    def get_vcenter_host_list(self):
        try:
            data = self.request_vcenter_resource('/api/vcenter/host')
            for i in data:
                print(i)
        except Exception as e:
            print(f"Error occured : {e}")

    def get_vcenter_network_list(self):
        try:
            data = self.request_vcenter_resource('/api/vcenter/network')
            for i in data:
                print(i)
        except Exception as e:
            print(f"Error occured : {e}")

    def request_vcenter_resource(self, path: str):
        try:
            rsp = self.session.get(
                url = self.host + path,
                headers={
                    "vmware-api-session-id": self.auth_token
                },
                verify=False
            )
            data = rsp.json()
            return data
        
        except Exception as e:
            print(f"Error occured when requesting resource, {e}")
    
        
if __name__ == "__main__":
    vcenter_app = VCenterUtils(VCENTER_HOST, VCENTER_USER, VCENTER_PASS)
    vcenter_app.get_vcenter_session()
    print("Cluster List")
    vcenter_app.get_vcenter_cluster_list()
    print("Datacenter List")
    vcenter_app.get_vcenter_datacenter_list()
    print("Datastore List")
    vcenter_app.get_vcenter_datastore_list()
    print("Host List")
    vcenter_app.get_vcenter_host_list()
    print("Network List")
    vcenter_app.get_vcenter_network_list()
    print("VM List")
    vcenter_app.get_vcenter_vm_list()
