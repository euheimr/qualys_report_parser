#qualys_report_parser
A Python library to get and process Qualys VM/PC scans data and asset
 inventory into better reports.
 
### Dependencies
  * Python >=3.8 -  [ [download]() ] [ [api docs]() ]
  * pandas - [ [main page]() ] [ [api]() ]
  * qualysapi 
    * uses requests via HTTPS to POST Qualys APIv2 for data
  * xmltodict - [ [main page](https://github.com/martinblech/xmltodict
  ) ] [ [api docs]() ] 
    * used to validate and convert the Qualys API XML responses to a
     dictionary object
  * pathlib

Development
  * loguru

#### 


### Install
1. Copy the repository 
2. Extract and go to the project directory
3. call `python main.py `
 
 
 
 
 
 
 ### Call chain:
  