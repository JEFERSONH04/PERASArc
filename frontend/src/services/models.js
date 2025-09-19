///Importar los recursos necesarios
import axios from "axios";

// Función para obtener la lista de datasets del usuario autenticado
export const getModels = async () => {
  const apiUrl = "http://localhost:8000/api/v1/models/";

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
    console.log("Modelos disponibles: ", response.data);
    return response.data;
  } catch (error) {
    // 4. Maneja los errores de la petición
    // El interceptor de Axios ya debería manejar el error 401 para refrescar el token
    console.error("Error al obtener los modelos:", error);
    throw error;
  }
};

export const getHyperparameters = async (modelId) => {
  const apiUrl = `http://localhost:8000/api/v1/models/hyperparameters/${modelId}/`;

  try {
    const accessToken = localStorage.getItem("access");
    const response = await axios.get(apiUrl, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });
    return response.data;
  } catch (error) {
    console.error(
      `Error fetching hyperparameters for model ${modelId}:`,
      error
    );
    throw error;
  }
};
