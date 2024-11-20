import xml.etree.ElementTree as ET

def create_experiment_xml(N, L, B):
    # Create the root element
    experiment = ET.Element('experiment', {'boot': 'kollaps:2.0'})

    # Create services element
    services = ET.SubElement(experiment, 'services')

    # Add dashboard service
    ET.SubElement(services, 'service', {
        'name': 'dashboard', 'image': 'kollaps/dashboard:1.0', 
        'supervisor': 'true', 'port': '8088'
    })

    # Add server services
    for i in range(1, N+1):
        ET.SubElement(services, 'service', {
            'name': f'server{i}', 'image': 'kauri', 'share': 'false', 
            'command': f"['bls','5','5','1','1','50','500','{N}','{i}']"
        })

    # Create bridges element
    bridges = ET.SubElement(experiment, 'bridges')

    # Add switch for each participant
    for i in range(1, N+1):
        ET.SubElement(bridges, 'bridge', {'name': f'switch{i}'})

    # Create links element
    links = ET.SubElement(experiment, 'links')
    
    # Add links between each server and its corresponding switch (with 750Kbps and 1ms)
    for i in range(1, N+1):
        ET.SubElement(links, 'link', {
            'origin': f'server{i}', 'dest': f'switch{i}', 
            'latency': '1', 'upload': B, 'download': B, 'network': 'kauri_network'
        })

    # Add links between each switch and all other switches (with 100Mbps and 50ms)
    for i in range(1, N+1):
        for j in range(i+1, N+1):
            ET.SubElement(links, 'link', {
                'origin': f'switch{i}', 'dest': f'switch{j}', 
                'latency': str(L), 'upload': '100Mbps', 'download': '100Mbps', 'network': 'kauri_network'
            })

    # Create dynamic element
    dynamic = ET.SubElement(experiment, 'dynamic')

    # Add schedule for joining servers
    for i in range(1, N+1):
        ET.SubElement(dynamic, 'schedule', {
            'name': f'server{i}', 'time': '0.0', 'action': 'join', 'amount': '1'
        })

    # Add schedule for leaving servers
    for i in range(1, N+1):
        ET.SubElement(dynamic, 'schedule', {
            'name': f'server{i}', 'time': '380.0', 'action': 'leave', 'amount': '1'
        })

    # Create a string representation of the XML
    tree = ET.ElementTree(experiment)
    xml_str = ET.tostring(experiment, encoding='unicode')

    return xml_str

# Example usage:
N = 31
L = 50  # Latency for switch-to-server
B = "750Kbps"  # Bandwidth for server-to-switch

xml_content = create_experiment_xml(N, L, B)
print(xml_content)

# Optionally, write to a file
with open('experiment.xml', 'w') as f:
    f.write(xml_content)
