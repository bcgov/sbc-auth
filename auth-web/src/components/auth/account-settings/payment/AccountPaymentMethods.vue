<template>
  <div>
    <PaymentMethods
      v-if="selectedPaymentMethod"
      :currentOrgType="savedOrganizationType"
      :currentOrganization="currentOrganization"
      :currentOrgPaymentType="currentOrgPaymentType"
      :currentSelectedPaymentMethod="selectedPaymentMethod"
      :isChangeView="true"
      :isAcknowledgeNeeded="isAcknowledgeNeeded"
      :isEditing="isEditing"
      isTouchedUpdate="true"
      :isInitialTOSAccepted="isTOSandAcknowledgeCompleted"
      :isInitialAcknowledged="isTOSandAcknowledgeCompleted"
      :isBcolAdmin="isBcolAdmin"
      @payment-method-selected="setSelectedPayment"
      @get-PAD-info="getPADInfo"
      @emit-bcol-info="setBcolInfo"
      @is-pad-valid="isPADValid"
      @is-ejv-valid="isEJVValid"
      @cancel="cancel"
      @save="save"
    />
    <v-slide-y-transition>
      <div
        v-show="errorMessage"
        class="pb-2"
      >
        <v-alert
          type="error"
          icon="mdi-alert-circle-outline"
          data-test="alert-bcol-error"
        >
          {{ errorMessage }}
        </v-alert>
      </div>
    </v-slide-y-transition>
    <v-divider class="my-10" />
    <div
      v-if="isEditing"
      class="form__btns d-flex"
    >
      <v-btn
        large
        class="save-btn"
        :class="{ 'disabled': isBtnSaved }"
        :color="isBtnSaved ? 'success' : 'primary'"
        :disabled="isDisableSaveBtn"
        :loading="isLoading"
        @click="save"
      >
        <v-expand-x-transition>
          <v-icon v-show="isBtnSaved">
            mdi-check
          </v-icon>
        </v-expand-x-transition>
        <span class="save-btn__label">{{ (isBtnSaved) ? 'Saved' : 'Save' }}</span>
      </v-btn>
      <v-btn
        large
        depressed
        data-test="cancel-button"
        class="cancel-button ml-2"
        @click="cancel"
      >
        Cancel
      </v-btn>
    </div>
    <!-- Alert Dialog (Error) -->
    <ModalDialog
      ref="errorDialog"
      :title="errorTitle"
      :text="errorText"
      dialog-class="notify-dialog"
      max-width="640"
    >
      <template #icon>
        <v-icon
          large
          color="error"
        >
          mdi-alert-circle-outline
        </v-icon>
      </template>
      <template #actions>
        <v-btn
          large
          color="primary"
          class="font-weight-bold"
          @click="closeError"
        >
          OK
        </v-btn>
      </template>
    </ModalDialog>
  </div>
</template>

<script lang="ts">
import { AccessType, Account, LoginSource, Pages, PaymentTypes, Permission, Role } from '@/util/constants'
import {
  CreateRequestBody, Member, MembershipType, OrgPaymentDetails, Organization, PADInfo, PADInfoValidation
} from '@/models/Organization'
import { computed, defineComponent, onMounted, reactive, ref, toRefs, watch } from '@vue/composition-api'
import { BcolProfile } from '@/models/bcol'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import PaymentMethods from '@/components/auth/common/PaymentMethods.vue'
import { StatementNotificationSettings } from '@/models/statement'
import { useAccount } from '@/composables/account-factory'
import { useOrgStore } from '@/stores/org'
import { useUserStore } from '@/stores/user'

