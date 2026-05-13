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