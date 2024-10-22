<template>
  <div
    v-if="!!review && !!filing"
    id="registered-office-contact"
  >
    <!-- Registered Office Contact Information -->
    <section class="section-container">
      <v-row no-gutters>
        <!-- First Column: Contact Information Label -->
        <v-col
          cols="12"
          sm="4"
        >
          <label>Contact Information</label>
        </v-col>
        <!-- Second Column: Email Address Label and Value -->
        <v-col
          cols="12"
          sm="4"
        >
          <label>Email Address</label>
          <div>{{ email || '[Unknown]' }}</div>
        </v-col>
        <!-- Third Column: Phone Number Label and Value -->
        <v-col
          cols="12"
          sm="4"
        >
          <label>Phone Number</label>
          <div>{{ phone || '[Unknown]' }}</div>
        </v-col>
      </v-row>
    </section>
  </div>
</template>

<script lang="ts">
import { ContinuationFilingIF, ContinuationReviewIF } from '@/models/continuation-review'
import { computed, defineComponent, reactive } from '@vue/composition-api'

export default defineComponent({
  name: 'RegisteredOfficeContact',

  props: {
    review: { type: Object as () => ContinuationReviewIF, required: true },
    filing: { type: Object as () => ContinuationFilingIF, required: true }
  },

  setup (props) {
    const state = reactive({
      continuationIn: computed<any>(() => {
        return props.filing?.continuationIn
      }),

      email: computed<string>(() => {
        return state.continuationIn?.parties[0]?.officer?.email
      }),

      phone: computed<string>(() => {
        return state.continuationIn?.parties[0]?.officer?.phone
      })
    })

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
  </style>
