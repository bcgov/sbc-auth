<template>
  <v-container
    id="shortname-details"
    class="view-container"
  >
    <div class="view-header flex-column">
      <h1 class="view-header__title">
        Refund Information
      </h1>
    </div>
    <v-card class="pl-5 py-2 mt-5 pr-5">
      <v-form ref="refundForm" v-model="isFormValid">
        <v-card-text>
          <v-row no-gutters>
            <v-col class="col-12 col-sm-12 ">
              <v-row>
                <v-col class="col-6 col-sm-3 font-weight-bold">
                  Short Name
                </v-col>
                <v-col class="pl-0">
                  {{ shortNameDetails.shortName }}
                </v-col>
              </v-row>

              <v-row>
                <v-col class="col-6 col-sm-3 font-weight-bold">
                  Unsettled Amount on Short Name
                </v-col>
                <v-col class="pl-0">
                  {{ unsettledAmount }}
                </v-col>
              </v-row>

              <v-row>
                <v-col class="col-6 col-sm-3 font-weight-bold">
                  Refund Amount
                </v-col>
                <v-text-field
                  v-model.trim="refundAmount"
                  filled
                  label="Refund Amount"
                  persistent-hint
                  data-test="refundAmount"
                  :rules="refundAmountRules"
                />
              </v-row>

              <v-row>
                <v-col class="col-6 col-sm-3 font-weight-bold">
                  CAS Supplier Number
                </v-col>
                <v-text-field
                  v-model.trim="casSupplierNum"
                  filled
                  label="CAS Supplier Number"
                  persistent-hint
                  data-test="casSupplierNumber"
                  :rules="casSupplierNumRules"
                />
              </v-row>

              <v-row>
                <v-col class="col-6 col-sm-3 font-weight-bold">
                  Email
                </v-col>
                <v-text-field
                  v-model.trim="email"
                  filled
                  label="Email"
                  persistent-hint
                  data-test="email"
                  :rules="emailRules"
                />
              </v-row>

              <v-row>
                <v-col class="col-6 col-sm-3 font-weight-bold">
                  Staff Comment
                </v-col>
                <v-text-field
                  v-model.trim="staffComment"
                  filled
                  label="Staff Comment (Optional)"
                  persistent-hint
                  data-test="staffComment"
                  :rules="staffCommentRules"
                />
              </v-row>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions class="pr-4 justify-end pa-3 pb-5">
          <v-btn
            large
            outlined
            class="px-7"
            color="primary"
            data-test="btn-edit-routing-cancel"
            @click="clearForm"
          >
            <span>Cancel</span>
          </v-btn>
          <v-btn
            large
            color="primary"
            class="px-8 font-weight-bold"
            data-test="btn-edit-routing-done"
            :disabled="!isFormValid"
            @click="submitRefundRequest"
          >
            <span>Submit Refund Request</span>
          </v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, reactive, ref, toRefs } from '@vue/composition-api'

export default defineComponent({
  name: 'ShortNameRefundView',
  props: {
    shortNameDetails: {
      type: Object,
      default: () => ({
        shortName: ''
      })
    },
    unsettledAmount: {
      type: String,
      default: ''
    }
  },
  emits: ['submit-refund-request'],
  setup (props, { emit }) {
    const state = reactive({
      refundAmount: '',
      casSupplierNum: '',
      email: '',
      staffComment: '',
      refundAmountRules: [
        v => !!v || 'Refund Amount is required',
        v => parseFloat(v) < parseFloat(props.shortNameDetails?.creditsRemaining) || 'Amount must be less than unsettled amount on short name',
        v => /^\d+(\.\d{1,2})?$/.test(v) || 'Amounts must be less than 2 decimal places'
      ],
      casSupplierNumRules: [
        v => !!v || 'CAS Supplier Number is required'
      ],
      emailRules: [
        v => !!v || 'Email is required',
        v => {
          const pattern = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
          return pattern.test(v) || 'Valid email is required'
        }
      ],
      staffCommentRules: [
        v => (v.length < 500) || 'Cannot exceed 500 characters'
      ]
    })

    const refundForm = ref(null)
    const isFormValid = ref(false)

    const clearForm = () => {
      state.refundAmount = ''
      state.casSupplierNum = ''
      state.email = ''
      state.staffComment = ''
      refundForm.value.resetValidation()
    }

    const submitRefundRequest = () => {
      if (refundForm.value.validate()) {
        emit('submit-refund-request', {
          refundAmount: state.refundAmount,
          casSupplierNum: state.casSupplierNum,
          email: state.email,
          staffComment: state.staffComment
        })
      }
    }

    return {
      ...toRefs(state),
      refundForm,
      isFormValid,
      clearForm,
      submitRefundRequest
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';
.account-alert-inner {
  .v-icon {
    color: $app-alert-orange;
  }
  background-color: $BCgovGold0 !important;
  display: flex;
  flex-direction: row;
  align-items: flex-start;
}
.account-alert__info {
  flex: 1 1 auto;
}
</style>
