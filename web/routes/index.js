const express = require('express');
const router = express.Router();

var pgp = require('pg-promise')();
 
var config = {
  user: 'postgres', 
  database: 'postgres',
  password: 'student', 
  host: 'localhost',  
  port: 5432,  
};
 
var db = pgp(config);

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
          if (data[0]) {
            return res.render('main', {
              "username": data[0].username, 
              "first_name": data[0].first_name, 
              "last_name": data[0].last_name, 
              "last_login_time": data[0].last_login_time, 
              "last_login_ip": data[0].last_login_ip
            });
          } else {
            return res.redirect('/wrongpassword.html');
          } 
      })
      .catch(error=> {
          // error
          console.error(error);
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
        } else {
          db.none("INSERT INTO userdata(username, password, first_name, last_name, last_login_time, last_login_ip, email) values($1, $2, $3, $4, $5, $6, $7)", [reqData.username, reqData.password, reqData.first_name, reqData.last_name, reqData.last_login_time, reqData.last_login_ip, reqData.email])
            .then(data => {
              console.log("Inserted new user!");
              return res.render('main', {
                "username": reqData.username, 
                "first_name": reqData.first_name, 
                "last_name": reqData.last_name, 
                "last_login_time": reqData.last_login_time, 
                "last_login_ip": reqData.last_login_ip
              });

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


// Fetch data from psql
router.get('/api/getusers', (req, res, next) => {

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


module.exports = router;
