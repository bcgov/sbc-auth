<template>
  <section
    v-if="!!review && !!filing"
    id="review-result"
    class="section-container"
  >
    <v-row no-gutters>
      <v-col
        cols="12"
        sm="3"
        class="pr-4"
      >
        <label class="font-weight-bold">Authorization Review</label>
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
            label="Authorization Decision"
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
import { ContinuationFilingIF, ContinuationReviewIF, ReviewStatus } from '@/models/continuation-review'
import { computed, defineComponent, reactive, ref, toRefs, watch } from '@vue/composition-api'

type VuetifyRuleFunction = (v: any) => boolean | string

export default defineComponent({
  name: 'ReviewResult',

  props: {
    review: { type: Object as () => ContinuationReviewIF, required: true },
    filing: { type: Object as () => ContinuationFilingIF, required: true }
  },

  setup () {
    // refs
    const form: InstanceType<typeof HTMLFormElement> = ref(null)

    const state = reactive({
      // local properties
      reviewResult: null as ReviewStatus,
      reviewResultItems: [
        { desc: 'Approve', code: ReviewStatus.APPROVED },
        { desc: 'Request Change', code: ReviewStatus.CHANGE_REQUESTED },
        { desc: 'Reject', code: ReviewStatus.REJECTED }
      ],
      emailBodyText: '',

      /** Whether the email body text is required. */
      isEmailBodyTextRequired: computed<boolean>(() => {
        return (
          state.reviewResult === ReviewStatus.CHANGE_REQUESTED ||
          state.reviewResult === ReviewStatus.REJECTED
        )
      }),

      /** The email body text label. */
      emailBodyTextLabel: computed<string>(() => {
        return state.isEmailBodyTextRequired
          ? 'Email Body Text (Required)'
          : 'Email Body Text (Optional)'
      }),

      /** The review result rules. */
      reviewResultRules: computed<Array<VuetifyRuleFunction>>(() => {
        return [
          (v: string) => !!v || 'A review result is required'
        ]
      }),

      /** The email body text rules. */
      emailBodyTextRules: computed<Array<VuetifyRuleFunction>>(() => {
        return [
          () =>
            !state.isEmailBodyTextRequired ||
            (state.emailBodyText.trim().length > 0) ||
            'Email body text is required'
        ]
      })
    })

    /**
     * Called externally to validate the form.
     * @returns True if valid, else False
     */
    function validate (): boolean {
      return form.value.validate()
    }

    /** When a new Review Result is selected, resets validation to clear any visual errors. */
    watch(() => state.reviewResult, () => {
      form.value.resetValidation()
    })

    return {
      form,
      validate,
      ...toRefs(state)
    }
  }
})
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
