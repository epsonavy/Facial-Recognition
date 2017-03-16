var express = require('express');
var router = express.Router();
var multiparty = require("connect-multiparty");
var multipartyMiddleware = multiparty();

/* GET home page. */
router.get('/', function(req, res, next) {
  res.render('index', { title: 'Express' });
});
router.post('/upload', multipartyMiddleware, function(req, res){
	console.log(req.files);
	console.log("File has been uploaded!");
	res.json({success: true});
});

module.exports = router;
