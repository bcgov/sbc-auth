import { AccessType } from '@/util/constants'
<template>
  <div>
    <p class="mb-1">Account has been suspended for outstanding balance.</p>
    <p class="mb-4">To unlock your account please complete the following steps</p>
    <v-row class="mb-12 pb-12">
      <v-col md="7">
        <v-card
          outlined
          flat
          class="suspended-info-card"
        >
          <v-card-text>
            <div class="mb-1">Your account has been suspended from:
              <strong>DD-MM-YYY</strong>
            </div>
            <div>Due to the following amount:
              <strong>$118.50</strong>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    <v-divider></v-divider>
    <v-row>
      <v-col
        cols="12"
        class="mt-5 pb-0 d-inline-flex"
      >
        <v-btn
          text
          link
          color="primary"
          class="download-pdf-btn"
          @click="downloadTransactionPDF"
        >
          Download transaction invoice in PDF
        </v-btn>
        <v-spacer></v-spacer>
        <v-btn
          large
          color="primary"
          @click="stepForward"
        >
          <span>Next</span>
          <v-icon class="ml-2">mdi-arrow-right</v-icon>
        </v-btn>
      </v-col>
    </v-row>
  </div>
</template>

<script lang="ts">
import { Component, Mixins, Prop } from 'vue-property-decorator'
import { mapMutations, mapState } from 'vuex'
import { Organization } from '@/models/Organization'
import Steppable from '@/components/auth/common/stepper/Steppable.vue'

@Component({
  computed: {
    ...mapState('org', [
      'currentOrganization'
    ])
  }
})
export default class AccountOverview extends Mixins(Steppable) {
  private readonly currentOrganization!: Organization

  private downloadTransactionPDF () {
    // download PDF
  }
}
</script>

<style lang="scss" scoped>
@import "$assets/scss/theme.scss";

.suspended-info-card {
  border-color: $BCgovInputError !important;
  border-width: 2px !important;
  .v-card__text {
    color: #000 !important;
  }
}

.download-pdf-btn {
  padding: 8px 0px !important;
  text-decoration: underline;
}
</style>
