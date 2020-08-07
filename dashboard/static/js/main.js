var socket = io();
$(document).ready(function () {
    var opts = {
        angle: -0.1,
        lineWidth: 0.4,
        radiusScale: 1,
        pointer: {
            length: 0.6,
            strokeWidth: 0.035,
            color: "#000000"
        },
        limitMax: true,
        limitMin: true,
        colorStart: "#6FADCF",
        colorStop: "#8FC0DA",
        strokeColor: "#E0E0E0",
        generateGradient: true,
        highDpiSupport: true,
        renderTicks: {
            divisions: 5,
            divWidth: 1.1,
            divLength: 0.42,
            divColor: "#333333",
            subDivisions: 4,
            subLength: 0.32,
            subWidth: 0.6,
            subColor: "#666666"
        },
        staticLabels: {
            font: "10px sans-serif",
            labels: [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
            color: "#000000",
            fractionDigits: 0
        }
    };
    var target = document.getElementById("gauge-canvas");
    var gauge = new Gauge(target).setOptions(opts);
    gauge.maxValue = 100;
    gauge.setMinValue(0);
    gauge.animationSpeed = 32;
    gauge.set(0);

    var opts2 = {
        angle: 0.25,
        lineWidth: 0.26,
        radiusScale: 1,
        pointer: {
            length: 0.52,
            strokeWidth: 0.022,
            color: '#000000'
        },
        limitMax: false,
        limitMin: false,
        colorStart: '#6F6EA0',
        colorStop: '#C0C0DB',
        strokeColor: '#EEEEEE',
        generateGradient: true,
        highDpiSupport: true,
        staticZones: [
            { strokeStyle: "#F03E3E", min: 13400, max: 14100 },
            { strokeStyle: "#FFDD00", min: 14100, max: 14500 },
            { strokeStyle: "#30B32D", min: 14500, max: 14900 },
            { strokeStyle: "#FFDD00", min: 14900, max: 15300 },
            { strokeStyle: "#F03E3E", min: 15300, max: 16000 }
        ]
        //percentColors: [[0.0, "#a9d70b"], [0.4, "#f9c802"], [0.5, "#00ff00"], [0.6, "#f9c802"], [1.0, "#a9d70b"]]
    };
    var target2 = document.getElementById('gauge2-canvas');
    var gauge2 = new Gauge(target2).setOptions(opts2);
    gauge2.maxValue = 16000;
    gauge2.setMinValue(13400);  // Prefer setter over gauge.minValue = 0
    gauge2.animationSpeed = 32; // set animation speed (32 is default value)
    gauge2.set(13400); // set actual value
    socket.on("connect", function () {
        socket.emit("my event");
    });
    socket.on("my response", function (msg) {
        gauge.set(msg.vehicle_speed);
        $("#vehicle-speed-val").text(msg.vehicle_speed + " mph");
        gauge2.set(msg.maf * 1000);
        $("#afr-val").text(msg.maf);
        $("#accel-bar").val(msg.accelerator);
        $("#accel-val").text(msg.accelerator + "%");
        $("#throttle-bar").val(msg.throttle);
        $("#throttle-val").text(msg.throttle + "%");
        parseDTC(msg.dtc);
    });
    $("#cruise-form").submit(function () {
        var arr = $("#cruise-form").serializeArray();
        if (arr.length === 2) {
            arr[0]["value"] = "true";
            document.getElementById("accel-range").disabled = true;
            console.log("DISABLING RANGE");
        } else {
            var obj = { "name": "cruise-enable", "value": "false" };
            arr.splice(0, 0, obj);
            document.getElementById("accel-range").disabled = false;
            console.log("ENABLING RANGE");
        }
        if (arr[1]["value"] == "") {
            arr[1]["value"] = "0";
        }
        socket.emit("update cruise", arr);
        return false;
    });
    setInterval(function () {
        socket.emit("my event");
    }, 600);
});

function updateAccel(val) {
    var obj = { "accel-val": val };
    socket.emit("update accel", obj);
}

function parseDTC(dtcList) {
    document.getElementById("dtc-div").innerHTML = "";
    for (dtc of dtcList) {
        var fname = "dtc-" + dtc.num;
        var node = document.createElement("img");
        node.src = "../static/images/" + fname + ".png";
        node.setAttribute("height", "64");
        node.setAttribute("width", "64");
        node.setAttribute("alt", fname);
        node.setAttribute("title", dtc.mesg);
        document.getElementById("dtc-div").appendChild(node);
    }
}