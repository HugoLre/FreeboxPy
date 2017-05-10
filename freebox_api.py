import json
import requests
import time
import hmac
import base64

class FreeboxAPI():
    def __init__(self, app_token = ""):
        # Variables
        self.api_url = "http://mafreebox.freebox.fr/api/v4/"
        self.app_id = "py.freebox"
        self.app_name = "FreeboxPy"
        self.app_version = "0.1"
        self.device_name = "FreeboxPyHost"
        self.app_token = app_token
        # Methods
        self.connect()
        self.open_session()


    def __exit__(self):
        # Close session
        requests.post(api_url + "login/logout/")


    def get_challenge(self):
        # Get the actual "challenge token" from freebox (change often)
        ret = requests.get(self.api_url + "login/").json()
        self.challenge = ret["result"]["challenge"]


    def get_password(self):
        # Refresh challenge token
        self.get_challenge()
        # Hash app token with challenge token
        hashed = hmac.new(self.app_token.encode(), self.challenge.encode(), 'sha1')
        password = hashed.hexdigest()
        return (password)


    def check_connexion(self):
        # Check validity of app token
        datas = {
                    "app_id" : self.app_id,
                    "password" : self.get_password()
                }
        ret = requests.post(self.api_url + "login/session/", json=datas).json()
        # Return True if app token is OK
        if (ret["success"]):
            return (True)
        return (False)


    def connect(self):
        if (self.app_token == ""):
            # No token specified so not connected
            print("[FreeboxAPI] No token provided")
        else:
            # Token specified, check it
            if (self.check_connexion()):
                # Token is OK
                print("[FreeboxAPI] App token is OK, connected !")
                return
            else:
                # Token is incorrect
                print("[FreeboxAPI] App token is INCORRECT")
        # Not connected, so getting a new token
        print("[FreeboxAPI] App not connected, getting a new token")
        # Request a new token
        datas = {
                    "app_id" : self.app_id,
                    "app_name" : self.app_name,
                    "app_version" : self.app_version,
                    "device_name" : self.device_name
                }
        ret = requests.post(self.api_url + "login/authorize/", json=datas).json()
        self.app_token = ret["result"]["app_token"]
        self.track_id = ret["result"]["track_id"]
        # Wait for user to accept new app on Freebox Server screen
        while (1):
            ret = requests.get(self.api_url + "login/authorize/" + str(self.track_id)).json()
            status = ret["result"]["status"]
            if (status == "pending"):
                print("[FreeboxAPI] Waiting for you to grant access on Freebox Server (touch right arrow)")
                time.sleep(3)
            if (status == "unknown"):
                print("[FreeboxAPI] Token is revoked, abort")
                exit()
            if (status == "timeout"):
                print("[FreeboxAPI] You take too long to grant access, abort")
                exit()
            if (status == "denied"):
                print("[FreeboxAPI] You denied the access, abort")
                exit()
            if (status == "granted"):
                print("[FreeboxAPI] App was granted on Freebox Server, all good !")
                print("[FreeboxAPI] IMPORTANT: instantiate the FreeboxAPI class with the new token next time")
                print(self.app_token)
                break


    def open_session(self):
        # Request session token from Freebox
        datas = {
                    "app_id" : self.app_id,
                    "password" : self.get_password()
                }
        ret = requests.post(self.api_url + "login/session/", json=datas).json()
        # Save it
        self.session_token = ret["result"]["session_token"]
        # Save http header format for requests
        self.session_header = {"X-Fbx-App-Auth" : self.session_token}


    # Return active ips on LAN
    def get_active_ips(self):
        # Check if API is still connected
        if (not self.check_connexion()):
            # Not connected, reopen session
            self.open_session()
        # Get interfaces from freebox
        ret = requests.get(self.api_url + "lan/browser/interfaces/", headers=self.session_header).json()
        interfaces = ret["result"]
        # For each interface, add the ip to active_ips array
        active_ips = []
        for interface in interfaces:
            interface_name = interface["name"]
            # Get all the DHCP client for interface
            ret = requests.get(self.api_url + "lan/browser/" + interface_name + "/", headers=self.session_header).json()
            for device in ret["result"]:
                # For each device
                for connectivity in device["l3connectivities"]:
                    # For each connectivity on the device
                    if (connectivity["af"] == "ipv4" and connectivity["active"]):
                        # If connectivity is IPv4 and is active, add it
                        active_ips.append(connectivity["addr"])
        # End, return active_ips on LAN
        return (active_ips)
