# msc01182023

## Smart contract for drone mission creation and formation control.

## Dapp
----

1. Download Ganache Image from https://github.com/trufflesuite/ganache-ui/releases. 
2. Change it into an executable using chmod +x command. 
3. Run the executable and select a quickstart from the initial menu. 
4. Copy the private key of the first account and paste it into .env file. 
5. Compile and deploy the smart contract using the provided scripts.

After deploying the smart contract successfully, it should return its address. Paste this address into .env file. Now you can test the scripts in the Dapp folder. 

1. First, run the leader.py and select the first option in order to register some addresses (drones) so they can access the smart contract's functionality. 
2. You can now create missions (declare formation), activate mission (a new mission must be activated), submit data and location, etc.
3. As follower you can retrieve (submit) data from blockchain, get leader's position, check if leader is up, retrieve mission details, select and submit a specific position in the formation etc.

## Gazebo
----

Tested on Ubuntu focal 20.04 with gazebo 11. 

1. Install mavsdk using: pip3 install mavsdk
2. Run a mavsdk server for each drone in order to work: ./mavsdk_server -p 50040 udp://:14540, ./mavsdk_server -p 50041 udp://:14541 ... etc.
3. For the drone models, I used PX4 Autopilot software: https://github.com/PX4/PX4-Autopilot. Here are the steps for setting up 
the environment: https://docs.px4.io/main/en/dev_setup/dev_env.html. 
4. The command for multiple vehicles is: ~/<PX4-clone>/Tools/simulation/gazebo-classic/sitl_multiple_run.sh -n <number_of_UAVs>
5. After setting up the simulation successfully run Ganache and follow the same instructions as before. You can now test gazebo folder's scripts.
6. First run the leader and then the follower scripts (Each script corresponds to each follower. Modify the parameters for each drone).
  
