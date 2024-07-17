<template>
  <div id="continuation-authorization-review">
    <!-- error dialog -->
    <ModalDialog
      ref="errorDialogComponent"
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
          @click="onDialogClose(true)"
        >
          OK
        </v-btn>
      </template>
    </ModalDialog>

    <!-- loading spinner -->
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
      v-if="!!review && !!filing"
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
          icon="mdi-domain"
          label="Extraprovincial Registration in B.C."
        />
        <ExtraprovincialRegistrationBc
          :review="review"
          :filing="filing"
        />
      </v-card>

      <!-- Home Jurisdiction Information -->
      <v-card
        id="home-jurisdiction-information-vcard"
        flat
        class="mt-8"
      >
        <CardHeader
          icon="mdi-home-city-outline"
          label="Home Jurisdiction Information"
        />
        <HomeJurisdictionInformation
          :review="review"
          :filing="filing"
        />
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
        <PreviousCorrespondence
          ref="reviewResultComponent"
          class="pt-8 px-6"
          :review="review"
          :filing="filing"
          @review-result="reviewResult = $event"
          @email-body-text="emailBodyText = $event"
        />

        <v-divider class="mt-7 mx-6" />

        <ReviewResult
          ref="reviewResultComponent"
          class="py-8 px-6"
          :review="review"
          :filing="filing"
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
import { ContinuationFilingIF, ContinuationReviewIF, ReviewStatus } from '@/models/continuation-review'
import BusinessService from '@/services/business.services'
import CardHeader from '@/components/CardHeader.vue'
import { EventBus } from '@/event-bus'
import ExtraprovincialRegistrationBc
  from '@/components/auth/staff/continuation-application/ExtraprovincialRegistrationBc.vue'
import HomeJurisdictionInformation
  from '@/components/auth/staff/continuation-application/HomeJurisdictionInformation.vue'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import { Pages } from '@/util/constants'
import PreviousCorrespondence from '@/components/auth/staff/continuation-application/PreviousCorrespondence.vue'
import ReviewResult from '@/components/auth/staff/continuation-application/ReviewResult.vue'

@Component({
  components: {
    CardHeader,
    ExtraprovincialRegistrationBc,
    HomeJurisdictionInformation,
    ModalDialog,
    PreviousCorrespondence,
    ReviewResult
  }
})
export default class ContinuationAuthorizationReview extends Vue {
  $refs: {
    errorDialogComponent: InstanceType<typeof ModalDialog>
    reviewResultComponent: InstanceType<typeof ReviewResult>
  }

  /** Review ID that comes from route. */
  @Prop({ required: true }) readonly reviewId: number

  // local variables
  isLoading = false
  isSubmitting = false
  haveUnsavedChanges = false
  dialogTitle = ''
  dialogText = ''
  review = null as ContinuationReviewIF
  filing = null as ContinuationFilingIF
  reviewResult = null as ReviewStatus
  emailBodyText = ''

  /** Whether the current application is an extraprovincial Continuation In. */
  get isExpro (): boolean {
    const mode = this.filing?.continuationIn?.mode
    return (mode === 'EXPRO')
  }

  /** Whether this Continuation Authorization Review is actionable. */
  get isActionable (): boolean {
    const status = this.review?.status
    return (status === 'AWAITING_REVIEW' || status === 'RESUBMITTED')
  }

  /** Called when this page is mounted. */
  async mounted (): Promise<void> {
    let review: ContinuationReviewIF
    let filing: ContinuationFilingIF

    this.isLoading = true
    review = await BusinessService.fetchContinuationReview(this.reviewId).catch(() => null)
    if (!review) {
      // eslint-disable-next-line no-console
      console.log('Missing review =', review)
    } else if (review.filingLink) {
      filing = await BusinessService.fetchFiling(review.filingLink).catch(() => null)

      if (!filing) {
        // eslint-disable-next-line no-console
        console.log('Missing filing =', filing)
      }
    }
    this.isLoading = false

    // check for expected data
    if (review && filing) {
      // assign local properties to unblock rendering
      this.review = review
      this.filing = filing
    } else {
      // show error dialog
      this.dialogTitle = 'Unable to load review'
      this.dialogText = 'An error occurred while loading the review. Please try again.'
      this.$refs.errorDialogComponent.open()
    }
  }

  /** Called when dialog is closed. */
  onDialogClose (returnToDashboard = true): void {
    this.$refs.errorDialogComponent.close()

    if (returnToDashboard) {
      // route back to staff dashboard
      this.$router.push(Pages.STAFF_DASHBOARD)
    }
  }

  @Watch('reviewResult')
  @Watch('emailBodyText')
  onDataChanged (): void {
    if (this.reviewResult || this.emailBodyText) {
      this.haveUnsavedChanges = true
    }
  }

  /** Called when user clicks Cancel button. */
  onClickCancel (): void {
    this.haveUnsavedChanges = false
    // route back to staff dashboard
    this.$router.push(Pages.STAFF_DASHBOARD)
  }

  /** Called when user clicks Submit button. */
  async onClickSubmit (): Promise<void> {
    // check component validity
    if (!this.$refs.reviewResultComponent.validate()) return

    try {
      this.isSubmitting = true
      await BusinessService.submitContinuationReviewResult(this.review.id, this.reviewResult, this.emailBodyText)
      this.haveUnsavedChanges = false

      // route back to staff dashboard
      this.$router.push(Pages.STAFF_DASHBOARD)

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
      this.$refs.errorDialogComponent.open()
    } finally {
      this.isSubmitting = false
    }
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
