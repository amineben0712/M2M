import http.server
import socketserver
import requests
from simple_om2m import createContentInstance

# Define the port for the HTTP server
PORT = 9999

# Custom HTTP Request Handler class
class CustomHttpRequestHandler(http.server.BaseHTTPRequestHandler):
    """
    A custom HTTP handler to process GET and POST requests.
    """

    def do_GET(self):
        """
        Handle HTTP GET requests:
        - Retrieve the current button status via a RETRIEVE request.
        - Change the light state based on the button status.
        - Send a response back to the client.
        """
        try:
            # Retrieve the button status
            button_status = get_button_status()

            # Update the light state based on the button status
            if button_status:
                if button_status == 'ON':
                    createContentInstance(
                        "admin:admin",
                        "http://127.0.0.1:8080/~/in-cse/in-name/Light/DATA",
                        "ON"
                    )
                elif button_status == 'OFF':
                    createContentInstance(
                        "admin:admin",
                        "http://127.0.0.1:8080/~/in-cse/in-name/Light/DATA",
                        "OFF"
                    )
                else:
                    print("Button state is unrecognized. No action taken.")
            else:
                print("Failed to retrieve button status. Default handling or fallback action required.")

            # Send a success response to the client
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"Action completed successfully!")
        except Exception as e:
            # Handle any errors during processing
            print("Error occurred during GET request handling:", e)
            self.send_response(500)
            self.end_headers()

    def do_POST(self):
        """
        Handle HTTP POST requests:
        - Parse and log incoming POST request data.
        - Respond to the client with success or error codes.
        """
        try:
            # Read POST request headers and content
            content_length = int(self.headers['Content-Length'])
            content_type = self.headers.get('Content-Type')
            request_id = self.headers.get('X-M2M-RI')
            post_data = self.rfile.read(content_length)

            # Log the received POST request details
            print("POST request received:")
            print(f"Content-Type: {content_type}")
            print(f"Request ID: {request_id}")
            print(f"Payload: {post_data.decode('utf-8')}")

            # Respond with a success status
            self.send_response(200)
            self.send_header('X-M2M-RSC', '2000')  # Indicate success
            self.send_header('X-M2M-RI', request_id)  # Echo back the request ID
            self.end_headers()
        except Exception as e:
            # Handle errors during POST request processing
            print("Error occurred during POST request handling:", e)
            self.send_response(500)
            self.end_headers()

# Helper function to retrieve the current button status
def get_button_status():
    """
    Perform a RETRIEVE request to fetch the button status.
    This simulates a query to a OneM2M-compatible server.
    """
    try:
        # Send a GET request to the OneM2M server
        response = requests.get(
            "http://localhost:8080/webui/index.html?ri=id-in&or=CAdmin",
            params={
                'to': '/Button/Button_Status',
                'originator': 'Cmyself',
                'requestIdentifier': '123',
                'releaseVersionIndicator': '3',
                'filterUsage': 'conditionalRetrieval',
                'filterCriteria': {'lbl': ['tag:greeting']},
                'resultContent': 'childResources'
            }
        )

        # Check if the response is successful
        if response.status_code == 200:
            return response.text.strip()  # Assume the button status is in plain text
        else:
            print(f"Failed to retrieve button status. HTTP status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        # Log any exceptions during the request
        print("Error occurred during RETRIEVE request:", e)
        return None

# Instantiate the HTTP server
Handler = CustomHttpRequestHandler

# Set up and start the HTTP server
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"HTTP Server running on port {PORT}")
    httpd.serve_forever()
