<template>
  <div
    class="d-flex flex-column flex-md-row justify-content-center align-items-center"
  >
    <div class="table-container" style="max-width: 700px">
      <h2 style="margin-bottom: 25px; text-align: center">
        Realizar Predicción
      </h2>
      <b-form @submit.prevent="submitAnalysis">
        <h5>Carga del Dataset</h5>
        <div>
          <b-form @submit.prevent="submitDataset">
            <b-form-group>
              <b-form-file v-model="form.file" ref="fileInput"></b-form-file>
              <div class="d-flex justify-content-center mt-3 mb-2">
                <b-button
                  pill
                  type="submit"
                  variant="primary"
                  style="background-color: #0252a6"
                  >Subir Dataset</b-button
                >
              </div>
            </b-form-group>
            <b-form-group disabled="">
              <b-form-input
                disabled=""
                v-model="form.name"
                readonly
                class="d-none"
              ></b-form-input>
            </b-form-group>
            <b-form-group>
              <b-form-input
                disabled=""
                v-model="form.description"
                class="d-none"
              ></b-form-input>
            </b-form-group>
          </b-form>
        </div>
        <h5>Selecciona el Dataset</h5>
        <b-form-group class="mb-4">
          <b-form-select
            v-model="selectedDatasetId"
            :options="datasetOptions"
            required
          ></b-form-select>
        </b-form-group>
        <h5>Modelos</h5>
        <div class="d-flex align-items-center">
          <b-form-select
            v-model="selectedModelName"
            :options="modelNames"
            class="me-3"
            required
          ></b-form-select>
          <b-form-select
            v-model="selectedVersion"
            :options="versionOptions"
            :disabled="!selectedModelName"
            required
          ></b-form-select>
        </div>

        <div v-if="hyperparameters.length > 0" class="mt-4">
          <h5>Hiperparámetros</h5>
          <b-form-group
            v-for="(param, index) in hyperparameters"
            :key="param.key_hint"
            :label="param.key_hint"
          >
            <b-form-input
              type="number"
              v-model="hyperparameterValues[`param_${index + 1}`]"
            ></b-form-input>
          </b-form-group>
        </div>
        <div class="d-flex justify-content-center">
          <b-button
            type="submit"
            variant="primary"
            class="mt-4"
            pill
            style="background-color: #0252a6"
            >Realizar Predicción</b-button
          >
        </div>
      </b-form>
    </div>
    <div class="analysis-result-container">
      <h2>Resultados del Análisis</h2>
      <div
        v-if="isProcessing"
        class="loading-state"
        style="
          max-width: 400px;
          display: flex;
          justify-content: center;
          align-items: center;
          padding-top: 50px;
        "
      >
        <h3>
          <strong>Su resultado se está procesando, espere por favor...</strong>
        </h3>
      </div>
      <div v-if="latestResult" class="mt-5">
        <b-card no-body class="p-4 custom-card">
          <b-list-group flush>
            <b-list-group-item>
              <h2><strong>Clasificacion:</strong></h2>
              <h2>{{ latestResult.resultado_texto.join(", ") }}</h2>
            </b-list-group-item>
            <b-list-group-item>
              <strong>Resultado Numérico:</strong>
              {{ latestResult.resultado_numerico.join(", ") }}
            </b-list-group-item>
            <b-list-group-item>
              <strong>ID de Análisis:</strong> {{ latestResult.analysis_id }}
            </b-list-group-item>
            <b-list-group-item>
              <strong>ID de Resultado:</strong> {{ latestResult.id }}
            </b-list-group-item>
            <b-list-group-item>
              <strong>Nombre del Modelo:</strong> {{ latestResult.model_name }}
            </b-list-group-item>
            <b-list-group-item>
              <strong>Estado:</strong>
              <b-badge :variant="getStatusVariant(latestResult.status)">
                {{ latestResult.status }}
              </b-badge>
            </b-list-group-item>

            <b-list-group-item>
              <strong>Fecha de Creación:</strong>
              {{ formatDate(latestResult.created_at) }}
            </b-list-group-item>
          </b-list-group>
          <b-button
            variant="primary"
            pill
            class="mt-3"
            style="background-color: #0252a6"
            @click="downloadJson(latestResult)"
          >
            <b-icon-download></b-icon-download> Descargar Archivo
          </b-button>
        </b-card>
      </div>
    </div>
  </div>
  <div class="table-container-results mx-auto">
    <h2 class="table-title">Historial de Análisis</h2>
    <b-table
      striped
      hover
      :items="analysisResults"
      :fields="fields"
      class="custom-table"
      responsive
    >
      <template #cell(id)="data">
        <div class="d-flex align-items-center justify-content-center">
          <span>{{ data.item.id }}</span>
          <b-button
            size="sm"
            class="toggle-button"
            @click="data.toggleDetails()"
          >
            <b-icon-chevron-down
              v-if="!data.detailsShowing"
            ></b-icon-chevron-down>
            <b-icon-chevron-up v-else></b-icon-chevron-up>
          </b-button>
        </div>
      </template>

      <template #cell(status)="data">
        <b-badge :variant="getStatusVariant(data.value)">
          {{ data.value }}
        </b-badge>
      </template>

      <template #cell(created_at)="data">
        {{ formatDate(data.value) }}
      </template>

      <template #row-details="row">
        <b-card class="details-card">
          <b-row class="mb-2">
            <b-col sm="3" class="text-sm-right"><b>Métricas:</b></b-col>
            <b-col>{{ JSON.stringify(row.item.metrics) }}</b-col>
          </b-row>
          <b-row class="mb-2">
            <b-col sm="3" class="text-sm-right"><b>Parametros:</b></b-col>
            <b-col>{{ JSON.stringify(row.item.parameters) }}</b-col>
          </b-row>
          <b-row class="mb-2">
            <b-col sm="3" class="text-sm-right"><b>Mensaje de Error:</b></b-col>
            <b-col>{{ row.item.error_message || "N/A" }}</b-col>
          </b-row>
          <b-row>
            <b-col sm="3" class="text-sm-right"><b>Actualizado:</b></b-col>
            <b-col>{{ formatDate(row.item.updated_at) }}</b-col>
          </b-row>
        </b-card>
      </template>
    </b-table>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from "vue";

