from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

router_node = {
    "device_type": "cisco_ios",
    "host": "192.168.121.50",       # IP configured on the router
    "username": "admin",
    "password": "cisco123",
    "secret": "cisco123",         # Enable secret
}

try:
    print(f"Connecting to {router_node['host']}...")
    with ConnectHandler(**router_node) as net_connect:
        # Enter enable mode if not already at privilege level 15
        net_connect.enable()

        # Execute show command
        output = net_connect.send_command("show ip interface brief")
        print("\n--- Command Output ---")
        print(output)

except NetmikoTimeoutException:
    print(f"Connection timed out. Check IP reachability to {router_node['host']}.")
except NetmikoAuthenticationException:
    print("Authentication failed. Check username and password.")
except Exception as err:
    print(f"An unexpected error occurred: {err}")