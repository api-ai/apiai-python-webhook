#!/usr/bin/env python

import urllib
import json
import os
from neo4j.v1 import GraphDatabase, basic_auth

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)

graphenedb_url = os.environ.get("GRAPHENEDB_WHITE_BOLT_URL")
graphenedb_user = os.environ.get("GRAPHENEDB_WHITE_BOLT_USER")
graphenedb_pass = os.environ.get("GRAPHENEDB_WHITE_BOLT_PASSWORD")

driver = GraphDatabase.driver(graphenedb_url, auth=basic_auth(graphenedb_user, graphenedb_pass))

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req.get("result").get("action") != "sourceProductsFrom":
        wellProducts
        response = makeSourceProductsFromResponse(req)
        res = makeWebhookResult(response)
    elif req.get("result").get("action") != "sellDevices":
        response = makeSellDevicesResponse(req)
        res = makeWebhookResult(response)
    else
        return {}
    return res

def makeSellDevicesResponse(req):
    result = req.get("result")
    parameters = result.get("parameters")
    device = parameters.get("device")
    print(device)
    session = driver.session()
    result = session.run("MATCH (we:Company {alternateName: 'we'})-[:SELLS]->(devices{name: 'Ipad 2'}) RETURN devices.name AS name")
    for record in result:
        print(record["name"])
        if record["name"] == device:
            return "We do sell %s! Would you like to buy one?" % device
    session.close()
    return "Test Webhook"

def makeSourceProductsFromResponse(req):
    result = req.get("result")
    parameters = result.get("parameters")
    country = parameters.get("geo-country")
    print(country)
    if country == 'United States of America':
        return 'Tech Data (Preferred), Ingram and Apple Direct.'
    if country == 'Canada':
        return 'Synnex Canada (Preferred), Ingram Canada and BlueStar Canada (AppleCare exclusively).'
    if country == 'Europe':
        return 'cheryl_mepham@shi.com is our Mobility Specialist out of the UK who can help assist.'
    return "Test Webhook"

def makeWebhookResult(data):

    speech = data

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "sourceProductsFrom"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print "Starting app on port %d" % port

    app.run(debug=False, port=port, host='0.0.0.0')
