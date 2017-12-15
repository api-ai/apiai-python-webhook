# -*- coding:utf8 -*-
# !/usr/bin/env python
# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()
from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os
import pyotp

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)
@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    print(json.dumps(req, indent=4))
    #res = processOTPRequest(req)
    res = processRequest(req)
    res = json.dumps(res, indent=4)
    # print(res)
    r=make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def processRequest(req):
    print("ACTION IS : ",req.get("result").get("action"))
    if req.get("result").get("action") == "yahooWeatherForecast":
        print("111")
        res = {}
    elif req.get("result").get("action") == "otpVerification":
        print("222")
        res = processOTPRequest(req)
    elif req.get("result").get("action") == 'emailVerification':
        print("333")
        res = processEmailVerificationRequest(req)
    elif req.get("result").get("action") == 'disputeAction':
        print("444")
        res = processDisputeRequest(req)
    elif req.get("result").get("action") == 'txnDateAction':
        print("555")
        res = processDisputTxnDateRequest(req)
    else:
        res = {}
    return res

#processDisputTxnDateRequest
def processDisputTxnDateRequest(req):
    email_txnCount_onSomeDay = {'nikhilraog@gmail.com': 1, 'sandeeptengli@gmail.com': 1}
    result = req.get("result")
    parameters = result.get("parameters")
    date = parameters.get("date")

    #default 
    numTxn = 0
    contexts = result.get("contexts")

    if contexts is not None:
        for  ctx in contexts:
            if  str(ctx.get("name")) == 'contextout':
                userEmail = ctx.get("parameters").get("Email").lower()
                print(" processDisputTxnDateRequest : Matched with email: ", userEmail)
                if userEmail is not None:
                    numTxn = email_txnCount_onSomeDay[userEmail]
                    print("processDisputTxnDateRequest userEmail and numTxns", userEmail, numTxn)
                    speech = "Ok. I found "+ str(numTxn)+ " transactios from Walmart posted on your account "+ str(date)+ ". Shall I proceed with filling Disput? Pick On of these."
                    speech += "1. Unauthorized transaction, 2. Item not received, 3. Debitted Incorrect amount, 4. Chargeback,  5.Others"
                    print(speech)

                    return {
                        "speech": speech,
                        "displayText": speech,
                        "source": "processDisputTxnDateRequest"
                    }
        return{
            "speech": 'I could not find any transaction on that day? Please check the date and say again',
            "displayText": 'I could not find any transaction on that day? Please check the date and say again',
            "source": "processDisputTxnDateRequest"
        }
        


            
    return{
        "speech": 'I could not find any transaction on that day? Please check the date and say again',
        "displayText": 'I could not find any transaction on that day? Please check the date and say again',
        "source": "makeEmailVerificationResult"
    }


#Dispute respose
def processDisputeRequest(req):
    speech = "Ok. I can help you, Could you tell me the more information on that? Say transaction Date or Store/Merchant name?"
    return {
        "speech": speech,
        "displayText": speech,
        "source": "makeEmailVerificationResult"
    }

def makeYqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    if city is None:
        return None
    return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "')"

def makeWebhookResult(data):
    query = data.get('query')
    if query is None:
        return {}
    result = query.get('results')
    if result is None:
        return {}
    channel = result.get('channel')
    if channel is None:
        return {}
    item = channel.get('item')
    location = channel.get('location')
    units = channel.get('units')
    if (location is None) or (item is None) or (units is None):
        return {}
    condition = item.get('condition')
    if condition is None:
        return {}
    # print(json.dumps(item, indent=4))
    speech = "Today the weather in " + location.get('city') + ": " + condition.get('text') + \
             ", And the temperature is " + condition.get('temp') + " " + units.get('temperature')
    print("Response:")
    print(speech)
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }

# OTP VERIFICATION
def processOTPRequest(req):
    otp_query = makeOTPQuery(req)
    if otp_query is None:
        return {}  
    res = checkOTP(otp_query)
    return res

def makeOTPQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    secretcode = parameters.get("secret-code")
    if secretcode is None:
        return None
    return secretcode

def checkOTP(userOTP):
    totp = pyotp.TOTP("JBSWY3DPEHPK3PXP")
    otp = totp.now()
    if str(userOTP) == otp:
        speech = "Got it.  Do you need to file dispute - charge back or change billing agreements?"
    else:
        speech = "Wrong OTP : Oops that was wrong OPT. Please say that again."
    return {
            "speech": speech,
            "displayText": speech,
            "source": "apiai-weather-webhook-sample"
    }

#EMAIL VERIFICATION
def processEmailVerificationRequest(req):
    print("processEmailVerificationRequest Nikhil....")
    result = req.get("result")
    parameters = result.get("parameters")
    emailId = parameters.get("email")
    print(" Received Email Address is :", emailId)

    if  emailId is None:
        return {}
    resp = makeEmailVerificationResult(emailId)
    return resp

def makeEmailVerificationResult(email):
    verifiedList = ['nikhilraog@gmail.com', 'rgautam@gmail.com', 'sandeeptengli@gmail.com', 'aggarwal@gmail.com']
    print("makeEmailVerificationResult ,, email is ", email)
    if  email is not None:
        if email in verifiedList: 
            speech = "Got it. Let me pull up your account. To get you further help, please say the OPT that I have sent to your phone."
        else:
            speech = "Oops I did not find any such account. Please say your paypal linked email address"
    return {
            "speech": speech,
            "displayText": speech,
            "source": "makeEmailVerificationResult"
    }
    

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host='0.0.0.0')
    #app.run(host='127.0.0.1',port='5000',   debug = False/True, ssl_context=context)
