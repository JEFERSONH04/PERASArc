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
};
</script>
<template>
  <div class="navbar">
    <nav class="bar">
      <RouterLink to="/">Inicio</RouterLink>
      <a href="#" @click.prevent="logout">Cerrar sesion</a>
    </nav>
  </div>
</template>
<style scoped>
.nav {
  display: flex;
  justify-content: center;
  gap: 20px;
  padding: 10px;
  background-color: #35495e; /* Un azul oscuro, para un buen contraste */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

a {
  color: rgb(0, 0, 0);
  text-decoration: none;
  font-weight: bold;
  padding: 5px 10px;
  border-radius: 5px;
  transition: background-color 0.3s ease;
}

a:hover {
  background-color: #1ff18f;
}
</style>
