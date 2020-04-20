# Welcome to company Animal Manager

Application broken down in 2 parts.     
API Server and CLI Client

## Requirements:
* Python 3.7
* Sqlite 3.31

## Running application localy:

#### Using Docker Compose
1) Run server application:
    `docker-compose up`

Upon starting server it will be available via browser at: https://localhost/

#### Available endpoints:    

    / (GET) 
    /status (GET)
    /animals (GET)
    /animal (POST)
    /animal/{id} (GET)
    /animals/species/{species} (GET)
    /user (POST)
    /users (GET)

### Using the client:

#### Demo users: 
shatilov18@gmail.com:password   

Use them to interact with our API via client application by providing them as parameters e.g. :
`./client.sh -u shatilov18@gmail.com -p password status`  

After a successful authentication, providing credentials is not necessary for duration of the 30 minute session.   

#### Commands to try:
* `./client.sh animals`   
* `./client.sh animals/species/cat`   
* `./client.sh animal/1`   
* `./client.sh animal --data "name=Sammy&species=Cat"`   
* `./client.sh user --data "name=Elena&last_name=Shatilov&email=shatilov15@gmail.com&password=nux"`

### Alternative ways of interacting with the server

* Curl: 
    `curl https://localhost:443/animals -k -u shatilov18@gmail.com:password --data "name=Sammy&species=Cat"`
* Browser:
    https://localhost/animals

