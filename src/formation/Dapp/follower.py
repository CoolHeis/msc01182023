from web3 import Web3
import math
import os
from dotenv import load_dotenv
from compile import compile_contract
import sys
from drone import Follower, Leader

"""
    The following three functions return a list of coordinates that correspond to a specific formation. 
    Available formations in the proposed smart contract are Vee, Line and Ring.
"""

def create_v_formation(num_drones, spacing):
    formation = []
    for i in range(num_drones):
        x = (i - (num_drones-1)/2) * spacing
        y = abs(x) * math.tan(math.pi/3)
        formation.append([x, y])
    return formation

def create_ring_formation(num_drones, radius):
    formation = [[0, 0]]
    for i in range(num_drones-1):
        angle = 2*math.pi*i/(num_drones-1)
        x = radius*math.cos(angle)
        y = radius*math.sin(angle)
        formation.append([x, y])
    return formation

def create_line_formation(num_drones, spacing):
    formation = []
    for i in range(num_drones):
        x = i * spacing
        y = 0
        formation.append([x, y])
    return formation

""" The next function can be used to calculate the follower's relative position with respect 
    to leader's position by using the relative_pos method from the Drone class. Assuming that 
    leader submits his position to the blockchain, it can be retrieved using the get_drone_data 
    method."""

def calculate_rel_pos_leader(follower, leader_add, contract_instance):
    location = ""
    data = follower.get_drone_data(contract_instance)
    for i in range(len(data)):
        if data[i][3] == leader_add:
            location = data[i][1]
    rel_pos_x, rel_pos_y = follower.relative_pos(location)
    return (rel_pos_x, rel_pos_y) 

""" Function for calculating euclidean distance between drone's location and a possible position
    in the formation."""

def eucl_dist(rel_pos, possible_pos):
    return math.sqrt((rel_pos[0]-possible_pos[0])**2 + (rel_pos[1]-possible_pos[1])**2)

""" The following function is used by drones in order to choose a specific position in the formation. 
    First they call get_available_positions method from Follower class and check which positions in 
    the formation are not occupied. Then by using select_position method from Follower class they can
    submit the position that is closest to them in the blockchain."""

def position_selection(distances, contract_instance, w3, follower):
    av_positions = follower.get_available_positions(contract_instance)
    for _ in range(len(av_positions)):
        min_dist = min(distances)
        position_to_be_selected = distances.index(min_dist)                    
        try:
            follower.select_position(contract_instance, w3, position_to_be_selected + 1)
            print('Position Submited Successfully in Blockchain')
            break
        except:                        
            pass
        print("Position " + str(position_to_be_selected+1) + " is already taken or u have already choose")
        distances[position_to_be_selected] = float('inf')
    
