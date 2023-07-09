const express = require("express");
const Config = require("./lib/config");
const Status = require("./lib/Status");
const app = express();
const port = 2001;

app.use(express.static("src"));
app.use(express.json());

const config = new Config();
const status = new Status();

app.get("/config.json", (req, res) => res.json(config.getConfig()));
app.put("/config.json", (req, res) => res.json(config.setConfig(req.body)));
app.get("/status.json", (req, res) => res.json(status.getStatus()));

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`);
});
