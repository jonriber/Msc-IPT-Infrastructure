
import requests
import json

# Define the <link>ONOS</link> controller's API endpoint
controller_url = 'http://172.17.0.2:8181/onos/v1/flows/'

# Example flow rule to be added
flow_rule = {
    "priority": 40001,
    "timeout": 0,
    "isPermanent": True,
    "deviceId": "of:0000000000000001",  # Replace with actual switch ID
    "treatment": {
        "instructions": [
            {
                "type": "OUTPUT",
                "port": 2  # Replace with the desired output port
            }
        ]
    },
    "selector": {
        "criteria": [
            {
                "type": "IN_PORT",
                "port": 1  # Replace with the input port
            }
        ]
    }
}

def applyRule():
    try:
        response = requests.post(controller_url, data=json.dumps(flow_rule), auth=('onos', 'rocks'))
        return response
    except Exception as e:
        print("Error happened here:",e)
# Add the flow rule to the <link>ONOS</link> controller


# Check the response

    
if __name__ == "__main__":
    running = True
    print("Starting the application.")

    while running:
        print("-")
        print("-")
        print("type 1 for rule addition")
        print("type 2 for authentication")
        print("type 3 for controller ip adress")
        print("to quit, type q")
        choice = input("Enter your choice:")
        
        if choice == "1":
            print(flow_rule)
            result = applyRule()
            if result.status_code == 200:
                print("Flow rule added successfully")
            else:
                print("Failed to add flow rule:", result.text)
        elif choice == "2":
            print("Authentication section")
            print("-")
            print("User name is: onos")
            print("-")
            print("Password is: rocks")
        elif choice == "3":
            print("Controller IP ADRESS: 172.17.0.2")
        elif choice == "q":
            print("Quitting")
            running = False
        else:
            print ("invalid choice, choose a better one")
            
    print("Program finished")
        
        