///Importar los recursos necesarios
import { sessionGetService } from "./sessionService";
import axios from "axios";

// Función para obtener la lista de datasets del usuario autenticado
export const getDatasets = async () => {
  const apiUrl = "http://localhost:8000/api/v1/datasets/";

  try {
    // 1. Obtiene el token de acceso del almacenamiento local
    const accessToken = localStorage.getItem("access");

    if (!accessToken) {
      console.error(
        "No se encontró el token de acceso. Por favor, inicia sesión."
      );
      // Opcionalmente, puedes redirigir al usuario a la página de login
      throw new Error("No Authenticated");
    }

    // 2. Realiza la petición GET, adjuntando el token en el encabezado
    const response = await axios.get(apiUrl, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });

    // 3. Devuelve los datos de la respuesta (la lista de datasets)
    console.log("Datasets del usuario:", response.data);
    return response.data;
  } catch (error) {
    // 4. Maneja los errores de la petición
    // El interceptor de Axios ya debería manejar el error 401 para refrescar el token
    console.error("Error al obtener los datasets:", error);
    throw error;
  }
};

export const uploadDataset = async (datasetForm) => {
  const apiUrl = "http://localhost:8000/api/v1/datasets/";
  const accessToken = sessionGetService("access");

  // Crear el objeto FormData
  const formData = new FormData();
  formData.append("name", datasetForm.name);
  formData.append("description", datasetForm.description);
  formData.append("file", datasetForm.file); // 'file' debe coincidir con el nombre de campo de tu modelo en Django

  try {
    const response = await axios.post(apiUrl, formData, {
      headers: {
        "Content-Type": "multipart/form-data", // Indicar que se está enviando un formulario multipart
        Authorization: `Bearer ${accessToken}`,
      },
    });

    return response.data;
  } catch (error) {
    console.error(
      "Error al subir el dataset:",
      error.response?.data || error.message
    );
    throw error;
  }
};
