INVENTORY = ["172.30.27.35", "172.30.27.67", "172.30.28.31"];
DEFAULT_PORT = "44444";

document.addEventListener("DOMContentLoaded", () => {
    // --- TAB SWITCHING ---
    const tabButtons = document.querySelectorAll(".tab-button");
    const tabPanels = document.querySelectorAll(".tab-panel");

    tabButtons.forEach(button => {
        button.addEventListener("click", () => {
            const targetTab = button.getAttribute("data-tab");

            // Activar tab seleccionado
            tabButtons.forEach(btn => btn.classList.remove("active"));
            button.classList.add("active");

            // Mostrar panel correspondiente
            tabPanels.forEach(panel => {
                if (panel.id === targetTab) {
                    panel.classList.add("active");
                } else {
                    panel.classList.remove("active");
                }
            });
        });
    });

    // --- CLUSTER LOADING DINAMICALLY ---
    const loadClusters = async (clusterType, dropdown) => {
    const clusterSelect = document.getElementById(dropdown);
    
    // Solo limpiar el dropdown si no estamos en modo automático
    if (!clusterSelect._isRefreshing) {
        clusterSelect.innerHTML = "";
        
        const defaultOption = document.createElement("option");
        defaultOption.value = "";
        defaultOption.textContent = "Seleccionar cluster";
        defaultOption.disabled = true;
        defaultOption.selected = true;
        clusterSelect.appendChild(defaultOption);
    }

    for (const submitIp of INVENTORY) {
        try {
            // SIN AbortController para refrescos automáticos
            const response = await fetch(`http://${submitIp}:${DEFAULT_PORT}`, {
                // signal: controller.signal // ← Eliminar esta línea
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const clusterInfo = await response.json();

            if (clusterType === "all" || clusterInfo.cluster_type === clusterType) {
                // Actualizar o crear opción existente
                let option = clusterSelect.querySelector(`option[value*="${submitIp}"]`);
                if (!option) {
                    option = document.createElement("option");
                    clusterSelect.appendChild(option);
                }
                option.value = `${clusterInfo.schedd_address} ${clusterInfo.collector_address}`;
                option.textContent = `${submitIp}: {slots: ${clusterInfo.slots}; éxito: ${clusterInfo.success_jobs}; cola: ${clusterInfo.idle_jobs}}`;
            }
            
        } catch (error) {
            console.error(`Error al obtener datos de ${submitIp}:`, error);
        }
    }
    
    clusterSelect._isRefreshing = true; // Marcar como en refresco automático
};

    const cleanClusters = () => {

	dropdown = "cluster-guiado";

	const clusterSelect = document.getElementById(dropdown);

	clusterSelect.innerHTML = ""

	const defaultOption = document.createElement("option");
	defaultOption.value = "";
	defaultOption.textContent = "Seleccionar cluster";
	defaultOption.disabled = true;
	defaultOption.selected = true;

	clusterSelect.appendChild(defaultOption);

    }

    // --- JOB TYPE SWITCHING (Vanilla / Parallel) ---
    const jobTypeSelect = document.getElementById("job-type");
    const vanillaOptions = document.getElementById("vanilla-options");
    const parallelOptions = document.getElementById("parallel-options");

    const updateJobOptions = () => {
        if (jobTypeSelect.value === "vanilla") {
            vanillaOptions.style.display = "block";
            parallelOptions.style.display = "none";
        } else if (jobTypeSelect.value === "parallel") {
            vanillaOptions.style.display = "none";
            parallelOptions.style.display = "block";
        }
    };

    jobTypeSelect.addEventListener("change", updateJobOptions);
    jobTypeSelect.addEventListener("change", cleanClusters);
    updateJobOptions(); // Inicial

    // --- VANILLA MODE SWITCHING (Range / Equal) ---
    const vanillaModeSelect = document.getElementById("vanilla-mode");
    const rangeOptions = document.getElementById("range-options");
    const equalOptions = document.getElementById("equal-options");

    const updateVanillaSubOptions = () => {
        if (vanillaModeSelect.value === "range") {
            rangeOptions.style.display = "block";
            equalOptions.style.display = "none";
        } else if (vanillaModeSelect.value === "equal") {
            rangeOptions.style.display = "none";
            equalOptions.style.display = "block";
        }
    };

    vanillaModeSelect.addEventListener("change", updateVanillaSubOptions);
    updateVanillaSubOptions(); // Inicial

    // --- DETECCIÓN DE VARIABLES ESPECIALES EN ARGUMENTOS ---
    const additionalArgsInput = document.getElementById("additional-args");
    const paramVariableSelect = document.getElementById("param-variable");
    const variableValuesSection = document.getElementById("variable-values");
    let variableValueStore = {}; // Guardará start/end/increment por variable

    paramVariableSelect.addEventListener("change", () => {
        const selectedVar = paramVariableSelect.value;

        // Guardar los valores actuales antes de cambiar
        const prevVar = paramVariableSelect.dataset.currentVar;
        if (prevVar) {
            variableValueStore[prevVar] = {
                start: document.getElementById("start-value").value,
                end: document.getElementById("end-value").value,
                increment: document.getElementById("increment").value
            };
        }

        // Mostrar la sección
        variableValuesSection.style.display = selectedVar ? "block" : "none";

        // Cargar valores guardados si existen
        if (variableValueStore[selectedVar]) {
            document.getElementById("start-value").value = variableValueStore[selectedVar].start;
            document.getElementById("end-value").value = variableValueStore[selectedVar].end;
            document.getElementById("increment").value = variableValueStore[selectedVar].increment;
        } else {
            document.getElementById("start-value").value = "";
            document.getElementById("end-value").value = "";
            document.getElementById("increment").value = "";
        }

        paramVariableSelect.dataset.currentVar = selectedVar;
    });

    const updateSpecialVariables = () => {
        const argsText = additionalArgsInput.value;
        // Detecta todas las variables con forma <x> o <y>
        const regex = /<([a-zA-Z0-9_]+)>/g;
        const matches = [...argsText.matchAll(regex)].map(m => m[0]);

        // Guardar la opción actualmente seleccionada
        const currentValue = paramVariableSelect.value;

        // Limpiar dropdown
        paramVariableSelect.innerHTML = '<option value="" disabled selected>Selecciona una variable</option>';

        // Agregar opciones únicas
        const uniqueMatches = [...new Set(matches)];
        uniqueMatches.forEach(variable => {
            const option = document.createElement("option");
            option.value = variable;
            option.textContent = variable;
            paramVariableSelect.appendChild(option);
        });

        // Restaurar valor si sigue disponible
        if (uniqueMatches.includes(currentValue)) {
            paramVariableSelect.value = currentValue;
        }

        // Actualizar el store con todas las variables encontradas
        uniqueMatches.forEach(variable => {
            if (!variableValueStore[variable]) {
                variableValueStore[variable] = {
                    start: "",
                    end: "",
                    increment: ""
                };
            }
        });

        // Limpiar variables que ya no existen en el texto
        Object.keys(variableValueStore).forEach(variable => {
            if (!uniqueMatches.includes(variable)) {
                delete variableValueStore[variable];
            }
        });
    };

    // Actualizar variables especiales cada vez que se cambian los argumentos
    additionalArgsInput.addEventListener("input", updateSpecialVariables);
    updateSpecialVariables(); // Inicial

    // --- FORM GUIADO SUBMISSION HANDLING ---
    const formGuiado = document.getElementById("form-guiado");

    formGuiado.addEventListener("submit", async (event) => {
        event.preventDefault();

        // Guardar valores actuales de la variable seleccionada antes de procesar
        const currentVar = paramVariableSelect.dataset.currentVar;
        if (currentVar) {
            variableValueStore[currentVar] = {
                start: document.getElementById("start-value").value,
                end: document.getElementById("end-value").value,
                increment: document.getElementById("increment").value
            };
        }

        // Completar información de todas las variables detectadas
        const argsText = additionalArgsInput.value;
        const regex = /<([a-zA-Z0-9_]+)>/g;
        const allVariables = [...argsText.matchAll(regex)].map(m => m[0]);
        const uniqueVariables = [...new Set(allVariables)];

        // Asegurar que todas las variables tienen valores por defecto si no están configuradas
        uniqueVariables.forEach(variable => {
            if (!variableValueStore[variable] || 
                (!variableValueStore[variable].start && 
                 !variableValueStore[variable].end && 
                 !variableValueStore[variable].increment)) {
                // Si una variable no tiene configuración, usar valores por defecto
                variableValueStore[variable] = {
                    start: "1",
                    end: "10", 
                    increment: "1"
                };
            }
        });

        const formData = new FormData(formGuiado);
        const jobType = formData.get("job-type");

        // Crear FormData para enviar al backend
        const submitData = new FormData();
        
        // Agregar archivo binario (no solo el nombre)
        const binaryFile = formData.get("binary-file");
        if (binaryFile && binaryFile.name) {
            submitData.append("binary-file", binaryFile);
        }

        // Preparar datos de configuración
        let configData = {
            jobType: jobType,
            additionalArgs: formData.get("additional-args") || "",
            cluster: formData.get("cluster-guiado") || null
        };

        if (jobType === "vanilla") {
            const vanillaMode = formData.get("vanilla-mode");
            configData.vanillaMode = vanillaMode;

            if (vanillaMode === "range") {
                // Incluir TODAS las variables parametrizables encontradas
                const allVariableValues = {};
                uniqueVariables.forEach(variable => {
                    if (variableValueStore[variable]) {
                        allVariableValues[variable] = { ...variableValueStore[variable] };
                    }
                });

                configData.rangeOptions = {
                    selectedVariable: formData.get("param-variable"), // Variable actualmente seleccionada en el UI
                    allVariables: allVariableValues, // TODAS las variables con sus valores
                };
            } else if (vanillaMode === "equal") {
                configData.equalOptions = {
                    repetitions: formData.get("equal-repetitions")
                };
            }
        } else if (jobType === "parallel") {
            configData.parallelOptions = {
                machinesCount: formData.get("machines-count"),
                coresPerMachine: formData.get("cores-per-machine")
            };
        }

        // Agregar configuración como JSON
        submitData.append("config", JSON.stringify(configData));

        try {
            const response = await fetch('/submit', {
                method: 'POST',
                body: submitData
            });

            if (response.ok) {
                const result = await response.json();
                // Redirigir a la página de resultados
                window.location.href = `/results/${result.job_id}`;
            } else {
                const error = await response.text();
                alert(`Error al enviar el trabajo: ${error}`);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error de conexión al enviar el trabajo');
        }
    });

    // --- FORM PERSONALIZADO SUBMISSION HANDLING ---
    const formPersonalizado = document.getElementById("form-personalizado");

    formPersonalizado.addEventListener("submit", async (event) => {
        event.preventDefault();

        const formData = new FormData(formPersonalizado);

        // Crear FormData para enviar al backend
        const submitData = new FormData();
        
        // Agregar archivos
        const binaryFile = formData.get("binary-file");
        const submitFile = formData.get("submit-file");
        
        if (binaryFile && binaryFile.name) {
            submitData.append("binary-file", binaryFile);
        }
        
        if (submitFile && submitFile.name) {
            submitData.append("submit-file", submitFile);
        }

        // Preparar datos de configuración
        let configData = {
            jobType: "custom",
            cluster: formData.get("cluster-personalizado") || null
        };

        submitData.append("config", JSON.stringify(configData));

        try {
            const response = await fetch('/submit', {
                method: 'POST',
                body: submitData
            });

            if (response.ok) {
                const result = await response.json();
                // Redirigir a la página de resultados
                window.location.href = `/results/${result.job_id}`;
            } else {
                const error = await response.text();
                alert(`Error al enviar el trabajo: ${error}`);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error de conexión al enviar el trabajo');
        }
    });

    loadClusters(jobTypeSelect.value, "cluster-guiado");
    loadClusters("all", "cluster-personalizado");

    setInterval(() => loadClusters(jobTypeSelect.value, "cluster-guiado"), 10000)
    setInterval(() => loadClusters("all", "cluster-personalizado"), 10000)

});
