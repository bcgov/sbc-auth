<template>
  <v-container class="view-container">
    <v-row justify="center">
      <v-col class="text-center">
        <div class="mt-5 mb-10 font-weight-bold">
          <h1>BC Registries Account Login</h1>
        </div>
        <v-card
          class="mx-auto"
          max-width="460"
        >
          <v-card-title>
            <v-img
              max-height="260"
              src="@/assets/img/BCReg_Generic_Login_image.jpg"
              alt="Generic Login Image">
            </v-img>
          </v-card-title>
          <v-card-text >
            <v-menu>
              <template v-slot:activator="{ on }">
                <v-btn
                  large
                  color="bcgovblue"
                  class="white--text font-weight-bold"
                  aria-label="log in"
                  id="loginBtn"
                  v-on="on">
                  <span>Log in to my BC Registries Account</span>
                  <v-icon class="mr-n1 ml-2">mdi-menu-down</v-icon>
                </v-btn>
              </template>
              <sbc-auth-menu :redirect-on-login-success="bookmarkPath" />
            </v-menu>
            <div class="mb-12"></div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component } from 'vue-property-decorator'
import SbcAuthMenu from 'sbc-common-components/src/components/SbcAuthMenu.vue'
import Vue from 'vue'

@Component({
  components: {
    SbcAuthMenu
  }
})
export default class BookmarkLoginView extends Vue {
  mounted () {
  }

  /** The route bookmarkPath. */
  get bookmarkPath (): string {
    return `${this.$route.query.bookmarkPath}`
  }
}
</script>

<style lang="scss" scoped>
  @import "$assets/scss/theme.scss";
</style>
