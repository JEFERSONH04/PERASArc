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
                <b-button pill type="submit" variant="primary"
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
          <b-button type="submit" variant="primary" class="mt-4" pill
            >Realizar Predicción</b-button
          >
        </div>
      </b-form>
    </div>
    <div class="analysis-result-container">
      <h2>Resultados del Análisis</h2>
      <div v-if="loading" class="loading-state">
        <p>Cargando resultados...</p>
      </div>
      <div v-else-if="error" class="error-state">
        <p>Error: {{ error }}</p>
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
            variant="success"
            class="mt-3"
            @click="downloadResultFile(latestResult.analysis_id)"
            >Descargar Archivo
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
            <b-col sm="3" class="text-sm-right"><b>Hyperparametros:</b></b-col>
            <b-col>{{ JSON.stringify(row.item.parameters) }}</b-col>
          </b-row>
          <b-row class="mb-2">
            <b-col sm="3" class="text-sm-right"><b>Ruta de Salida:</b></b-col>
            <b-col>{{ row.item.output_path }}</b-col>
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
  downloadFile,
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
const nextResultId = ref(null);


// --- DESCARGA

// La función que se activará al hacer clic en el botón
const downloadResultFile = async (resultId) => {
    try {
        await downloadFile(resultId);
    } catch (error) {
        // La función de servicio ya maneja el error.
        // Puedes agregar una alerta aquí si lo deseas.
    }
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

    console.log("Respuesta del servidor:", response.data);
    alert("Análisis de tarea enviado con éxito!");
    fetchAnalysisResults();
    setTimeout(fetchAnalysisResults, 5000);
    const analysisIdresult = response.data.id;
    console.log(analysisIdresult);

    // 1. Incrementar el ID para la siguiente petición de resultados
    if (nextResultId.value !== null) {
      nextResultId.value++;
      // 2. Usar el nuevo ID para obtener el resultado
      const result = await getAnalysisResultById(nextResultId.value);
      latestResult.value = result;
    } else {
      // Manejar el caso si no se pudo obtener el último ID al inicio
      alert(
        "No se pudo obtener el ID del resultado. Por favor, recarga la página."
      );
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

onMounted(() => {
  fetchAnalysisResults();

  //  websocket.onmessage = (event) => {
  //    const data = JSON.parse(event.data);
  //    const message = data.message;

  //    switch (message.type) {
  //      case "success":
  //        toast.success(message.text);
  //        if (message.analysis_id) {
  //          fetchAnalysisResults();
  //        }
  //        break;
  //      case "error":
  //        toast.error(message.text);
  //        fetchAnalysisResults();
  //       break;
  //      default:
  //        toast.info(message.text);
  //    }
  //  };
});
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
