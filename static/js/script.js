function obtenerEstadoTrabajo() {
    
    job_id = document.getElementById("job_id").textContent
    fetch(`/state/${job_id}.0`)
    .then(res => res.text())
    .then(texto => {
        document.getElementById("estado").textContent = texto
        if (texto == 'Completed') {
            clearInterval(id)
        }
    })
}

let id = setInterval(obtenerEstadoTrabajo, 2000)