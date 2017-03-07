const express = require('express');
const router = express.Router();

var pg = require('pg');
 
// create a config to configure both pooling behavior 
// and client options 
// note: all config is optional and the environment variables 
// will be read if the config is not present 
var config = {
  user: 'postgres', //env var: PGUSER 
  database: 'postgres', //env var: PGDATABASE 
  password: 'student', //env var: PGPASSWORD 
  host: 'localhost', // Server hosting the postgres database 
  port: 5432, //env var: PGPORT 
  max: 10, // max number of clients in the pool 
  idleTimeoutMillis: 30000, // how long a client is allowed to remain idle before being closed 
};
 
 
//this initializes a connection pool 
//it will keep idle connections open for a 30 seconds 
//and set a limit of maximum 10 idle clients 
var pool = new pg.Pool(config);

// Fetch data from psql
router.get('/api/getusers', (req, res, next) => {
    // to run a query we can acquire a client from the pool, 
    // run a query on the client, and then return the client to the pool 
    pool.connect(function(err, client, done) {
      if(err) {
        return console.error('error fetching client from pool', err);
      }
      client.query('SELECT * FROM userdata', function(err, result) {
        //call `done(err)` to release the client back to the pool (or destroy it if there is an error) 
        done(err);
     
        if(err) {
          return console.error('error running query', err);
        }
        return res.json(result.rows);
        //console.log(result.rows[0]);
      });
    });
     
    pool.on('error', function (err, client) {
      // if an error is encountered by a client while it sits idle in the pool 
      // the pool itself will emit an error event with both the error and 
      // the client which emitted the original error 
      // this is a rare occurrence but can happen if there is a network partition 
      // between your application and the database, the database restarts, etc. 
      // and so you might want to handle it and at least log it out 
      console.error('idle client error', err.message, err.stack)
    }) 
});

// Insert data
//curl --data "username=test&password=789&first_name=first&last_name=last" http://127.0.0.1:3000/api/adduser
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
    const data = {
      username: req.body.username,
      password: req.body.password,
      first_name: req.body.first_name,
      last_name: req.body.last_name,
      last_login_time: new Date(Date.now()),
      last_login_ip: getIP()
    };

    pool.connect(function(err, client, done) {
      if(err) {
        return console.error('error fetching client from pool', err);
      }
      client.query('INSERT INTO userdata(username, password, first_name, last_name, last_login_time, last_login_ip) values($1, $2, $3, $4, $5, $6)', [data.username, data.password, data.first_name, data.last_name, data.last_login_time, data.last_login_ip], function(err, result) {
        //call `done(err)` to release the client back to the pool (or destroy it if there is an error) 
        done(err);
     
        if(err) {
          return console.error('error running query', err);
        }
        return res.json(result);
        //console.log(result.rows[0]);
      });
    });
     
    pool.on('error', function (err, client) {
      // if an error is encountered by a client while it sits idle in the pool 
      // the pool itself will emit an error event with both the error and 
      // the client which emitted the original error 
      // this is a rare occurrence but can happen if there is a network partition 
      // between your application and the database, the database restarts, etc. 
      // and so you might want to handle it and at least log it out 
      console.error('idle client error', err.message, err.stack)
    }) 
});


// Update data





module.exports = router;
