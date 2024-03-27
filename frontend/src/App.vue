<template>
  <v-app app>
    <v-app-bar
      v-if="!$route.meta.hideNavigation"
      color="navbar"
      ref="appBar"
      id="app-bar"
      elevate-on-scroll
      fixed
      app
    >
      <v-container class="d-flex align-end full-height pa-0 align-center">
        <router-link :to="{ path: `/` }" class="logo">
          <img :src="require('@/assets/img/logo-w.png')" alt="home" />
        </router-link>
        <div class="spacer"></div>
        <v-card
          class="nav-items mr-2 d-flex mr-4"
          :elevation="2"
          v-if="!$vuetify.breakpoint.mdAndDown"
        >
          <v-btn
            color="white"
            v-for="path of paths"
            :key="path.attrs.to || path.attrs.href"
            v-bind="path.attrs"
            :id="`navbar-nav-${path.label.replaceAll(/[\/\s]/g, ``)}`"
            :elevation="0"
            active-class="primary"
            :class="path.isActive?.() ? 'primary' : ''"
          >
            {{ path.label }}
          </v-btn>
        </v-card>

        <template v-if="!$vuetify.breakpoint.mdAndDown">
          <v-btn
            id="navbar-login"
            v-if="!isLoggedIn"
            @click="openLogInDialog()"
            rounded
            >Log In</v-btn
          >
          <template v-else>
            <v-menu bottom left offset-y>
              <template v-slot:activator="{ on, attrs }">
                <v-btn
                  :color="
                    $route.matched.some((p) => p.name === 'profile')
                      ? 'primary'
                      : ''
                  "
                  elevation="2"
                  rounded
                  v-bind="attrs"
                  v-on="on"
                >
                  <v-icon>mdi-account-circle</v-icon>
                  <v-icon>mdi-menu-down</v-icon>
                </v-btn>
              </template>

              <v-list class="pa-0">
                <!-- <v-list-item
                  :to="{ path: '/profile' }"
                  active-class="primary white--text"
                >
                  <v-list-item-icon class="mr-2">
                    <v-icon>mdi-account-circle</v-icon>
                  </v-list-item-icon>

                  <v-list-item-content>
                    <v-list-item-title>Account & Settings</v-list-item-title>
                  </v-list-item-content>
                </v-list-item> -->

                <!-- <v-divider></v-divider> -->

                <v-list-item id="navbar-logout" @click="logOut()">
                  <v-list-item-icon class="mr-2">
                    <v-icon>mdi-logout</v-icon>
                  </v-list-item-icon>

                  <v-list-item-content>
                    <v-list-item-title>Log Out</v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
              </v-list>
            </v-menu>
          </template>
        </template>

        <v-app-bar-nav-icon
          @click.stop="showMobileNavigation = true"
          v-if="$vuetify.breakpoint.mdAndDown"
        />
      </v-container>
    </v-app-bar>

    <v-main app>
      <v-container id="main-container">
        <v-sheet
          min-height="70vh"
          rounded
          :elevation="$route.meta.hideNavigation || $route.meta.flat ? 0 : 2"
        >
          <router-view name="content" :key="$route.fullPath" />
        </v-sheet>
      </v-container>
    </v-main>

    <v-footer class="mt-8 secondary lighten-4">
      <router-view name="footer" />
    </v-footer>

    <v-navigation-drawer
      v-if="!$route.meta.hideNavigation || $route.meta.flat"
      class="mobile-nav-items"
      v-model="showMobileNavigation"
      temporary
      app
    >
      <v-list nav dense class="nav-items">
        <v-list-item-group class="text-body-1">
          <v-list-item
            v-for="path of paths"
            @click="showMobileNavigation = false"
            :id="`drawer-nav-${path.label.replaceAll(/[\/\s]/g, ``)}`"
            :key="path.attrs.to || path.attrs.href"
            active-class="primary darken-3 white--text"
            :class="path.isActive?.() ? 'primary darken-4 white--text' : ''"
            v-bind="path.attrs"
          >
            <v-icon
              :class="path.isActive?.() ? 'white--text' : ''"
              class="mr-2"
              >{{ path.icon }}</v-icon
            >
            <span>{{ path.label }}</span>
          </v-list-item>
        </v-list-item-group>
        <v-divider class="my-4"></v-divider>

        <v-list-item-group class="text-body-1">
          <v-list-item
            id="drawer-nav-login"
            v-if="!isLoggedIn"
            @click="
              openLogInDialog();
              showMobileNavigation = false;
            "
          >
            <v-icon class="mr-2">mdi-login</v-icon>
            <span>Log In</span>
          </v-list-item>

          <template v-else>
            <!-- <v-list-item :to="{ path: '/profile' }">
              <v-icon class="mr-2">mdi-account-circle</v-icon>
              <span>Account & Settings</span>
            </v-list-item> -->

            <v-list-item id="drawer-nav-logout" @click="logOut()">
              <v-icon class="mr-2">mdi-logout</v-icon>
              <span>Log Out</span>
            </v-list-item>
          </template>
        </v-list-item-group>
      </v-list>
    </v-navigation-drawer>

    <cz-notifications />

    <v-dialog v-model="logInDialog.isActive" width="500">
      <cz-login
        @cancel="logInDialog.isActive = false"
        @logged-in="logInDialog.onLoggedIn"
      ></cz-login>
    </v-dialog>

    <link
      href="https://fonts.googleapis.com/css?family=Roboto:100,300,400,500,700,900"
      rel="stylesheet"
    />
    <link
      href="https://cdn.jsdelivr.net/npm/@mdi/font@6.x/css/materialdesignicons.min.css"
      rel="stylesheet"
    />
  </v-app>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import { APP_NAME } from "./constants";
