class Drone:
"""
A simple class for simulating swarm drones in Dapp and checking smart contract's functionality. 

Attributes: id (Drone's ID)
            location (Drone's location)
            battery (Drone's battery level)
"""


    def __init__(self, id, location, battery) -> None:
        self.id = id
        self.location = location
        self.battery = battery

    def set_battery(self, battery):
        self.battery = battery
    
    def __str__(self) -> str:
        return f'Drone:ID={self.id}, Position=({self.location})'
    
    def relative_pos(self, pos):
        """Calculates drone's relative coordinates to a specific reference point.""" 
        coords_self = self.location.split(", ")
        x_self = float(coords_self[0])
        y_self = float(coords_self[1])
        coords_other = pos.split(", ")
        x_other = float(coords_other[0])
        y_other = float(coords_other[1])
        x_relative = x_self - x_other
        y_relative = y_self - y_other
        return x_relative, y_relative

class Leader(Drone):

    """
    This class inherits from Drone and has as methods all the smart contract's available functions for Leader. Same for the Follower class.
    """

    def __init__(self, id, location, battery) -> None:
        super().__init__(id, location, battery)

    def add_drone(self, contract_instance, w3, drone_address):
        tx_hash = contract_instance.functions.addDrone(drone_address).transact({"from": w3.eth.accounts[self.id]})
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_receipt

    def remove_drone(self, contract_instance, w3, drone_address):
        tx_hash = contract_instance.functions.removeDrone(drone_address).transact({"from": w3.eth.accounts[self.id]})
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_receipt

    def create_mission(self, contract_instance, w3, mission_name, mission_type, formation_type):
        tx_hash = contract_instance.functions.createMission(mission_name, mission_type, formation_type).transact({"from": w3.eth.accounts[self.id]})
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_receipt

    def update_mission(self, contract_instance, w3, missionId, mission_name, mission_type, formation_type):
        tx_hash = contract_instance.functions.updateMission(missionId, mission_name, mission_type, formation_type).transact({"from": w3.eth.accounts[self.id]})
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_receipt

    def activate_mission(self, contract_instance, w3, missionId):
        tx_hash = contract_instance.functions.activateMission(missionId).transact({"from": w3.eth.accounts[self.id]})
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_receipt

    def deactivate_mission(self, contract_instance, w3, missionId):
        tx_hash = contract_instance.functions.deactivateMission(missionId).transact({"from": w3.eth.accounts[self.id]})
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_receipt

    def get_available_positions(self, contract_instance):
        return contract_instance.functions.getAvailablePositions().call()
    
    def submit_data(self, contract_instance, w3, location, data):
        tx_hash = contract_instance.functions.submitData(location, data).transact({"from": w3.eth.accounts[self.id]})
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_receipt
    
    def send_heartbeat(self, contract_instance, w3):
        tx_hash = contract_instance.functions.sendHeartbeat().transact({"from": w3.eth.accounts[self.id]})
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_receipt
    
    def submit_battery_level(self, contract_instance, w3, battery):
        tx_hash = contract_instance.functions.submitBatteryLevel(battery).transact({"from": w3.eth.accounts[self.id]})
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_receipt
        

class Follower(Drone):
    def __init__(self, id, location, battery) -> None:
        super().__init__(id, location, battery)

    def select_position(self, contract_instance, w3, position):
        tx_hash = contract_instance.functions.assignPosition(position).transact({"from": w3.eth.accounts[self.id]})
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_receipt

    def submit_data(self, contract_instance, w3, location, data):
        tx_hash = contract_instance.functions.submitData(location, data).transact({"from": w3.eth.accounts[self.id]})
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_receipt

    def get_drone_data(self, contract_instance):
        return contract_instance.functions.getDroneData().call()

    def get_available_positions(self, contract_instance):
        return contract_instance.functions.getAvailablePositions().call()

    def get_mission(self, contract_instance, missionId):
        return contract_instance.functions.getMission(missionId).call()
    
    def check_leader_status(self, contract_instance, w3):
        tx_hash = contract_instance.functions.checkLeaderStatus().transact({"from": w3.eth.accounts[self.id]})
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_receipt
    
    def leader_is_alive(self, contract_instance, w3):
        return contract_instance.functions.leaderIsAlive().call({"from": w3.eth.accounts[self.id]})

    def submit_battery_level(self, contract_instance, w3, battery):
        tx_hash = contract_instance.functions.submitBatteryLevel(battery).transact({"from": w3.eth.accounts[self.id]})
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_receipt
    
    def leader_address(self, contract_instance, w3):
        return contract_instance.functions.leader().call({"from": w3.eth.accounts[self.id]})
