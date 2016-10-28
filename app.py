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
    res = processRequest(req)   #Receive data from api.ai and retrieve request data
    res = json.dumps(res, indent=4)
    r = make_response(res)      #Use retrieved data to form response to api.ai
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):    #Parse data provided to script and retrieve request data
    if req.get("result").get("action") != "current_price":
        return {}
    #url = "http://data.asx.com.au/data/1/share/BHP/"
    url = makeURL(req)  #construct request url
    if url is None:
        return {}
    result = urllib.urlopen(url).read() #read target url
    data = json.loads(result)   #grab target url json data
    res = makeWebhookResult(data)   #process data to pass back to api.ai
    return res


def makeURL(req):   #construct request url
    baseurl = "http://data.asx.com.au/data/1/share/"    #url root
    result = req.get("result")      #grab data from api.ai input
    parameters = result.get("parameters")
    stock = parameters.get("ASX_stock")
    if stock is None:
        return None
    fullURL = baseurl + stock + "/"     #build url
    return fullURL


def makeWebhookResult(data):    #process data to pass back to api.ai
    code = data.get('code')     #get data
    if code is None:
        return {}
    last_price = data.get('last_price')
    if last_price is None:
        return {}
    change_in_percent = data.get('change_in_percent')
    if change_in_percent is None:
        return {}
    #build output string
    speech = "The current price for " + code + " is " + str(last_price) + " (percentage change " + str(change_in_percent) + ")"
    return {"speech": speech, "displayText": speech, "source": "cv-asxdata"}


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=False, port=port, host='0.0.0.0')
