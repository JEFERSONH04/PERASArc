<template>
  <div>
    <h2>Modelos y Versiones</h2>
    <div class="d-flex align-items-center">
      <b-form-select
        v-model="selectedModel"
        :options="modelNames"
        class="me-3"
      ></b-form-select>
      <b-form-select
        v-model="selectedVersion"
        :options="versionOptions"
        :disabled="!selectedModel"
      ></b-form-select>
    </div>

    <div v-if="hyperparameters.length > 0" class="mt-4">
      <h3>Hiperparámetros</h3>
      <b-form-group
        v-for="param in hyperparameters"
        :key="param.name"
        :label="param.name"
      >
        <b-form-input
          type="number"
          :value="param.default_value"
          @input="updateHyperparameter(param.name, $event)"
        ></b-form-input>
      </b-form-group>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from "vue";
import { BFormSelect } from "bootstrap-vue-next";
import { getModels, getHyperparameters } from "@/services/models";

const allModels = ref([]);
const groupedModels = ref({});
const selectedModel = ref(null);
const selectedVersion = ref(null);
const hyperparameters = ref([]);
const hyperparameterValues = ref({}); // To store the values of the inputs

// Lógica de Agrupación de Modelos
const groupModels = (models) => {
  return models.reduce((accumulator, currentModel) => {
    if (!accumulator[currentModel.name]) {
      accumulator[currentModel.name] = {
        versions: [],
      };
    }
    accumulator[currentModel.name].versions.push(currentModel);
    return accumulator;
  }, {});
};

// Obtener y agrupar los modelos al montar el componente
onMounted(async () => {
  try {
    const data = await getModels();
    allModels.value = data;
    groupedModels.value = groupModels(data);
  } catch (error) {
    console.error("Error al cargar los modelos:", error);
  }
});

// Opción 1: Usar una propiedad computada para las versiones
const versionOptions = computed(() => {
  if (!selectedModel.value || !groupedModels.value[selectedModel.value]) {
    return [{ value: null, text: "Selecciona una versión" }];
  }

  return groupedModels.value[selectedModel.value].versions.map((version) => ({
    value: version.version, // Usamos la versión como valor
    text: `Versión ${version.version}`, // Texto para mostrar
  }));
});

// Opción 2: Usar un watcher para las versiones (alternativa)
// Watch for changes in both model and version selections
watch([selectedModel, selectedVersion], async ([newModel, newVersion]) => {
  if (newModel && newVersion) {
    // Find the selected model object to get its ID
    const modelObject = groupedModels.value[newModel].versions.find(
      (v) => v.version === newVersion
    );

    if (modelObject) {
      try {
        const params = await getHyperparameters(modelObject.id);
        hyperparameters.value = params;

        // Initialize the hyperparameter values with their defaults
        hyperparameterValues.value = params.reduce((acc, param) => {
          acc[param.name] = param.default_value;
          return acc;
        }, {});
      } catch (error) {
        console.error("Failed to load hyperparameters:", error);
        hyperparameters.value = [];
      }
    }
  } else {
    // Clear hyperparameters if no model or version is selected
    hyperparameters.value = [];
    hyperparameterValues.value = {};
  }
});

// Propiedad computada para los nombres de los modelos
const modelNames = computed(() => {
  const names = Object.keys(groupedModels.value).map((name) => ({
    value: name,
    text: name,
  }));
  return [{ value: null, text: "Selecciona un modelo" }, ...names];
});

// Update the hyperparameter values object
const updateHyperparameter = (name, value) => {
  hyperparameterValues.value[name] = value;
};
</script>

<style scoped>
.d-flex {
  display: flex;
}
.align-items-center {
  align-items: center;
}
.me-3 {
  margin-right: 1rem;
}
</style>
