<template>
  <div id="continuation-authorization-review">
    <!-- error dialog -->
    <ModalDialog
      ref="errorDialog"
      :title="dialogTitle"
      :text="dialogText"
      dialog-class="notify-dialog"
      max-width="640"
    >
      <template #icon>
        <v-icon
          large
          color="error"
        >
          mdi-alert-circle-outline
        </v-icon>
      </template>
      <template #actions>
        <v-btn
          large
          color="error"
          data-test="dialog-ok-button"
          @click="$refs.errorDialog.close()"
        >
          OK
        </v-btn>
      </template>
    </ModalDialog>

    <!-- spinner -->
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

    <v-container
      v-if="!!continuationReview"
      class="view-container"
    >
      <div class="view-header mb-0">
        <h1 class="view-header__title">
          Continuation Authorization Review
        </h1>
      </div>

      <!-- Extraprovincial Registration in B.C. -->
      <v-card
        v-if="isExpro"
        id="extraprovincial-registration-bc-vcard"
        flat
        class="mt-8"
      >
        <CardHeader
          icon="mdi-home-city-outline"
          label="Extraprovincial Registration in B.C."
        />
        <ExtraprovincialRegistrationBc :continuationReview="continuationReview" />
      </v-card>

      <!-- Home Jurisdiction Information -->
      <v-card
        id="home-jurisdiction-information-vcard"
        flat
        class="mt-8"
      >
        <CardHeader
          icon="mdi-domain"
          label="Home Jurisdiction Information"
        />
        <HomeJurisdictionInformation :continuationReview="continuationReview" />
      </v-card>

      <!-- Continuation Authorization Review Result -->
      <h2 class="mt-8">
        Continuation Authorization Review Result
      </h2>
      <v-card
        id="continuation-authorization-review-result-vcard"
        flat
        class="mt-6"
      >
        <ContinuationAuthorizationReviewResult
          ref="reviewResult"
          :continuationReview="continuationReview"
          @review-result="reviewResult = $event"
          @email-body-text="emailBodyText = $event"
        />
      </v-card>
    </v-container>

    <div
      v-if="isActionable"
      id="actions-wrapper"
      class="d-flex justify-end px-6 py-8"
    >
      <v-btn
        class="cancel-btn px-6 font-size-15"
        large
        outlined
        color="primary"
        :disabled="isSubmitting"
        @click="onClickCancel()"
      >
        <span>Cancel</span>
      </v-btn>

      <v-btn
        class="submit-btn px-6 font-size-15 ml-3"
        large
        color="primary"
        :disabled="isSubmitting"
        :loading="isSubmitting"
        @click="onClickSubmit()"
      >
        <span>Submit</span>
        <v-icon>mdi-chevron-right</v-icon>
      </v-btn>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue, Watch } from 'vue-property-decorator'
import { ContinuationReviewIF, ContinuationReviewStatus } from '@/models/continuation-review'
import BusinessService from '@/services/business.services'
import CardHeader from '@/components/CardHeader.vue'
import ContinuationAuthorizationReviewResult
  from '@/components/auth/staff/continuation-application/ContinuationAuthorizationReviewResult.vue'
import { EventBus } from '@/event-bus'
import ExtraprovincialRegistrationBc
  from '@/components/auth/staff/continuation-application/ExtraprovincialRegistrationBc.vue'
import HomeJurisdictionInformation
  from '@/components/auth/staff/continuation-application/HomeJurisdictionInformation.vue'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import { Pages } from '@/util/constants'

@Component({
  components: {
    CardHeader,
    ContinuationAuthorizationReviewResult,
    ExtraprovincialRegistrationBc,
    HomeJurisdictionInformation,
    ModalDialog
  }
})
export default class ContinuationAuthorizationReview extends Vue {
  $refs: {
    errorDialog: InstanceType<typeof ModalDialog>
    reviewResult: InstanceType<typeof ContinuationAuthorizationReviewResult>
  }

  /** Review ID that comes from route. */
  @Prop({ required: true }) readonly reviewId: number

  // local variables
  isLoading = false
  haveUnsavedChanges = false
  dialogTitle = ''
  dialogText = ''
  continuationReview = null as ContinuationReviewIF
  reviewResult = null as ContinuationReviewStatus
  emailBodyText = ''
  isSubmitting = false

  /** Whether the current application is an extraprovincial continuation in. */
  get isExpro (): boolean {
    const mode = this.continuationReview?.filing?.continuationIn?.mode
    return (mode === 'EXPRO')
  }

  /** Whether this authorization review is actionable. */
  get isActionable (): boolean {
    const status = this.continuationReview?.review?.status
    return (status === 'AWAITING_REVIEW' || status === 'RESUBMITTED')
  }

  async mounted (): Promise<void> {
    this.isLoading = true
    this.continuationReview = await BusinessService.fetchContinuationReview(this.reviewId).catch(() => null)
    this.isLoading = false

    // check for expected data
    const review = this.continuationReview?.review
    const results = this.continuationReview?.results
    const filing = this.continuationReview?.filing

    if (!review || !results || !filing) {
      // eslint-disable-next-line no-console
      console.log(`Missing data for Continuation Review ${this.reviewId} = ${this.continuationReview}`)

      // show error dialog
      this.dialogTitle = 'Unable to fetch review'
      this.dialogText = 'An error occurred while fetching the review. Please try again.'
      this.$refs.errorDialog.open()
    }
  }

  @Watch('reviewResult')
  @Watch('emailBodyText')
  onDataChanged (): void {
    if (this.reviewResult || this.emailBodyText) {
      this.haveUnsavedChanges = true
    }
  }

  onClickCancel (): void {
    this.haveUnsavedChanges = false
    this.$router.push(Pages.STAFF_DASHBOARD)
  }

  async onClickSubmit (): Promise<void> {
    if (!this.$refs.reviewResult.validate()) return

    try {
      this.isSubmitting = true
      await BusinessService.saveContinuationReviewResult(this.reviewResult, this.emailBodyText)
      this.haveUnsavedChanges = false

      // indicate success via toast (snackbar) on main page
      EventBus.$emit('show-toast', {
        message: 'Review submitted successfully',
        type: 'primary',
        timeout: 3000
      })
    } catch (error) {
      // eslint-disable-line no-console
      console.log(`Error submitting review = ${error}`)

      // show error dialog
      this.dialogTitle = 'Unable to submit review'
      this.dialogText = 'An error occurred while submitting the review. Please try again.'
      this.$refs.errorDialog.open()
    } finally {
      this.isSubmitting = false
    }

    // if submit succeeded, route back to staff dashboard
    if (!this.haveUnsavedChanges) this.$router.push(Pages.STAFF_DASHBOARD)
  }

  /** Intercepts route change (but not page unloads). */
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  async beforeRouteLeave (to, from, next): Promise<void> {
    if (this.haveUnsavedChanges) {
      alert('You have unsaved changes. Please cancel or submit this review instead.')
    } else {
      next()
    }
  }
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';

// add whitespace to the right of the container
@media (min-width: 960px) {
  .view-container {
    padding-right: 5rem;
  }
}

@media (min-width: 1264px) {
  .view-container {
    padding-right: 10rem;
  }
}

@media (min-width: 1360px) {
  .view-container {
    padding-right: 20rem;
  }
}

h2 {
  font-size: $px-18;
}

#actions-wrapper {
  background-color: $BCgovInputBG;
}

.font-size-15 {
  font-size: $px-15 !important;
}
</style>
