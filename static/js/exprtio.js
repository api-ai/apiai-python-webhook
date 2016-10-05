EXPRTIO = { }

EXPRTIO.apiaiurl = "https://api.api.ai/v1";

EXPRTIO.CYPHER_URL = "http://app5505001242pigb.sb10.stations.graphenedb.com:24789/db/data/transaction/commit";

EXPRTIO.CYPHER_AUTH = "Basic YXBwNTUwNTAwMTItQ252WGxnOnd3WUVVUW9hSXlNdjEzUzg0Qllk";

EXPRTIO.APIAI_CLIENTAUTH = "Bearer 43ab7b832fb1437abf82f2a77a1d5952";

EXPRTIO.APIAI_DEVAUTH = "Bearer 69d4385715ae43568cdd9e75b92afdcc";

EXPRTIO.entities = [ ];

EXPRTIO.query = function(text, callback) {
    var data = {
        query: [ text ],
        "lang": "en",
    };
    jQuery.ajax({
        url: EXPRTIO.apiaiurl + "/query?v=20150910",
        type: 'post',
        data: JSON.stringify(data),
        headers: {
            Authorization: EXPRTIO.APIAI_CLIENTAUTH
        },
        dataType: "json",
        contentType: "application/json",
        success: function (data) {
            console.info(data);
            callback(data.result.fulfillment.speech);
        }
    });
}

EXPRTIO.lastOperation = (new Date()).getTime();
EXPRTIO.debounce = function() {
    var now = (new Date()).getTime();
    var last = EXPRTIO.lastOperation;
    EXPRTIO.lastOperation = now;
    if (now - last < 100) {
        return true;
    }
    return false;
}

EXPRTIO.handleQueryInput = function(field) {
    if (EXPRTIO.debounce()) {
        return;
    }
    EXPRTIO.query(field.value, function (text) {
        document.getElementById("exprt-response").innerHTML = text;
    });
}

EXPRTIO.refreshEntities = function() {
    jQuery.ajax({
        url: EXPRTIO.apiaiurl + "/entities",
        type: 'get',
        headers: {
            Authorization: "Bearer 69d4385715ae43568cdd9e75b92afdcc"
        },
        dataType: "json",
        contentType: "application/json",
        success: function (data) {
            console.info(data);
            EXPRTIO.entities = data;
            for (i in EXPRTIO.entities) {
                var entity = EXPRTIO.entities[i];
                EXPRTIO.refreshEntity(entity);
            }
        }
    });
}

EXPRTIO.refreshEntity = function(entity, callback) {
    jQuery.ajax({
        url: EXPRTIO.apiaiurl + "/entities/" + entity.name,
        type: 'get',
        headers: {
            Authorization: EXPRTIO.APIAI_DEVAUTH
        },
        dataType: "json",
        contentType: "application/json",
        success: function (data) {
            console.info(data);
            entity.entries = data.entries;
        }
    });
}

EXPRTIO.getEntityId = function(entityName) {
    for (var i in EXPRTIO.entities) {
        var entity = EXPRTIO.entities[i];
        if (entity.name == entityName) {
            return entity.id;
        }
    }
}

//build a synonym-mapping hash table to optimize this
EXPRTIO.normalizeEntity = function(entityValue, entityName) {
    for (var i in EXPRTIO.entities) {
        var entity = EXPRTIO.entities[i];
        if (entityName && (entity.name != entityName)) {
            continue;
        }
        var scopedValue = EXPRTIO.normalizeScopedEntity(entityValue, entity);
        if (scopedValue) {
            return scopedValue;
        }
    }

    return entityValue;
}

EXPRTIO.normalizeScopedEntity = function(entityValue, entity) {
    for (var j in entity.entries) {
        var entry = entity.entries[j];
        for (var k in entry.synonyms) {
            var synonym = entry.synonyms[k];
            if (synonym.toLowerCase() == entityValue.toLowerCase()) {
                return entry.value;
            }
        }
    }
    return null;
}

EXPRTIO.extendEntity = function(entityName, entity) {
    var entityId = EXPRTIO.getEntityId(entityName);
    if (!entityId) {
        return;
    }
    var data = [{
        value: entity,
    }];
    jQuery.ajax({
        url: EXPRTIO.apiaiurl + "/entities/" + entityId + "/entries",
        type: 'post',
        data: JSON.stringify(data),
        headers: {
            Authorization: "Bearer 69d4385715ae43568cdd9e75b92afdcc"
        },
        dataType: "json",
        contentType: "application/json",
        success: function (data) {
            console.info(data);
        }
    });
}

