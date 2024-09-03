require 'webrick'
require 'json'

class MyServlet < WEBrick::HTTPServlet::AbstractServlet
  def do_POST(request, response)
    begin
      # Read and parse the incoming JSON data
      post_data = request.body
      data = JSON.parse(post_data)
      keyboard_data = data['keyboardData'] || ''

      # Print or log the incoming keystrokes data
      puts "Received data: #{keyboard_data}"

      # Respond with a status code 200 (OK)
      response.status = 200
      response.content_type = 'application/json'
      response.body = { 'status' => 'success' }.to_json
    rescue JSON::ParserError
      # Handle JSON parsing errors
      response.status = 400
      response.content_type = 'application/json'
      response.body = { 'status' => 'error', 'message' => 'Invalid JSON' }.to_json
    end
  end
end

# Define the port and address for the server
port = 8080

server = WEBrick::HTTPServer.new :Port => port, :Logger => WEBrick::Log::new($stderr, WEBrick::Log::ERROR)

server.mount '/', MyServlet

trap 'INT' do
  server.shutdown
end

puts "Starting server on port #{port}..."
server.start
