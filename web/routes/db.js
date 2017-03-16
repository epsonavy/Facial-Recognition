var pgp = require('pg-promise')();
 
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