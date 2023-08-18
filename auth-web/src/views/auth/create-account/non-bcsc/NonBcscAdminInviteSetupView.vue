<template>
  <v-container class="view-container">
    <header class="d-flex flex-column mb-10">
      <v-icon
        class="align-start mb-6"
        color="primary"
        x-large
      >
        mdi-information-outline
      </v-icon>
      <h1
        class="text-center"
        data-test="title"
      >
        Verify your identity by a notarized affidavit
      </h1>
    </header>
    <v-card
      data-test="nonbcsc-admin-invite-flow"
      max-width="1028"
      class="mx-auto"
    >
      <v-container class="wrapper">
        <v-card-title
          data-test="dialog-header"
          class="pa-0"
        >
          <h2 class="mb-3">
            {{ getStepTitle }}
          </h2>
        </v-card-title>
        <v-card-text class="pa-0">
          <!-- Step 1: upload affidavit-->
          <upload-affidavit-step
            v-if="currentStep === 1"
            :isAffidavitUpload="true"
            @emit-admin-affidavit-complete="goToNextStep"
          />
          <!-- Step 2: upload user profile -->
          <user-profile-form
            v-if="currentStep === 2"
            :isAffidavitUpload="true"
            @emit-admin-profile-previous-step="goBackPreviousStep"
            @emit-admin-profile-complete="goToNextStep"
          />
        </v-card-text>
      </v-container>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { Component, Mixins, Prop } from 'vue-property-decorator'
import NextPageMixin from '@/components/auth/mixins/NextPageMixin.vue'
import UploadAffidavitStep from '@/components/auth/create-account/non-bcsc/UploadAffidavitStep.vue'
import { User } from '@/models/user'
import UserProfileForm from '@/components/auth/create-account/UserProfileForm.vue'
import { namespace } from 'vuex-class'

const UserModule = namespace('user')

@Component({
  components: {
    UploadAffidavitStep,
    UserProfileForm
  }
})
export default class NonBcscAdminInviteSetupView extends Mixins(NextPageMixin) {
  @Prop({ default: undefined }) private readonly orgId: number // org id used for bceid re-upload
  @Prop() token: string
  @UserModule.Action('createAffidavit') private createAffidavit!: () => User

  currentStep: number = 1

  public async goToNextStep () {
    // Update currentstep
    if (!this.isLastStep) {
      this.currentStep++
    } else {
      // save all trh details and mark invitation as accepted
      //  user details will be saved from userprofile before emitting this event
      // redirect to confirmtoken will set invitation accepted
      await this.createAffidavit()
      // if no token then it will re-upload
      if (this.token) {
        this.$router.push('/confirmtoken/' + this.token)
      } else if (this.orgId) {
        this.$store.commit('updateHeader')
        this.$router.push(this.getNextPageUrl())
      }
    }
  }

  public goBackPreviousStep (): void {
    // Update currentstep to previous step
    if (!this.isFirstStep) {
      this.currentStep--
    }
  }

  get isFirstStep (): boolean {
    return this.currentStep === 1
  }

  get isLastStep (): boolean {
    // Currently, there are two steps in the flow, can be updated in the future
    return this.currentStep === 2
  }

  get getStepTitle (): string {
    switch (this.currentStep) {
      case 1:
        return 'Upload Your Notarized Affidavit'
      case 2:
        return 'User Profile'
      default:
        return ''
    }
  }
}
</script>

<style lang="scss" scoped>
  @import "$assets/scss/theme.scss";
  .wrapper {
    padding: 3.125rem 2.5rem !important;
  }
</style>