import { CzNotifications, Notifications } from "@cznethub/cznet-vue-core";
import { Subscription } from "rxjs";
import User from "@/models/user.model";
import CzLogin from "@/components/account/cz.login.vue";
import { RawLocation } from "vue-router";
import { setupRouteGuards } from "@/router/router";

@Component({
  name: "app",
  components: { CzNotifications, CzLogin },
})
export default class App extends Vue {
  protected onOpenLogInDialog!: Subscription;
  public showMobileNavigation = false;
  protected logInDialog: any & { isActive: boolean } = {
    isActive: false,
    onLoggedIn: () => {},
    onCancel: () => {},
  };
  public paths: any[] = [
    {
      attrs: { to: "/search" },
      label: "Search",
      icon: "mdi-magnify",
    },
  ];

  protected get isLoggedIn(): boolean {
    return User.$state.isLoggedIn;
  }

  protected logOut() {
    Notifications.openDialog({
      title: "Log out?",
      content: "Are you sure you want to log out?",
      confirmText: "Log Out",
      cancelText: "Cancel",
      onConfirm: () => {
        User.logOut();
      },
    });
  }

  async created() {
    document.title = APP_NAME;

    User.fetchSchemas();
    // Guards are setup after checking authorization and loading access tokens
    // because they depend on user logged in status
    setupRouteGuards();

    this.onOpenLogInDialog = User.logInDialog$.subscribe(
      (redirectTo: RawLocation | undefined) => {
        this.logInDialog.isActive = true;

        this.logInDialog.onLoggedIn = () => {
          if (redirectTo) {
            this.$router.push(redirectTo);
          }
          this.logInDialog.isActive = false;
        };
      }
    );
  }

  beforeDestroy() {
    // Good practice
    this.onOpenLogInDialog.unsubscribe();
  }

  protected openLogInDialog() {
    User.openLogInDialog();
  }
}
</script>

<style lang="scss" scoped>
.logo {
  height: 100%;
  cursor: pointer;

  img {
    height: 100%;
  }
}

#footer {
  width: 100%;
  margin: 0;
  min-height: unset;
  margin-top: 4rem;
  box-shadow: none;
}

.v-toolbar.v-app-bar--is-scrolled > .v-toolbar__content > .container {
  align-items: center !important;
  will-change: padding;
  padding-top: 0;
  padding-bottom: 0;
}

.nav-items {
  border-radius: 2rem !important;
  overflow: hidden;

  & > a.v-btn:first-child {
    border-top-left-radius: 2rem !important;
    border-bottom-left-radius: 2rem !important;
  }

  & > a.v-btn:last-child {
    border-top-right-radius: 2rem !important;
    border-bottom-right-radius: 2rem !important;
  }

  .v-btn {
    margin: 0;
    border-radius: 0;
    height: 39px !important;
  }
}

// .nav-items .v-btn.is-active,
// .mobile-nav-items .v-list-item.is-active {
//   background-color: #1976d2 !important;
//   color: #FFF;
// }
</style>
