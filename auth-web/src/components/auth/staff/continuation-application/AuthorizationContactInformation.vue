<template>
  <div
    v-if="!!filing"
    id="authorization-contact-information"
  >
    <!-- Authorization Contact Information -->
    <section class="section-container">
      <v-row no-gutters>
        <!-- First Column: Contact Information Label -->
        <v-col
          cols="12"
          sm="3"
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
          <div>{{ phone || '(Not entered)' }}</div>
        </v-col>
      </v-row>
    </section>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, reactive } from '@vue/composition-api'
import { ContinuationFilingIF } from '@/models/continuation-review'

export default defineComponent({
  name: 'AuthorizationContactInformation',

  props: {
    filing: { type: Object as () => ContinuationFilingIF, required: true }
  },

  setup (props) {
    const state = reactive({
      continuationIn: computed<any>(() => {
        return props.filing.continuationIn
      }),

      email: computed<string>(() => {
        return state.continuationIn?.contactPoint?.email
      }),

      phone: computed<string>(() => {
        return state.continuationIn?.contactPoint?.phone
      })
    })

    return {
      ...state
    }
  }
})
</script>

  <style lang="scss" scoped>
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
