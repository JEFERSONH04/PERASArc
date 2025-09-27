<script>
export default {
  methods: {
    logout() {
      // Remueve el token de acceso del localStorage
      localStorage.removeItem("access");
      localStorage.removeItem("username");
      // Opcional: Redirige al usuario a la página de inicio de sesión
      this.$router.push("/login");
    },
  },
  data() {
    return {
      username: "", // Inicializamos la variable que contendrá el nombre
    };
  },
  mounted() {
    // Al cargar el componente, leemos el valor del localStorage
    this.username = localStorage.getItem("username");
  },
};
</script>
<template>
  <div class="header">
    <div
      style="
        display: flex;
        max-width: 400px;
        text-align: start;
        align-items: center;
      "
    >
      <img src="/src/assets/images/logo.jpg" alt="logo BIOMOL" height="80px" />
      <p style="padding-left: 20px">
        <strong>Biomol - Biología Molecular y Biotecnología</strong>
      </p>
    </div>
    <div class="bienvenida">
      <h3>Bienvenido, {{ username }}!</h3>
    </div>
    <div
      style="
        width: 400px;
        display: flex;
        align-items: center;
        justify-content: flex-end;
      "
    >
      <button class="login-button">
        <a href="#" @click.prevent="logout" style="color: white"
          >Cerrar sesion</a
        >
      </button>
    </div>
  </div>
</template>
<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  background-color: hsl(0, 0%, 100%); /* Un verde vibrante, muy 'Vue' */
  color: rgb(0, 0, 0);
  padding: 20px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 1, 0.1);
}

h2 {
  margin: 0;
  font-size: 2.5em;
}

p {
  margin-top: 5px;
  font-size: 1.2em;
}

.login-button {
  display: flex;
  justify-content: center;
  max-width: 150px;
  width: 100%;
  padding: 12px;
  background-color: #0252a6;
  color: #fff;
  border: none;
  border-radius: 24px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.1s ease;
}

.bienvenida {
  display: flex;
  justify-content: center;
  align-items: center;
}

@media (max-width: 768px){
  .bienvenida {
    display: none;
  }
}
</style>
