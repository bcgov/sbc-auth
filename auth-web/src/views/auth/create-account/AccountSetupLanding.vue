<template>
  <v-container
    class="view-container"
    data-test="div-account-setup-container"
  >
    <!-- Loading status -->
    <v-fade-transition>
      <div
        v-if="isLoading"
        class="loading-container"
      >
        <v-progress-circular
          size="50"
          width="5"
          color="primary"
          :indeterminate="isLoading"
        />
      </div>
    </v-fade-transition>
    <template v-if="!isLoading">
      <component
        :is="displayComponent.component"
        :key="displayComponent.id"
        v-bind="displayComponent.props"
        v-on="displayComponent.events"
      />
    </template>
  </v-container>
</template>

<script lang="ts">
import { Action, State } from 'pinia-class'
import { Component, Prop, Vue, Watch } from 'vue-property-decorator'
import { LoginSource, Pages } from '@/util/constants'
import AccountSetupView from '@/views/auth/create-account/AccountSetupView.vue'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import NonBcscAccountSetupView from '@/views/auth/create-account/non-bcsc/NonBcscAccountSetupView.vue'
import { namespace } from 'vuex-class'
import { useUserStore } from '@/stores/user'

// Will be taken out with Vue 3.
const AuthModule = namespace('auth')

@Component
export default class AccountSetupLanding extends Vue {
  @Prop({ default: false }) skipConfirmation!: boolean
  @Prop({ default: '' }) redirectToUrl!: string

  public displayComponent: any
  public isLoading = true

  @State(useUserStore) private currentUser!: KCUserProfile
  @Action(useUserStore) private getUserAccountSettings!: () => Promise<any>

  @AuthModule.Getter('isAuthenticated') private isAuthenticated!: boolean

  // Watch property access type and update model
  @Watch('skipConfirmation')
  async onDataChange (newVal, oldVal) {
    if (newVal !== oldVal) {
      this.isLoading = true
      await this.duplicateCheck()
      this.displayComponent = await this.getComponent()
      this.isLoading = false
    }
  }
  // dynamically calculating which component o display
  // if bceid show bceid stepper else normal
  async getComponent ():Promise<any> {
    let comp: any = {
      id: 1,
      component: AccountSetupView,
      props: {
        skipConfirmation: this.skipConfirmation,
        redirectToUrl: this.redirectToUrl
      }
    }

    const isBceidUser = this.currentUser?.loginSource === LoginSource.BCEID
    if (isBceidUser) {
      comp = {
        id: 2,
        component: NonBcscAccountSetupView,
        props: {}
      }
    }
    return comp
  }

  //  tookout from AccountSetupView.vue and used here in parent
  async duplicateCheck () {
    try {
      if (this.isAuthenticated && !this.skipConfirmation) {
        const currentUserAccountSettings = await this.getUserAccountSettings()
        const hasExistingAccount = currentUserAccountSettings.length > 0
        if (hasExistingAccount) {
          let redirectUrlToDuplicateAccountWarning = this.redirectToUrl
            ? `${
              Pages.DUPLICATE_ACCOUNT_WARNING
            }?redirectToUrl=${encodeURIComponent(this.redirectToUrl)}`
            : `${Pages.DUPLICATE_ACCOUNT_WARNING}`
          this.$router.push(redirectUrlToDuplicateAccountWarning)
        }
      }
    } catch (ex) {
      // eslint-disable-next-line no-console
      console.log('error while setting up account view')
    }
  }
  async created () {
    await this.duplicateCheck()
  }

  async mounted () {
    this.displayComponent = await this.getComponent()
    this.isLoading = false
  }
}
</script>
