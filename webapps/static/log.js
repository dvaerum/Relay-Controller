"use strict";
(function () {
    var ws = new ReconnectingWebSocket("ws://" + window.location.host + "/log_socket/");

    ws.onopen = function(event) {
        $(".connection_status").text("Successfully connected to the host (" + window.location.host + ")");
    };

    ws.onerror = function(event) {
        $(".connection_status").text("Fail to connect to the host (" + window.location.host + ")");
    };

    ws.onclose = function(event) {
        $(".connection_status").text("Lost connection to the host (" + window.location.host + ")");
    };

    ws.onmessage = function (event) {
        var data = JSON.parse(event.data);
        switch (data.COMMAND) {
            case 1:
                log(data.DATA);
                break
            case 2:
                relays(data.DATA)
                break
        }
    };

    var log_count = 0
    var log_max_line_number = 20

    var log = function (data) {
        var kilowatt = Math.round(data[0]*1000)/1000;
        var second   = Math.round(data[1]*100)/100;
        log_count++;
        var date = new Date();
        var log_time = $("<div></div>").attr("data-datetime", new Date()).formatDateTime('[yy-mm-dd hh:ii:ss]');
        var log_kW = $("<div></div>").text($.number(kilowatt, 3, ',', ' ') + " kW (" + $.number(second, 2, ',', ' ') + "s)");
        $(".log_box").prepend($("<div></div>").attr({"id": log_count, "class": "line", "style": "background-color: " + ((log_count%2) ? "lightgray" : "white")}).append(log_time, log_kW));
//        $(".log_box").prepend($("<br>").attr({"id": log_count, "class": "line", "style": "background-color: " + ((log_count%2) ? "lightgray" : "white")}).append(log_time, log_kW));
        if (log_count > log_max_line_number) {
            $("#" + (log_count - log_max_line_number)).remove();
        }
    }

    var relays = function (data) {
        for (var i = 0; i < data.length; i++) {
            var relay = $("#status > #" + (data[i][0]))
            if (data[i][1]) {
                relay.css("background-color", "green")
            } else {
                relay.css("background-color", "red")
            }
        }
    }
})();