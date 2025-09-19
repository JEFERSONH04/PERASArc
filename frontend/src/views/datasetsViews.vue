<template>
  <div>
    <h2>Mis Datasets</h2>
    <b-form-select v-model="selectedDataset" :options="datasetOptions"></b-form-select>
    <div v-if="selectedDataset">
      <p>ID del Dataset seleccionado: {{ selectedDataset }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { BFormSelect } from 'bootstrap-vue-next';
import { getDatasets } from '@/services/datasets';

const datasets = ref([]);
const datasetOptions = ref([]);
const selectedDataset = ref(null);

// Función para cargar los datasets
const loadDatasets = async () => {
  try {
    const data = await getDatasets();
    datasets.value = data;
    
    // Mapear los datos de la API al formato de b-form-select
    datasetOptions.value = data.map(dataset => ({
      value: dataset.id,
      text: dataset.name
    }));

    // Si quieres seleccionar el primer elemento por defecto
    if (datasetOptions.value.length > 0) {
      selectedDataset.value = datasetOptions.value[0].value;
    }

  } catch (error) {
    console.error("No se pudieron cargar los datasets:", error);
    // Aquí puedes mostrar un mensaje de error al usuario
  }
};

// Cargar los datasets cuando el componente se monte
onMounted(() => {
  loadDatasets();
});
</script>