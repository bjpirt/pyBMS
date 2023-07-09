#!/bin/env node

const Inliner = require("inliner");
const fs = require("fs");

const buildPage = (path, outputPath, name) => {
  new Inliner(path, function (error, html) {
    if (error) {
      throw error;
    }
    const py = `${name} = """\n${html}\n"""`;
    fs.writeFileSync(`${outputPath}/${name}.py`, py);
  });
};

buildPage("./src/ui.html", "../bms/pages", "bms_ui");
buildPage("./src/config.html", "../bms/pages", "bms_config");
