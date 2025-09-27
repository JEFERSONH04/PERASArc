<script setup>
import { reactive, ref } from "vue";
import { loginService } from "@/services/authService";
import { sessionSetService } from "@/services/sessionService";
import router from "@/router";
const loading = ref(false);
const errorMessage = ref("");
const formLogin = reactive({
  username: null,
  password: null,
});
const login = async (event) => {
  event.preventDefault();
  loading.value = true;
  errorMessage.value = "";
  try {
    const data = await loginService(formLogin.username, formLogin.password);

    sessionSetService("access", data.access);
    sessionSetService("username", data.user.username);
    router.push({ path: "/" });
  } catch (error) {
    if (error.response && error.response.data && error.response.data.message) {
      errorMessage.value = error.response.data.message; // 3. Asigna el mensaje de error usando .value
    } else {
      errorMessage.value =
        "Credenciales inválidas. Por favor, inténtalo de nuevo."; // 4. Mismo caso, usando .value
    }
  } finally {
    loading.value = false;
  }
};
</script>
<template>
  <br />
  <div class="login_contenedor">
    <div class="image-section">
      <img
        src="/src/assets/images/imagenFormulario.png"
        alt="Imagen de fondo para el login"
      />
    </div>
    <div class="form-section">
      <div class="login-card">
        <div class="logo">
          <img
            src="/src/assets/images/logo.jpg"
            alt="logo BIOMOL"
            height="150px"
          />
          <h1>Biomol - Biología Molecular y Biotecnología</h1>
        </div>
        <BCard style="border: none; width: 100%">
          <h2
            style="
              font-size: 1.5rem;
              font-weight: 500;
              margin-bottom: 1.5rem;
              text-align: center;
            "
          >
            Iniciar Sesión
          </h2>
          <BForm @submit="login">
            <div class="input-group">
              <input
                type="text"
                id="email"
                v-model="formLogin.username"
                placeholder="Nombre de usuario"
                autocomplete="off"
                required
              />
            </div>
            <div class="input-group">
              <input
                type="password"
                id="password"
                v-model="formLogin.password"
                placeholder="Contraseña"
                autocomplete="off"
                required
              />
            </div>
            <br />

            <button type="submit" :disabled="loading" class="login-button">
              {{ loading ? "Entrando..." : "Entrar" }}
            </button>
            <p style="text-align: center; padding-top: 20px">
              ¿No tienes cuenta?
              <router-link to="/register">Regístrate aquí</router-link>
            </p>
            <div v-if="errorMessage" class="error-message">
              {{ errorMessage }}
            </div>
          </BForm>
        </BCard>
      </div>
    </div>
  </div>
</template>
<style>
.login_contenedor {
  display: flex;
  width: 1000px;
  height: auto;
  background-color: #ffffffe4;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  margin-left: auto;
  margin-right: auto;
  margin-top: 100px;
}
.login {
  width: 400px;
  margin: auto;
  padding-top: 20px;
}

.image-section {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}

.image-section img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.form-section {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px;
  position: relative;
}

.login-card {
  width: 100%;
  max-width: 400px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.logo {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 2rem;
}

.logo img {
  border-radius: 50%;
  border: #0252a6 10px solid;
}

.logo h1 {
  font-size: 1.8rem;
  font-weight: 600;
  color: var(--text-color-dark);
  margin-top: 0.5rem;
}

form {
  width: 100%;
  text-align: left;
}

.input-group {
  margin-bottom: 1.5rem;
}

.input-group label {
  display: block;
  font-size: 0.9rem;
  color: #333;
  margin-bottom: 0.5rem;
}

.input-group input {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid #dddddd4d;
  border-radius: 8px;
  font-size: 1rem;
  color: var(--text-color-dark);
  transition: border-color 0.3s ease;
}

.input-group input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(75, 137, 220, 0.2);
}

.login-button {
  width: 100%;
  padding: 12px;
  background-color: #0252a6;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.1s ease;
}

.login-button:hover {
  background-color: #3b76c8;
}

.login-button:active {
  transform: translateY(1px);
}

.forgot-password {
  display: block;
  margin-top: 1rem;
  text-align: center;
  color: var(--primary-color);
  text-decoration: none;
  font-size: 0.9rem;
  transition: color 0.3s ease;
}

.forgot-password:hover {
  color: #3b76c8;
}

.error-message {
  color: red;
  font-weight: bold;
  margin-bottom: 15px;
  text-align: center; /* o la separación que prefieras */
}

/* Media Queries para responsividad */
@media (max-width: 768px) {
  .login_contenedor {
    flex-direction: column;
    height: auto;
    width: 90%;
    max-width: 500px;
  }

  .image-section {
    display: none; /* Oculta la imagen en dispositivos móviles */
  }

  .form-section {
    padding: 30px;
  }
}
</style>
