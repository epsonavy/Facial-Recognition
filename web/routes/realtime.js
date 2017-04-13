var express = require('express');
var fs = require('fs');
var multipart = require('connect-multiparty');
var multipartMiddleware = multipart({ uploadDir: './public/videos/' });
var router = express.Router();
var config = require('../config.js');
var fs = require('fs');
var db = require('./db.js');

router.post('/', (req, res, next) => {
	//console.log(req.body.imgBase64);
	var base64Data = req.body.imgBase64.replace(/^data:image\/jpeg;base64,/, "");
	// file output to node js root path /web/out.jpg
	fs.writeFile("./public/videos/out.jpg", base64Data, 'base64', function(err) {
  		console.log(err);
	});
	// add __realtime__ with a generated id afterwards
	//FFKnmfsakfnsaFDKDnsfdsaFKNsdafdSAKNFDSAknffdknsafkanFNKDA__realtime__45cxzCOkdsaNgFDgodngf.png
	//this is how we will split it
    //res.redirect('/');
	res.end;
});

router.get('/', (req, res, next) => {
	//We will add load balancer hijacker here later but for now it is okay

	// We need to pass in the username as the token
	res.render('realtime', {address: '54.183.94.59', port: 6654, token: "FFKnmfsakfnsaFDKDns.fdsaFKNsdafdSAKNFDSAkn.ffdknsafkanFNKDA"});
	// Reconnecting will reroute the new socket anyways
});

module.exports = router;