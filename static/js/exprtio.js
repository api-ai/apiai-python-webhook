EXPRTIO = { }

EXPRTIO.apiaiurl = "https://api.api.ai/v1";

EXPRTIO.entities = [ ];

EXPRTIO.query = function(text, callback) {
    var data = {
        query: [ text ],
        "lang": "en",
    };
    jQuery.ajax({
        url: EXPRTIO.apiaiurl + "/query",
        type: 'post',
        data: JSON.stringify(data),
        headers: {
            Authorization: "Bearer 43ab7b832fb1437abf82f2a77a1d5952"
        },
        dataType: "json",
        contentType: "application/json",
        success: function (data) {
            console.info(data);
            callback(data.result.speech);
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

EXPRTIO.handleKnowledgeInput = function(field) {
    if (EXPRTIO.debounce()) {
        return;
    }
    var knowledgeWords = field.value.split(" ");
    var vendor = knowledgeWords.shift();
    var offering = knowledgeWords.shift();
    var product = knowledgeWords.join(" ");

    EXPRTIO.extendEntity("vendor", vendor);
//    EXPRTIO.extendEntity("offering", offering);
    EXPRTIO.extendEntity("product", product);
}

EXPRTIO.changeOnEnter = function(event) {
    if (event.keyCode == 13) {
        event.target.onchange();
    }
}

EXPRTIO.refreshEntities();
