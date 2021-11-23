<template>
  <v-container class="view-container">
    <header class="d-flex flex-column mb-10">
      <v-icon class="align-start mb-6" color="primary" x-large>mdi-information-outline</v-icon>
      <h1 class="text-center" data-test="title">Verify your identity by a notarized affidavit</h1>
    </header>
    <v-card data-test="nonbcsc-admin-invite-flow" max-width="1028" class="mx-auto">
      <v-container class="wrapper">
        <v-card-title data-test="dialog-header" class="pa-0">
          <h2 class="mb-3">{{ getStepTitle }}</h2>
        </v-card-title>
        <v-card-text class="pa-0">
          <!-- Step 1: upload affidavit-->
          <upload-affidavit-step v-if="currentStep === 1" :isAdminAffidavitMode="true"
            @emit-admin-affidavit-complete="goToNextStep">
          </upload-affidavit-step>
          <!-- Step 2: upload user profile -->
          <user-profile-form  v-if="currentStep === 2" :isAdminAffidavitMode="true"
            @emit-admin-profile-previous-step="goBackPreviousStep"
            @emit-admin-profile-complete="goToNextStep">
          </user-profile-form>
        </v-card-text>
      </v-container>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import UploadAffidavitStep from '@/components/auth/create-account/non-bcsc/UploadAffidavitStep.vue'
import UserProfileForm from '@/components/auth/create-account/UserProfileForm.vue'

@Component({
  components: {
    UploadAffidavitStep,
    UserProfileForm
  }
})
export default class NonBcscAdminInviteSetupView extends Vue {
  @Prop({ default: undefined }) private readonly orgId: number; // org id used for bceid re-upload
  private currentStep: number = 1

  public goToNextStep (): void {
    // Update currentstep
    if (!this.isLastStep) {
      this.currentStep++
    } else {
      // TODO: add submit action
    }
  }

  public goBackPreviousStep (): void {
    // Update currentstep to previous step
    if (!this.isFirstStep) {
      this.currentStep--
    }
  }

  private get isFirstStep (): boolean {
    return this.currentStep === 1
  }

  private get isLastStep (): boolean {
    // Currently, there are two steps in the flow, can be updated in the future
    return this.currentStep === 2
  }

  private get getStepTitle (): string {
    switch (this.currentStep) {
      case 1:
        return 'Upload Your Notarized Affidavit'
      case 2:
        return 'User Profile'
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
