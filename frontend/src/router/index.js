import { createRouter, createWebHistory } from "vue-router";
import mainLayout from "@/layouts/mainLayout.vue";
import homeView from "@/views/homeView.vue";
import authLayout from "@/layouts/authLayout.vue";
import LoginView from "@/views/LoginView.vue";
import RegisterView from "@/views/RegisterView.vue";
import datasetsViews from "@/views/datasetsViews.vue";
import dstUpload from "@/views/dstUpload.vue";
import modelsView from "@/views/modelsView.vue";
import analysisresultsView from "@/views/analysisresultsView.vue";
import { sessionGetService } from "@/services/sessionService";
import usersView from "@/views/usersView.vue";
import UsersView from "@/views/usersView.vue";
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
      path: "/login/login",
      component: authLayout,
      children: [
        {
          path: "",
          component: UsersView,
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
    {
      path: "/datasets",
      component: mainLayout,
      children: [
        {
          path: "",
          component: datasetsViews,
          beforeEnter: (to, from) => {
            if (sessionGetService("access")) {
              return true;
            } else {
              router.push({ path: "/login" });
            }
          },
        },
        {
          path: "/upload",
          component: dstUpload,
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
      path: "/models",
      component: mainLayout,
      children: [
        {
          path: "",
          component: modelsView,
          beforeEnter: (to, from) => {
            if (sessionGetService("access")) {
              return true;
            } else {
              router.push({ path: "/login" });
            }
          },
        },
        {
          path: "analysis",
          //component: modelsHyperparms,
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
      path: "/results",
      component: mainLayout,
      children: [
        {
          path: "",
          component: analysisresultsView,
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
  ],
});

export default router;
