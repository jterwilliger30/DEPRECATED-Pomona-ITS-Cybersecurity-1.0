import msal
import requests
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import json
import datetime

def get_token():
    scopes = ['User.Read']
    clientId = "<INSERT>"
    authority = "https://login.microsoftonline.com/<INSERT>"

    app = msal.PublicClientApplication(client_id=clientId, authority=authority)

    with open("../../Desktop/token", "r", encoding="utf-8") as token_file:
        x = token_file.readline()

    if x == "":
        a = app.initiate_device_flow(scopes)
        print(a['user_code'])
        auth_json = app.acquire_token_by_device_flow(a)

        token = auth_json['access_token']

        now = datetime.datetime.now()
        with open("./Desktop/token", "w", encoding="utf-8") as token_file:
            token_file.write(str(token) + "\n")
            token_file.write(str(now) + "\n")
            token_file.write(str(auth_json["expires_in"]))
    else:
        token = x

    return token

def api_request(token):
    username = input("What user would you like to query for:\t")

    token = token.strip()

    r = requests.get("https://graph.microsoft.com/v1.0/auditLogs/signIns?&$filter=startsWith(userPrincipalName,'" +
                     username + "')", headers={'Authorization': "Bearer " + token})
    data = r.content

    data = data.decode('utf-8')
    #####
    json_data = json.loads(data)
    #####

    appDisplayName_dict = {}
    clientAppUsed_dict = {}
    resourceDisplayName_dict = {}
    conditionalAccessStatus_dict = {}
    ipAddress_dict = {}
    location_dict = {}
    deviceDetail_dict = {}

    latitude = []
    longitude = []

    for i in range(len(json_data["value"])):
        # DEBUG
        # print(json_data["value"][i])

        # appDisplayName
        if json_data["value"][i]["appDisplayName"] in appDisplayName_dict:
            appDisplayName_dict[json_data["value"][i]["appDisplayName"]] += 1
        else:
            appDisplayName_dict[json_data["value"][i]["appDisplayName"]] = 1

        # clientAppUsed
        if json_data["value"][i]["clientAppUsed"] in clientAppUsed_dict:
            clientAppUsed_dict[json_data["value"][i]["clientAppUsed"]] += 1
        else:
            clientAppUsed_dict[json_data["value"][i]["clientAppUsed"]] = 1

        # resourceDisplayName
        if json_data["value"][i]["resourceDisplayName"] in resourceDisplayName_dict:
            resourceDisplayName_dict[json_data["value"][i]["resourceDisplayName"]] += 1
        else:
            resourceDisplayName_dict[json_data["value"][i]["resourceDisplayName"]] = 1

        # conditionalAccessStatus
        if json_data["value"][i]["conditionalAccessStatus"] in conditionalAccessStatus_dict:
            conditionalAccessStatus_dict[json_data["value"][i]["conditionalAccessStatus"]] += 1
        else:
            conditionalAccessStatus_dict[json_data["value"][i]["conditionalAccessStatus"]] = 1

        # ipAddress
        if json_data["value"][i]["ipAddress"] in ipAddress_dict:
            ipAddress_dict[json_data["value"][i]["ipAddress"]] += 1
        else:
            ipAddress_dict[json_data["value"][i]["ipAddress"]] = 1

        # location
        if str(json_data["value"][i]["location"]) in location_dict:
            location_dict[str(json_data["value"][i]["location"])] += 1
        else:
            location_dict[str(json_data["value"][i]["location"])] = 1

        # deviceDetail
        if str(json_data["value"][i]["deviceDetail"]) in deviceDetail_dict:
            deviceDetail_dict[str(json_data["value"][i]["deviceDetail"])] += 1
        else:
            deviceDetail_dict[str(json_data["value"][i]["deviceDetail"])] = 1

        # LATITUDE & LONGITUDE
        latitude.append(float(json_data["value"][i]["location"]["geoCoordinates"]["latitude"]))
        longitude.append(float(json_data["value"][i]["location"]["geoCoordinates"]["longitude"]))

    # print(appDisplayName_dict)
    # print(clientAppUsed_dict)
    # print(resourceDisplayName_dict)
    # print(conditionalAccessStatus_dict)
    # print(ipAddress_dict)
    # print(location_dict)
    # print(deviceDetail_dict)

    """
    for key in ipAddress_dict:
        print(str(key) + ": " + str(ipAddress_dict[key]))
    """







    ###
    option = 2
    ###

    if option == 1:
        Graph_Dict = location_dict
        plt.bar(range(len(Graph_Dict)), list(Graph_Dict.values()), align='center')
        plt.xticks(range(len(Graph_Dict)), list(Graph_Dict.keys()), rotation=90, fontsize=8)
        plt.yscale("log")
        plt.tight_layout()
        plt.show()


    elif option == 2:
        countries = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
        countries.head()

        countries.plot(color="lightgrey")

        plt.scatter(longitude, latitude, s=1, edgecolors="r")
        plt.show()

    return json_data