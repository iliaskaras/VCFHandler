# VCFHandler
###A REST API written with the Flask Web Framework

A Flask Rest API that provides endpoints for manipulating VCF type of files.

## Description

#####This project is a simple template of a typical Flask REST API application.
#####Showcasing:
1. Authentication via JWT
2. Authorization via user permissions
3. Error handling / Multiple error handling capabilities
4. CRUD endpoints
5. Unit & Integration tests
6. SQLAlchemy integration
7. Marshmallow schema validations
8. Rest API response and error formatting.

####VCF file handling endpoints:
1. ***GET***: Retrieve by ID rows from a VCF file in a pagination way.
    * ETag implementation
    * Different type of responses depending on the ACCEPT HTTP header.
      * application/json | application/xml | */*
2. ***POST***: Appends a received row to a VCF file.
3. ***PUT***: Update VCF records that much an ID with a provided row.
4. ***Delete***: Deletes VCF records that match a provided ID. 
######Note: All the endpoints of the application are guarded with user permission, authenticated with JWT, marshmallow request validation, map of the response to a specific format.
## Getting Started

### Dependencies

* Have Docker and docker-compose installed in your OS.
* Linux

### Deploying the REST API

* Download the repository.
* Change directory to VCFHandler where the Makefile is located.
* Run the docker-compose with the Makefile command (warning: you might be required to type your sudo code):
```
make deploy-local
```

### Tests

* Run unit and integration tests with the Makefile command: 
```
make deploy-local
```

## Version History

* 0.1
    * Initial Release
