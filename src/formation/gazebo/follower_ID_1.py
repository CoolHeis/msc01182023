#!/usr/bin/env python3

#Add as many followers as u want
from web3 import Web3
import asyncio
from mavsdk import System 
from dotenv import load_dotenv
from compile import compile_contract
import os
import math
import sys

""" 
    This script automates some of the processes that we've tested with the Dapp 
    (drone registration, mission creation and activation and position selection)
    and can be used in combination with gazebo software, for a visual result.    
    Mavsdk API is used for drone handling and web3 module for accessing the 
    smart contract's functions. Haversine formula is used for coordinate 
    transformation.
"""


async def run():
    ID = 1 #follower ID
    uav_follower_1 = System(mavsdk_server_address="127.0.0.1", port=50041) #must run an mavsdk server for each follower 
    await uav_follower_1.connect() #Connects to the uav_follower_1

    print("Establishing Connection...")
    #checking connection
    async for  state in uav_follower_1.core.connection_state():
        if state.is_connected:
            print("uav_follower_1 target UUID: {state.uuid}") #Prints the UUID of the uav_follower_1 to which the system connected
            break

    #connecting to blockchain
    load_dotenv()
    URL_RPC = os.getenv("URL_RPC")
    CONTR_ADD = os.getenv("CONTR_ADD")

    w3 = Web3(Web3.HTTPProvider(URL_RPC))
    abi, bytecode = compile_contract()

    contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    contract_address = CONTR_ADD
    contract_instance = w3.eth.contract(address=contract_address, abi=abi)
    print("Smart Contract Instance Created...")

    # checking the gps Connection via telemetry health command
    print("Establishing GPS lock on uav_follower_1..")
    async for health in uav_follower_1.telemetry.health():
        if health.is_global_position_ok:
            print("Established GPS lock...")#GPS health approved
            break

    print("Fetching amsl altitude at home location....")
    async for terrain_info in uav_follower_1.telemetry.home():
        absolute_altitude = terrain_info.absolute_altitude_m
        break

    leader_add = w3.eth.accounts[0]
    print(f"Leader's Address is: {leader_add}\n")
    print("Retriving Leader's Location from Blockchain")

    #Retrieving data from blockchain, including leader's location.    
    data = get_drone_data(w3, contract_instance, ID)
    for i in range(len(data)):
        if data[i][3] == leader_add:
            location = data[i][1]
    print(f"Location: {location}") 

    leader_coords = location.split(", ")
    lat_lead = float(leader_coords[0])
    long_lead = float(leader_coords[1])

    position_mapping = {'1': (47.397761766994634, 8.542927142069864),
                        '2': (47.39791753383577, 8.542794283354194),
                        '3': (47.397761766994634, 8.543192857930137),
                        '4': (47.39791753383577, 8.543325716645807)
                        }
    
    #Retrieving available positions from blockchain.
    avail_positions = get_available_positions(w3, contract_instance, ID)

    print(f" Available Positions are: {avail_positions}\n")

    avail_positions_mapped = []
    if 1 in avail_positions:
        avail_positions_mapped.append(position_mapping["1"])
    if 2 in avail_positions:
        avail_positions_mapped.append(position_mapping["2"])
    if 3 in avail_positions:
        avail_positions_mapped.append(position_mapping["3"])
    if 4 in avail_positions:
        avail_positions_mapped.append(position_mapping["4"])
    
    
    #Sending follower in a random location near leader
    flying_alt = absolute_altitude + 20

    print("Arming uav_follower_1")
    await uav_follower_1.action.arm()

    print("Taking Off")
    await uav_follower_1.action.takeoff()

    await asyncio.sleep(5)

    drone_lat = 47.397661
    drone_lon = 8.542879

    #sending drone to random location
    print("Drone going to random position")
    await uav_follower_1.action.goto_location(drone_lat, drone_lon, flying_alt, 0)
    await asyncio.sleep(90)

    formation_distance = 20 #Distance beetween follower leader. change this according the formation 
    #angles for V formation    
    formation_angle = [math.radians(30), math.radians(-30)]
    
    #calculating closest position for every drone
    closest_position = select_closest_position(drone_lat, drone_lon, lat_lead, long_lead, formation_distance, formation_angle, avail_positions_mapped)
    
    key_postition = [k for k, v in position_mapping.items() if v == closest_position][0]
    
    #sumbitting position into blockchain    
    print(f"Position {key_postition} selected... Sumbitting into blockchain")
    select_position(contract_instance, w3, int(key_postition), ID)

    print("going to clossest position")
    await uav_follower_1.action.goto_location(closest_position[0], closest_position[1], flying_alt, 0)
    
    while True:
        print("Staying connected, press Ctrl-C to exit")
        await asyncio.sleep(1)


def get_drone_data(w3, contract_instance, ID):
    return contract_instance.functions.getDroneData().call({"from": w3.eth.accounts[ID]})

    #inverse Haversine formula
def calculate_follower_coordinates(leader_lat, leader_lon, distance, angle):
    leader_lat_rad = math.radians(leader_lat)
    leader_lon_rad = math.radians(leader_lon)

    # Earth's radius in meters
    earth_radius = 6371000


    distance_rad = distance / earth_radius

    # Calculate the follower's latitude and longitude
    follower_lat_rad = math.asin(math.sin(leader_lat_rad) * math.cos(distance_rad) +
                                 math.cos(leader_lat_rad) * math.sin(distance_rad) * math.cos(angle))

    follower_lon_rad = leader_lon_rad + math.atan2(math.sin(angle) * math.sin(distance_rad) * math.cos(leader_lat_rad),
                                                   math.cos(distance_rad) - math.sin(leader_lat_rad) * math.sin(follower_lat_rad))

    follower_lat = math.degrees(follower_lat_rad)
    follower_lon = math.degrees(follower_lon_rad)

    return follower_lat, follower_lon

def get_available_positions(w3, contract_instance, ID):
        return contract_instance.functions.getAvailablePositions().call({"from": w3.eth.accounts[ID]})

def select_position(contract_instance, w3, position, ID):
        tx_hash = contract_instance.functions.assignPosition(position).transact({"from": w3.eth.accounts[ID]})
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_receipt

def select_closest_position(drone_lat, drone_lon, leader_lat, leader_lon, formation_distance, formation_angle, available_positions):
    closest_distance = float('inf')  # Initialize with a large value
    closest_position = None

    for angle in formation_angle:

        follower_lat, follower_lon = calculate_follower_coordinates(leader_lat, leader_lon, formation_distance, angle)

        # calculating the distance between the drone and the follower position
        distance = math.sqrt((drone_lat - follower_lat) ** 2 + (drone_lon - follower_lon) ** 2)

        # checking if this position is closer than the previous closest position
        if distance < closest_distance and (follower_lat, follower_lon) in available_positions:
            closest_distance = distance
            closest_position = (follower_lat, follower_lon)

    return closest_position

if __name__ == "__main__":
    asyncio.run(run())

