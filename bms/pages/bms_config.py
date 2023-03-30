bmsConfig = """
<!DOCTYPE html>
<html>
  <head>
    <title>pyBms Config</title>
  </head>
  <body>
    <h1>pyBms Config</h1>
    <table id="config">
    </table>
    <button>Update config</button>
    <span id="message"></span>
  </body>
  <script type="text/javascript">

  const fetchUrl = async (url) => {
    return fetch(url)
      .then((response) => response.json())
  }

  const getInput = (key, value) => {
    if (typeof value === "boolean"){
      return `<input type="checkbox" name="${key}" checked="${value}" />`
    } else if (typeof value === "number"){
      return `<input type="number" name="${key}" value="${value}" />`
    }
    return `<input type="text" name="${key}" value="${value}" />`
  }

  const renderConfig = (config) => {
    const table = document.querySelector("#config");
    const rows = Object.keys(config).filter(k => k != "soc_lookup").sort().map(
      k => `<tr><td>${k}</td><td>${getInput(k, config[k])}</td>`
    );
    rows.push("<tr><td>soc_lookup</td><td></td></tr>");
    rows.push("<tr><td>V</td><td>%</td></tr>");
    rows.push(...config.soc_lookup.map((point, i) =>
    `<tr><td>${getInput(`soc_lookupV[${i}]`, point[0])}</td><td>${getInput(`soc_lookupPc[${i}]`, point[1] * 100)}</td></tr>`
    ))
    table.innerHTML = rows.join("")
  }

  const rowToJson = (input) => {
    const name = input.name
    if (input.type === "number") {
      return {[name]: Number(input.value)}
    } else if (input.type === "checkbox") {
      return {[name]:input.checked}
    }
  }

  const tableToJson = () => {
    const inputs = [...document.querySelectorAll("input")]
    const mainInputs = inputs.filter(i => !i.name.startsWith("soc_lookup"))
    const socInputs = inputs.filter(i => i.name.startsWith("soc_lookup"))
    const output = mainInputs.reduce((acc, input) => ({...acc, ...rowToJson(input)}), {})
    output.soc_lookup = Array(4).fill(0).map((_, i) => {
      return [
        Number(document.querySelector(`input[name="soc_lookupV[${i}]"]`).value),
        Number(document.querySelector(`input[name="soc_lookupPc[${i}]"]`).value)/100
      ]
    })
    return output
  }

  const setMessage = (msg) => {
    document.querySelector("#message").innerHTML = msg
  }

  const submit = async () => {
    const config = tableToJson()
    const result = await fetch("/config.json", {
      method: "PUT",
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config)
    }).catch(e => e)
   
    if(result instanceof Error){
      setMessage("Error saving config")
    }else{
      setMessage("Config successfully saved")
    }
    setTimeout(() => setMessage(""), 3000)
  }
  
  const init = async() => {
    const config = await fetchUrl("/config.json")
    const button = document.querySelector("button")
    button.addEventListener('click', submit)
    renderConfig(config)
  }

  init();
  
  </script>
</html>

"""
