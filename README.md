# Facial-Recognition

## A Better way to connect postgresSQL

### More detail please see official pg-promise

*Postgres SQL setting:*

``````
var pgp = require('pg-promise')();
 
var config = {
  user: 'postgres', 
  database: 'postgres',
  password: 'student', 
  host: 'localhost',  
  port: 5432,  
};
 
var db = pgp(config);

```````
