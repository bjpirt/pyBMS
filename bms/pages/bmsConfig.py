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
    const rows = Object.keys(config).filter(k => k != "socLookup").sort().map(
      k => `<tr><td>${k}</td><td>${getInput(k, config[k])}</td>`
    );
    rows.push("<tr><td>socLookup</td><td></td></tr>");
    rows.push("<tr><td>V</td><td>%</td></tr>");
    rows.push(...config.socLookup.map((point, i) => 
    `<tr><td>${getInput(`socLookupV[${i}]`, point[0])}</td><td>${getInput(`socLookupPc[${i}]`, point[1] * 100)}</td></tr>`
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
    const mainInputs = inputs.filter(i => !i.name.startsWith("socLookup"))
    const socInputs = inputs.filter(i => i.name.startsWith("socLookup"))
    const output = mainInputs.reduce((acc, input) => ({...acc, ...rowToJson(input)}), {})
    output.socLookup = Array(4).fill(0).map((_, i) => {
      return [
        Number(document.querySelector(`input[name="socLookupV[${i}]"]`).value),
        Number(document.querySelector(`input[name="socLookupPc[${i}]"]`).value)/100
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
