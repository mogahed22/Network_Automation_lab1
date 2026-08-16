from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

# Management connection parameters (Ethernet0/1 connected to Cloud0)
router_nodes = {
    "router1": {
        "device_type": "cisco_ios",
        "host": "192.168.121.50",
        "username": "admin",
        "password": "cisco123",
        "secret": "cisco123",
    },
    "router2": {
        "device_type": "cisco_ios",
        "host": "192.168.121.51",
        "username": "admin",
        "password": "cisco123",
        "secret": "cisco123",
    },
    "router3": {
        "device_type": "cisco_ios",
        "host": "192.168.121.52",
        "username": "admin",
        "password": "cisco123",
        "secret": "cisco123",
    },
}

# Data-plane interfaces, peer ping targets, and OSPF configurations
router_configs = {
    "router1": {
        "interfaces": {
            "Ethernet0/0": "10.1.1.1 255.255.255.0",  # To R2 (Ethernet0/0)
            "Ethernet0/2": "11.1.1.1 255.255.255.0",  # To R3 (Ethernet0/0)
        },
        "peer_ips": ["10.1.1.2", "11.1.1.2"],
        "ospf": [
            "router ospf 1",
            "network 10.1.1.0 0.0.0.255 area 0",
            "network 11.1.1.0 0.0.0.255 area 1",
        ],
    },
    "router2": {
        "interfaces": {
            "Ethernet0/0": "10.1.1.2 255.255.255.0",  # To R1 (Ethernet0/0)
        },
        "peer_ips": ["10.1.1.1"],
        "ospf": [
            "router ospf 1",
            "network 10.1.1.0 0.0.0.255 area 0",
        ],
    },
    "router3": {
        "interfaces": {
            "Ethernet0/0": "11.1.1.2 255.255.255.0",  # To R1 (Ethernet0/2)
        },
        "peer_ips": ["11.1.1.1"],
        "ospf": [
            "router ospf 1",
            "network 11.1.1.0 0.0.0.255 area 1",
        ],
    },
}

verification_commands = [
    "show ip interface brief",
    "show ip ospf neighbor",
    "show ip route ospf",
]

# Apply configurations and verify
for router_name, device_params in router_nodes.items():
    try:
        print(f"\n{'='*25} Configuring {router_name} ({device_params['host']}) {'='*25}")
        with ConnectHandler(**device_params) as net_connect:
            net_connect.enable()

            # 1. Configure Data-Plane Interfaces
            interface_commands = []
            for intf, ip_mask in router_configs[router_name]["interfaces"].items():
                interface_commands.extend([
                    f"interface {intf}",
                    "no shutdown",
                    f"ip address {ip_mask}",
                ])
            print("\n--- Pushing Interface Configs ---")
            print(net_connect.send_config_set(interface_commands))

            # 2. Configure OSPF
            print("\n--- Pushing OSPF Configs ---")
            print(net_connect.send_config_set(router_configs[router_name]["ospf"]))

            # 3. Direct Link Reachability Test
            print("\n--- Direct Neighbor Ping ---")
            for peer in router_configs[router_name]["peer_ips"]:
                print(f"Pinging {peer}...")
                print(net_connect.send_command(f"ping {peer}"))

            # 4. Routing & Neighbor State Verification
            print("\n--- Routing & Adjacency State ---")
            for cmd in verification_commands:
                print(f"\n[Command: {cmd}]")
                print(net_connect.send_command(cmd))

    except NetmikoTimeoutException:
        print(f"[ERROR] Connection timed out to {device_params['host']}.")
    except NetmikoAuthenticationException:
        print(f"[ERROR] Authentication failed for {device_params['host']}.")
    except Exception as err:
        print(f"[ERROR] Unexpected error on {router_name}: {err}")