import requests
import csv
import zipfile
import io
import os
import time

# This script downloads data through the ERCOT API
# in order to use this script, you first need to 
# register (for free) on the ERCOT website
# https://apiexplorer.ercot.com/
# click SignUp on the top right, and create
# an account - once the account is created, sign
# in with your username/password and you should get
# to a landing page with a 'Profile' tab at the top
# right - click on Profile and scroll down to 'subscriptions'
# there should be a row called 'Primary Key' that shows XXXXXX
# click on 'show' to get your subscription keys
# assign your username, password, and subscription key as strings
# to the variables described below

USERNAME = "your username"
PASSWORD = "your password"
SUBSCRIPTION_KEY = "your subscription key"

# keep this auth_url as it appears here
AUTH_URL = "https://ercotb2c.b2clogin.com/ercotb2c.onmicrosoft.com/B2C_1_PUBAPI-ROPC-FLOW/oauth2/v2.0/token\
?username={username}\
&password={password}\
&grant_type=password\
&scope=openid+fec253ea-0d06-4272-a5e6-b478baeecd70+offline_access\
&client_id=fec253ea-0d06-4272-a5e6-b478baeecd70\
&response_type=id_token"

# This request signs you into your ERCOT account
auth_response = requests.post(AUTH_URL.format(username = USERNAME, password=PASSWORD))
# This will give you an access token associated with your account
access_token = auth_response.json().get("access_token")

# EMIL code
# this is for the specific data type you want to downloads
# electric bus locational marginal price is: np6-787-cd
emil_code = 'np6-787-cd'
headers = {"Authorization": "Bearer " + access_token, "Ocp-Apim-Subscription-Key": SUBSCRIPTION_KEY}
response = requests.get('https://api.ercot.com/api/public-reports/archive/' + emil_code, headers=headers)
print(response.status_code)
# use metadata from first request to find the number of pages
# you need to make a new request for each page
all_vals = response.json()
num_pages = all_vals['_meta']['totalPages']
print(num_pages)
file_read_failure = [] # for keeping track of any file names that do not download

# create directory to store downloaded data files
output_dir = 'ercot'
os.makedirs(output_dir, exist_ok = True)

# loop through all the pages in the archive
for page_no in range(1000, 1100):
  # for each page, make a new request to the API
  response = requests.get('https://api.ercot.com/api/public-reports/archive/np6-787-cd', headers=headers, params = {'page':page_no})
  # get list of files associated with your EMIL code (data type)
  all_vals = response.json() # get response as dictionary
  # get list of all files on this 'page' (1000 files per page)
  list_of_files = all_vals['archives']
  
  # loop through list of each file, download and unzip
  for file_no in range(0, len(list_of_files)):
    # api path for individual file
    filename = list_of_files[file_no]['_links']['endpoint']['href']
    # call API for individual file
    response2 = requests.get(filename, headers=headers)
    print(response2.status_code)
    if response2.status_code == 429:
      # if you get rate limited, wait 30 seconds then 
      # make a new request
      time.sleep(2) # wait 30 seconds
      response2 = requests.get(filename, headers=headers)
    elif response2.status_code == 401:
      auth_response = requests.post(AUTH_URL.format(username = USERNAME, password=PASSWORD))
      # This will give you an access token associated with your account
      access_token = auth_response.json().get("access_token")
      headers = {"Authorization": "Bearer " + access_token, "Ocp-Apim-Subscription-Key": SUBSCRIPTION_KEY}
      time.sleep(2) # wait 30 seconds
      response2 = requests.get(filename, headers=headers)
 
    # if file exists, unzip
    file_found = True
    try:
      z = zipfile.ZipFile(io.BytesIO(response2.content))
    except:
      # this will error if you are rate limited by ERCOT
      # API (in which case increase time.sleep(X) value of X
      file_found = False
    
    # if data exists, store in directory
    if file_found:
      z.extractall(output_dir)
    else:
      # make note of any file that did not download
      file_read_failure.append(filename)
      with open('file_read_errors.txt', 'w') as file:
        for item in file_read_failure:
          file.write(f"{item}\n")
    time.sleep(2) # wait 30 seconds
