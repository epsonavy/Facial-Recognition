var pgp = require('pg-promise')();

//Postgres configured for localhost
var config = {
  user: 'postgres', 
  database: 'postgres',
  password: 'student', 
  host: 'localhost',  
  port: 5432,  
};
 
var db = pgp(config);

// Exporting the database object for shared use:
module.exports = db;