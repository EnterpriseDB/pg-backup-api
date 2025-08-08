import json
import re
from wsgiref.util import setup_testing_defaults
from wsgiref import simple_server

# Import the controller functions that contain the application logic
from pg_backup_api.logic.utility_controller import (
    diagnose,
    instance_operation,
    instance_operation_id_get,
    instance_operations_post,
    status,
    server_operation,
    servers_operations_post,
    servers_operation_id_get,
)

# Define the routing table for the application.
# Each route is a tuple containing:
# (HTTP_METHOD, regex_pattern_for_url, handler_function, tuple_of_parameter_names)
ROUTES = [
    ('GET', re.compile(r'^/diagnose$'), diagnose, ()),
    ('GET', re.compile(r'^/status$'), status, ()),

    ('GET', re.compile(r'^/servers/([^/]+)/operations$'), server_operation, ('server_name',)),
    ('POST', re.compile(r'^/servers/([^/]+)/operations$'), servers_operations_post, ('server_name',)),
    ('GET', re.compile(r'^/servers/([^/]+)/operations/([^/]+)$'), servers_operation_id_get, ('server_name', 'operation_id')),

    ('GET', re.compile(r'^/operations$'), instance_operation, ('server_name')),
    ('POST', re.compile(r'^/operations/$'), instance_operations_post, ('operation_id')),
    ('GET', re.compile(r'^/operations/([^/]+)$'), instance_operation_id_get, ('operation_id',)),
]

def get_lightweight_server():
    return simple_server.make_server


def process_request(handler, **kwargs):
    """
    Process a WSGI request by matching the request path and method to a route,
    calling the appropriate handler, and returning the response.
    """
    response_body = None
    status = '500 Internal Server Error'
    print("Processing request with handler:", handler.__name__)
    try:
        # Call the handler function with the extracted parameters
        response_data, status_code = handler(**kwargs)

        # Determine the HTTP status string
        if status_code == 200:
            status = '200 OK'
        elif status_code == 202:
            status = '202 Accepted'
        elif status_code == 404:
            status = '404 Not Found'
        else:
            status = f'{status_code} '

        # Serialize the response data to JSON
        response_body = json.dumps(response_data).encode('utf-8')

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        error_message = {"error": "An internal server error occurred.", "details": str(e)}
        response_body = json.dumps(error_message).encode('utf-8')
        print(response_body)

    return response_body, status


def application(environ, start_response):
    """
    The main WSGI application function. It receives the request environment
    and a function to start the HTTP response.
    """
    # Set up default WSGI environment variables
    setup_testing_defaults(environ)

    # default response
    status = '404 Not Found'
    response_body = b'{"error": "Not Found"}'

    path = environ.get('PATH_INFO', '')
    method = environ.get('REQUEST_METHOD', 'GET')

    # Iterate through the defined routes to find a match
    for http_method, pattern, handler, param_names in ROUTES:
        if http_method == method:
            match = pattern.match(path)
            if match:
                # If a route matches, extract parameters from the URL
                params = match.groups()
                print("Match found for path:", path)
                kwargs = dict(zip(param_names, params))
                if method == 'POST':
                    try:
                        content_length = int(environ.get('CONTENT_LENGTH', 0))
                    except (ValueError):
                        content_length = 0

                    request_body = environ['wsgi.input'].read(content_length)
                    body_data = json.loads(request_body)
                    kwargs['request_body'] = body_data
                    print("Request body:", body_data)

                response_body, status = process_request(handler, **kwargs)
                break


    headers = [('Content-Type', 'application/json'),
               ('Content-Length', str(len(response_body)))]
    start_response(status, headers)
    return [response_body]