def main():
    """ Loading variables from .env, compiling smart contract and creating an instance,
        declaring a follower object (id, location as string, bettery level), using the 
        above formation functions and retrieve the coordinates list."""
    load_dotenv()
    URL_RPC = os.getenv("URL_RPC")
    w3 = Web3(Web3.HTTPProvider(URL_RPC))
    NUMB_DRONES = int(os.getenv("NUMB_DRONES"))

    abi, bytecode = compile_contract()

    contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    contract_address = os.getenv("CONTR_ADD")

    contract_instance = w3.eth.contract(address=contract_address, abi=abi)
    follower_1 = Follower(1, "31.3, 49.2", 95) #For each follower in terminals, modify the attributes as u wish(id, location, battery).
                                               #For instance follower_2 = Follower(2, "32.1, 47.2", 89) etc...                             
    leader_add = w3.eth.accounts[0]
    rel_pos = calculate_rel_pos_leader(follower_1, leader_add, contract_instance)
    
    positions_V = create_v_formation(NUMB_DRONES,3)
    positions_V.remove([0, 0])
    positions_Ring = create_ring_formation(NUMB_DRONES,3)
    positions_Ring.remove([0, 0])
    positions_Line = create_line_formation(NUMB_DRONES,3)
    positions_Line.remove([0, 0])

    distances_V = []
    distances_Ring = []
    distances_Line = []
    for pos in positions_V:
        distances_V.append(eucl_dist(rel_pos, pos))
    for pos in positions_Ring:
        distances_Ring.append(eucl_dist(rel_pos, pos))
    for pos in positions_Line:
        distances_Line.append(eucl_dist(rel_pos, pos))

    """ A simple UI to test smart contract functions acting as a follower. 
        If the leader is down,the election process takes place, and the drone 
        with the highest battery becomes the new leader."""
    while True:
        print("\nChecking who is the leader...")
        if follower_1.leader_address(contract_instance, w3) != w3.eth.accounts[follower_1.id]:
            print(f"[-] Drone with ID={follower_1.id}, is not the leader...")
            print("Submitting Battery Level...")
            follower_1.set_battery(follower_1.battery - 1)
            follower_1.submit_battery_level(contract_instance, w3, follower_1.battery)
            print("[+] Battery Level Submited Succesfully\n")

            print(""" What to do? 
                      1. Select position in the formation
                      2. Submit Data
                      3. Get Data 
                      4. Get available positions
                      5. Get Mission
                      6. Check Leader Status 
                      7. Quit""")
            choice = int(input('\n> '))
            match choice:
                case 1: 
                    missionID = int(input('Mission ID?:'))
                    missionFormation = int(follower_1.get_mission(contract_instance, missionID)[2])
                    if missionFormation == 1:
                        position_selection(distances_V, contract_instance, w3, follower_1)
                    elif missionFormation == 0:
                        position_selection(distances_Line, contract_instance, w3, follower_1)                            
                    elif missionFormation == 2:
                        position_selection(distances_Ring, contract_instance, w3, follower_1)  
                    else:
                        print("Error")                  
                case 2:
                    location = str(input('Location: '))
                    data = str(input('Data: '))
                    tx = follower_1.submit_data(contract_instance, w3, location, data)
                    print(f'Data Stored Successfully in Blockchain')
                case 3:
                    print()
                    print(follower_1.get_drone_data(contract_instance))
                case 4:
                    print('The available positions are:')
                    print(follower_1.get_available_positions(contract_instance))
                case 5:
                    missionID = int(input('Mission ID?:'))
                    print(follower_1.get_mission(contract_instance, missionID))
                case 6:
                    print("Checking if leader is up...")
                    follower_1.check_leader_status(contract_instance, w3)
                    if follower_1.leader_address(contract_instance, w3) == w3.eth.accounts[0]:
                        print("[+] Leader is UP.")
                    else:
                        print(f"[-] Leader is DOWN, New Leader Has Been Elected.")    
                        print(f"Leader's Address: {follower_1.leader_address(contract_instance, w3)}")
                case 7:
                    print('Exciting...')
                    sys.exit(0)

        """ The options' menu changes in the event that the follower becomes the new leader after 
            the election process takes place."""
        else:
            print(f"[+] Drone with ID={follower_1.id}, is the leader")
            lead = Leader(follower_1.id, follower_1.loaction, follower_1.battery)

            print("Sending HeartBeat Signal...")
            tx = lead.send_heartbeat(contract_instance, w3)
            print(f"[+] Signal Sent Successfully\n")

            print("Submitting Battery Level...")
            lead.set_battery(lead.battery - 1)
            lead.submit_battery_level(contract_instance, w3, lead.battery)
            print("[+] Battery Level Submited Succesfully\n")

            print(""" What to do?
                      1. Add drones in the swarm
                      2. Remove Drone
                      3. Create Mission
                      4. Update Mission
                      5. Activate Mission
                      6. Deactivate Mission
                      7. Submit Data
                      8. Quit""")
            choice = int(input('\n> '))
            match choice:
                case 1:
                    add = str(input("Give drone's address u want to add in the swarm"))
                    tx_rec=lead.add_drone(contract_instance, w3, add)
                    print(f'\n\nDrone - {add} Added Successfully.')
                case 2:
                    drone = str(input('Give the address of the drone u want to remove: '))
                    tx = lead.remove_drone(contract_instance, w3, drone)
                    print(f'Drone - {drone} Removed Successfully.')
                case 3:
                    missionName = str(input('Mission Name: '))
                    print('Choose a mission type: 0 for Search, 1 for Dive & Attack, 2 for City Surveillance')
                    missionType = int(input('> '))
                    if missionType == 0:
                        formationType = 2 #Circle
                        lead.create_mission(contract_instance, w3, missionName, missionType, formationType)
                    elif missionType == 1:
                        formationType = 1 #V
                        lead.create_mission(contract_instance, w3, missionName, missionType, formationType)
                    else:
                        formationType = 0 #Line
                        lead.create_mission(contract_instance, w3, missionName, missionType, formationType)  
                    print('Mission Created Successfully')
                case 4:
                    missionID = int(input('Give ID of mission u want to update: '))
                    missionName = str(input('Give new name: '))
                    print('Choose a mission type: 0 for Search, 1 for Dive & Attack, 2 for City Surveillance')
                    missionType = int(input('> '))
                    if missionType == 0:
                        formationType = 2 #Circle
                        lead.update_mission(contract_instance, w3, missionID, missionName, missionType, formationType)
                    elif missionType == 1:
                        formationType == 1 #V
                        lead.update_mission(contract_instance, w3, missionID, missionName, missionType, formationType)
                    else:
                        formationType == 0 #Line
                        lead.update_mission(contract_instance, w3, missionID, missionName, missionType, formationType) 
                    print('Mission Updated Successfully')
                case 5:
                    missionID = int(input('Give ID of mission u want to activate: '))  
                    lead.activate_mission(contract_instance, w3, missionID)
                    print('Mission Activated Successfully')
                case 6:
                    missionID = int(input('Give ID of mission u want to de-activate: '))  
                    lead.deactivate_mission(contract_instance, w3, missionID)
                    print('Mission de-Activated Successfully')
                case 7:
                    location = str(input('Location: '))
                    data = str(input('Data: '))
                    tx = lead.submit_data(contract_instance, w3, location, data)
                    print(f'Data Stored Successfully in Blockchain')
                case 8:
                    print('Exciting...')
                    sys.exit(0)


if __name__ == '__main__':
    main()
