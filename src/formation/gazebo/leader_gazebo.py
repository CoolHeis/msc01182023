#!/usr/bin/env python3
from web3 import Web3
import asyncio
from mavsdk import System 
from dotenv import load_dotenv
from compile import compile_contract
import os

async def run():
    uav_leader = System(mavsdk_server_address="127.0.0.1", port=50040)
    await uav_leader.connect() #Connects to the UAV_leader

    print("Establishing Connection...")
    #Check connection state
    async for  state in uav_leader.core.connection_state():
        if state.is_connected:
            print("UAV_leader target UUID: {state.uuid}") #Prints the UUID of the UAV_leader to which the system connected
            break

    #connecting to blockchain
    load_dotenv()
    URL_RPC = os.getenv("URL_RPC")
    NUMB_DRONES = int(os.getenv("NUMB_DRONES"))
    CONTR_ADD = os.getenv("CONTR_ADD")

    w3 = Web3(Web3.HTTPProvider(URL_RPC))
    abi, bytecode = compile_contract()

    contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    contract_address = CONTR_ADD
    contract_instance = w3.eth.contract(address=contract_address, abi=abi)
    print("Smart Contract Instance Created...")


    print("Establishing GPS lock on UAV_leader..")
    #checking the gps Connection via telemetry health command
    async for health in uav_leader.telemetry.health():
        if health.is_global_position_ok:
            print("Established GPS lock...")#GPS health approved
            break

    print("Fetching amsl altitude at home location....")
    async for terrain_info in uav_leader.telemetry.home():
        absolute_altitude = terrain_info.absolute_altitude_m
        break

    print("Arming UAV_leader")
    await uav_leader.action.arm()

    print("Taking Off")
    await uav_leader.action.takeoff()

    await asyncio.sleep(5)


    flying_alt = absolute_altitude + 20

    await uav_leader.action.goto_location(47.397606, 8.543060, flying_alt, 0)

    drone_add = []
    for i in range(1, NUMB_DRONES):
        drone_add.append(w3.eth.accounts[i])

    print("Adding Drones Into Blockchain...")
    count = 1
    for drone in drone_add:
        add_drone(contract_instance, w3, drone, ID=0)
        print(f"Drone with ID:{count} added to Blockchain with address: {drone}")
        count += 1    
    
    flag = True
    location = "47.397606, 8.543060"
    data = "Hello from Leader!"
    while True:
        if flag:
            submit_data_once(contract_instance, w3, location, data, ID=0)
            flag = False
            print("Data Sumbited Successfully into Blockchain")
        print("Staying connected, press Ctrl-C to exit")
        await asyncio.sleep(1)


def submit_data_once(contract_instance, w3, location, data, ID):
        tx_hash = contract_instance.functions.submitData(location, data).transact({"from": w3.eth.accounts[ID]})
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_receipt

def add_drone(contract_instance, w3, drone_address, ID):
        tx_hash = contract_instance.functions.addDrone(drone_address).transact({"from": w3.eth.accounts[ID]})
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_receipt


if __name__ == "__main__":
    asyncio.run(run())
