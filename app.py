from flask import Flask, request, render_template, Response
import os
import subprocess
import re

JOB_STATUS = {
    '1': 'Idle',
    '2': 'Running',
    '3': 'Removed',
    '4': 'Completed',
    '5': 'Held'
}

app = Flask(__name__)
DEFAULT_PROJECT_FOLDER = '/home/pi/2025-1/grid_manager/app/'
#DEFAULT_PROJECT_FOLDER = '/home/juan/Documents/trabajo_de_grado/grid_manager/'
UPLOAD_FOLDER = os.path.join(DEFAULT_PROJECT_FOLDER, 'uploads/')
#os.makedirs(os.path.join(DEFAULT_PROJECT_FOLDER, UPLOAD_FOLDER), exist_ok=True)

@app.route("/")
def hello():
    return render_template("upload.html")

@app.route("/upload", methods=['POST'])
def execute():
    
    # Cambio de directorio de trabajo al del proyecto
    cwd = os.getcwd()
    os.chdir(DEFAULT_PROJECT_FOLDER)
    
    # Obtener los archivos del multipart request que mandó el formulario
    submit = request.files.get('submit')
    executable = request.files.get('executable')
    
    # Guardar los archivos en el equipo para luego ejecutarlos
    os.chdir(UPLOAD_FOLDER)
    if submit: submit.save(submit.filename)
    if executable:executable.save(executable.filename)
    
    # Ejecutar el proceso de Condor que ejecuta el trabajo    
    try:
            
        result = subprocess.run(
            ['condor_submit', submit.filename],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # Manejo basico de salida para ver con que ID salió el trabajo
        lines = result.stdout.split('\n')
        job_number = None
        
        for line in lines:
            match = re.search(r"(\d+)\s+job\(s\)\s+submitted to cluster\s+(\d+)", line)
            if match:
                job_number = match.group(2)
        
    except Exception as e:
        return "Error ejecutando comando: " + str(e)
        #print("error")
        
    return render_template('state.html', job_id=job_number)

@app.route("/state/<id>")
def estado_trabajo(id):
    
    try:
        
        result = subprocess.run(
            "condor_q {} -long | grep -E '^JobStatus'".format(id),
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )

        match = re.search(r'JobStatus = "?(.*?)"?$', result.stdout.strip(), re.MULTILINE)
        if match:
            status = match.group(1)
            return Response(JOB_STATUS[status], mimetype='text/plain')
        else:
            return Response("Estado no encontrado", mimetype='text/plain', status=400)
        
    except Exception as e:
        return "Error ejecutando comando: " + str(e)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
