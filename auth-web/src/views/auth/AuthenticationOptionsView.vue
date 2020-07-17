<template>
  <v-container class="view-container">
    <div class="view-header flex-column mb-10">
      <h1 class="view-header__title">Log in to BC Registries</h1>
      <p class="mt-2 mb-3">Don't have a BC Registries account?
        <a class="text-decoration-underline" @click="goToCreateAccount">Create an account</a>
      </p>
    </div>
    <v-row>
      <v-col
        class="d-flex align-stretch"
        sm="12" md="6"
        v-for="authOption in authOptions"
        :key="authOption.type"
      >
        <v-card
          flat
          class="account-card text-center pa-7 d-flex flex-column"
        >
          <div class="account-type__icon mb-6 mt-2">
            <v-icon>{{authOption.icon}}</v-icon>
          </div>
          <div class="account-type__title mb-8">
            {{authOption.title}}
          </div>
          <div class="account-type__details mb-8 mx-6">
            {{authOption.description}}
          </div>
          <div class="mt-10 mb-2">
            <v-btn
              large
              depressed
              block
              color="primary"
              class="font-weight-bold"
              @click="selectAuthType(authOption.type)"
            >
              {{ authOption.btnLabel }}
            </v-btn>
          </div>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component, Mixins, Vue } from 'vue-property-decorator'
import { IdpHint, LoginSource, Pages } from '@/util/constants'
import { mapActions, mapMutations, mapState } from 'vuex'
import AccountChangeMixin from '@/components/auth/mixins/AccountChangeMixin.vue'
import AccountLoginOptionPicker from '@/components/auth/AccountLoginOptionPicker.vue'
import { Organization } from '@/models/Organization'

@Component({})
export default class AuthenticationOptionsView extends Vue {
  private authOptions = [
    {
      type: LoginSource.BCSC,
      title: 'BC Services Card',
      description: `Residents of British Columbia can use their government-issued 
                    BC Services Card to securly access BC Registries.`,
      icon: 'mdi-smart-card-outline',
      btnLabel: 'Log in with BC Services Card'
    },
    {
      type: LoginSource.BCEID,
      title: 'BCeID',
      description: `Non-BC residents and residents do not have a BC Services Card 
                    can use a BCeID account to securly access BC Registries.`,
      icon: 'mdi-two-factor-authentication',
      btnLabel: 'Log in with BCeID'
    }
  ]

  private selectAuthType (type:string) {
    switch (type) {
      case LoginSource.BCSC:
        this.$router.push(`/${Pages.SIGNIN}/${IdpHint.BCSC}`)
        break
      case LoginSource.BCEID:
        this.$router.push(`/${Pages.SIGNIN}/${IdpHint.BCEID}`)
        break
    }
  }

  private goToCreateAccount () {
    this.$router.push(`/${Pages.CHOOSE_AUTH_METHOD}`)
  }
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';

.view-container {
  max-width: 60rem;
}

.save-btn.disabled {
  pointer-events: none;
}

.save-btn__label {
  padding-left: 0.2rem;
  padding-right: 0.2rem;
}

.change-account-link {
  font-size: 0.875rem;
}

.account-card {
  .account-type__icon {
    .v-icon {
      font-size: 4rem;
      color: var(--v-primary-base) !important;
    }
  }
  .account-type__title {
    font-size: 1.5rem;
    font-weight: 600;
  }
}
</style>
