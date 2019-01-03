import greenstalk
import requests
import json
import getopt
import sys

class Client():
    """Main class used for reading the queue and sending to the API."""
    def __init__(self, qhost, qport, end_system, ehost, eport):
        self.host = qhost
        self.port = qport
        if end_system is 'Log':
            self.endpoint = Log_system(ehost, eport)
        elif end_system is 'Events':
            self.endpoint = Events_system(ehost, eport)
        else:
            uri = 'None'
            self.endpoint = Endpoint_system(ehost, eport, uri)

    def consume(self):
        """Loop which is reading the queue. Deleteing the massage only if message accepted."""
        with greenstalk.Client(host=self.host, port=self.port) as queue:
            while True:
                try:
                    job = queue.reserve()
                    #print(job.body)
                    self.endpoint.send(job.body)
                    queue.delete(job) 
                except Exception as err: 
                    queue.delete(job)
                    queue.put(job.body, delay=10)
                    print("Delaying the send to API.") 

class Endpoint_system():
    """Super class for the endpoint system classes."""
    def __init__(self, ehost, eport, uri):
        self.host = ehost
        self.port = eport
        self.uri = uri

    def endpoint(self):
        return "http://{0}:{1}{2}".format(self.host, self.port, self.uri)

    def send(self, data):
        raise Exception("No system selected", data)

    def get_databox(self, data):
        return data.split(' ')


class Log_system(Endpoint_system):
    def __init__(self, ehost, eport):
        uri = '/api/log'
        super().__init__(ehost, eport, uri)
        print('Log system init')

    def create_data(self, data):
        """Create a JSON for log system"""
        databox = self.get_databox(data)
        
        self.json_data = {
            "what": "DEPLOY-"+databox[0],
            "tags": "code-relase",
            "datetime": databox[1]+" "+databox[2]
            } 

    def send(self, data):
        self.create_data(data)
        r = requests.put(url = self.endpoint(), data = self.json_data)
        response = r.text
        print("The response URL is:{0}".format(response))


class Events_system(Endpoint_system):
    def __init__(self, ehost, eport):
        uri = '/api/event/create'
        super().__init__(ehost, eport, uri)
        print('Events system init')

    def create_data(self, data):
        """Create a JSON for event system"""
        databox = self.get_databox(data)
        import datetime
        import time
        import re
        try:
            matchbox = re.match(r'(\d+)-(\d+)-(\d+)\s(\d+):(\d+):(\d+)', 
                            databox[1] + " " + databox[2])
        except Exception as err:
            raise Exception(err)

        dt = datetime.datetime(int(matchbox[1]), int(matchbox[2]), 
                               int(matchbox[3]), int(matchbox[4]), 
                               int(matchbox[5]), int(matchbox[6]))
        timestamp = int((time.mktime(dt.timetuple()) + dt.microsecond/1000000.0)*1000) 

        self.json_data = json.dumps({"event":[ 
                                       { "id": str(databox[0]), 
                                         "type": 2, 
                                         "timestamp": str(timestamp) 
                                       }]
                                    }) 

    def send(self, data):
        """Send the data to the API of the server."""
        self.create_data(data)
        r = requests.post(url = self.endpoint(), data = self.json_data)
        response = r.text
        print("The response URL is:{0}".format(response))  
        


if __name__ == '__main__':
    
    opts, args = getopt.getopt(sys.argv[1:], 'le') 
    endpoint_system = 'None'

    for o, a in opts:
        if o == '-l':
            endpoint_system = 'Log'
        elif o == '-e':
            endpoint_system = 'Events'

    queue_address = '0.0.0.0'
    queue_port = 11300
    #endpoint_system = 'Events'
    endpoint_address = '0.0.0.0'
    endpoint_port = 5000

    client = Client(queue_address, queue_port, endpoint_system, endpoint_address, endpoint_port)    
    client.consume()
