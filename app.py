#!/usr/bin/env python

import urllib
import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


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
    if req.get("result").get("action") != "current_price":
        speech = "couldn't get the action right"
        return {
            "speech": speech,
            "displayText": speech,
            "source": "apiai-webhook-test-asxdata-cv"
        }

    url = makeURL(req)
    if url is None:
        speech = "couldn't get the url right"
        return {
            "speech": speech,
            "displayText": speech,
            "source": "apiai-webhook-test-asxdata-cv"
        }
    #yql_url = "http://data.asx.com.au/data/1/share/BHP/"
    result = urllib.urlopen(url).read()
    data = json.loads(result)
    res = makeWebhookResult(data)
    return res


def makeURL(req):
    baseurl = "http://data.asx.com.au/data/1/share/"
    result = req.get("result")
    parameters = result.get("parameters")
    stock = parameters.get("stock")
    if stock is None:
        return None

    fullURL = baseurl + urllib.urlencode({'q': stock}) + "/"
    return fullURL

#def makeWebhookResult(data):
#    query = data.get('query')
#    if query is None:
#        return {}
#
#    result = query.get('results')
#    if result is None:
#        return {}
#
#    channel = result.get('channel')
#    if channel is None:
#        return {}
#
#    item = channel.get('item')
#    location = channel.get('location')
#    units = channel.get('units')
#    if (location is None) or (item is None) or (units is None):
#        return {}
#
#    condition = item.get('condition')
#    if condition is None:
#        return {}
#
#    # print(json.dumps(item, indent=4))
#
#    speech = "Today in " + location.get('city') + ": " + condition.get('text') + \
#             ", the temperature is " + condition.get('temp') + " " + units.get('temperature')
#
#    print("Response:")
#    print(speech)
#
#    return {
#        "speech": speech,
#        "displayText": speech,
#        # "data": data,
#        # "contextOut": [],
#        "source": "apiai-weather-webhook-sample"
#    }



def makeWebhookResult(data):
    code = data.get('code')
    #if code is None:
    #    return {}

    last_price = data.get('last_price')
    #if last_price is None:
    #    return {}

    change_in_percent = data.get('change_in_percent')
    #if change_in_percent is None:
    #    return {}

    speech = "The current price for " + code + " is " + str(last_price) + " (percentage change " + str(change_in_percent) + ")"

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-webhook-test-asxdata-cv"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print "Starting app on port %d" % port

    app.run(debug=False, port=port, host='0.0.0.0')
