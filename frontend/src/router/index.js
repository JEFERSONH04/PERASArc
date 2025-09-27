import { createRouter, createWebHistory } from "vue-router";
import mainLayout from "@/layouts/mainLayout.vue";
import homeView from "@/views/homeView.vue";
import authLayout from "@/layouts/authLayout.vue";
import LoginView from "@/views/LoginView.vue";
import RegisterView from "@/views/RegisterView.vue";
import { sessionGetService } from "@/services/sessionService";
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      component: mainLayout,
      children: [
        {
          path: "",
          component: homeView,
          beforeEnter: (to, from) => {
            if (sessionGetService("access")) {
              return true;
            } else {
              router.push({ path: "/login" });
            }
          },
        },
      ],
    },
    {
      path: "/login",
      component: authLayout,
      children: [
        {
          path: "",
          component: LoginView,
        },
      ],
    },
    {
      path: "/register",
      component: authLayout,
      children: [
        {
          path: "",
          component: RegisterView,
        },
      ],
    },
  ],
});

export default router;
