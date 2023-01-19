from urllib.parse import urlparse, parse_qs
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from views import *

# Here's a class. It inherits from another class.
# For now, think of a class as a container for functions that
# work together for a common purpose. In this case, that
# common purpose is to respond to HTTP requests from a client.

class HandleRequests(BaseHTTPRequestHandler):
    # Here's a class function
    # replace the parse_url function in the class
    def parse_url(self, path):
        """Parse the url into the resource and id"""
        parsed_url = urlparse(path)
        path_params = parsed_url.path.split('/')  # ['', 'animals', 1]
        resource = path_params[1]
        if parsed_url.query:
            query = parse_qs(parsed_url.query)
            return (resource, query)
        pk = None
        try:
            pk = int(path_params[2])
        except (IndexError, ValueError):
            pass
        return (resource, pk)

    def do_GET(self):
        # self._set_headers(200)
        self._set_headers(200)
        response = {}
        # Parse URL and store entire tuple in a variable
        parsed = self.parse_url(self.path)
        # If the path does not include a query parameter, continue with the original if block
        if '?' not in self.path:
            (resource, id) = parsed
            if resource == "customers":
                if id is not None:
                    response = get_single_customer(id)
                else:
                    response = get_all_customers()
            elif resource == "animals":
                if id is not None:
                    response = get_single_animal(id)
                else:
                    response = get_all_animals()
            elif resource == "employees":
                if id is not None:
                    response = get_single_employee(id)
                else:
                    response = get_all_employees()
            elif resource == "locations":
                if id is not None:
                    response = get_single_location(id)
                else:
                    response = get_all_locations()
        else:  # There is a ? in the path, run the query param functions
            (resource, query) = parsed
            # see if the query dictionary has an email key
            if query.get('email') and resource == 'customers':
                response = get_customer_by_email(query['email'][0])
            elif query.get('status') and resource == 'animals':
                response = get_animal_by_status(query['status'][0])
            elif query.get('location_id') and resource == 'animals':
                response = get_animal_by_location(query['location_id'][0])
            elif query.get('location_id') and resource == 'employees':
                response = get_employee_by_location(query['location_id'][0])
        self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        content_len = int(self.headers.get('content-length', 0))
        post_body = self.rfile.read(content_len)

        # Convert JSON string to a Python dictionary
        post_body = json.loads(post_body)

        # Parse the URL
        (resource, id) = self.parse_url(self.path)
        # Initialize new response
        new_response = None
        if resource == "animals":
            self._set_headers(201)
            new_response = create_animal(post_body)
        elif resource == "locations":
            if "name" in post_body and "address" in post_body:
                self._set_headers(201)
                new_response = create_location(post_body)
            else:
                self._set_headers(405)
                new_response = "ERROR"
        elif resource == "employees":
            self._set_headers(201)
            new_response = create_employee(post_body)
        elif resource == "customers":
            self._set_headers(201)
            new_response = create_customer(post_body)
        # Encode the new animal and send in response
        self.wfile.write(json.dumps(new_response).encode())

    # handle return boolean value
    def do_PUT(self):
        content_len = int(self.headers.get('content-length', 0))
        post_body = self.rfile.read(content_len)
        post_body = json.loads(post_body)
        # Parse the URL
        (resource, id) = self.parse_url(self.path)
        success = False
        if resource == "animals":
            success = update_animal(id, post_body)

        elif resource == "customers":
            success = update_customer(id, post_body)

        elif resource == "employees":
            success = update_employee(id, post_body)

        elif resource == "locations":
            success = update_location(id, post_body)
        # rest of the elif's
        if success:
            self._set_headers(204)
        else:
            self._set_headers(404)

        self.wfile.write("".encode())
    # setting metadata
    # can set status=200 and remove 200 from do_GET method

    def do_DELETE(self):
        # Set a 204 response code
        # Parse the URL
        (resource, id) = self.parse_url(self.path)
        # Delete a single animal from the list
        if resource == "animals":
            self._set_headers(204)
            delete_animal(id)
        elif resource == "customers":
            self._set_headers(405)
            response = "Deleting customers requires contacting the company directly"
            # delete_customer(id)
        elif resource == "employees":
            self._set_headers(204)
            delete_employee(id)
        elif resource == "locations":
            self._set_headers(204)
            delete_location(id)
                # Encode the new animal and send in response
        # self.wfile.write("".encode())
        self.wfile.write(json.dumps(response).encode())

    def _set_headers(self, status):
        # Notice this Docstring also includes information about the arguments passed to the function
        """Sets the status code, Content-Type and Access-Control-Allow-Origin
        headers on the response
        Args:
            status (number): the status code to return to the front end
        """
        self.send_response(status)
        # if "plain/text" added after content-type, there will be no formatting after the comma will format the information
        # API can support multiple formatting
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    # Another method! This supports requests with the OPTIONS verb.
    def do_OPTIONS(self):
        """Sets the options headers
        """
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods',
                         'GET, POST, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers',
                         'X-Requested-With, Content-Type, Accept')
        self.end_headers()


# This function is not inside the class. It is the starting
# point of this application.
def main():
    """Starts the server on port 8088 using the HandleRequests class
    """
    host = ''
    port = 8088
    HTTPServer((host, port), HandleRequests).serve_forever()


if __name__ == "__main__":
    main()
