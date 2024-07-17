<template>
  <div id="continuation-authorization-review">
    <!-- error dialog -->
    <ModalDialog
      ref="errorDialogComponent"
      :isPersistent="true"
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
          @click="onDialogClose()"
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
          class="pt-8 px-6"
          :review="review"
          :filing="filing"
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
import { ContinuationFilingIF, ContinuationReviewIF, ReviewStatus } from '@/models/continuation-review'
import { defineComponent, onMounted, reactive, ref, toRefs, watch } from '@vue/composition-api'
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

export default defineComponent({
  name: 'ContinuationAuthorizationReview',

  components: {
    CardHeader,
    ExtraprovincialRegistrationBc,
    HomeJurisdictionInformation,
    ModalDialog,
    PreviousCorrespondence,
    ReviewResult
  },

  props: {
    /** Review id that comes from route. */
    reviewId: { type: String, required: true }
  },

  setup (props) {
    // refs
    const errorDialogComponent: InstanceType<typeof ModalDialog> = ref(null)
    const reviewResultComponent: InstanceType<typeof ReviewResult> = ref(null)

    const state = reactive({
      // local properties
      isLoading: false,
      isSubmitting: false,
      haveUnsavedChanges: false,
      dialogTitle: '',
      dialogText: '',
      review: null as ContinuationReviewIF,
      filing: null as ContinuationFilingIF,
      reviewResult: null as ReviewStatus,
      emailBodyText: '',

      /** Whether the current application is an extraprovincial Continuation In. */
      get isExpro (): boolean {
        const mode = this.filing?.continuationIn?.mode
        return (mode === 'EXPRO')
      },

      /** Whether this Continuation Authorization Review is actionable. */
      get isActionable (): boolean {
        const status = this.review?.status
        return (status === 'AWAITING_REVIEW' || status === 'RESUBMITTED')
      }
    })

    /** Called when dialog is closed. */
    function onDialogClose (): void {
      const value = errorDialogComponent.value as any; value.close()

      if (!state.haveUnsavedChanges) {
        // route back to staff dashboard
        this.$router.push(Pages.STAFF_DASHBOARD)
      }
    }

    /** Called when user clicks Cancel button. */
    function onClickCancel (): void {
      state.haveUnsavedChanges = false
      // route back to staff dashboard
      this.$router.push(Pages.STAFF_DASHBOARD)
    }

    /** Called when user clicks Submit button. */
    async function onClickSubmit (): Promise<void> {
      // check component validity
      if (!(reviewResultComponent as any).value.validate()) return

      try {
        state.isSubmitting = true
        await BusinessService.submitContinuationReviewResult(state.review.id, state.reviewResult, state.emailBodyText)
        state.haveUnsavedChanges = false

        // route back to staff dashboard
        this.$router.push(Pages.STAFF_DASHBOARD)

        // indicate success via toast (snackbar) on main page
        EventBus.$emit('show-toast', {
          message: 'Review submitted successfully',
          type: 'primary',
          timeout: 3000
        })
      } catch (error) {
        console.log(`Error submitting review = ${error}`) // eslint-disable-line no-console

        // show error dialog
        state.dialogTitle = 'Unable to submit review'
        state.dialogText = 'An error occurred while submitting the review. Please try again.'
        const v = errorDialogComponent.value as any; v.open()
      } finally {
        state.isSubmitting = false
      }
    }

    watch(() => state.reviewResult, () => {
      if (state.reviewResult) state.haveUnsavedChanges = true
    })

    watch(() => state.emailBodyText, () => {
      if (state.emailBodyText) state.haveUnsavedChanges = true
    })

    onMounted(async () => {
      let review: ContinuationReviewIF
      let filing: ContinuationFilingIF

      state.isLoading = true
      review = await BusinessService.fetchContinuationReview(+props.reviewId).catch(() => null)
      if (!review) {
        console.log(`Failed to fetch review # ${props.reviewId}`) // eslint-disable-line no-console
      } else if (review.filingLink) {
        filing = await BusinessService.fetchFiling(review.filingLink).catch(() => null)

        if (!filing) {
          console.log(`Failed to fetch filing for review = ${review}`) // eslint-disable-line no-console
        }
      }
      state.isLoading = false

      // check for expected data
      if (review && filing) {
        // assign local properties to unblock rendering
        state.review = review
        state.filing = filing
      } else {
        // show error dialog
        state.dialogTitle = 'Unable to load review'
        state.dialogText = 'An error occurred while loading the review. Please try again.'
        const v = errorDialogComponent.value as any; v.open()
      }
    })

    return {
      errorDialogComponent,
      reviewResultComponent,
      onDialogClose,
      onClickCancel,
      onClickSubmit,
      ...toRefs(state)
    }
  }
})
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
