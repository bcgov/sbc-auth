import { AccessType } from '@/util/constants'
<template>
  <div>
    <p class="mb-6">
      Please ensure your pre-authorized debit account has the funds available to avoid failed payments in the future.
    </p>
    <v-row>
      <v-col>
        <h4 class="mb-3">
          Payment Method
        </h4>
        <v-card
          outlined
          flat
          class="payment-info-card"
        >
          <v-card-text>
            <div>
              You will have to pay your balance by
              <strong>Credit Card</strong>
            </div>
            <div>to unlock your account immediately.</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    <v-row class="mb-12">
      <v-col>
        <v-checkbox
          v-model="isAcknowledged"
          color="primary"
          class="auth-checkbox align-checkbox-label--top"
        >
          <template #label>
            I understand that this is a one time use credit card and will cover future transactions with pre-authorized debit.
          </template>
        </v-checkbox>
      </v-col>
    </v-row>
    <v-divider />
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
          <v-icon
            left
            class="mr-2 ml-n2"
          >
            mdi-arrow-left
          </v-icon>
          <span>Back</span>
        </v-btn>
        <v-spacer />
        <v-btn
          large
          color="primary"
          class="proceed-btn font-weight-bold"
          :disabled="!isAcknowledged"
          @click="proceedToPayment"
        >
          Proceed
        </v-btn>
      </v-col>
    </v-row>
  </div>
</template>

<script lang="ts">
import { Component, Emit, Mixins } from 'vue-property-decorator'
import { Organization } from '@/models/Organization'
import Steppable from '@/components/auth/common/stepper/Steppable.vue'
import { mapState } from 'vuex'

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

  @Emit('final-step-action')
  private async proceedToPayment () {
  }

  private goBack () {
    this.stepBack()
  }
}
</script>

<style lang="scss" scoped>
@import "$assets/scss/theme.scss";

  .payment-info-card {
    max-width: 55ch;
    border-color: var(--v-primary-base) !important;
    border-width: 2px !important;
  }

  .auth-checkbox {
    max-width: 70ch;
  }

  .align-checkbox-label--top {
      ::v-deep {
        .v-input__slot {
          align-items: flex-start;
        }
      }
    }

  .v-input--checkbox {
    color: var(--v-grey-darken4) !important;
  }

  ::v-deep {
    .v-input--checkbox .v-label {
      color: var(--v-grey-darken4) !important;
    }
  }
</style>
