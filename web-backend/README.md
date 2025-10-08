# Web Backend
This is the web backend for the PPH dection device. It uses OAuth with client credentials workflow to securly communicate between the device and api.
## Installing
This uses FastApi and various libraries to run. The relvant packages can be installed using 
`
pip install -r requirements.txt
`
in this directory

## Running
This uses fast api which can be ran via uvicorn via
`
 python3 -m uvicorn web-backendmain:app --reload --host 0.0.0.0
`
in root directory