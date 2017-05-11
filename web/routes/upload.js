var express = require('express');
var multipart = require('connect-multiparty');
var multipartMiddleware = multipart({ uploadDir: './uploading' });
var multipartDistributed = multipart({uploadDir: './uploading_distributed'});
var router = express.Router();
var config = require('../config.js');
var fs = require('fs');
var db = require('./db.js');
//var Upload = require('../models/upload.js');

router.post('/', multipartMiddleware, function(req, res) {
	var files = req.files;
	//console.log(files);
	console.log(files.upload.path);
	console.log(req.body.username);

	fs.createReadStream(files.upload.path).pipe(fs.createWriteStream('/Facial-Recognition/web/processing/' + req.body.username + '.mp4'));
	fs.unlink(files.upload.path, function(err){
		if(err) throw err;
	});

router.post('/distributed', multipartMiddleware, function(req, res){
	var files = req.files;
	console.log(files.upload.path);
	console.log(req.body.username);

	fs.createReadStream(files.upload.path).pipe(fs.createWriteStream('/Facial-Recognition/web/processing_distributed/' + req.body.username + '.mp4'));
	fs.unlink(files.upload.path, function(err){
		if(err) throw err;
	});
});
/*
	db.none("INSERT INTO user_videos(path, username) values($1, $2)", [files.upload.path, req.body.username])
            .then(data => {
              console.log("Inserted new video!");
			  res.redirect('/dashboard');
            })
            .catch(error => {
                 error;
                console.error(error);
           });*/

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
