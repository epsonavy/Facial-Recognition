# Facial-Recognition


*Postgres SQL setting:*

``````
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
```````
