EXPRTIO = { }

EXPRTIO.apiaiurl = "https://api.api.ai/v1";

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

EXPRTIO.handleQueryInput = function(field) {
    EXPRTIO.query(field.value, function (text) {
        document.getElementById("exprt-response").innerHTML = text;
    });
}
