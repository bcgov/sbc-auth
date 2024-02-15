<template>
  <v-container class="terms-of-use-container view-container">
    <h1 class="mb-10">
      Business Pre-Authorized Debit Terms and Conditions Agreement BC Registries and Online Services
    </h1>
    <v-card flat>
      <v-card-text class="pa-8">
        <TermsOfUse
          :tosType="'termsofuse_pad'"
        />
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import TermsOfUse from '@/components/auth/common/TermsOfUse.vue'
import { defineComponent } from '@vue/composition-api'

export default defineComponent({
  name: 'PADTermsAndConditionsView',
  components: {
    TermsOfUse
  }
})
</script>

<style lang="scss" scoped>
  .terms-of-use-container {
    max-width: 65rem;
  }

  // TODO: Payor Authoriztion section of the PAD Terms does not apply in this content so we don't display it
  // TODO: Better strategy to show/hide this content VS hacking it out with styling
  ::v-deep {
    section:last-child {
      display: none;
    }
  }

</style>
