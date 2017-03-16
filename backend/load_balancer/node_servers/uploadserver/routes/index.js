var express = require('express');
var router = express.Router();
var request = require('request');
var io = require('socket.io-client');
var net = require('net');

/* GET home page. */
router.get('/', function(req, res, next) {
  res.render('index', { title: 'Express' });
});

router.post('/upload', function(req, res){
	console.log("i'm here");
	var rerouteSocket = new net.Socket();
	rerouteSocket.connect(27015, 'localhost', function(){
		rerouteSocket.on('data', function(data){
			var meow = data.toString();
			res.redirect(307, meow);
		});
	});
});

module.exports = router;
