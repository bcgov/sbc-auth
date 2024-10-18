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
                  Type
                </v-col>
                <v-col class="pl-0">
                  {{ getShortNameTypeDescription(shortNameDetails.shortNameType) }}
                </v-col>
              </v-row>

              <v-row v-if="!readOnly">
                <v-col class="col-6 col-sm-3 font-weight-bold">
                  Unsettled Amount on Short Name
                </v-col>
                <v-col class="pl-0">
                  {{ formatCurrency(Number(shortNameDetails.creditsRemaining)) }}
                </v-col>
              </v-row>

              <v-row>
                <v-col class="col-6 col-sm-3 font-weight-bold">
                  Refund Amount
                </v-col>
                <v-col
                  v-if="readOnly"
                  class="pl-0"
                >
                  {{ formatCurrency(Number(refundDetails.refundAmount)) }}
                </v-col>
                <v-text-field
                  v-else
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
                <v-col
                  v-if="readOnly"
                  class="pl-0"
                >
                  {{ refundDetails.casSupplierNumber }}
                </v-col>
                <v-text-field
                  v-else
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
                <v-col
                  v-if="readOnly"
                  class="pl-0"
                >
                  {{ refundDetails.refundEmail }}
                </v-col>
                <v-text-field
                  v-else
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

              <v-row v-if="!readOnly">
                <v-col class="col-6 col-sm-3 font-weight-bold">
                  Reason for Refund
                </v-col>
                <v-col
                  v-if="readOnly"
                  class="pl-0"
                >
                  {{ refundDetails.comment }}
                </v-col>
                <v-text-field
                  v-else
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
          <v-row v-if="readOnly">
            <v-col class="col-6 col-sm-3 font-weight-bold">
              Requested By Qualified Receiver
            </v-col>
            <v-col class="pl-0">
              {{ refundDetails.createdBy }} {{ formatDate(refundDetails.createdOn, dateDisplayFormat) }}
            </v-col>
          </v-row>
          <v-row v-if="readOnly">
            <v-col class="col-6 col-sm-3 font-weight-bold">
              Qualified Receiver Comment
            </v-col>
            <v-col class="pl-0">
              {{ refundDetails.comment }}
            </v-col>
          </v-row>
          <v-row v-if="readOnly && isApproved()">
            <v-col class="col-6 col-sm-3 font-weight-bold">
              Approved By Expense Authority
            </v-col>
            <v-col class="pl-0">
              {{ refundDetails.updatedBy }} {{ formatDate(refundDetails.updatedOn, dateDisplayFormat) }}
            </v-col>
          </v-row>
          <v-row v-if="readOnly">
            <v-col class="col-6 col-sm-3 font-weight-bold">
              Refund Status
            </v-col>
            <v-col class="pl-0">
              {{ getEFTRefundTypeDescription(refundDetails.status) }}
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions
          v-if="!readOnly"
          class="pr-4 justify-end pa-3 pb-5"
        >
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
import { EFTRefund, ShortNameDetails } from '@/models/pay/short-name'
import { computed, defineComponent, onMounted, reactive, ref, toRefs, watch } from '@vue/composition-api'
import CommonUtils from '@/util/common-util'
import { EFTRefundType } from '@/util/constants'
import { EftRefundRequest } from '@/models/refund'
import PaymentService from '@/services/payment.services'
import ShortNameUtils from '@/util/short-name-utils'
import { useOrgStore } from '@/stores/org'

export default defineComponent({
  name: 'ShortNameRefundView',
  props: {
    shortNameId: {
      type: Number,
      default: undefined
    },
    eftRefundId: {
      type: Number,
      default: undefined
    }
  },
  setup (props, { root }) {
    const dateDisplayFormat = 'MMM DD, YYYY h:mm A [Pacific Time]'
    const state = reactive({
      shortNameDetails: {} as ShortNameDetails,
      refundDetails: {} as EFTRefund,
      refundAmount: undefined,
      casSupplierNum: '',
      email: '',
      staffComment: '',
      isLoading: false,
      readOnly: false,
      refundAmountRules: [
        v => !!v || 'Refund Amount is required',
        v => parseFloat(v) > 0 || 'Refund Amount must be greater than zero',
        v => parseFloat(v) <= parseFloat(state.shortNameDetails?.creditsRemaining) || 'Amount must be less than unsettled amount on short name',
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

    function isApproved () {
      return state.refundDetails?.status === EFTRefundType.APPROVED
    }

    onMounted(async () => {
      await loadShortnameDetails()
      if (props.shortNameId && props.eftRefundId) {
        state.readOnly = true
        await loadShortnameRefund()
      }
    })

    async function loadShortnameDetails (): Promise<void> {
      try {
        const response = await PaymentService.getEFTShortnameSummary(props.shortNameId)
        if (response?.data) {
          state.shortNameDetails = response.data['items'][0]
        } else {
          throw new Error('No response from getEFTShortname')
        }
      } catch (error) {
        // eslint-disable-next-line no-console
        console.error('Failed to getEFTShortname.', error)
      }
    }

    async function loadShortnameRefund (): Promise<void> {
      try {
        const response = await PaymentService.getEFTRefund(props.eftRefundId)
        if (response?.data) {
          state.refundDetails = response.data[0]
        } else {
          throw new Error('No response from getEFTRefund')
        }
      } catch (error) {
        // eslint-disable-next-line no-console
        console.error('Failed to getEFTRefund.', error)
      }
    }

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
          shortNameId: state.shortNameDetails.id,
          refundAmount: state.refundAmount,
          casSupplierNum: state.casSupplierNum,
          refundEmail: state.email,
          comment: state.staffComment
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
      isApproved,
      refundForm,
      isFormDisabled,
      isFormValid,
      submitRefundRequest,
      buttonText,
      buttonColor,
      handleCancelButton,
      getShortNameTypeDescription: ShortNameUtils.getShortNameTypeDescription,
      getEFTRefundTypeDescription: ShortNameUtils.getEFTRefundTypeDescription,
      formatCurrency: CommonUtils.formatAmount,
      formatDate: CommonUtils.formatUtcToPacificDate,
      dateDisplayFormat
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
