var ws = new WebSocket("ws://localhost:8000/log_socket/");


ws.onopen = function() {
//    ws.send("Hello, world");
};

count = 0
max = 30

ws.onmessage = function (evt) {
    data = JSON.parse(evt.data);
    kilowatt = Math.round(data.kilowatt*1000)/1000;
    second   = Math.round(data.second  *100)/100;
    count++;
    $(".log_box").prepend("<p id=" + count + ">" + kilowatt + " kW (" + second + "s)" + "</p>");

    if (count > max) {
        $("#" + (count - max)).remove();
    }
};
