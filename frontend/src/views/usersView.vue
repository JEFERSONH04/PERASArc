<template>
  <div class="login-container">
    <div class="image-section">
      <img
        src="https://picsum.photos/400/400/?image=20"
        alt="Imagen de fondo para el login"
      />
    </div>

    <div class="form-section">
      <div class="login-card">
        <div class="logo">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="currentColor"
          >
            <path d="M12 2L2 22h20L12 2zm0 10l-4 8h8l-4-8z" />
          </svg>
          <h1>Tu Marca</h1>
        </div>

        <form @submit.prevent="register">
          <h2>Registrar Usuario</h2>
          <div class="input-group">
            <label for="Username">Nombre de usuario</label>
            <input
              type="text"
              id="username"
              v-model="formRegister.username"
              placeholder="Nombre de usuario"
              required
            />
          </div>
          <div class="input-group">
            <label for="email">Correo electrónico</label>
            <input
              type="email"
              id="email"
              v-model="formRegister.email"
              placeholder="john.doe@ejemplo.com"
              required
            />
          </div>
          <div class="input-group">
            <label for="password">Contraseña</label>
            <input
              type="password"
              id="password"
              v-model="formLogin.password"
              placeholder="••••••••"
              required
            />
          </div>
          <button type="submit" class="register-button">Crear</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue";
import { loginService } from "@/services/authService";
import { sessionSetService } from "@/services/sessionService";
import router from "@/router";
const loading = ref(false);
const formLogin = reactive({
  username: null,
  password: null,
});
const login = async (event) => {
  event.preventDefault();
  loading.value = true;
  try {
    const data = await loginService(this.username, this.password);
    console.log("...", data);

    sessionSetService("access", data.access);
    sessionSetService("username", data.user.username);
    router.push({ path: "/" });
  } catch (error) {
    console.error("Error al obtener el perfil:", error);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-container {
  display: flex;
  width: 900px;
  height: 600px;
  background-color: #ffffffe4;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  margin-left: auto;
  margin-right: auto;
  margin-top: 150px;
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

.logo svg {
  width: 50px;
  height: 50px;
  color: var(--primary-color);
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

form h2 {
  font-size: 1.5rem;
  font-weight: 500;
  color: var(--text-color-dark);
  margin-bottom: 1.5rem;
  text-align: center;
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

/* Media Queries para responsividad */
@media (max-width: 768px) {
  .login-container {
    flex-direction: column;
    height: auto;
    width: 90%;
    max-width: 500px;
  }

  .image-section {
    display: none; /* Oculta la imagen en dispositivos móviles */
  }
}
</style>
