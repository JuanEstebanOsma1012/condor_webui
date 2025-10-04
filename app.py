from flask import Flask, request, render_template, Response, jsonify, redirect, url_for
import os
import subprocess
import re
import json
import uuid
import time
import threading

JOB_STATUS = {
    '1': 'Idle',
    '2': 'Running',
    '3': 'Removed',
    '4': 'Completed',
    '5': 'Held'
}

app = Flask(__name__)
DEFAULT_PROJECT_FOLDER = '/home/juan/Documents/trabajo_de_grado/Raspberries/services/app_submit/app/'
#DEFAULT_PROJECT_FOLDER = '/opt/app/'
SUBMIT_FOLDER = os.path.join(DEFAULT_PROJECT_FOLDER, 'submits/')
SCRIPTS_FOLDER = os.path.join(DEFAULT_PROJECT_FOLDER, 'scripts/')

@app.route("/")
def hello():
    return render_template("upload.html")

@app.route("/submit", methods=['POST'])
def submit_job():
    try:
        # Cambio de directorio de trabajo al del proyecto
        cwd = os.getcwd()
        os.chdir(DEFAULT_PROJECT_FOLDER)
        
        # Generar ID único para el trabajo
        job_id = str(uuid.uuid4())[:8]
        
        # Obtener archivos y configuración
        binary_file = request.files.get('binary-file')
        submit_file = request.files.get('submit-file')
        input_file = request.files.get('input-file')
        config_str = request.form.get('config', '{}')
        config = json.loads(config_str)
        
        # Crear directorio para este trabajo
        job_dir = os.path.join(SUBMIT_FOLDER, job_id)
        os.makedirs(job_dir, exist_ok=True)
        
        # Guardar archivo binario
        binary_filename = None
        if binary_file and binary_file.filename:
            binary_filename = binary_file.filename
            binary_path = os.path.join(job_dir, binary_filename)
            binary_file.save(binary_path)
            # Hacer ejecutable
            os.chmod(binary_path, 0o755)
            
        input_filename = None
        if input_file and input_file.filename:
            input_filename = input_file.filename
            input_path = os.path.join(job_dir, input_filename)
            input_file.save(input_path)
            # Hacer ejecutable
            os.chmod(input_path, 0o755)
                
        submit_path = os.path.join(job_dir, 'job.sub')
        
        # Si hay submit file personalizado, usarlo
        if submit_file and submit_file.filename:
            submit_file.save(submit_path)
        else:
            # Crear archivo submit basado en la configuración
            create_submit_file(submit_path, config, binary_filename, job_id, input_filename)
        
        # Guardar configuración para referencia
        config_path = os.path.join(job_dir, 'config.json')
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Cambiar al directorio del trabajo para ejecutar condor_submit
        os.chdir(job_dir)
        
        if config.get('jobType') == 'vanilla':
            
            # Ejecutar condor_submit
            result = subprocess.run(
                ['condor_submit', 'job.sub'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                cwd=job_dir
            )
            
            if result.returncode != 0:
                return jsonify({"error": "Error en condor_submit: {}".format(result.stderr)}), 500
            
            # Extraer número de cluster de la salida
            lines = result.stdout.split('\n')
            cluster_id = None
            
            for line in lines:
                match = re.search(r"(\d+)\s+job\(s\)\s+submitted to cluster\s+(\d+)", line)
                if match:
                    cluster_id = match.group(2)
                    break
            
            # Guardar información del trabajo
            job_info = {
                'job_id': job_id,
                'cluster_id': cluster_id,
                'config': config,
                'binary_filename': binary_filename,
                'submit_output': result.stdout,
                'created_at': time.time()
            }
            
            info_path = os.path.join(job_dir, 'job_info.json')
            with open(info_path, 'w') as f:
                json.dump(job_info, f, indent=2)
            
            os.chdir(cwd)  # Volver al directorio original
            
            return jsonify({
                "success": True,
                "job_id": job_id,
                "cluster_id": cluster_id,
                "message": "Trabajo enviado exitosamente"
            })
            
        elif config.get('jobType') == 'parallel':
            
            submit_ip = config.get('cluster').split(':')[0]
            
            # Ejecutar condor_submit
            result = subprocess.run(
                ['./send-submit.sh', str(job_dir), str(submit_ip), str(job_id)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                cwd=SCRIPTS_FOLDER
            )
            
            if result.returncode != 0:
                return jsonify({"error": "Error en condor_submit: {}".format(result.stderr)}), 500
            
            # Extraer número de cluster de la salida
            lines = result.stdout.split('\n')
            cluster_id = None
            
            for line in lines:
                match = re.search(r"(\d+)\s+job\(s\)\s+submitted to cluster\s+(\d+)", line)
                if match:
                    cluster_id = match.group(2)
                    break
            
            # Guardar información del trabajo
            job_info = {
                'job_id': job_id,
                'cluster_id': cluster_id,
                'config': config,
                'binary_filename': binary_filename,
                'submit_output': result.stdout,
                'created_at': time.time()
            }
            
            info_path = os.path.join(job_dir, 'job_info.json')
            with open(info_path, 'w') as f:
                json.dump(job_info, f, indent=2)
                
            def traer_salidas():
                
                subprocess.run(
                    ['./fetch-outputs.sh', str(job_dir), str(submit_ip), str(job_id)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    cwd=SCRIPTS_FOLDER
                )
                
            thread = threading.Thread(target=traer_salidas)
            thread.start()
            
            os.chdir(cwd)  # Volver al directorio original
            
            return jsonify({
                "success": True,
                "job_id": job_id,
                "cluster_id": cluster_id,
                "message": "Trabajo enviado exitosamente"
            })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def create_submit_file(submit_path, config, binary_filename, job_id, input_filename):
    """Crear archivo submit basado en la configuración"""
    job_type = config.get('jobType', 'vanilla')
    
    submit_content = """# HTCondor Submit File - Job ID: {}
# Generated automatically
""".format(job_id)
    
    if job_type == 'vanilla':
        
        grid_resource = config.get('cluster', '')
        additional_args = config.get('additionalArgs', '')
        
        submit_content += """universe = grid
remote_universe = {}
grid_resource = condor {}
executable = {}
output = job_$(Process).out
error = job_$(Process).err
log = job.log
# Configuraciones adicionales
transfer_executable = YES
should_transfer_files = YES
when_to_transfer_output = ON_EXIT
requirements = (Arch == "armv7l")
""".format(job_id, job_type, grid_resource, binary_filename)

        vanilla_mode = config.get('vanillaMode', '')
        
        submit_content += """requirements = (Arch == "armv7l")\n"""
        
        if vanilla_mode == 'range':
            # Distribución en rangos - generar lista explícita
            range_options = config.get('rangeOptions', {})
            all_variables = range_options.get('allVariables', {})
            
            if all_variables and additional_args:
                # Obtener las variables del string de argumentos
                variables_in_args = []
                processed_args_template = additional_args
                
                # Identificar variables en el orden que aparecen en additional_args
                for var_name in all_variables.keys():
                    if var_name in processed_args_template:
                        variables_in_args.append(var_name)
                
                if variables_in_args:
                    # Tomar la primera variable para determinar el número de jobs
                    primary_var = variables_in_args[0]
                    primary_config = all_variables[primary_var]
                    
                    #start = int(primary_config.get('start', 1))
                    end = int(primary_config.get('end', 10))
                    #increment = int(primary_config.get('increment', 1))
                    
                    # Generar lista explícita de trabajos
                    submit_content += "# Lista explícita de trabajos\n"
                    
                    current_values = {}
                    # Inicializar valores actuales para cada variable
                    for var_name in variables_in_args:
                        var_config = all_variables[var_name]
                        current_values[var_name] = int(var_config.get('start', 1))
                    
                    # Generar cada trabajo
                    while current_values[primary_var] <= end:
                        # Crear string de argumentos para este trabajo
                        current_args = additional_args
                        for var_name in variables_in_args:
                            current_args = current_args.replace(var_name, str(current_values[var_name]))
                        
                        submit_content += "arguments = {}\n".format(current_args)
                        submit_content += "queue 1\n"
                        
                        # Incrementar valores para el siguiente trabajo
                        for var_name in variables_in_args:
                            var_config = all_variables[var_name]
                            var_increment = int(var_config.get('increment', 1))
                            current_values[var_name] += var_increment
            else:
                # Si no hay variables, usar comportamiento original
                if additional_args:
                    submit_content += "arguments = {}\n".format(additional_args)
                submit_content += "queue 1\n"
                
        elif vanilla_mode == 'equal':
            # Repeticiones iguales - mantener funcionalidad original
            equal_options = config.get('equalOptions', {})
            queue_count = int(equal_options.get('repetitions', 1))
            
            if additional_args:
                submit_content += "arguments = {}\n".format(additional_args)
            submit_content += "queue {}\n".format(queue_count)
        else:
            # Modo vanilla sin especificación
            if additional_args:
                submit_content += "arguments = {}\n".format(additional_args)
            submit_content += "queue 1\n"

    elif job_type == 'parallel':
        
        additional_args = config.get('additionalArgs', '')
        
        submit_content += """universe = parallel
executable = /usr/share/doc/condor/examples/openmpiscript
arguments = {} {} """.format(binary_filename, input_filename)

        if additional_args:
            submit_content += "{}\n".format(additional_args)
        
        parallel_opts = config.get('parallelOptions', {})
        
        machines_count = int(parallel_opts.get('machinesCount', 1))
        cores_per_machine = int(parallel_opts.get('coresPerMachine', 1))

        submit_content += """machine_count = {}
request_cpus = {}
should_transfer_files = yes
when_to_transfer_output = ON_EXIT_OR_EVICT
transfer_input_files = {},{}
log = job.log
output = job_$(NODE).out
error = job_$(NODE).err
+ParallelShutdownPolicy = "WAIT_FOR_NODE0"
environment = "PATH=/usr/lib64/openmpi/bin:$PATH;LD_LIBRARY_PATH=/usr/lib64/openmpi/lib:$LD_LIBRARY_PATH"
queue
""".format(machines_count, cores_per_machine, binary_filename, input_filename)

    else:
        # Tipo de trabajo no especificado
        if additional_args:
            submit_content += "arguments = {}\n".format(additional_args)
        submit_content += "queue 1\n"
    
    # Escribir el archivo
    with open(submit_path, 'w') as f:
        f.write(submit_content)

@app.route("/results/<job_id>")
def show_results(job_id):
    """Mostrar página de resultados con grid dinámico"""
    try:
        job_dir = os.path.join(SUBMIT_FOLDER, job_id)
        
        if not os.path.exists(job_dir):
            return "Trabajo no encontrado", 404
        
        # Cargar información del trabajo
        info_path = os.path.join(job_dir, 'job_info.json')
        if os.path.exists(info_path):
            with open(info_path, 'r') as f:
                job_info = json.load(f)
        else:
            job_info = {'job_id': job_id}
        
        # Obtener archivos de salida
        output_files = []
        
        if job_info.get('config').get('jobType') == 'vanilla':
            
            for filename in os.listdir(job_dir):
                if filename.startswith('job_') and filename.endswith('.out'):
                    output_files.append(filename)
            
            output_files.sort()  # Ordenar para mostrar consistentemente
        
            return render_template('results.html', 
                                job_info=job_info, 
                                output_files=output_files,
                                job_id=job_id)
            
        elif job_info.get('config').get('jobType') == 'parallel':
            
            output_files = ['job_0.out']
            
            return render_template('results.html', 
                                job_info=job_info, 
                                output_files=output_files,
                                job_id=job_id)
        
    except Exception as e:
        return "Error al cargar resultados: {}".format(str(e)), 500

@app.route("/output/<job_id>/<filename>")
def get_output(job_id, filename):
    """Obtener contenido de archivo de salida específico"""
    try:
        job_dir = os.path.join(SUBMIT_FOLDER, job_id)
        output_path = os.path.join(job_dir, filename)
        
        if not os.path.exists(output_path):
            return "Archivo no encontrado", 404
        
        with open(output_path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
        
        return Response(content, mimetype='text/plain')
        
    except Exception as e:
        return "Error al leer archivo: {}".format(str(e)), 500

@app.route("/job_status/<job_id>")
def get_job_status(job_id):
    """Obtener estado actual del trabajo"""
    try:
        job_dir = os.path.join(SUBMIT_FOLDER, job_id)
        info_path = os.path.join(job_dir, 'job_info.json')
        
        if not os.path.exists(info_path):
            return jsonify({"error": "Trabajo no encontrado"}), 404
        
        with open(info_path, 'r') as f:
            job_info = json.load(f)
        
        cluster_id = job_info.get('cluster_id')
        if not cluster_id:
            return jsonify({"status": "unknown"})
        
        statuses = []

        # Consultar estado con condor_q
        result = subprocess.run(
            "condor_q {} -long | grep -E '^JobStatus'".format(cluster_id),
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        for line in result.stdout.split('\n'):
            match = re.search(r'JobStatus = "?(\d+)"?', line)
            if match:
                status_code = match.group(1)
                statuses.append(JOB_STATUS.get(status_code, 'Unknown'))

	# 2. Si no está en condor_q → buscar en condor_history (terminados)
        if not statuses:
            result_hist = subprocess.run(
                "condor_history {} -limit 1 -long | grep -E '^JobStatus'".format(cluster_id),
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            for line in result_hist.stdout.split('\n'):
                match = re.search(r'JobStatus = "?(\d+)"?', line)
                if match:
                    status_code = match.group(1)
                    statuses.append(JOB_STATUS.get(status_code, 'Unknown'))

        # Determinar estado general
        if not statuses:
            overall = "Unknown"
        elif all(s == "Completed" for s in statuses):
            overall = "Completed"
        elif "Running" in statuses:
            overall = "Running"
        elif len(set(statuses)) > 1:
            overall = "Mixed"
        else:
            overall = statuses[0]

        return jsonify({
            "job_id": job_id,
            "cluster_id": cluster_id,
            "statuses": statuses,
            "overall_status": overall
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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