export default defineComponent({
  name: 'AccountPaymentMethods',
  components: {
    PaymentMethods,
    ModalDialog
  },
  props: {
    hasPaymentChanged: {
      type: Boolean,
      default: false
    },
    isEditing: {
      type: Boolean,
      default: false
    }
  },
  emits: ['emit-bcol-info'],
  setup (props, { emit, root }) {
    const orgStore = useOrgStore()
    const userStore = useUserStore()

    const state = reactive({
      savedOrganizationType: '',
      selectedPaymentMethod: '',
      padInfo: {} as PADInfo,
      isBtnSaved: props.hasPaymentChanged,
      disableSaveBtn: false,
      errorMessage: '',
      errorTitle: 'Payment Update Failed',
      bcolInfo: {} as BcolProfile,
      errorText: '',
      isLoading: false,
      padValid: false,
      ejvValid: false,
      paymentMethodChanged: props.hasPaymentChanged,
      isFuturePaymentMethodAvailable: false, // set true if in between 3 days cooling period
      isTOSandAcknowledgeCompleted: false, // set true if TOS already accepted
      activeOrgMembers: computed<Member[]>(() => orgStore.activeOrgMembers),
      currentOrganization: computed<Organization>(() => orgStore.currentOrganization)
    })

    const errorDialog = ref<InstanceType<typeof ModalDialog>>()

    const { currentOrganization, currentOrgPaymentType, currentOrgAddress, currentMembership, permissions, currentOrgGLInfo } = useAccount()

    const currentUser = computed(() => userStore.currentUser)
    const isBcolAdmin = currentUser.value.roles?.includes(Role.BcolStaffAdmin)

    function setSelectedPayment (payment) {
      state.errorMessage = ''
      state.selectedPaymentMethod = payment.selectedPaymentMethod
      state.isBtnSaved = (state.isBtnSaved && !payment.isTouched) || false
      state.paymentMethodChanged = payment.isTouched || false
    }

    function isPadSelectedAndInvalid () {
      return state.selectedPaymentMethod === PaymentTypes.PAD && !state.padValid
    }

    function isEjvSelectedAndInvalid () {
      return state.selectedPaymentMethod === PaymentTypes.EJV && !state.ejvValid
    }

    function paymentMethodNotChangedAndNotEjv () {
      return !isBcolAdmin && !state.paymentMethodChanged && state.selectedPaymentMethod !== PaymentTypes.EJV
    }

    const isDisableSaveBtn = computed(() => {
      if (state.isBtnSaved) {
        return false
      }

      return isPadSelectedAndInvalid() ||
            isEjvSelectedAndInvalid() ||
            paymentMethodNotChangedAndNotEjv() ||
            disableSaveButtonForBCOL()
    })

    function disableSaveButtonForBCOL () {
      return (state.selectedPaymentMethod === PaymentTypes.BCOL &&
             (state.bcolInfo?.password === undefined || state.bcolInfo?.password === ''))
    }

    function getPADInfo (padInfoValue: PADInfo) {
      state.padInfo = padInfoValue
    }

    function isPADValid (isValid) {
      state.padValid = isValid
    }

    function isEJVValid (isValid) {
      state.ejvValid = isValid
      if (state.isBtnSaved) {
        state.isBtnSaved = false
      }
    }

    const isAcknowledgeNeeded = computed(() => {
      // isAcknowledgeNeeded should show if isFuturePaymentMethodAvailable (3 days cooling period)
      return (state.selectedPaymentMethod !== currentOrgPaymentType.value || state.isFuturePaymentMethodAvailable)
    })

    const isPaymentViewAllowed = computed(() => {
      // checking permission instead of roles to give access for staff
      return [Permission.VIEW_PAYMENT_METHODS, Permission.MAKE_PAYMENT].some(per => permissions.value.includes(per))
    })

    async function initialize () {
      state.errorMessage = ''
      state.bcolInfo = {} as BcolProfile
      // check if address info is complete if not redirect user to address page
      const isNotAnonUser = currentUser.value?.loginSource !== LoginSource.BCROS
      if (isNotAnonUser) {
        // do it only if address is not already fetched.Or else try to fetch from DB
        if (!currentOrgAddress.value || Object.keys(currentOrgAddress.value).length === 0) {
          // sync and try again
          await orgStore.syncAddress()
          if (!currentOrgAddress.value || Object.keys(currentOrgAddress.value).length === 0) {
            await root.$router.push(`/${Pages.MAIN}/${currentOrganization.value.id}/settings/account-info`)
            return
          }
        }
      }

      if (isPaymentViewAllowed.value) {
        state.savedOrganizationType =
        ((currentOrganization.value?.orgType === Account.PREMIUM) &&
          !currentOrganization.value?.bcolAccountId && currentOrganization.value?.accessType !== AccessType.GOVM)
          ? Account.UNLINKED_PREMIUM : currentOrganization.value.orgType
        const orgPayments: OrgPaymentDetails = await orgStore.getOrgPayments()
        // setting flag for futurePaymentMethod and TOS to show content and TOS checkbox
        state.isFuturePaymentMethodAvailable = !!orgPayments.futurePaymentMethod || false
        state.isTOSandAcknowledgeCompleted = orgPayments.padTosAcceptedBy !== null || false
        state.selectedPaymentMethod = currentOrgPaymentType.value || ''

        // Rare cases where GOVN account has payment switched from PAD to BCOL in the backend
        if (currentOrganization.value.accessType === AccessType.GOVN && orgPayments.paymentMethod === PaymentTypes.BCOL) {
          state.savedOrganizationType = currentOrganization.value.orgType
        }
      } else {
        // if the account switching happening when the user is already in the transaction page,
        // redirect to account info if its a basic account
        await root.$router.push(`/${Pages.MAIN}/${currentOrganization.value.id}/settings/account-info`)
      }
    }

    async function verifyPAD () {
      const verifyPad: PADInfoValidation = await orgStore.validatePADInfo()
      if (!verifyPad || verifyPad?.isValid) {
        // proceed to update payment even if the response is empty or valid account info
        return true
      } else {
        state.isLoading = false
        state.errorText = 'Bank information validation failed'
        if (verifyPad?.message?.length) {
          let msgList = ''
          verifyPad.message.forEach((msg) => {
            msgList += `<li>${msg}</li>`
          })
          state.errorText = `<ul style="list-style-type: none;">${msgList}</ul>`
        }
        errorDialog.value.open()
        return false
      }
    }

    async function cancel () {
      await initialize()
      emit('cancel-payment-method-changes')
    }

    async function getCreateRequestBody () {
      let isValid = false
      let createRequestBody: CreateRequestBody

      if (state.selectedPaymentMethod === PaymentTypes.PAD) {
        isValid = await verifyPAD()
        createRequestBody = {
          paymentInfo: {
            paymentMethod: PaymentTypes.PAD,
            bankTransitNumber: state.padInfo.bankTransitNumber,
            bankInstitutionNumber: state.padInfo.bankInstitutionNumber,
            bankAccountNumber: state.padInfo.bankAccountNumber
          }
        }
      } else if (state.selectedPaymentMethod === PaymentTypes.BCOL) {
        isValid = !!(state.bcolInfo.userId && state.bcolInfo.password)
        if (!isValid) {
          state.errorMessage = 'Missing User ID and Password for BC Online.'
          state.isLoading = false
        }
        createRequestBody = {
          paymentInfo: {
            paymentMethod: PaymentTypes.BCOL
          },
          bcOnlineCredential: state.bcolInfo
        }
      } else if (state.selectedPaymentMethod === PaymentTypes.EJV) {
        isValid = true
        createRequestBody = {
          paymentInfo: {
            paymentMethod: PaymentTypes.EJV,
            revenueAccount: currentOrgGLInfo.value
          }
        }
      } else {
        isValid = true
        createRequestBody = {
          paymentInfo: {
            paymentMethod: state.selectedPaymentMethod
          }
        }
      }

      return { isValid, createRequestBody }
    }

    async function save () {
      state.isBtnSaved = false
      state.isLoading = true

      const { isValid, createRequestBody } = await getCreateRequestBody()
      const selectedPaymentMethod = state.selectedPaymentMethod

      if (isValid) {
        try {
          await orgStore.updateOrg(createRequestBody)
          state.isBtnSaved = true
          state.isLoading = false
          state.paymentMethodChanged = false
          initialize()
          orgStore.setCurrentOrganizationPaymentType(selectedPaymentMethod)
          if (selectedPaymentMethod === PaymentTypes.EFT) {
            const recipientList = []
            await orgStore.syncActiveOrgMembers()
            state.activeOrgMembers.forEach((member) => {
              if (member.membershipTypeCode !== MembershipType.User) {
                recipientList.push({
                  authUserId: member.user?.id,
                  firstname: member.user?.firstname,
                  lastname: member.user?.lastname,
                  email: member.user?.contacts[0]?.email
                })
              }
            })
            const statementNotification: StatementNotificationSettings = {
              statementNotificationEnabled: true,
              recipients: recipientList,
              accountName: state.currentOrganization.name
            }
            await orgStore.updateStatementNotifications(statementNotification)
          }
        } catch (error) {
          console.error(error)
          state.isLoading = false
          state.isBtnSaved = false
          state.paymentMethodChanged = false
          switch (error.response.status) {
            case 409:
              state.errorMessage = error.response.data.message?.detail || error.response.data.message
              break
            case 400:
              state.errorMessage = error.response.data.message?.detail || error.response.data.message
              break
            default:
              state.errorMessage = 'An error occurred while attempting to create your account.'
          }
        }
      }
    }

    function closeError () {
      errorDialog.value.close()
    }

    function setBcolInfo (bcolProfile: BcolProfile) {
      state.bcolInfo = bcolProfile
      emit('emit-bcol-info', state.bcolInfo)
      state.paymentMethodChanged = true
    }

    onMounted(async () => {
      watch(
        () => orgStore.currentOrganization,
        async () => {
          await initialize()
        }
      )
      await initialize()
    })

    return {
      ...toRefs(state),
      setSelectedPayment,
      isBcolAdmin,
      isDisableSaveBtn,
      getPADInfo,
      isPADValid,
      isEJVValid,
      isAcknowledgeNeeded,
      initialize,
      isPaymentViewAllowed,
      verifyPAD,
      cancel,
      save,
      closeError,
      errorDialog,
      currentOrganization,
      currentOrgPaymentType,
      currentMembership,
      currentOrgAddress,
      permissions,
      currentUser,
      setBcolInfo
    }
  }
})
</script>

<style lang="scss" scoped>
.form__btns {
  display: flex;
  flex-direction: row;
  justify-content: flex-end;
  align-items: center;
  margin-top: 2rem;

  .v-btn {
    width: 6rem;
  }
}

.save-btn.disabled {
  pointer-events: none;
}
</style>
