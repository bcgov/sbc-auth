<template>
  <div
    v-if="!!review && !!filing"
    id="extraprovincial-registration-bc"
  >
    <!-- Registration Number in B.C. -->
    <section class="section-container">
      <v-row no-gutters>
        <v-col
          cols="12"
          sm="3"
          class="pr-4"
        >
          <label>Registration Number in B.C.</label>
        </v-col>
        <v-col
          cols="12"
          sm="9"
          class="pt-4 pt-sm-0"
        >
          <div id="registration-number-bc">
            {{ identifier || '[Unknown]' }}
          </div>
        </v-col>
      </v-row>
    </section>

    <!-- Registered Name in B.C. -->
    <section class="section-container">
      <v-row no-gutters>
        <v-col
          cols="12"
          sm="3"
          class="pr-4"
        >
          <label>Registered Name in B.C.</label>
        </v-col>
        <v-col
          cols="12"
          sm="9"
          class="pt-4 pt-sm-0"
        >
          <div id="registered-name-bc">
            {{ legalName || '[Unknown]' }}
          </div>
        </v-col>
      </v-row>
    </section>

    <!-- Date of Registration in B.C. -->
    <section class="section-container">
      <v-row no-gutters>
        <v-col
          cols="12"
          sm="3"
          class="pr-4"
        >
          <label>Date of Registration in B.C.</label>
        </v-col>
        <v-col
          cols="12"
          sm="9"
          class="pt-4 pt-sm-0"
        >
          <div id="registration-date-bc">
            {{ foundingDate || '[Unknown]' }}
          </div>
        </v-col>
      </v-row>
    </section>
  </div>
</template>

<script lang="ts">
import { ContinuationFilingIF, ContinuationReviewIF } from '@/models/continuation-review'
import { computed, defineComponent, reactive } from '@vue/composition-api'
import CommonUtils from '@/util/common-util'
import moment from 'moment'

export default defineComponent({
  name: 'ExtraprovincialRegistrationBc',

  props: {
    review: { type: Object as () => ContinuationReviewIF, required: true },
    filing: { type: Object as () => ContinuationFilingIF, required: true }
  },

  setup (props) {
    const state = reactive({
      continuationIn: computed<any>(() => {
        return props.filing?.continuationIn
      }),

      identifier: computed<string>(() => {
        return state.continuationIn?.business?.identifier
      }),

      legalName: computed<string>(() => {
        return state.continuationIn?.business?.legalName
      }),

      foundingDate: computed<string>(() => {
        return strToPacificDate(state.continuationIn?.business?.foundingDate)
      })
    })

    /**
     * Converts a date-time string to a Pacific date string.
     * @example
     * Sample input: "2007-01-23T08:00:00.000+00:00".
     * Sample output: "Jan 23, 2007".
     */
    function strToPacificDate (str: string): string {
      const date = moment.utc(str).toDate()
      return CommonUtils.formatDisplayDate(date, 'MMM D, YYYY')
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
</style>
