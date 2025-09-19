<template>
  <div class="table-container">
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
import { ref, onMounted } from "vue";
import { BTable, BBadge } from "bootstrap-vue-next";
//import { useToast } from "vue-toastification";
//import websocket from "@/services/websocketService.js";
import { getAnalysisResults } from "@/services/results";

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
.table-container {
  max-width: 1000px;
  margin: 2rem auto;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 10px;
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
</style>
