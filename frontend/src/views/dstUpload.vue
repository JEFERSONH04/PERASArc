<template>
  <b-form-input type="text" placeholder="Este input está oculto"></b-form-input>
  <div>
    <b-form @submit.prevent="submitDataset">
      <b-form-group label="Cargar Archivo">
        <b-form-file v-model="form.file" ref="fileInput"></b-form-file>
      </b-form-group>
      <b-form-group label="Nombre del Dataset" disabled="">
        <b-form-input
          disabled=""
          v-model="form.name"
          readonly
          class="d-none"
        ></b-form-input>
      </b-form-group>
      <b-form-group label="Descripción del Dataset">
        <b-form-input
          disabled=""
          v-model="form.description"
          class="d-none"
        ></b-form-input>
      </b-form-group>
      <b-button type="submit" variant="primary">Subir Dataset</b-button>
    </b-form>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";
import {
  BForm,
  BFormGroup,
  BFormFile,
  BFormInput,
  BButton,
} from "bootstrap-vue-next";
import { uploadDataset } from "@/services/datasets";

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
    console.log("Dataset subido con éxito:", response);
  } catch (error) {
    console.error("Error al subir el dataset:", error);
  }
};
</script>
