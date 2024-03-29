import { RouteConfig } from "vue-router";
import CdHome from "@/components/home/cd.home.vue";
import CdSearchResults from "@/components/search-results/cd.search-results.vue";
import CdSubmissions from "@/components/submissions/cd.submissions.vue";
import CdFooter from "@/components/base/cd.footer.vue";
import CdContribute from "@/components/contribute/cd.contribute.vue";
import CdDataset from "@/components/dataset/cd.dataset.vue";
import AuthRedirect from "@/components/account/auth-redirect.vue";
import CdRegisterDataset from "@/components/register/cd.register-dataset.vue";

export const routes: RouteConfig[] = [
  {
    name: "home",
    path: "/",
    components: {
      content: CdHome,
      footer: CdFooter,
    },
  },
  {
    name: "search",
    path: "/search",
    components: {
      content: CdSearchResults,
      footer: CdFooter,
    },
    meta: {
      title: "Search",
    },
  },
  {
    name: "contribute",
    path: "/contribute",
    components: {
      content: CdContribute,
      footer: CdFooter,
    },
    meta: {
      hasLoggedInGuard: true,
      // hasAccessTokenGuard: true,
      hasUnsavedChangesGuard: true,
      title: "Contribute",
      flat: true,
    },
  },
  {
    name: "register",
    path: "/register",
    components: {
      content: CdRegisterDataset,
      footer: CdFooter,
    },
    meta: {
      hasLoggedInGuard: true,
      title: "Register Dataset",
    },
  },
  {
    name: "submissions",
    path: "/submissions",
    components: {
      content: CdSubmissions,
      footer: CdFooter,
    },
    meta: {
      title: "My Submissions",
      hasLoggedInGuard: true,
    },
  },
  {
    name: "dataset",
    path: "/dataset/:id",
    components: { content: CdDataset, footer: CdFooter },
    meta: {
      title: "Dataset",
    },
  },
  {
    name: "dataset-edit",
    path: "/dataset/:id/edit",
    components: { content: CdContribute, footer: CdFooter },
    meta: {
      title: "Edit Dataset",
      hasUnsavedChangesGuard: true,
      hasLoggedInGuard: true,
      flat: true,
    },
  },
  {
    name: "auth-redirect",
    path: "/auth-redirect",
    components: {
      content: AuthRedirect,
    },
    meta: {
      hideNavigation: true,
    },
  },
  {
    path: "*",
    redirect: "/",
  },
];
