import os
from solcx import compile_standard, install_solc
from dotenv import load_dotenv
import json

def compile_contract():

    load_dotenv()
    SOLC_VERSION = os.getenv('SOLC_VERSION')
    install_solc(SOLC_VERSION)

    with open('./formation.sol', 'r') as file:
        formation_file = file.read()

    compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"formation.sol": {"content": formation_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                    }
                }
            },
        },
        solc_version=SOLC_VERSION,
    )

    with open("compiled_formation.json", "w") as file:
        json.dump(compiled_sol, file)

    # get bytecode
    bytecode = compiled_sol["contracts"]["formation.sol"]["LeaderFormation"]["evm"]["bytecode"]["object"]
    # get abi
    abi = json.loads(compiled_sol["contracts"]["formation.sol"]["LeaderFormation"]["metadata"])["output"]["abi"]
    return abi, bytecode
    
    
if __name__ == "__main__":
    compile_contract()