import {
  BForm,
  BFormGroup,
  BFormSelect,
  BFormInput,
  BButton,
  BTable,
  BBadge,
} from "bootstrap-vue-next";
import { getDatasets } from "@/services/datasets";
import { getModels, getHyperparameters } from "@/services/models";
import {
  getAnalysisResults,
  getAnalysisResultById,
  getLastAnalysisId,
} from "@/services/results";
import { uploadDataset } from "@/services/datasets";
import axios from "axios";
import { Alert } from "bootstrap";

// Estado de la aplicación
const selectedDatasetId = ref(null);
const datasets = ref([]);
const datasetOptions = ref([]);

const allModels = ref([]);
const groupedModels = ref({});
const selectedModelName = ref(null);
const selectedVersion = ref(null);

const hyperparameters = ref([]);
const hyperparameterValues = ref({});

const latestResult = ref(null);
const isProcessing = ref(false);
const nextResultId = ref(null);

// --- DESCARGA

// La función que se activará al hacer clic en el botón
const downloadJson = (data) => {
  if (!data) {
    alert("No hay datos para descargar.");
    return;
  }

  // 1. Convierte el objeto JavaScript a una cadena JSON con formato
  const jsonData = JSON.stringify(data, null, 2);

  // 2. Crea un objeto Blob con el contenido JSON
  const blob = new Blob([jsonData], { type: "application/json" });

  // 3. Crea una URL temporal para el Blob
  const url = URL.createObjectURL(blob);

  // 4. Crea un enlace temporal en el DOM
  const link = document.createElement("a");
  link.href = url;

  // 5. Establece el nombre del archivo para la descarga
  link.setAttribute("download", `resultado_${data.id}.json`);

  // 6. Simula un clic en el enlace para iniciar la descarga
  document.body.appendChild(link);
  link.click();

  // 7. Limpia el DOM y libera la URL
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

// --- LOGICA DE LA CARGA DE DATASETS

const form = ref({
  file: null,
  name: "",
  description: "",
});

// Usar un watcher para observar los cambios en form.file
watch(
  () => form.value.file,
  (newFile) => {
    if (newFile) {
      const fileName = newFile.name;
      form.value.name = fileName;
      form.value.description = `Dataset ${fileName}`;
    } else {
      form.value.name = "";
      form.value.description = "";
    }
  }
);

const submitDataset = async () => {
  // El resto de la función de envío permanece igual
  if (!form.value.file) {
    alert("Por favor, selecciona un archivo para subir.");
    return;
  }

  try {
    const response = await uploadDataset(form.value);
    alert("Dataset cargado con exito!");
    loadDatasets();
  } catch (error) {
    console.error("Error al subir el dataset:", error);
  }
};

// --- LÓGICA EXISTENTE DE DATASETS Y MODELOS ---

// Cargar datasets al iniciar
const loadDatasets = async () => {
  try {
    const data = await getDatasets(); // Esta función debe obtener los datasets del endpoint
    datasets.value = data;
    datasetOptions.value = data.map((d) => ({ value: d.id, text: d.name }));
  } catch (error) {
    console.error("Error cargando datasets:", error);
  }
};

// Lógica de agrupamiento de modelos
const groupModels = (models) => {
  return models.reduce((acc, curr) => {
    if (!acc[curr.name]) {
      acc[curr.name] = { versions: [] };
    }
    acc[curr.name].versions.push(curr);
    return acc;
  }, {});
};

// Cargar modelos al iniciar
const loadAndGroupModels = async () => {
  try {
    const data = await getModels();
    allModels.value = data;
    groupedModels.value = groupModels(data);
  } catch (error) {
    console.error("Error cargando modelos:", error);
  }
};

// Propiedades computadas para los selects
const modelNames = computed(() => {
  const names = Object.keys(groupedModels.value).map((name) => ({
    value: name,
    text: name,
  }));
  return [{ value: null, text: "Selecciona un modelo" }, ...names];
});

const versionOptions = computed(() => {
  if (
    !selectedModelName.value ||
    !groupedModels.value[selectedModelName.value]
  ) {
    return [{ value: null, text: "Selecciona una versión" }];
  }
  const versions = groupedModels.value[selectedModelName.value].versions;
  return versions.map((v) => ({
    value: v.version,
    text: `Versión ${v.version}`,
  }));
});

// Watcher para cargar hiperparámetros
watch([selectedModelName, selectedVersion], async ([newModel, newVersion]) => {
  if (newModel && newVersion) {
    const modelObject = groupedModels.value[newModel].versions.find(
      (v) => v.version === newVersion
    );
    if (modelObject) {
      try {
        const params = await getHyperparameters(modelObject.id);
        hyperparameters.value = params;
        hyperparameterValues.value = params.reduce((acc, param) => {
          acc[param.key_hint] = param.default_value;
          return acc;
        }, {});
      } catch (error) {
        console.error("Error cargando hiperparámetros:", error);
        hyperparameters.value = [];
        hyperparameterValues.value = {};
      }
    }
  } else {
    hyperparameters.value = [];
    hyperparameterValues.value = {};
  }
});

// Cargar datos iniciales
onMounted(async () => {
  // Cargar el último ID al iniciar la aplicación
  try {
    const lastId = await getLastAnalysisId();
    nextResultId.value = lastId;
    console.log(nextResultId);
  } catch (error) {
    console.error("No se pudo obtener el último ID de análisis:", error);
    // Puedes establecer un valor por defecto o mostrar un error al usuario
    nextResultId.value = 0;
  }

  loadDatasets();
  loadAndGroupModels();
  fetchAnalysisResults();
});

// --- LÓGICA DE ENVÍO DEL FORMULARIO ---

const submitAnalysis = async () => {
  // 1. Validaciones y obtención del ID del modelo
  if (
    !selectedDatasetId.value ||
    !selectedModelName.value ||
    !selectedVersion.value
  ) {
    alert("Por favor, completa todos los campos requeridos.");
    return;
  }

  const selectedModelObject = groupedModels.value[
    selectedModelName.value
  ].versions.find((v) => v.version === selectedVersion.value);
  const modelId = selectedModelObject ? selectedModelObject.id : null;

  // 2. Preparar los datos para la solicitud POST
  const postData = {
    dataset: selectedDatasetId.value,
    model: modelId,
    ...hyperparameterValues.value, // <--- Este es el cambio clave
  };

  console.log("Datos que se enviarán:", postData);

  // 4. Realizar la solicitud POST
  try {
    const accessToken = localStorage.getItem("access");
    const response = await axios.post(
      "http://localhost:8000/api/v1/analysis/",
      postData,
      {
        headers: {
          Authorization: `Bearer ${accessToken}`,
          "Content-Type": "application/json",
        },
      }
    );

    const lastId = await getLastAnalysisId();
    nextResultId.value = lastId;

    // Obtener el ID del análisis para identificar la conexión
    const analysisId = response.data.id;
    console.log("Análisis enviado con ID:", analysisId);
    console.log("Respuesta del servidor:", response.data);

    alert("El analisis se envió con exito!");

    const analysisIdresult = response.data.id;
    console.log(analysisIdresult);

    // 1. Incrementar el ID para la siguiente petición de resultados
    if (nextResultId.value !== null) {
      let success = false;
      let attempts = 0;
      const maxAttempts = 5; // Define el número máximo de reintentos
      const retryInterval = 3000; // Define el intervalo de reintento en milisegundos (3 segundos)

      isProcessing.value = true;
      latestResult.value = null;

      while (!success && attempts < maxAttempts) {
        try {
          // 2. Usar el nuevo ID para obtener el resultado
          const result = await getAnalysisResultById(nextResultId.value);
          latestResult.value = result;
          fetchAnalysisResults();
          success = true;
        } catch (error) {
          // Manejar el error de la petición HTTP
          if (error.response && error.response.status === 500) {
            console.log(
              `Error 500. Reintentando en ${retryInterval / 1000} segundos...`
            );
            attempts++;
            if (attempts < maxAttempts) {
              // Esperar 'e' segundos antes del próximo reintento
              await new Promise((resolve) =>
                setTimeout(resolve, retryInterval)
              );
            } else {
              // Si se excede el número máximo de intentos, se lanza la alerta
              alert(
                "No se pudo obtener el ID del resultado después de varios intentos. Por favor, recarga la página."
              );
              isProcessing.value = false;
            }
          } else {
            // Si el error no es 500, lanzar una alerta o manejarlo de otra forma
            alert(
              "Ocurrió un error inesperado al obtener los resultados. Por favor, recarga la página."
            );
            isProcessing.value = false;
            break; // Salir del bucle para evitar reintentos innecesarios
          }
        }
      }
      // Si la petición fue exitosa, desactivamos el estado de procesamiento
      if (success) {
        isProcessing.value = false;
      }
    } else {
      // Manejar el caso si no se pudo obtener el último ID al inicio
      alert(
        "No se pudo obtener el ID del resultado. Por favor, recarga la página."
      );
      isProcessing.value = false;
    }

    /*
    // Código para el manejo de notificaciones en tiempo real (omitido por ahora)
    // Para usar esta sección, asegúrate de que tu WebSocket esté configurado y activo

    // websocketService.send({ type: 'start_analysis', data: response.data });
    // toast.info("Tarea de análisis iniciada. Te notificaremos los resultados en tiempo real.", { timeout: false });
    */
  } catch (error) {
    console.error(
      "Error al enviar el análisis:",
      error.response?.data || error.message
    );
    alert("Error al enviar el análisis. Por favor, revisa la consola.");
  }
};

///LOGICA PARA LA TABLA DE RESULTADOS

const analysisResults = ref([]);
//const toast = useToast();

const fields = [
  { key: "id", label: "ID", sortable: true },
  { key: "dataset", label: "Dataset", sortable: true },
  { key: "model", label: "Modelo", sortable: true },
  { key: "status", label: "Estado", sortable: true },
  { key: "created_at", label: "Fecha de Creación", sortable: true },
  // Ocultar las siguientes columnas de la tabla principal
  { key: "metrics", label: "Métricas", class: "d-none" },
  { key: "parameters", label: "Hyperparametros", class: "d-none" },
  { key: "output_path", label: "Ruta de Salida", class: "d-none" },
  { key: "error_message", label: "Mensaje de Error", class: "d-none" },
  { key: "updated_at", label: "Actualizado", class: "d-none" },
];

const getStatusVariant = (status) => {
  switch (status) {
    case "success":
      return "success";
    case "pending":
      return "warning";
    case "failed":
      return "danger";
    default:
      return "info";
  }
};

const formatDate = (dateString) => {
  const options = {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  };
  return new Date(dateString).toLocaleDateString("es-ES", options);
};

const fetchAnalysisResults = async () => {
  try {
    const data = await getAnalysisResults();
    analysisResults.value = data;
  } catch (error) {
    console.error("Error fetching analysis results:", error);
  }
};
</script>
<style scoped>
.table-container,
.table-container-results {
  max-width: 1000px;
  margin: 2rem;
  padding: 3rem;
  background-color: #f8f9fa;
  border-radius: 40px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.table-title {
  text-align: center;
  font-weight: 600;
  color: #343a40;
  margin-bottom: 1.5rem;
}

.custom-table {
  border: none;
  border-radius: 24px;
}

.custom-table thead th {
  background-color: #34495e;
  color: white;
  border: none;
  font-weight: 500;
  text-transform: uppercase;
}

.custom-table tbody tr {
  transition: background-color 0.3s ease;
}

.custom-table tbody tr:hover {
  background-color: #e9ecef;
}

.custom-table tbody tr:nth-of-type(odd) {
  background-color: #f2f4f6;
}

.table-container-results {
  padding: auto;
}

.analysis-result-container {
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 8px;
  margin-top: 20px;
  min-height: 500px;
}
.loading-state,
.error-state {
  text-align: center;
  color: #555;
}
.error-state {
  color: #d9534f;
}
.results-display p {
  margin: 8px 0;
}

.analysis-result-container {
  max-width: 1000px;
  background-color: #f8f9fa;
  border-radius: 40px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  border: none;
  padding: 3rem;
}
</style>
