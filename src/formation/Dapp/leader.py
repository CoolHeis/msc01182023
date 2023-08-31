from web3 import Web3
#import json
import os
from dotenv import load_dotenv
from compile import compile_contract
import sys
from drone import Leader


def main():
  """ Before running follower.py, it is necessary to run this file and add some drones to the swarm with 
      option 1. Next, submit the leader's location using option 7. After, create a mission and declare a specific 
      formation with option 3. Finally, activate the mission and run the follower.py files in separate terminals.
      This procedure could be automated, but I decided to use an UI to see how it works by following
      all the steps one by one. Drone registration, mission creation and activation, position selecting 
      and the creation of the formation processes are automated in the gazebo sim.   
  """
    load_dotenv()
    URL_RPC = os.getenv("URL_RPC")
    NUMB_DRONES = int(os.getenv("NUMB_DRONES"))
    w3 = Web3(Web3.HTTPProvider(URL_RPC))

    abi, bytecode = compile_contract()

    contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    contract_address = os.getenv("CONTR_ADD")
    contract_instance = w3.eth.contract(address=contract_address, abi=abi)

    lead = Leader(0, "32.4, 51.2", 97) #This can be modified
    drone_add = []
    for i in range(1, NUMB_DRONES):
        drone_add.append(w3.eth.accounts[i])
    
    while True:
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
                for drone in drone_add:
                    tx_rec=lead.add_drone(contract_instance, w3, drone)
                    print(f'\n\nDrone - {drone} Added Successfully.')
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
