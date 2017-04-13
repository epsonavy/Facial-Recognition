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
    //res.redirect('/');
	res.end;
});

module.exports = router;