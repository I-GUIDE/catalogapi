import { RouteConfig } from "vue-router";
import CdSearchResults from "@/components/search-results/cd.search-results.vue";
import CdFooter from "@/components/base/cd.footer.vue";
import AuthRedirect from "@/components/account/auth-redirect.vue";

export const routes: RouteConfig[] = [
  {
    name: "search",
    path: "/",
    components: {
      content: CdSearchResults,
      footer: CdFooter,
    },
    meta: {
      title: "Search",
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
