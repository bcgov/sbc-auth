import { AccessType } from '@/util/constants'
<template>
  <div>
    <p class="mb-6">
      Please monitor your pre-authorized debit account balance availability to avoid future non-sufficient funds.
    </p>
    <v-row class="mb-5">
      <v-col md="7">
        <h4 class="mb-3">Payment Method</h4>
        <v-card
          outlined
          flat
          class="payment-info-card"
        >
          <v-card-text>
            <div>You will have to pay your balance by
              <strong>Credit Card</strong>
            </div>
            <div>to unlock your account immediately.</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <v-checkbox
          class="acknowledge-checkbox"
          v-model="isAcknowledged"
        >
          <template v-slot:label>
            I understand that this is a one time use credit card and will cover future transactions with pre-authorized debit.
          </template>
        </v-checkbox>
      </v-col>
    </v-row>
    <v-divider></v-divider>
    <v-row>
      <v-col
        cols="12"
        class="mt-5 pb-0 d-inline-flex"
      >
        <v-btn
          large
          depressed
          color="default"
          @click="goBack"
        >
          <v-icon left class="mr-2 ml-n2">mdi-arrow-left</v-icon>
          <span>Back</span>
        </v-btn>
        <v-spacer></v-spacer>
        <v-btn
          large
          color="primary"
          @click="proceed"
          class="proceed-btn"
          :disabled="!isAcknowledged"
        >
          Proceed
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
export default class PaymentReview extends Mixins(Steppable) {
  private readonly currentOrganization!: Organization
  private isAcknowledged: boolean = false

  private proceed () {
    // proceed final step
  }

  private goBack () {
    this.stepBack()
  }
}
</script>

<style lang="scss" scoped>
@import "$assets/scss/theme.scss";

.payment-info-card {
  border-color: #1976d2 !important;
  border-width: 2px !important;
  .v-card__text {
    color: #000 !important;
  }
}

.acknowledge-checkbox {
  ::v-deep {
    .v-input__slot {
      align-items: flex-start;
    }
  }
}
</style>
