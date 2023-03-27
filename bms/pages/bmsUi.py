bmsUi = """
<!DOCTYPE html>
<html>
  <head>
    <title>pyBms UI</title>
  </head>
  <body>
    <h1>pyBms UI</h1>
    <div id="content"></div>
  </body>
  <script type="text/javascript">

  const fetchUrl = async (url) => {
    return fetch(url)
      .then((response) => response.json())
  }

  const render = async () => {
    const status = await fetchUrl("/status.json")
    const content = document.querySelector("#content")
    content.innerHTML = `<pre>${JSON.stringify(status, null, 2)}</pre>`
    setTimeout(render, 1000)
  }
  
  const init = async () => {
    console.log("Initialising")
    await render()
  }

  init();
  
  </script>
</html>

"""
