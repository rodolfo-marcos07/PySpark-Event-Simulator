from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import csv
import json
from urllib.parse import urlparse, parse_qs
import datetime
import glob

# Ensure the input_stream directory exists
os.makedirs("input_stream", exist_ok=True)

class EventHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the URL path
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        # Handle different endpoints
        if path == "/getAggregation":
            self.handle_get_aggregation()
        else:
            # Assume this is for the event handling endpoint
            self.handle_event(parsed_url)

    def handle_get_aggregation(self):
        try:
            # Get the most recent JSON file in the output directory
            output_files = glob.glob("output/**/*.json", recursive=True)

            if not output_files:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "No aggregation data found"}).encode())
                return

            # Sort files by modification time, newest first
            latest_file = max(output_files, key=os.path.getmtime)

            # Read the content of the file
            with open(latest_file, 'r') as f:
                content = f.read()

            # Send the content as JSON response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')  # For CORS
            self.end_headers()
            self.wfile.write(content.encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
            print(f"Error in getAggregation: {str(e)}")

    def handle_event(self, parsed_url):
        # Parse query parameters
        query_params = parse_qs(parsed_url.query)

        # Check if required parameters are present
        if 'event_time' not in query_params or 'event_value' not in query_params:
            self.send_response(400)
            self.send_header('Content-type', 'text/plain')
            self.send_header('Access-Control-Allow-Origin', '*')  # For CORS
            self.end_headers()
            self.wfile.write(b"Missing required parameters: event_time or event_value")
            return

        # Extract parameters
        event_time_raw = query_params['event_time'][0]
        event_value = query_params['event_value'][0]

        try:
            # Convert event_time from YYYY-mm-dd_HH-mm-ss to YYYY-mm-dd HH:mm:ss
            event_time = event_time_raw.replace('_', ' ')
            date_part, time_part = event_time.split(' ')
            time_part = time_part.replace('-', ':')
            event_time = f"{date_part} {time_part}"

            # Create a unique filename for this event
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
            filename = f"input_stream/event_{timestamp}.csv"

            # Save to CSV file
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['event_time', 'value'])
                writer.writerow([event_time, event_value])

            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.send_header('Access-Control-Allow-Origin', '*')  # For CORS
            self.end_headers()
            self.wfile.write(f"Event saved to {filename}".encode())
            print(f"Event saved: {event_time}, {event_value} in {filename}")

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Error processing request: {str(e)}".encode())
            print(f"Error: {str(e)}")


if __name__ == '__main__':
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, EventHandler)
    print('Starting server on port 8080...')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Shutting down server...')
        httpd.server_close()