const express = require('express');
const router = express.Router();
const moment = require('moment');
var db = require('./db.js');
var fs = require('fs');

// Logout
router.post('/logout', (req, res, next) => {
	req.session.destroy();
    res.redirect('/');
});

// Dashboard
router.get('/dashboard', (req, res, next) => {
  if(req.session && req.session.user) {
    db.tx(t=> {
        return t.batch([
            t.one("SELECT username, password, first_name, last_name, last_login_time, last_login_ip FROM userdata WHERE username=$1 and password=$2", [req.session.user.username, req.session.user.password]),
            t.any("SELECT path FROM user_videos WHERE username=($1)", [req.session.user.username])
        ]);
    }).then(data => {
    	console.log(data[1]);
    	var myFiles = [];
    	for (var i = 0, len = data[1].length; i < len; i++) {
        	var tmp = data[1][i].path.split("/");
        	myFiles.push(tmp[tmp.length - 1]);
		}
		var myTime = data[0].last_login_time;
		var USTime = (moment.unix(myTime/1000).subtract(7, 'hours').format('dddd, MMMM Do YYYY, h:mm a'));
        res.render('main', {
              "username": data[0].username, 
              "first_name": data[0].first_name, 
              "last_name": data[0].last_name, 
              "last_login_time": USTime, 
              "last_login_ip": data[0].last_login_ip,
        	  files : myFiles
            });
      })
      .catch(error => {
          console.error(error);
          res.redirect('/index.html');
      });

  } else {
    res.redirect('/index.html');
  }
});

// Login
router.post('/api/login', (req, res, next) => {


    // Get IP
    function getIP() {
      var str = req.headers['x-forwarded-for'] || 
         req.connection.remoteAddress || 
         req.socket.remoteAddress ||
         req.connection.socket.remoteAddress;

      var res = str.split(":");
      return res[res.length - 1];
    }

    // Grab data from http request
    const reqData = {
      username: req.body.username,
      password: req.body.password,
      last_login_time: Date.now(),
      last_login_ip: getIP()
    };
    var saveData;

    db.tx(t=> {
        return t.batch([
            t.one("SELECT username, password, first_name, last_name, last_login_time, last_login_ip FROM userdata WHERE username=$1 and password=$2", [reqData.username, reqData.password]),
            t.none("UPDATE userdata SET last_login_time=now()::timestamp, last_login_ip=($1) WHERE username=($2)", [reqData.last_login_ip, reqData.username])
        ]);
      })
      .then(data=> {
          if (data) {
            // Store session data 
            req.session.user = data[0];
            res.redirect('/dashboard');
          } else {
            res.redirect('/wrongpassword.html');
          } 
      })
      .catch(error=> {
          // error
          //console.error(error);
          res.redirect('/wrongpassword.html');
      });
});

// Register
router.post('/api/register', (req, res, next) => {
    // Get IP
    function getIP() {
      var str = req.headers['x-forwarded-for'] || 
         req.connection.remoteAddress || 
         req.socket.remoteAddress ||
         req.connection.socket.remoteAddress;

      var res = str.split(":");
      return res[res.length - 1];
    }

    // Grab data from http request
    const reqData = {
      username: req.body.username,
      password: req.body.password,
      first_name: req.body.first_name,
      last_name: req.body.last_name,
      last_login_time: new Date(Date.now()),
      last_login_ip: getIP(),
      email: req.body.email
    };

    db.any("SELECT username FROM userdata")
      .then(data => {
        //console.log(data[0].username);
        function checkExist() {
            var i = null;
            for (i = 0; data.length > i; i += 1) {
                if (data[i].username === reqData.username) {
                    return true;
                }
            }
            return false;
        };

        if (checkExist()) {
          console.log("Duplicate username!");
          res.redirect('/duplicated.html');
        } else {
          db.none("INSERT INTO userdata(username, password, first_name, last_name, last_login_time, last_login_ip, email) values($1, $2, $3, $4, $5, $6, $7)", [reqData.username, reqData.password, reqData.first_name, reqData.last_name, reqData.last_login_time, reqData.last_login_ip, reqData.email])
            .then(data => {
              console.log("Inserted new user!");
              // Store session data 
              req.session.user = reqData;
              res.redirect('/dashboard');
            })
            .catch(error => {
                // error;
                console.error(error);
            });
        }
      })
      .catch(error => {
          // error;
          console.error(error);
      });
});


