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
print(graphenedb_url)
print(graphenedb_user)
print(graphenedb_pass)

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
    res = {}
    if req.get("result").get("action") == "sourceProductsFrom":
        response = makeSourceProductsFromResponse(req)
        res = makeWebhookResult(response, "sourceProductsFrom")
    elif req.get("result").get("action") == "sellDevices":
        response = makeSellDevicesResponse(req)
        res = makeWebhookResult(response, "sellDevices")
    #each function tests the request and returns data if it is the handler
    r = answer(req)
    if r != None:
        return r
    return res

def makeSellDevicesResponse(req):
    result = req.get("result")
    parameters = result.get("parameters")
    device = parameters.get("device")
    company = parameters.get("company")
    print(device)
    print(company)
    query = "MATCH (comp:Company {alternateName: '%s'})-[:SELLS]->(devices{name: '%s'}) RETURN devices.name AS name" % (company, device)
    print(query)
    variable = "Webhook didn't work "
    session = driver.session()
    resultDB = list(session.run(query))
    session.close()
    for record in resultDB:
        variable = "%s do sell %s! Would you like to buy one?" % (company, record["name"])
    return variable

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

def makeWebhookResult(data, source):

    speech = data

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": source
    }

def answer(req):
    source = "offeringTriple"
    if req.get("result").get("action") != source:
        return None

    offering = req.get("result").get("parameters").get("offering")
    product = req.get("result").get("parameters").get("product")
    vendor = req.get("result").get("parameters").get("vendor")

    speech = "All of our graph representatives are busy. If you want %s to %s your %ss, you should ask them." % (vendor, offering, product)
    print(speech)
    speech = "Accessing... "

    query = "MATCH (comp:Company {alternateName: '%s'})-[:SELLS]->(devices{name: '%s'}) RETURN devices.name AS name" % (vendor, product)
    print(query)
    session = driver.session()
    resultDB = list(session.run(query))
    session.close()
    for record in resultDB:
        speech += "%s do %s %s! Would you like to buy one?" % (vendor, offering, record["name"])

    res = {
        "speech": speech,
        "displayText": "The displayText is the answer",
        "source": source
    }

    return res


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print "Starting app on port %d" % port

    app.run(debug=False, port=port, host='0.0.0.0')
