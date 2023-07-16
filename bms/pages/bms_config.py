bms_config = """
<!DOCTYPE html> <html> <head> <title>pyBms Config</title> <style> *, *::before, *::after{ box-sizing:border-box;} body, h1, h2, h3, h4, p, figure, blockquote, dl, dd{ margin:0;} ul[role='list'], ol[role='list']{ list-style:none;} html:focus-within{ scroll-behavior:smooth;} body{ min-height:100vh;text-rendering:optimizeSpeed;line-height:1.5;} a:not([class]){ text-decoration-skip-ink:auto;} input, button, textarea, select{ font:inherit;}</style> <style>body{ background:#333;padding:10px;}*{ color:#CCC;font-family:sans-serif;}input, button{ color:#333;}</style> <style>#modules{ display:flex;flex-wrap:wrap;column-gap:10px;row-gap:10px;}.module{ border:1px solid #111;flex-basis:49%;box-sizing:border-box;padding:5px;}.module .cell{ border:1px solid #111;margin:3px 0;padding:3px;}.label{ display:inline-block;padding:2px 4px 0;font-weight:bold;border-radius:5px;margin:0 5px }.alert{ background:orange;color:#333 }.fault{ background:#900;color:#FFF }</style> </head> <body> <h1>pyBms Config</h1> <table id="config"> </table> <button>Update Configuration</button> <span id="message"></span> </body> <script type="text/javascript">const fetchUrl = async (url) => fetch(url).then((response) => response.json());</script> <script type="text/javascript">const getInput = (key, value) => {
  if (typeof value === "boolean") {
    return `<input type="checkbox" name="${key}" checked="${value}" />`;
  } else if (typeof value === "number") {
    return `<input type="number" name="${key}" value="${value}" />`;
  }
  return `<input type="text" name="${key}" value="${value}" />`;
};

const renderConfig = (config) => {
  const table = document.querySelector("#config");
  const rows = Object.keys(config)
    .filter((k) => k != "soc_lookup")
    .sort()
    .map((k) => `<tr><td>${k}</td><td>${getInput(k, config[k])}</td>`);
  rows.push("<tr><td>soc_lookup</td><td></td></tr>");
  rows.push("<tr><td>V</td><td>%</td></tr>");
  rows.push(
    ...config.soc_lookup.map(
      (point, i) =>
        `<tr><td>${getInput(`soc_lookupV[${i}]`, point[0])}</td><td>${getInput(
          `soc_lookupPc[${i}]`,
          point[1] * 100
        )}</td></tr>`
    )
  );
  table.innerHTML = rows.join("");
};

const rowToJson = (input) => {
  const name = input.name;
  if (input.type === "number") {
    return { [name]: Number(input.value) };
  } else if (input.type === "checkbox") {
    return { [name]: input.checked };
  }
};

const tableToJson = () => {
  const inputs = [...document.querySelectorAll("input")];
  const mainInputs = inputs.filter((i) => !i.name.startsWith("soc_lookup"));
  const socInputs = inputs.filter((i) => i.name.startsWith("soc_lookup"));
  const output = mainInputs.reduce(
    (acc, input) => ({ ...acc, ...rowToJson(input) }),
    {}
  );
  output.soc_lookup = Array(4)
    .fill(0)
    .map((_, i) => {
      return [
        Number(document.querySelector(`input[name="soc_lookupV[${i}]"]`).value),
        Number(
          document.querySelector(`input[name="soc_lookupPc[${i}]"]`).value
        ) / 100,
      ];
    });
  return output;
};

const setMessage = (msg) => {
  document.querySelector("#message").innerHTML = msg;
};

const submit = async () => {
  const config = tableToJson();
  const result = await fetch("/config.json", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(config),
  }).catch((e) => e);

  if (result instanceof Error) {
    setMessage("Error saving config");
  } else {
    setMessage("Config successfully saved");
  }
  setTimeout(() => setMessage(""), 3000);
};

const init = async () => {
  const config = await fetchUrl("/config.json");
  const button = document.querySelector("button");
  button.addEventListener("click", submit);
  renderConfig(config);
};

init();</script> </html> 
"""