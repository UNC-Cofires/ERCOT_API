# ERCOT_API
data downloads and analysis of gridmet data

## Getting Started
 This script downloads data through the ERCOT API
 in order to use this script, you first need to 
 register (for free) on the ERCOT website
 https://apiexplorer.ercot.com/
 click SignUp on the top right, and create
 an account - once the account is created, sign
 in with your username/password and you should get
 to a landing page with a 'Profile' tab at the top
 right - click on Profile and scroll down to 'subscriptions'
 there should be a row called 'Primary Key' that shows XXXXXX
 click on 'show' to get your subscription key
 
 take your username, password, and subscription key
 and assign them to the appropriate variables on lines
 22-24 in read_ercot_api.py

### Dependencies

Python Libraries:

* requests
* csv
* zipfile
* io
* os
* time

### Executing program

* Once username, password, and subscription key have been set, download
* data from the api by running
```
python -W ignore read_ercot_api.py
```
* To get different data types, change the EMIL code on line 43
