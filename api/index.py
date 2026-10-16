from http.server import BaseHTTPRequestHandler
import json
import subprocess
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 1. Parse incoming url query variables
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        imdb_id = query_params.get('imdb_id', [None])[0]
        
        # Cross-Origin Headers so your website can read the response safely
        headers = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type'
        }

        if parsed_url.path != '/api' and parsed_url.path != '/api/index':
            self.send_response(404)
            for k, v in headers.items(): self.send_header(k, v)
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Path not found. Use /api?imdb_id=ID"}).encode())
            return

        if not imdb_id:
            self.send_response(400)
            for k, v in headers.items(): self.send_header(k, v)
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Missing imdb_id parameter"}).encode())
            return

        try:
            # 2. Run streamgrabber
            result = subprocess.run(
                ["streamgrabber", imdb_id, "--list"],
                capture_output=True,
                text=True,
                check=True
            )
            stream_url = result.stdout.strip()
            
            self.send_response(200)
            for k, v in headers.items(): self.send_header(k, v)
            self.end_headers()
            self.wfile.write(json.dumps({"imdb_id": imdb_id, "m3u8_url": stream_url}).encode())
            
        except Exception as e:
            self.send_response(500)
            for k, v in headers.items(): self.send_header(k, v)
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
