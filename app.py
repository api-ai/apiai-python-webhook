#!/usr/bin/env python

import urllib
import json
import os
from neo4j.v1 import GraphDatabase, basic_auth
from neo4j.v1.types import Node, Relationship

from flask import Flask
from flask import request
from flask import make_response
from flask import render_template
from flask import send_from_directory

# Flask app should start in global layout
app = Flask(__name__)

graphenedb_url = os.environ.get("GRAPHENEDB_WHITE_BOLT_URL")
graphenedb_user = os.environ.get("GRAPHENEDB_WHITE_BOLT_USER")
graphenedb_pass = os.environ.get("GRAPHENEDB_WHITE_BOLT_PASSWORD")
print(graphenedb_url)
print(graphenedb_user)
print(graphenedb_pass)

driver = GraphDatabase.driver(graphenedb_url, auth=basic_auth(graphenedb_user, graphenedb_pass))

@app.route('/')
def root():
    return send_from_directory('static', "index.html")


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


@app.route('/<path:path>')
def send_js(path):
    return send_from_directory('static', path)


def processRequest(req):
    res = {}
    if req.get("result").get("action") == "sourceProductsFrom":
        response = makeSourceProductsFromResponse(req)
        res = makeWebhookResult(response, "sourceProductsFrom")
    elif req.get("result").get("action") == "sellDevices":
        response = makeSellDevicesResponse(req)
        res = makeWebhookResult(response, "sellDevices")
    #each function tests the request and returns data if it is the handler
    try:
        r = findQuery(req)
        if r != None:
            return r
    except Exception as err:
        print("Error %s:" % (str(err)) )

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


def findQuery(req):
    action = req.get("result").get("action")
    queryQuery = "MATCH (QUERY:Query {name: '%s'}) RETURN QUERY AS query" % (action)
    resultList = grapheneQuery(queryQuery)

    if len(resultList) == 0:
        return None

    parameters = req.get("result").get("parameters")
    foundQuery = resultList[0]["query"].properties

    query = foundQuery["query"]
    queryArgs = foundQuery["queryArgs"]
    #failedMessage message must take the same arguments as the query itself
    failedMessage = foundQuery.get("fail") or "No data found."
    formatter = foundQuery["formatter"]
    formatterArgs = foundQuery["formatterArgs"]

    queryArgList = []
    for arg in queryArgs:
        components = arg.split(".")
        if components[0] == "parameters":
            queryArgList.append(parameters.get(components[1]))

    print("Query %s with arguments %s" % (query, queryArgList))

    concreteQuery = query % tuple(queryArgList)

    print("Expands to %s " % (concreteQuery))

    resultList = grapheneQuery(concreteQuery)

    speech = ""
    if len(resultList) == 0 :
        speech += failedMessage % tuple(queryArgList)

    for record in resultList:
        print(record)
        formatterArgList = extractRecordParameters(parameters, record, formatterArgs)
        print("Applied to formatter %s with arguments %s" % (formatter, formatterArgList))
        speech += formatter % tuple(formatterArgList)

    res = {
        "speech": speech,
        "displayText": speech,
        "source": action
    }

    return res


def extractRecordParameters(parameters, record, formatterArgs):
    formatterArgList = []
    for arg in formatterArgs:
        components = arg.split(".")
        if components[0] == "parameters":
            formatterArgList.append(parameters.get(components[1]))
        elif components[0] == "record":
            formatterArgList.append(record[components[1]].properties[components[2]])

    return formatterArgList


def grapheneQuery(query):
    print(query)
    session = driver.session()
    resultDB = session.run(query)
    session.close()
    return list(resultDB)


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print "Starting app on port %d" % port

    app.run(debug=False, port=port, host='0.0.0.0')
