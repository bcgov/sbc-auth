<template>
  <section
    v-if="!!review && !!filing"
    id="previous-correspondence"
    class="section-container"
  >
    <v-row no-gutters>
      <v-col
        cols="12"
        sm="3"
        class="pr-4"
      >
        <label class="font-weight-bold">Previous Correspondence</label>
      </v-col>

      <v-col
        id="correspondences"
        cols="12"
        sm="9"
        class="pt-4 pt-sm-0"
      >
        <div
          v-for="(item, index) in correspondences"
          :key="index"
        >
          <label
            class="font-weight-bold"
            :for="`textarea-${index}`"
            v-html="item.label"
          />

          <textarea
            v-if="item.body"
            :id="`textarea-${index}`"
            v-auto-resize
            class="mt-4"
            readonly
            rows="1"
            :value="item.body"
          />

          <v-divider
            v-if="(index + 1) < correspondences.length"
            class="my-6"
          />
        </div>
      </v-col>
    </v-row>
  </section>
</template>

<script lang="ts">
import { ContinuationFilingIF, ContinuationReviewIF, ReviewStatus } from '@/models/continuation-review'
import { computed, defineComponent, reactive } from '@vue/composition-api'
import AutoResize from 'vue-auto-resize'
import CommonUtils from '@/util/common-util'
import moment from 'moment'

export default defineComponent({
  name: 'PreviousCorrespondence',

  directives: { AutoResize },

  props: {
    review: { type: Object as () => ContinuationReviewIF, required: true },
    filing: { type: Object as () => ContinuationFilingIF, required: true }
  },

  setup (props) {
    const state = reactive({
      /** The list of correspondence items. */
      correspondences: computed<Array<any>>(() => {
        if (!props.review) return [] // safety check

        const list = []

        // always add initial submission
        // get date and user from review object
        list.push({
          label: `${strToPacificDateTime(props.review.creationDate)} &mdash; ` +
            `Application Submitted &mdash; ${props.review.completingParty}`,
          body: ''
        })

        // add items according to review results
        props.review.results.forEach((result) => {
          // did staff request a change?
          if (result.status === ReviewStatus.CHANGE_REQUESTED) {
            list.push({
              label: `${strToPacificDateTime(result.creationDate)} &mdash; ` +
                `Change Requested &mdash; ${result.reviewer}`,
              body: result.comments
            })

            // did user resubmit?
            // get date from result object; don't display user
            if (result.submissionDate) {
              list.push({
                label: `${strToPacificDateTime(result.submissionDate)} &mdash; ` +
                  'Application Resubmitted',
                body: ''
              })
            }
          }

          // did staff approve the review?
          if (result.status === ReviewStatus.APPROVED) {
            list.push({
              label: `${strToPacificDateTime(result.creationDate)} &mdash; ` +
                `Application Approved &mdash; ${result.reviewer}`,
              body: result.comments
            })
          }

          // did staff reject the review?
          if (result.status === ReviewStatus.REJECTED) {
            list.push({
              label: `${strToPacificDateTime(result.creationDate)} &mdash; ` +
                `Application Rejected &mdash; ${result.reviewer}`,
              body: result.comments
            })
          }
        })

        return list
      })
    })

    /**
     * Converts a date-time string to a Pacific date-time string.
     * Sample input: "2024-06-04T04:20:00+00:00".
     * Sample output: "Jun 3, 2024 at 9:20 pm Pacific Time".
     */
    function strToPacificDateTime (str: string): string {
      const date = moment.utc(str).toDate()
      return CommonUtils.formatDisplayDate(date, 'MMM D, YYYY [at] h:mm a [Pacific Time]')
    }

    return {
      ...state
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

// reduce top whitespace for all articles except first one
section:not(:first-child) {
  padding-top: 1.5rem;
}

// clear bottom whitespace for all articles except last one
section:not(:last-child) {
  padding-bottom: 0;
}

.col-sm-9 {
  font-size: $px-15;
}

#correspondences {
  max-height: 32rem !important;
  overflow: hidden auto;
}

textarea {
  width: 100%;
  resize: none;
  // FUTURE: use field-sizing instead of "v-auto-resize" directive
  // ref: https://developer.mozilla.org/en-US/docs/Web/CSS/field-sizing
  // field-sizing: content;
}
</style>
