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

"""Module that holds the configuration for app.py including
API keys, temperature and forecast defaults and limits

This is meant to be used with the sample weather agent for Dialogflow, located at
https://console.dialogflow.com/api-client/#/agent//prebuiltAgents/Weather

This requires setting the WWO_API_KEY constant in config.py to a string with
a valid WWO API key for retrieving weather up to 14 days in the future. Get an
WWO API key here: https://developer.worldweatheronline.com/api/
"""

WWO_API_KEY = 'd051af1acc324dc8a50144457183004'
MAX_FORECAST_LEN = 13
_DEFAULT_TEMP_UNIT = 'F'

_TEMP_LIMITS = {
    'hot': {'C': 25, 'F': 77},
    'warm': {'C': 15, 'F': 59},
    'chilly': {'C': 15, 'F': 41},
    'cold': {'C': -5, 'F': 23}
}
