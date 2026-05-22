from datetime import datetime

"""MODULE 4: Surveillance and reports"""

class NetworkMonitor:
    
    """This class tracks equipment status, packet statistics, and link usage."""
    
    def __init__(self, topology):
        self.topology = topology
        self.packet_history = []
        self.stats={} #Dictionary to store the statistics
        
    def log_packet(self,packet,status="transmitted"):  #Audree has to call this function and update statistics whenever the packet is sent
        timestamp = datetime.now().strftime("%YYYY-%mm-%dd %H:%M:%S")
        entry = f"[{timestamp}]{packet.protocol} from {packet.src} to {packet.dest} - {status}"
        self.packet_history.append(entry)
        if len(self.packet_history)>10:
            self.packet_history.pop(0)
            
    def update_stats(self,equip_name, success=True):
        if equip_name not in self.stats:
            self.stats[equip_name]={'sent':0, 'lost':0}
        if success:
            self.stats[equip_name]['sent'] += 1
        else:
            self.stats[equip_name]['lost'] += 1
            
    def calculate_link_usage(self,link,packet):
        packet_megabits = (packet.size * 8)/1_000_000
        usage_percent = (packet_megabits / link.bandwidth) * 100
        return round(usage_percent, 4)
    
    def generate_report(self):
        with open("rapport_simnet.txt","w") as f:
            f.write( "=== SIMNet MODULE 4: NETWORK REPORT ===\n" )
            f.write(f"Generated on{datetime.now()}\n\n")
            f.write("1. EQUIPEMENT STATUS:\n")
            for equip in self.topology.equipements:
                status = "ACTIVE" if equip.status == "actif" else "INACTIVE"
                f.write(f"-{equip.name}: {status}\n")
            f.write("\n2. TRAFFIC STATISTICS:\n")
            for name, data in self.stats.items():
                f.write(f"-{name}: {data['sent']} Passed, {data['lost']} Lost\n")
            f.write("\n3. PACKET LOG (Last 10):\n")
            for log in self.packet_history:
                f.write(f" {log}\n")
            print("Report generated successfully.")
        
        
        
        
    def calculate_link_load(self,link,packet):
        """  Calculates what percentage of the link's bandwidth a single packet represents. """
        
        packet_megabits = (packet.size * 8)/1000000
        usage_percent = (packet_megabits / link.bandwidth) * 100
        
        return round(usage_percent,4)
    
    def get_topology_utilization(sekf):
        """ Returns a summary of how busy the liks are."""
        
        report_lines = []
        for link in self.topology.links:
            usage = f"Link {link.id}: Bandwidth{link.bandwidth} Mbps, Latency {link.latency} ms"
            report_lines.append(usage)
        return report_lines