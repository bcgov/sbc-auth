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
                  :disabled="isFormDisabled"
                />
              </v-row>

              <v-row>
                <v-col class="col-6 col-sm-3 font-weight-bold">
                  CAS Supplier Number
                </v-col>
                <v-text-field
                  v-model.trim="casSupplierNum"
                  hint="This number should be created in CAS before issuing a refund"
                  filled
                  label="CAS Supplier Number"
                  persistent-hint
                  data-test="casSupplierNumber"
                  :rules="casSupplierNumRules"
                  :disabled="isFormDisabled"
                />
              </v-row>

              <v-row>
                <v-col class="col-6 col-sm-3 font-weight-bold">
                  Email
                </v-col>
                <v-text-field
                  v-model.trim="email"
                  hint="The email provided in the client's Direct Deposit Application form"
                  filled
                  label="Email"
                  persistent-hint
                  data-test="email"
                  :rules="emailRules"
                  :disabled="isFormDisabled"
                />
              </v-row>

              <v-row>
                <v-col class="col-6 col-sm-3 font-weight-bold">
                  Reason for Refund
                </v-col>
                <v-text-field
                  v-model.trim="staffComment"
                  filled
                  label="Reason for Refund"
                  persistent-hint
                  data-test="staffComment"
                  :rules="staffCommentRules"
                  :disabled="isFormDisabled"
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
            data-test="btn-edit-cancel"
            :disabled="isLoading"
            @click="handleCancelButton"
          >
            <span>Cancel</span>
          </v-btn>
          <v-btn
            large
            :color="buttonColor"
            class="px-8 font-weight-bold"
            data-test="btn-edit-done"
            :disabled="!isFormValid || isFormDisabled"
            @click="submitRefundRequest"
          >
            <span v-if="!isLoading">{{ buttonText }}</span>
            <v-progress-circular
              v-else
              indeterminate
              color="white"
              size="24"
            />
          </v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, ref, toRefs, watch } from '@vue/composition-api'
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
      isLoading: false,
      refundAmountRules: [
        v => !!v || 'Refund Amount is required',
        v => parseFloat(v) > 0 || 'Refund Amount must be greater than zero',
        v => parseFloat(v) <= parseFloat(props.shortNameDetails?.creditsRemaining) || 'Amount must be less than unsettled amount on short name',
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
        v => !!v || 'Reason for Refund is required',
        v => (v.length < 500) || 'Cannot exceed 500 characters'
      ],
      isSubmitted: false
    })

    const refundForm = ref(null)
    const isFormValid = ref(false)
    const buttonText = ref('Submit Refund Request')
    const buttonColor = ref('primary')

    function handleCancelButton () {
      root.$router?.push({
        name: 'shortnamedetails'
      })
    }

    async function submitRefundRequest () {
      state.isLoading = true
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
          state.isLoading = false
          // 2-second delay before navigating away
          await new Promise(resolve => setTimeout(resolve, 2000)) // 2-second delay
          handleCancelButton()
        } catch (error) {
          state.isSubmitted = false
          buttonText.value = 'Failed'
          buttonColor.value = 'red'
        } finally {
          state.isLoading = false
        }
      } else {
        state.isLoading = false
      }
    }

    const isFormDisabled = computed(() => {
      return state.isSubmitted || state.isLoading
    })

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
      isFormDisabled,
      isFormValid,
      submitRefundRequest,
      buttonText,
      buttonColor,
      handleCancelButton
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
