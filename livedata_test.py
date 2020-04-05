# importing the requests library 
import requests 
import json
  
# api-endpoint 
URL = "https://127.0.0.1:2999/liveclientdata/activeplayer"
  
# sending get request and saving the response as response object 
r = requests.get(url = URL, verify=False) 
  
# extracting data in json format 
data = r.json() 

json_formatted_str = json.dumps(data, indent=2)

# printing the output 
print(json_formatted_str) 