EXPRTIO.graphCall = function(data, callback) {
    jQuery.ajax({
        url: EXPRTIO.CYPHER_URL,
        type: 'post',
        data: JSON.stringify(data),
        headers: {
            Authorization: EXPRTIO.CYPHER_AUTH
        },
        dataType: "json",
        contentType: "application/json",
        success: function (data) {
            callback(data.results);
        }
    });
}

//need to hook this up to an api.ai action
EXPRTIO.testFindQuery = function() {
    EXPRTIO.findQuery({ "vendor": "Safeway", "anything": "Asia", "offering": "SHIPS_TO" }, "offeringPath", function(speech) {
        console.log("Databases-stored query result: " + speech);
    });
}

EXPRTIO.findQuery = function(parameters, action, callback) {
    var statement = "MATCH (QUERY:Query {name: '" +action + "'}) RETURN QUERY AS query";
    var statements = [{statement: statement}];

    var data = {
        statements: statements
    };
    EXPRTIO.graphCall(data, function(results) {
        var query = EXPRTIO.unpackNeoResults(results)[0]["query"];
        EXPRTIO.runGenericQuery(parameters, query, callback);
    });
}

EXPRTIO.unpackNeoResults = function(results) {
    var unpacked = [];
    //these multiple result entries must be from multiple queries,
    //we just run one typically
    var result = results[0];
    for (i in result.data) {
        var namedResult = { };
        var row = result.data[i].row;
        for (j in result.columns) {
            var name = result.columns[j];
            namedResult[name] = row[j];
        }
        unpacked.push(namedResult);
    }
    return unpacked;
}

EXPRTIO.runGenericQuery = function(parameters, genericQuery, callback) {
    var formatter = genericQuery.formatter;
    var formatterArgs = genericQuery.formatterArgs;
    var query = genericQuery.query;
    var queryArgs = genericQuery.queryArgs;

    var concreteQuery = query;
    for (i in queryArgs) {
        var arg = queryArgs[i];
        var components = arg.split(".")
        if (components[0] == "parameters") {
            concreteQuery = concreteQuery.replace(/%s/, parameters[components[1]]);
        }
    }

    var statement = concreteQuery;
    var statements = [{statement: statement}];

    var data = {
        statements: statements
    };
    EXPRTIO.graphCall(data, function(results) {
        var speech = "";
        var neoResults = EXPRTIO.unpackNeoResults(results);
        for (i in neoResults) {
            var neoResult = neoResults[i];
            var speechLine = formatter;
            for (j in formatterArgs) {
                var arg = formatterArgs[j];
                var components = arg.split(".")
                if (components[0] == "parameters") {
                    speechLine = speechLine.replace(/%s/, parameters[components[1]]);
                } else if (components[0] == "record") {
                    speechLine = speechLine.replace(/%s/, neoResult[components[1]][components[2]]);
                }
            }
            speech += speechLine;
        }
        callback(speech);
    });
}

EXPRTIO.createGraphKnowledge = function(vendor, offering, product) {
    vendor = EXPRTIO.normalizeEntity(vendor, "vendor");
    offering = EXPRTIO.normalizeEntity(offering, "offering");
    product = EXPRTIO.normalizeEntity(product, "product");

    var statement = "MERGE (VENDOR:Company {name:'" + vendor + "'}) MERGE (PRODUCT:Device {name:'" + product + "'}) CREATE (VENDOR)-[:"+offering+"]->(PRODUCT)";
    var statements = [{statement: statement}];

    var data = {
        statements: statements
    };
    EXPRTIO.graphCall(data);
}

EXPRTIO.handleKnowledgeInput = function(field) {
    if (EXPRTIO.debounce()) {
        return;
    }
    var knowledgeWords = field.value.split(" ");
    var vendor = knowledgeWords.shift();
    var offering = knowledgeWords.shift();
    var product = knowledgeWords.join(" ");

    EXPRTIO.extendEntity("vendor", vendor);
    EXPRTIO.extendEntity("offering", offering);
    EXPRTIO.extendEntity("product", product);
    EXPRTIO.createGraphKnowledge(vendor, offering, product);
    field.value = "";
}

EXPRTIO.changeOnEnter = function(event) {
    if (event.keyCode == 13) {
        event.target.onchange();
    }
}

EXPRTIO.refreshEntities();