// Fetch data from psql ******TEST ONLY*******
router.get('/api/getusers', (req, res, next) => {


  db.any("SELECT * FROM userdata")
    .then(data => {
      res.json(data);
    })
    .catch(error => {
        // error;
        console.error(error);
    });
});

// Insert data
// curl --data "username=test4&password=789&first_name=first&last_name=last&email=123@test.com" http://127.0.0.1:3000/api/adduser
router.post('/api/adduser', (req, res, next) => {
    // Get IP
    function getIP() {
      var str = req.headers['x-forwarded-for'] || 
         req.connection.remoteAddress || 
         req.socket.remoteAddress ||
         req.connection.socket.remoteAddress;

      var res = str.split(":");
      return res[res.length - 1];
    }

    // Grab data from http request
    const reqData = {
      username: req.body.username,
      password: req.body.password,
      first_name: req.body.first_name,
      last_name: req.body.last_name,
      last_login_time: new Date(Date.now()),
      last_login_ip: getIP(),
      email: req.body.email
    };

    db.none("INSERT INTO userdata(username, password, first_name, last_name, last_login_time, last_login_ip, email) values($1, $2, $3, $4, $5, $6, $7)", [reqData.username, reqData.password, reqData.first_name, reqData.last_name, reqData.last_login_time, reqData.last_login_ip, reqData.email])
      .then(data => {
        console.log("Inserted new user!");
      })
      .catch(error => {
          // error;
          console.error(error);
      });
});


// Update 
// curl -X PUT --data "username=test5&password=789&first_name=first&last_name=last&email=123@test.com" http://127.0.0.1:3000/api/updateuser/2
router.put('/api/updateuser/:user_id', (req, res, next) => {
    // Get IP
    function getIP() {
      var str = req.headers['x-forwarded-for'] || 
         req.connection.remoteAddress || 
         req.socket.remoteAddress ||
         req.connection.socket.remoteAddress;

      var res = str.split(":");
      return res[res.length - 1];
    }
    // Grab data from the URL parameters
    const id = req.params.user_id;

    // Grab data from http request
    const reqData = {
      username: req.body.username,
      password: req.body.password,
      first_name: req.body.first_name,
      last_name: req.body.last_name,
      last_login_time: new Date(Date.now()),
      last_login_ip: getIP(),
      email: req.body.email
    };

    db.none("UPDATE userdata SET username=($1), password=($2), first_name=($3), last_name=($4), last_login_time=($5), last_login_ip=($6), email=($7) WHERE id=($8)", [reqData.username, reqData.password, reqData.first_name, reqData.last_name, reqData.last_login_time, reqData.last_login_ip, reqData.email, id])
      .then(data => {
        console.log("Updated new user!");

      })
      .catch(error => {
          // error;
          console.error(error);
      });

});

// Delete one video
router.get('/videos', (req, res, next) => {
	console.log("delete video section!!");

    db.none("DELETE FROM user_videos WHERE path=$1", ["public/videos/" + req.query.filename])
      .then(data => {
        fs.unlink("public/videos/" + req.query.filename);
        console.log("Deleted a video!");
      })
      .catch(error => {
          // error;
          console.error(error);
      });
	res.redirect('/dashboard');
});

// Mobile user router to video player
router.get('/*.(mov|MOV|mp4|MP4)', function (req, res) {
	res.render('videoplayer', {
               "url": req.url 
	});

})

// Check new file update
router.get('/checkUpdate', (req, res, next) => {

  var name = req.query.username; 
  var statusFile = '/Facial-Recognition/web/status/' + name + '.status';
  db.any("SELECT count(*) FROM user_videos WHERE username=$1", [name])
    .then(data => {

	function checkIfFile(file, cb) {
 	 fs.stat(file, function fsStat(err, stats) {
    	if (err) {
      	if (err.code === 'ENOENT') {
        	return cb(null, false);
      	} else {
        	return cb(err);
     	 }
    	}
    	return cb(null, stats.isFile());
  	});
	}

		checkIfFile(statusFile, function(err, isFile) {
			if (isFile) {
			fs.readFile(statusFile, function (err, context) { 
	  			if (err) throw err;
				var ary = context.toString().split('\n');
	    		var lastline = ary[ary.length-2];	
			    console.log(data[0].count);
				res.send(JSON.stringify({msg:lastline, count:data[0].count}));
			}); 
			} else {
				res.send(JSON.stringify({count:data[0].count}));
			} 
		});
      //res.json(data);
    })
    .catch(error => {
        // error;
        console.error(error);
    });
	
     //res.send(JSON.stringify({key:new Date()}));
});

module.exports = router;
