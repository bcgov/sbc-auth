<template>
  <div
    v-if="!!continuationIn"
    id="continuation-authorization-review-result"
  >
    <!-- Previous Correspondence -->
    <section class="section-container">
      <v-row no-gutters>
        <v-col
          cols="12"
          sm="3"
          class="pr-4"
        >
          <label>Previous Correspondence</label>
        </v-col>

        <v-col
          id="previous-correspondence"
          cols="12"
          sm="9"
          class="pt-4 pt-sm-0"
        >
          <!--
            FUTURE: implement this (ticket #22072)
          -->

          <!-- User Submission -->
          <div>
            <p class="ma-0 font-weight-bold">
              June 2, 2024 at 1:30 pm Pacific time &mdash; User Submission
            </p>
          </div>

          <v-divider class="my-6" />

          <!-- Change Requested -->
          <div>
            <p class="ma-0 font-weight-bold">
              June 3, 2024 at 11:45 am Pacific time &mdash; Change Requested &mdash; Staffanie Stafford
            </p>

            <p class="mt-4 mb-0">
              Thank you for submitting your application and the accompanying files.
            </p>
            <p class="mt-4 mb-0">
              Please review the following items of concern with your application:
            </p>
            <p class="mt-4 mb-0">
              We found that some of the uploaded files are not legible. Please re-upload the following
              document(s): Home Jurisdiction Authorization.
            </p>
            <p class="mt-4 mb-0">
              You can update your application by visiting [your application].
            </p>
          </div>

          <v-divider class="my-6 " />

          <!-- User Resubmission -->
          <div>
            <p class="ma-0 font-weight-bold">
              June 3, 2024 at 9:20 pm Pacific time &mdash; User Resubmission
            </p>
          </div>
        </v-col>
      </v-row>
    </section>

    <v-divider class="my-6 mx-6" />

    <!-- Review Result -->
    <section
      v-if="isActionable"
      class="section-container pt-0"
    >
      <v-row no-gutters>
        <v-col
          cols="12"
          sm="3"
          class="pr-4"
        >
          <label>Review Result</label>
        </v-col>

        <v-col
          cols="12"
          sm="9"
          class="pt-4 pt-sm-0"
        >
          <v-form
            ref="form"
            lazy-validation
            @submit.prevent
          >
            <v-select
              v-model="reviewResult"
              filled
              :items="reviewResultItems"
              item-text="desc"
              item-value="code"
              label="Review Result"
              :rules="reviewResultRules"
              :menu-props="{ offsetY: true }"
              @change="$emit('review-result', reviewResult)"
            />

            <v-textarea
              v-model.trim="emailBodyText"
              class="mb-n2"
              filled
              maxlength="2000"
              counter="2000"
              :label="emailBodyTextLabel"
              :rules="emailBodyTextRules"
              @change="$emit('email-body-text', emailBodyText)"
            />
          </v-form>
        </v-col>
      </v-row>
    </section>
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import { ContinuationReviewFilingIF, ContinuationReviewIF, ContinuationReviewStatus }
  from '@/models/continuation-review'
// import DateUtils from '@/util/date-utils'

type VuetifyRuleFunction = (v: any) => boolean | string

@Component({})
export default class ContinuationAuthorizationReviewResult extends Vue {
  $refs: {
    form: HTMLFormElement
  }

  /** Continuation Review object that comes from parent component. */
  @Prop({ required: true }) readonly continuationReview: ContinuationReviewIF

  // local variables
  reviewResult = null as ContinuationReviewStatus
  reviewResultItems = [
    { desc: 'Authorization Accepted', code: ContinuationReviewStatus.ACCEPTED },
    { desc: 'Request Change', code: ContinuationReviewStatus.CHANGE_REQUESTED },
    { desc: 'Rejected', code: ContinuationReviewStatus.REJECTED }
  ]
  emailBodyText = ''

  /** The continuation in filing object. */
  get continuationIn (): ContinuationReviewFilingIF {
    return this.continuationReview?.filing?.continuationIn
  }

  /** Whether this authorization review is actionable. */
  get isActionable (): boolean {
    const status = this.continuationReview?.review?.status
    return (
      status === ContinuationReviewStatus.AWAITING_REVIEW ||
      status === ContinuationReviewStatus.RESUBMITTED
    )
  }

  /** Whether this email body text is required. */
  get isEmailBodyTextRequired (): boolean {
    return (
      this.reviewResult === ContinuationReviewStatus.CHANGE_REQUESTED ||
      this.reviewResult === ContinuationReviewStatus.REJECTED
    )
  }

  /** The email body text label. */
  get emailBodyTextLabel (): string {
    return this.isEmailBodyTextRequired
      ? 'Email Body Text (Required)'
      : 'Email Body Text (Optional)'
  }

  /** The review result rules. */
  get reviewResultRules (): Array<VuetifyRuleFunction> {
    return [
      (v: string) => !!v || 'A review result is required'
    ]
  }

  /** The email body text rules. */
  get emailBodyTextRules (): Array<VuetifyRuleFunction> {
    return [
      () =>
        !this.isEmailBodyTextRequired ||
        (this.emailBodyText.trim().length > 0) ||
        'Email body text is required'
    ]
  }

  /**
   * Called externally to validate the form.
   * @returns True if valid, else False
   */
  public validate (): boolean {
    return this.$refs.form.validate()
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

.section-container {
  font-size: $px-16;
  color: $gray7;
  padding: 2rem 1.5rem;

  label {
    color: $gray9;
    font-weight: bold;
  }
}

// reduce top whitespace for all articles except first one
section:not(:first-child) {
  padding-top: 1.5rem;
}

// clear bottom whitespace for all articles except last one
section:not(:last-child) {
  padding-bottom: 0;
}

#previous-correspondence {
  max-height: 25rem;
  overflow: hidden auto;
}

.col-sm-9 {
  font-size: $px-15;
}

// unset overflow to show descenders (eg, "g")
::v-deep .v-text-field .v-select__selection {
  overflow: unset !important;
}
</style>
