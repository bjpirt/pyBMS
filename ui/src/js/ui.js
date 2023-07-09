const graphColor = "#42758a";

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

const labels = (input, type) =>
  input
    ? input
        .map((i) => `<span class="${type} label">${i.replace("_", " ")}</span>`)
        .join("")
    : "None";

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

  setElementValue("#packDetail .warnings", labels(status.warnings, "warning"));
  setElementValue("#packDetail .alarms", labels(status.alarms, "alarm"));
  setElementValue("#packDetail .fault", status.fault ? "Yes" : "No");
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

init();
