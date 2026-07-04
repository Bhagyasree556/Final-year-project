import base64
from web3 import Web3
import json

web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

one = {"from":"0x52C03815A6307a8d6e762fd2C182D47f7Ae03713"} #account adress

with open("blocks/build/contracts/Store.json") as data:
    contract_file = web3.eth.contract(
        abi = json.load(data)["abi"],
        address = "0x455bc3863De95923a21b8f4B814eF23D51567014"  #contarct adress
    )

def addNewData(user:dict) -> str:
    try:
        variable = base64.b64encode(json.dumps(user).encode()).decode()
        contract_file.functions.addString(variable).transact(one)
        return "Success"
    except Exception as e:
        return f'{e}'
    
import json
import base64

def retrieveData() -> list:
    try:
        data = []

        # 🔹 Get data from blockchain
        variable = contract_file.functions.getAll().call(one)

        for i in variable:
            try:
                # 🔹 Decode + convert to dictionary
                decoded_data = base64.b64decode(i[1]).decode()
                v = json.loads(decoded_data)

                # 🔹 Add extra field
                v['sumID'] = i[0]

                # 🔹 Append to list
                data.append(v)

            except Exception as inner_error:
                print("Skipping invalid record:", inner_error)
                continue  # skip wrong data

        return data

    except Exception as e:
        print("Error in retrieveData():", e)
        return []   # ✅ ALWAYS return list (IMPORTANT)
    
def updateData(position:int, data:dict) ->str:
    try:
        pp = base64.b64encode(json.dumps(data).encode()).decode()
        contract_file.functions.updateStore(position,pp).transact(one)
        return "Success"
    except Exception as e:
        return f'{e}'