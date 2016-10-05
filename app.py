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
        r = answer(req)
        if r != None:
            return r
        r = answerHow(req)
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


def answer(req):
    source = "offeringTriple"
    if req.get("result").get("action") != source:
        return None

    offering = req.get("result").get("parameters").get("offering")
    product = req.get("result").get("parameters").get("product")
    vendor = req.get("result").get("parameters").get("vendor")

    speech = "All of our graph representatives are busy. If you want %s to %s your %ss, you should ask them." % (vendor, offering, product)
    print(speech)
    speech = ": "

    query = "MATCH (comp:Company {name: '%s'})-[:%s]->(devices{name: '%s'}) RETURN devices.name AS name" % (vendor, offering, product)
    print(query)
    session = driver.session()
    resultDB = list(session.run(query))
    session.close()
    print("The query returned %d items" % (len(resultDB)) )
    if len(resultDB) == 0 :
        speech += "Sorry, %s doesn't %s %s." % (vendor, offering, product)

    for record in resultDB:
        speech += "%s does %s %s! Would you like to buy one?" % (vendor, offering, record["name"])

    res = {
        "speech": speech,
        "displayText": "The displayText is the answer",
        "source": source
    }

    return res


def answerHow(req):
    source = "offeringPath"
    if req.get("result").get("action") != source:
        return None

    offering = req.get("result").get("parameters").get("offering")
    anything = req.get("result").get("parameters").get("anything")
    vendor = req.get("result").get("parameters").get("vendor")

    query = "MATCH (comp:Company {name: '%s'})-[r*]->(offerer)-[s:%s]->(anything{name: '%s'}) RETURN comp AS origin, offerer AS offerer, r AS chain, s AS offering, anything AS destination" % (vendor, offering, anything)
    resultList = grapheneQuery(query)

    speech = ""

    if len(resultList) == 0:
        speech += "Sorry, %s doesn't %s %s." % (vendor, offering, anything)
    else:
        print(resultList)

    for record in resultList:
        print(record)
        speech += " %s %s %s via %s!" % (vendor, record["offering"].properties["name"], record["destination"].properties["name"], record["offerer"].properties["name"])

    res = {
        "speech": speech,
        "displayText": speech,
        "source": source
    }

    return res


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

    speech = "D: "
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
