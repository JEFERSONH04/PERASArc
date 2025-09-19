import { createBootstrap } from "bootstrap-vue-next";
import { createApp } from "vue";
import { createPinia } from "pinia";


import App from "./App.vue";
import router from "./router";

// Add the necessary CSS
import "bootstrap/dist/css/bootstrap.css";
import "bootstrap-vue-next/dist/bootstrap-vue-next.css";

const app = createApp(App);

app.use(createPinia());
app.use(createBootstrap());
app.use(router);

app.mount("#app");
