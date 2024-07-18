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
      <v-form
        ref="refundForm"
        v-model="isFormValid"
      >
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
            @click="handleCancelOrBack"
          >
            <span>{{ backButtonLabel }}</span>
          </v-btn>
          <v-btn
            large
            :color="buttonColor"
            class="px-8 font-weight-bold"
            data-test="btn-edit-routing-done"
            :disabled="!isFormValid || isSubmitted"
            @click="submitRefundRequest"
          >
            <span>{{ buttonText }}</span>
          </v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, reactive, ref, toRefs, watch } from '@vue/composition-api'
import { EftRefundRequest } from '@/models/refund'
import { useOrgStore } from '@/stores/org'

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
    },
    shortNameId: {
      type: Number,
      default: undefined
    }
  },
  setup (props, { root }) {
    const state = reactive({
      refundAmount: undefined,
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
      orgStore: useOrgStore(),
      staffCommentRules: [
        v => (v.length < 500) || 'Cannot exceed 500 characters'
      ],
      isSubmitted: false
    })

    const refundForm = ref(null)
    const isFormValid = ref(false)
    const buttonText = ref('Submit Refund Request')
    const buttonColor = ref('primary')
    const backButtonLabel = ref('Cancel')

    function handleCancelOrBack () {
      if (backButtonLabel.value === 'Cancel') {
        clearForm()
      } else {
        root.$router?.push({
          name: 'shortnamedetails',
          query: {
            shortNameId: props.shortNameDetails.id
          }
        })
      }
    }

    function clearForm () {
      state.refundAmount = undefined
      state.casSupplierNum = ''
      state.email = ''
      state.staffComment = ''
      refundForm.value.resetValidation()
      state.isSubmitted = false
      buttonText.value = 'Submit Refund Request'
      buttonColor.value = 'primary'
      backButtonLabel.value = 'Cancel'
    }

    async function submitRefundRequest () {
      if (refundForm.value.validate()) {
        const refundPayload: EftRefundRequest = {
          shortNameId: props.shortNameDetails.id,
          refundAmount: state.refundAmount,
          casSupplierNum: state.casSupplierNum,
          refundEmail: state.email,
          comment: state.staffComment,
          shortName: props.shortNameDetails.shortName
        }
        try {
          await state.orgStore.refundEFT(refundPayload)
          state.isSubmitted = true
          buttonText.value = 'Approved'
          buttonColor.value = 'green'
          backButtonLabel.value = 'Back'
        } catch (error) {
          state.isSubmitted = false
          buttonText.value = 'Failed'
          buttonColor.value = 'red'
        }
      }
    }

    watch(() => state.isSubmitted, (newVal) => {
      if (newVal) {
        buttonText.value = 'Approved'
        buttonColor.value = 'green'
      } else {
        buttonText.value = 'Submit Refund Request'
        buttonColor.value = 'primary'
      }
    })

    return {
      ...toRefs(state),
      refundForm,
      isFormValid,
      clearForm,
      submitRefundRequest,
      buttonText,
      buttonColor,
      backButtonLabel,
      handleCancelOrBack
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
