bms_ui = """
<!DOCTYPE html> <html> <head> <title>pyBms UI</title> <style> *, *::before, *::after{ box-sizing:border-box;} body, h1, h2, h3, h4, p, figure, blockquote, dl, dd{ margin:0;} ul[role='list'], ol[role='list']{ list-style:none;} html:focus-within{ scroll-behavior:smooth;} body{ min-height:100vh;text-rendering:optimizeSpeed;line-height:1.5;} a:not([class]){ text-decoration-skip-ink:auto;} input, button, textarea, select{ font:inherit;}</style> <style>body{ background:#333;padding:10px;}*{ color:#CCC;font-family:sans-serif;}input, button{ color:#333;}</style> <style>#modules{ display:flex;flex-wrap:wrap;column-gap:10px;row-gap:10px;}.module{ border:1px solid #111;flex-basis:49%;box-sizing:border-box;padding:5px;}.module .cell{ border:1px solid #111;margin:3px 0;padding:3px;}.label{ display:inline-block;padding:2px 4px 0;font-weight:bold;border-radius:5px;margin:0 5px }.alert{ background:orange;color:#333 }.fault{ background:#900;color:#FFF }</style> </head> <body> <h1>pyBms UI</h1> <table id="packDetail"> <tr> <td></td> <td>Min</td> <td>Now</td> <td>Max</td> </tr> <tr class="voltage"> <td>Voltage</td> <td class="min"></td> <td class="now"></td> <td class="max"></td> </tr> <tr class="temperature"> <td>Temperature</td> <td class="min"></td> <td class="now"></td> <td class="max"></td> </tr> <tr> <td>Current</td> <td colspan="3" class="current"></td> </tr> <tr> <td>State of Charge</td> <td colspan="3" class="soc"></td> </tr> <tr> <td>Alerts</td> <td colspan="3" class="alerts"></td> </tr> <tr> <td>Faults</td> <td colspan="3" class="faults"></td> </tr> </table> <div id="modules"></div> </body> <template id="module"> <div class="module"> <h2></h2> <table class="moduleDetail"> <tr> <td>Voltage</td> <td class="voltage"></td> </tr> <tr> <td>Temperature</td> <td class="temperature"></td> </tr> </table> <div class="labels"></div> <div class="cells"></div> </div> </template> <template id="cell"> <div class="cell"> <div class="voltage"></div> </div> </template> <script type="text/javascript">const fetchUrl = async (url) => fetch(url).then((response) => response.json());</script> <script type="text/javascript">const graphColor = "#42758a";

const createTableRow = (content, table) => {
  const row = document.createElement("tr");
  content.forEach((label) => {
    const item = document.createElement("td");
    item.innerText = label;
    row.appendChild(item);
  });
  table.appendChild(row);
};

const setElementValue = (id, value, unit) =>
  (document.querySelector(id).innerHTML = `${value}${unit ?? ""}`);

const createLabel = (value, type) =>
  `<span class="${type} label">${value.replace("_", " ")}</span>`;

const labels = (input, type) =>
  input ? input.map((value) => createLabel(value, type)).join("") : "None";

const updatePackDetail = (status) => {
  setElementValue("#packDetail .voltage .min", status.lowest_voltage, "V");
  setElementValue("#packDetail .voltage .now", status.voltage, "V");
  setElementValue("#packDetail .voltage .max", status.highest_voltage, "V");

  setElementValue(
    "#packDetail .temperature .min",
    status.lowest_temperature,
    "&deg;C"
  );
  setElementValue(
    "#packDetail .temperature .max",
    status.highest_temperature,
    "&deg;C"
  );
  setElementValue("#packDetail .current", status.current, "A");
  setElementValue("#packDetail .soc", status.state_of_charge * 100, "%");

  setElementValue("#packDetail .alerts", labels(status.alerts, "alert"));
  setElementValue("#packDetail .faults", labels(status.faults, "fault"));
};

const createModuleElement = (module, moduleIndex) => {
  const moduleElement = document
    .querySelector("template#module")
    .content.cloneNode(true)
    .querySelector("div.module");
  document.querySelector("#modules").appendChild(moduleElement);
  moduleElement.classList.add(`module-${moduleIndex}`);
  moduleElement.querySelector("h2").innerText = `Module ${moduleIndex + 1}`;

  for (const [cellIndex, cell] of module.cells.entries()) {
    const cellElement = document
      .querySelector("template#cell")
      .content.cloneNode(true)
      .querySelector("div.cell");
    moduleElement.querySelector(".cells").appendChild(cellElement);
    cellElement.classList.add(`cell-${cellIndex}`);
  }
  return moduleElement;
};

const graphBackground = (level, color, bgcolor) =>
  `linear-gradient(90deg, ${color} 0% ${level * 100}%, ${bgcolor} ${
    level * 100
  }% 100%)`;

const updateCell = (moduleElement, cell, cellIndex, config) => {
  const min = config.cell_low_voltage_setpoint;
  const max = config.cell_high_voltage_setpoint;
  const level = (cell.voltage - min) / (max - min);
  const cellElement = moduleElement.querySelector(`.cell-${cellIndex}`);
  cellElement.querySelector(".voltage").innerText = `${cell.voltage}V`;
  cellElement.style.background = graphBackground(level, graphColor, "#444");
};

const updateModuleElement = (moduleElement, module, config) => {
  moduleElement.querySelector(".voltage").innerText = `${module.voltage}V`;
  moduleElement.querySelector(
    ".temperature"
  ).innerHTML = `${module.temperatures[0]}&deg;C`;

  const alerts = module.alerts.map((alert) => createLabel(alert, "alert"));
  const faults = module.faults.map((fault) => createLabel(fault, "fault"));
  moduleElement.querySelector(".labels").innerHTML = alerts
    .concat(faults)
    .join("");
  for (const [cellIndex, cell] of module.cells.entries()) {
    updateCell(moduleElement, cell, cellIndex, config);
  }
};

const updateModuleDetails = (status, config) => {
  for (const [moduleIndex, module] of status.modules.entries()) {
    let moduleElement = document.querySelector(
      `#modules .module-${moduleIndex}`
    );

    if (!moduleElement) {
      moduleElement = createModuleElement(module, moduleIndex);
    }

    updateModuleElement(moduleElement, module, config);
  }
};

const render = async (config) => {
  const status = await fetchUrl("/status.json");
  updatePackDetail(status);
  updateModuleDetails(status, config);
  setTimeout(() => render(config), 1000);
};

const init = async () => {
  console.log("Initialising");
  const config = await fetchUrl("/config.json");
  await render(config);
};

init();</script> </html> 
"""