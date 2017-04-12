var express = require('express');
var multipart = require('connect-multiparty');
var multipartMiddleware = multipart({ uploadDir: './public/videos/' });

var router = express.Router();
var config = require('../config.js');
var fs = require('fs');
//var Upload = require('../models/upload.js');

router.post('/', multipartMiddleware, function(req, res) {
	var files = req.files;
	console.log(files.file);
	res.redirect('/dashboard');

/*
	var upload = new Upload();
	var id = upload._id;
	fs.createReadStream(files.file.path).pipe(fs.createWriteStream(config.static_folder + id + ".png"));
	fs.unlink(files.file.path, function(err){
		if (err) throw err;
	})
	upload.url = config.site + "static/" + id + ".png";
	upload.userId = req.id;
	upload.save(function(err, user){
		if(err) throw err;

	});
	res.status(200);
	res.json({
		success: true,
		message: "File was uploaded successfully",
		url: upload.url
	})*/

});

module.exports = router;