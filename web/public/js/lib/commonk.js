//<script src="socket.io/socket.io.js"></script>
//add this outside
var hostname, client;

hostname = window.location.hostname;

client   = new BinaryClient('ws://' + hostname + ':9000');


function fizzle(e) {
    e.preventDefault();
    e.stopPropagation();
}

function emit(event, data, file) {
    file       = file || {};
    data       = data || {};
    data.event = event;
    console.log("kevin is gay!");

	var socket = new io.Socket();
	socket.connect('localhost:27015');

	var onConnectPromise = new Promise(function(resolve, reject){
		socket.on('connect', function(){
			resolve("connected");
		});
	});
	
	onConnectPromise.then(function(value){
		console.log("Success!");
	}, function(reason){
		console.log("Error occurred while connecting to load balancer");
	});

	var onReceivePromise = new Promise(function(Resolve, reject){
		socket.on('message', function(data){
			resolve(data);
		});
	});

	var address;
	onReceivePromise.then(function(value){
		address = value;
	}, function(reason){
		console.log("Could not receive message from load balancer");
	});

	client = new BinaryClient('ws://' + address + ':9000');
	console.log("PEI LOOK FOR THIS " + address);
    return client.send(file, data);
}
