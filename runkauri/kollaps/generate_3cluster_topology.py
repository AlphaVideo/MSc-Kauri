import xml.etree.ElementTree as ET

def create_experiment_xml(N, L_intra, B_intra, L_inter_A_B, B_inter_A_B, L_inter_B_C, B_inter_B_C, L_inter_A_C, B_inter_A_C):
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
            'command': f"['bls','5','3','1','1','50','500','{N}','{i}']"
        })

    # Create bridges element
    ET.SubElement(experiment, 'bridges')

    # Create links element
    links = ET.SubElement(experiment, 'links')
    
    # Define clusters
    cluster_A = list(range(1, 11))
    cluster_B = list(range(11, 21))
    cluster_C = list(range(21, 32))
    
    # Function to determine if two nodes are in the same cluster
    def same_cluster(node1, node2):
        return ((node1 in cluster_A and node2 in cluster_A) or
                (node1 in cluster_B and node2 in cluster_B) or
                (node1 in cluster_C and node2 in cluster_C))

    # Function to get inter-cluster latency and bandwidth
    def get_inter_cluster_params(node1, node2):
        if (node1 in cluster_A and node2 in cluster_B) or (node1 in cluster_B and node2 in cluster_A):
            return L_inter_A_B, B_inter_A_B
        elif (node1 in cluster_B and node2 in cluster_C) or (node1 in cluster_C and node2 in cluster_B):
            return L_inter_B_C, B_inter_B_C
        elif (node1 in cluster_A and node2 in cluster_C) or (node1 in cluster_C and node2 in cluster_A):
            return L_inter_A_C, B_inter_A_C
        return None, None

    # Add links between servers
    for i in range(1, N+1):
        for j in range(i+1, N+1):
            if same_cluster(i, j):
                # Intra-cluster links
                ET.SubElement(links, 'link', {
                    'origin': f'server{i}', 'dest': f'server{j}', 
                    'latency': str(L_intra), 'upload': B_intra, 'download': B_intra, 'network': 'kauri_network'
                })
            else:
                # Inter-cluster links
                latency, bandwidth = get_inter_cluster_params(i, j)
                if latency and bandwidth:
                    ET.SubElement(links, 'link', {
                        'origin': f'server{i}', 'dest': f'server{j}', 
                        'latency': str(latency), 'upload': bandwidth, 'download': bandwidth, 'network': 'kauri_network'
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

# Latency and bandwidth for intra-cluster links
L_intra = 50  # Latency in milliseconds
B_intra = "750Kbps"  # Bandwidth

# Latency and bandwidth for inter-cluster links (A <-> B, B <-> C, A <-> C)
L_inter_A_B = 150  # Latency between cluster A and B
B_inter_A_B = "750Kbps"  # Bandwidth between cluster A and B

L_inter_B_C = 150  # Latency between cluster B and C
B_inter_B_C = "750Kbps"  # Bandwidth between cluster B and C

L_inter_A_C = 250  # Latency between cluster A and C
B_inter_A_C = "750Kbps"  # Bandwidth between cluster A and C

# Generate XML content
xml_content = create_experiment_xml(N, L_intra, B_intra, L_inter_A_B, B_inter_A_B, L_inter_B_C, B_inter_B_C, L_inter_A_C, B_inter_A_C)
print(xml_content)

# Optionally, write to a file
with open('experiment_heterogeneous.xml', 'w') as f:
    f.write(xml_content)
