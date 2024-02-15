<template>
  <v-container class="view-container">
    <v-row justify="center">
      <v-col
        cols="12"
        lg="6"
        class="text-center"
      >
        <v-icon
          size="48"
          color="error"
          class="mb-6"
        >
          mdi-information-outline
        </v-icon>
        <h1 class="mb-5">
          Not Authorized
        </h1>
        <p class="mb-9">
          {{ errorMessage }}
        </p>
        <div>
          <v-btn
            large
            color="primary"
            @click="navigate('termsofuse')"
          >
            Terms of Use
          </v-btn>
          <v-btn
            large
            color="default"
            class="ml-4"
            @click="navigate('logout')"
          >
            Log out
          </v-btn>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { LoginSource, Pages } from '@/util/constants'
import { defineComponent, onMounted, reactive } from '@vue/composition-api'
import ConfigHelper from '@/util/config-helper'
import { useUserStore } from '@/stores/user'

export default defineComponent({
  name: 'UnauthorizedView',
  setup (props, { root }) {
    const userStore = useUserStore()

    const state = reactive({
      errorMessage: ''
    })

    onMounted(() => {
      state.errorMessage = root.$t('dirSearchUnauthorizedMsg').toString()
    })

    function navigate (page) {
      switch (page) {
        case 'termsofuse':
          root.$router.push(`/${Pages.USER_PROFILE_TERMS}`)
          break
        case 'logout':
          if (userStore.currentUser?.loginSource === LoginSource.BCROS) {
            let redirectUrl = `${ConfigHelper.getSelfURL()}/signin/bcros/`
            root.$router.push(`/${Pages.SIGNOUT}/${encodeURIComponent(redirectUrl)}`)
          } else {
            root.$router.push(`/${Pages.SIGNOUT}`)
          }
          break
      }
    }

    return {
      navigate
    }
  }
})
</script>

<style lang="scss" scoped>
  @import "$assets/scss/theme.scss";

  .v-btn {
    width: 8rem;
  }

  .v-btn.primary {
    font-weight: 700;
  }
</style>
