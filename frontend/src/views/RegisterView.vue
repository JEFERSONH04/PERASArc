<script setup>
import { reactive, ref } from "vue";
import { registerService } from "@/services/authService";
import router from "@/router";

const loading = ref(false);
const formRegister = reactive({
  username: null,
  password: null,
  email: null,
});
const register = async (event) => {
  event.preventDefault();
  loading.value = true;
  try {
    const data = await registerService(
      formRegister.username,
      formRegister.email,
      formRegister.password
    );
    console.log("...", data);

    router.push({ path: "/login" });
  } catch (error) {
    console.error("Error al crear el perfil", error);
  } finally {
    loading.value = false;
  }
};
</script>
<template>
  <br />
  <div class="register_contenedor">
    <div class="image-section">
      <img
        src="https://picsum.photos/400/400/?image=20"
        alt="Imagen de fondo para el login"
      />
    </div>
    <div class="form-section">
      <div class="register-card">
        <div class="logo">
          <img
            src="/src/assets/images/logo.jpg"
            alt="logo BIOMOL"
            height="150px"
          />
          <h1>Biomol - Biología Molecular y Biotecnología</h1>
        </div>
        <form @submit.prevent="register">
          <h2>Registrar Usuario</h2>
          <div class="input-group">
            <input
              type="text"
              id="username"
              v-model="formRegister.username"
              placeholder="Nombre de usuario"
              required
            />
          </div>
          <div class="input-group">
            <input
              type="email"
              id="email"
              v-model="formRegister.email"
              placeholder="Correo"
              required
            />
          </div>
          <div class="input-group">
            <input
              type="password"
              id="password"
              v-model="formRegister.password"
              placeholder="Contraseña"
              required
            />
          </div>
          <button type="submit" class="register-button">Crear</button>
        </form>
      </div>
    </div>
  </div>
</template>
<style scoped>
.register_contenedor {
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

.register-card {
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
  margin-bottom: 8px;
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

.register-button {
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

.register-button:hover {
  background-color: #3b76c8;
}

.register-button:active {
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
  .register_contenedor {
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
