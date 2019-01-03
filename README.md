Dependancies:
    python3
    beanstalkd
    flask

Queue system start:
$ beanstalkd -V

Producent message send:
./producer.extension 2016.20 2012-07-08 11:14:15

Consument start :
    Log system API
    $ python3 consument.py -l
    Event system API
    $ python3 consument.py -e

Flask server to receive the PUT and POST:
    Flask server is printing the received message from producent.
    $./run_server.sh 

Unit Testing: 
$ python3 -m unittest test.py
