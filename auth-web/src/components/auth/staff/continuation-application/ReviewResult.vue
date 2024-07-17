<template>
  <section
    v-if="!!review && !!filing && isActionable"
    id="review-result"
    class="section-container"
  >
    <v-row no-gutters>
      <v-col
        cols="12"
        sm="3"
        class="pr-4"
      >
        <label class="font-weight-bold">Review Result</label>
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
</template>

<script lang="ts">
import { Component, Prop, Vue, Watch } from 'vue-property-decorator'
import { ContinuationFilingIF, ContinuationReviewIF, ReviewStatus } from '@/models/continuation-review'

type VuetifyRuleFunction = (v: any) => boolean | string

@Component({})
export default class ReviewResult extends Vue {
  $refs: {
    form: HTMLFormElement
  }

  @Prop({ required: true }) readonly review: ContinuationReviewIF
  @Prop({ required: true }) readonly filing: ContinuationFilingIF

  // local variables
  reviewResult = null as ReviewStatus
  readonly reviewResultItems = [
    { desc: 'Approve', code: ReviewStatus.APPROVED },
    { desc: 'Request Change', code: ReviewStatus.CHANGE_REQUESTED },
    { desc: 'Reject', code: ReviewStatus.REJECTED }
  ]
  emailBodyText = ''

  /** Whether this Continuation Authorization Review is actionable. */
  get isActionable (): boolean {
    const status = this.review?.status
    return (
      status === ReviewStatus.AWAITING_REVIEW ||
      status === ReviewStatus.RESUBMITTED
    )
  }

  /** Whether the email body text is required. */
  get isEmailBodyTextRequired (): boolean {
    return (
      this.reviewResult === ReviewStatus.CHANGE_REQUESTED ||
      this.reviewResult === ReviewStatus.REJECTED
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

  /** When a new Review Result is selected, resets validation to clear any visual errors. */
  @Watch('reviewResult')
  private onReviewResultChanged (): void {
    this.$refs.form.resetValidation()
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

.section-container {
  font-size: $px-16;
  color: $gray7;
  // padding: 2rem 1.5rem;

  label {
    color: $gray9;
    // font-weight: bold;
  }
}

.col-sm-9 {
  font-size: $px-15;
}

// unset overflow to show descenders (eg, "g")
::v-deep .v-text-field .v-select__selection {
  overflow: unset !important;
}
</style>
