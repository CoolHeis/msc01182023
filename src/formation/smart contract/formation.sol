// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/* 
    A lightweight and easy-to-deploy smart contract for automating decision making process in UAV swarms.
    This smart contract can be used for secure communication, mission creation and formation control in drone clusters.
    It supports three mission types: Search, Dive&Attack and City Surveillance (can be modified) 
    and three formation types: Ring, Vee, Line accordingly (mission based). It follows the Leader-Follower strategy.
    Also a new leader, election mechanism is included. The drone with the highest battery level in the swarm becomes
    the new leader. 
*/

contract LeaderFormation {
    
    // Mission and formation type
    enum MissionType {
        Search,
        DiveAttack,
        CitySurveillance
    }

    
    enum FormationType {
        Line,
        V,
        Circle
    }
/*      
    Structure for data collected by drones. A timestamp, drone's coordinates, 
    drone's data that submits into the blockchain and drone's address are 
    the members of this struct. 
*/ 
     struct DataCollectedByDrone {
        
        uint256 timestamp;
        string location;
        string data;
        address submitter;

    }
/*      
    A mission can be defined by an identifier, a name, the type (Dive, Search etc...), 
    the formation type and the boolean var that indicates if the mission is active.
*/ 
      struct Mission {
        uint16 id;
        string name;
        MissionType missionType;
        FormationType formationType;
        bool active;
    }
    // Declaring variables and maps that will be used below.

    address public leader; //leader address
    uint8 public droneCount; 

    bool public leaderIsAlive = true; 
    uint256 public lastHeartbeat; 
    uint16 public heartbeatTimeout = 180; // heartbeat timeout in seconds

    mapping(address => bool) public drones;
    mapping(uint256 => address) public positionsTaken; 
    mapping(address => uint8) public positions;

    mapping(address => uint8) public batteryLevels;

    mapping(uint256 => Mission) public missions; 
    uint16 public missionCount;

    event MissionCreated(uint16 indexed missionId);
    event MissionUpdated(uint16 indexed missionId);
    event MissionActivated(uint16 indexed missionId);
    event MissionDeactivated(uint16 indexed missionId);

    DataCollectedByDrone[] public droneData;
    
    //events
    
    event DroneAdded(address drone);
    event PositionAssigned(address drone, uint8 position);

    constructor() {
        leader = msg.sender;
        drones[leader] = true;
        droneCount = 1;
    }

    modifier onlyLeader() {
        require(msg.sender == leader, "Only the leader can perform this action.");
        _;
    }
    // (Only) leader can add (or remove) drones with these functions
    function addDrone(address drone) public onlyLeader {
        drones[drone] = true;
        droneCount++; //increasing droneCount var
        emit DroneAdded(drone);
    }
    
    function removeDrone(address drone) public onlyLeader {
        drones[drone] = false;
        droneCount--;
    }
  
    // Clearing positions in case the formation changes
    function clearPositions() private {
        for (uint8 i = 0; i < droneCount; i++) {
            address drone = positionsTaken[i+1];
            if (drones[drone]) {
            delete positions[drone];
            }
            positionsTaken[i+1] = address(0);
        }
    }
    // each drone in the swarm can select its position in the formation
    function assignPosition(uint8 position) public {
        require(drones[msg.sender], "Only drones can assign positions");
        require(position > 0 && position < droneCount, "Invalid position");
        require(positions[msg.sender] == 0, "Position already assigned");
        require(positionsTaken[position] == address(0), "Position already taken");
        positions[msg.sender] = position;
        positionsTaken[position] = msg.sender;
        emit PositionAssigned(msg.sender, position);
    }

    // Data submition funcion. Drone's location and data they collect can be stored.
     function submitData(string memory _location, string memory _data) public {
        require(drones[msg.sender], "Error: A drone must be in the swarm in order to submit data.");
        droneData.push(DataCollectedByDrone(block.timestamp, _location, _data, msg.sender));
    }

    // Retrieving submitted data from Blockchain. 
    function getDroneData() public view returns (DataCollectedByDrone[] memory) {
        DataCollectedByDrone[] memory output = new DataCollectedByDrone[](droneData.length);
        for (uint i = 0; i < droneData.length; i++) {
            output[i] = DataCollectedByDrone({
                timestamp: droneData[i].timestamp,
                location: droneData[i].location,
                data: droneData[i].data,
                submitter: droneData[i].submitter
            });
        }
        return output;
    }
    // Getting the available positions in the formation.
    function getAvailablePositions() public view returns (uint256[] memory) {
    uint256[] memory availablePositions = new uint256[](droneCount);
    uint8 count = 0;
    for (uint8 i = 1; i < droneCount; i++) {
        if (positionsTaken[i] == address(0)) {
            availablePositions[count] = i;
            count++;
        }
    }

    uint256[] memory result = new uint256[](count);
    for (uint8 i = 0; i < count; i++) {
        result[i] = availablePositions[i];
        }   
    return result;
    }
    // The following functions can be used for mission creation, mission details update, mission (de)activation.
    function createMission(string memory name, MissionType missionType, FormationType formationType) public onlyLeader {
        uint16 missionId = missionCount;
        missions[missionId] = Mission(missionId, name, missionType, formationType, false);
        missionCount++;
        emit MissionCreated(missionId);
    }

    function updateMission(uint16 missionId, string memory name, MissionType missionType, FormationType formationType) public onlyLeader {
        require(missions[missionId].id == missionId, "Mission does not exist.");
        missions[missionId].name = name;
        missions[missionId].missionType = missionType;
        missions[missionId].formationType = formationType;
        emit MissionUpdated(missionId);
    }

    function activateMission(uint16 missionId) public onlyLeader {
            require(missions[missionId].id == missionId, "Mission does not exist.");
            missions[missionId].active = true;
            emit MissionActivated(missionId);
        }
        
    function deactivateMission(uint16 missionId) public onlyLeader {
        require(missions[missionId].id == missionId, "Mission does not exist.");
        missions[missionId].active = false;
        emit MissionDeactivated(missionId);
    }

    function getMission(uint16 missionId) public view returns(string memory name, MissionType missionType, FormationType formationType, bool active) {
        require(missions[missionId].id == missionId, "Mission does not exist.");
        Mission storage mission = missions[missionId];
        name = mission.name;
        missionType = mission.missionType;
        formationType = mission.formationType;
        active = mission.active;
    }

    // Can be used by leader to submit a heartbeat message into the blockchain.
    function sendHeartbeat() public onlyLeader {
        require(drones[msg.sender], "Only Leader can send a heartbeat signal.");
        lastHeartbeat = block.timestamp;
    }
    // Can be used by follower to check if their leader is alive.
    function checkLeaderStatus() public {
        if (block.timestamp - lastHeartbeat > heartbeatTimeout) {
            leaderIsAlive = false;
            if (msg.sender != leader) {
                electNewLeader();
            }
        }
    }
    // New leader election mechanism based on battery levels.
    function electNewLeader() private {
        uint8 maxBattery = 0;
        address newLeader = address(0);
        for (uint8 i = 0; i < droneCount; i++) {
            address drone = positionsTaken[i+1];
            if (drones[drone]) {
                uint8 battery = getBatteryLevel(drone);
                if (battery > maxBattery) {
                    maxBattery = battery;
                    newLeader = drone;
                }
            }
        }
        if (newLeader != address(0)) {
            leader = newLeader;
            leaderIsAlive = true;
        }
    }

    function getBatteryLevel(address drone) public view returns (uint8) {
        require(drones[drone], "Only drones can retrieve battery levels.");
        return batteryLevels[drone];
    }

    function submitBatteryLevel(uint8 batteryLevel) public {
        require(drones[msg.sender], "Only drones can submit battery levels.");
        batteryLevels[msg.sender] = batteryLevel;
    }    
}
