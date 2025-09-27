///Importar los recursos necesarios
import axios from "axios";
import router from "@/router";
// Función para obtener la lista de resultados del usuario autenticado
export const getAnalysisResults = async () => {
  const apiUrl = "http://localhost:8000/api/v1/analysis/";

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
    console.log("Resultadods disponibles: ", response.data);
    return response.data;
  } catch (error) {
    // Si el error tiene una respuesta y el estado es 403, redirigimos
    if (error.response && error.response.status === 403) {
      alert("Token expirado o no válido, redirigiendo a la página de login...");
      // Elimina el token del localStorage
      localStorage.removeItem("access");
      localStorage.removeItem("username");
      // Redirige al usuario a la ruta de login
      router.push({ path: "/login" });
    }
  }
};

export const getLastAnalysisId = async () => {
  const apiUrl = `http://localhost:8000/analisis/ultimo`;
  const accessToken = localStorage.getItem("access");

  try {
    const response = await axios.get(apiUrl, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });
    return response.data.last_analysis_id;
  } catch (error) {
    console.error("Error al obtener el último ID de análisis:", error);
    throw error;
  }
};

export const getAnalysisResultById = async (analysisId) => {
  const apiUrl = `http://localhost:8000/analisis/${analysisId}/`;
  const accessToken = localStorage.getItem("access");

  try {
    const response = await axios.get(apiUrl, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });
    return response.data;
  } catch (error) {
    console.error(
      `Error fetching analysis result for ID ${analysisId}:`,
      error
    );
    throw error;
  }
};

