var ws = new WebSocket("ws://192.168.1.38:8000/log_socket/");


ws.onopen = function() {
//    ws.send("Hello, world");
};


ws.onmessage = function (event) {
    data = JSON.parse(event.data);
    switch (data.COMMAND) {
        case 1:
            log(data.DATA);
            break
        case 2:
            relays(data.DATA)
            break
    }
};

count = 0
max = 30

log = function (data) {
    kilowatt = Math.round(data[0]*1000)/1000;
    second   = Math.round(data[1]*100)/100;
    count++;
    $(".log_box").prepend("<p id=" + count + ">" + kilowatt + " kW (" + second + "s)" + "</p>");

    if (count > max) {
        $("#" + (count - max)).remove();
    }
}

relays = function (data) {
    for (i = 0; i < data.length; i++) {
        relay = $("#status > #" + (i+1))
        if (data[i]) {
            relay.css("background-color", "green")
        } else {
            relay.css("background-color", "red")
        }
    }
//    $(".relays").prepend("<p id=" + count + ">" + kilowatt + " kW (" + second + "s)" + "</p>");
}