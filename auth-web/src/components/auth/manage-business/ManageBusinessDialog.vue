<template>
  <div id="manage-business-dialog">
    <v-dialog
      v-model="isDialogVisible"
      attach="#entity-management"
      persistent
      scrollable
      max-width="50rem"
      data-test-tag="add-business"
      @keydown.esc="resetForm(true)"
    >
      <HelpDialog
        ref="helpDialog"
        :helpDialogBlurb="helpDialogBlurb"
        :inline="true"
      />

      <AuthorizationEmailSent
        v-if="!showHelp && showAuthorizationEmailSentDialog"
        :email="businessContactEmail"
        @open-help="openHelp"
        @close-dialog="onAuthorizationEmailSentClose"
      />

      <v-card v-if="!showHelp && !showAuthorizationEmailSentDialog">
        <v-card-title data-test="dialog-header">
          <h2>Manage a B.C. Business</h2>
        </v-card-title>

        <v-card-text>
          <v-form
            ref="addBusinessForm"
            lazy-validation
            class="mt-0"
          >
            <template>
              <div class="font-weight-bold mr-2 float-left">
                Business Name:
              </div>
              <div>{{ businessName }}</div>

              <div class="font-weight-bold mr-2 float-left">
                Incorporation Number:
              </div>
              <div>{{ businessIdentifier }}</div>

              <div class="my-2">
                You must be authorized to manage this business. You can be authorized in one of the following ways:
              </div>
            </template>

            <v-card
              class="mx-auto"
              flat
            >
              <v-list class="mr-2">
                <v-list-group
                  v-if="isBusinessLegalTypeCorporation || isBusinessLegalTypeCoOp"
                  id="manage-business-dialog-passcode-group"
                  v-model="passcodeOption"
                  class="top-of-list"
                  eager
                >
                  <template #activator>
                    <v-list-item-title>Use the business {{ passwordText }}</v-list-item-title>
                  </template>
                  <div class="item-content">
                    <v-text-field
                      v-if="isBusinessIdentifierValid"
                      v-model="passcode"
                      filled
                      :label="passcodeLabel"
                      :hint="passcodeHint"
                      persistent-hint
                      :rules="passcodeRules"
                      :maxlength="passcodeMaxLength"
                      autocomplete="off"
                      type="input"
                      class="passcode mt-0 mb-2"
                      :aria-label="passcodeLabel"
                    />
                    <Certify
                      v-if="isBusinessIdentifierValid && isBusinessLegalTypeFirm"
                      :certifiedBy="certifiedBy"
                      entity="registered entity"
                      class="certify"
                      :class="(isBusinessIdentifierValid && showAuthorization) ? 'mt-4 mb-5' : 'mt-6 mb-5'"
                      @update:isCertified="isCertified = $event"
                    />
                  </div>
                </v-list-group>

                <v-list-group
                  v-if="isBusinessLegalTypeFirm"
                  id="manage-business-dialog-proprietor-partner-name-group"
                  v-model="nameOption"
                  class="top-of-list"
                >
                  <template #activator>
                    <v-list-item-title>
                      Use the name of a proprietor or partner
                    </v-list-item-title>
                  </template>
                  <div class="item-content">
                    <v-text-field
                      v-model="proprietorPartnerName"
                      filled
                      label="Proprietor or Parter Name (e.g., Last Name, First Name Middlename)"
                      hint="Name as it appears on the Business Summary or the Statement of Registration"
                      persistent-hint
                      :rules="proprietorPartnerNameRules"
                      maxlength="150"
                      autocomplete="off"
                      aria-label="Proprietor or Parter Name (e.g., Last Name, First Name Middlename)"
                    />
                  </div>
                  <Certify
                    :certifiedBy="certifiedBy"
                    entity="registered entity"
                    class="certify"
                    :class="(isBusinessIdentifierValid && showAuthorization) ? 'mt-4 mb-5' : 'mt-6 mb-5'"
                    @update:isCertified="isCertified = $event"
                  />
                </v-list-group>

                <v-list-group
                  v-if="(isBusinessLegalTypeCorporation || isBusinessLegalTypeCoOp || isBusinessLegalTypeFirm) && businessContactEmail"
                  id="manage-business-dialog-email-group"
                  v-model="emailOption"
                >
                  <template #activator>
                    <v-list-item-title>
                      Confirm authorization using your {{ computedAddressType }} email address
                      <div
                        v-if="isBusinessLegalTypeCorporation || isBusinessLegalTypeCoOp"
                        class="subtitle"
                      >
                        (If you forgot or don't have a business {{ passwordText }})
                      </div>
                    </v-list-item-title>
                  </template>
                  <div class="list-body">
                    <div>
                      An email will be sent to the {{ computedAddressType }} contact email of the business:
                    </div>
                    <div><b>{{ businessContactEmail }}</b></div>
                    <div class="mt-1 mr-1 mb-4">
                      To confirm your access, please click on the link in the email. This will add the business to your Business Registry List. The link is valid for 15 minutes.
                    </div>
                  </div>
                </v-list-group>

                <template v-if="enableDelegationFeature">
                  <v-list-group v-model="requestAuthBusinessOption">
                    <template #activator>
                      <v-list-item-title>Request authorization from the business</v-list-item-title>
                    </template>
                    <div class="list-body">
                      <!-- Placeholder for RTR -->
                    </div>
                  </v-list-group>

                  <v-list-group
                    v-model="requestAuthRegistryOption"
                  >
                    <template #activator>
                      <v-list-item-title>Request authorization from the Business Registry</v-list-item-title>
                    </template>
                    <div class="list-body">
                      <!-- Placeholder for RTR-->
                    </div>
                  </v-list-group>
                </template>
              </v-list>
            </v-card>
          </v-form>
        </v-card-text>

        <v-card-actions class="form__btns">
          <span
            id="help-button"
            class="pl-2 pr-2 mr-auto"
            @click.stop="openHelp()"
          >
            <v-icon>mdi-help-circle-outline</v-icon>
            Help
          </span>
          <v-btn
            id="cancel-button"
            large
            outlined
            color="primary"
            @click="resetForm(true)"
          >
            <span>Cancel</span>
          </v-btn>
          <v-btn
            id="add-button"
            large
            color="primary"
            :loading="isLoading"
            @click="manageBusiness()"
          >
            <span>Manage This Business</span>
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script lang="ts">
import { CorpTypes, LDFlags } from '@/util/constants'
import { computed, defineComponent, ref, watch } from '@vue/composition-api'
import AffiliationInvitationService from '@/services/affiliation-invitation.services'
import AuthorizationEmailSent from './AuthorizationEmailSent.vue'
import BusinessService from '@/services/business.services'
import Certify from './Certify.vue'
import CommonUtils from '@/util/common-util'
import { CreateAffiliationInvitation } from '@/models/affiliation-invitation'
import HelpDialog from '@/components/auth/common/HelpDialog.vue'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import { LoginPayload } from '@/models/business'
import { StatusCodes } from 'http-status-codes'
import { useStore } from 'vuex-composition-helpers'

export default defineComponent({
  components: {
    AuthorizationEmailSent,
    Certify,
    HelpDialog
  },
  props: {
    orgId: {
      type: String,
      default: ''
    },
    initialBusinessIdentifier: {
      type: String,
      default: ''
    },
    initialBusinessName: {
      type: String,
      default: ''
    },
    businessLegalType: {
      type: String,
      default: ''
    },
    showBusinessDialog: {
      type: Boolean,
      default: false
    },
    isStaffOrSbcStaff: {
      type: Boolean,
      default: false
    },
    userFirstName: {
      type: String,
      default: ''
    },
    userLastName: {
      type: String,
      default: ''
    }
  },
  setup (props, { emit }) {
    // Store and Actions
    const store = useStore()
    const addBusiness = async (loginPayload: LoginPayload) => {
      return store.dispatch('business/addBusiness', loginPayload)
    }
    const updateBusinessName = async (businessNumber: string) => {
      return store.dispatch('business/updateBusinessName', businessNumber)
    }

    // Local variables
    const businessName = ref('')
    const businessIdentifier = ref('') // aka incorporation number of registration number
    const businessIdentifierRules = ref(null)
    const contactInfo = ref(null)
    const passcode = ref('') // aka password or proprietor/partner
    const proprietorPartnerName = ref('') // aka password or proprietor/partner name
    const folioNumber = ref('')
    const isLoading = ref(false)
    const isCertified = ref(false) // firms only
    const authorizationName = ref('')
    const addBusinessForm = ref<HTMLFormElement>()
    const helpDialog = ref<HelpDialog>()
    const passcodeOption = ref(false)
    const emailOption = ref(false)
    const nameOption = ref(false)
    const enableDelegationFeature = ref(false)
    const requestAuthBusinessOption = ref(false)
    const requestAuthRegistryOption = ref(false)
    const authorizationLabel = 'Legal name of Authorized Person (e.g., Last Name, First Name)'
    const authorizationMaxLength = 100
    const showAuthorizationEmailSentDialog = ref(false)

    const isBusinessLegalTypeFirm = computed(() => {
      return props.businessLegalType === CorpTypes.SOLE_PROP || props.businessLegalType === CorpTypes.PARTNERSHIP
    })

    const isBusinessLegalTypeCorporation = computed(() => {
      return props.businessLegalType === CorpTypes.BC_COMPANY
    })

    const isBusinessLegalTypeCoOp = computed(() => {
      return props.businessLegalType === CorpTypes.COOP
    })

    const enableBusinessNrSearch = computed(() => {
      return LaunchDarklyService.getFlag(LDFlags.EnableBusinessNrSearch) || false
    })

    const isBusinessIdentifierValid = computed(() => {
      return CommonUtils.validateIncorporationNumber(businessIdentifier.value)
    })

    const isCooperative = computed(() => {
      return CommonUtils.isCooperativeNumber(businessIdentifier.value)
    })

    const showAuthorization = computed(() => {
      return isBusinessLegalTypeFirm.value && props.isStaffOrSbcStaff
    })

    const certifiedBy = computed(() => {
      return props.isStaffOrSbcStaff ? authorizationName.value : `${props.userLastName}, ${props.userFirstName}`
    })

    const authorizationRules = computed(() => {
      return [
        (v) => !!v || 'Authorization is required'
      ]
    })

    const passcodeLabel = computed(() => {
      if (isBusinessLegalTypeFirm.value) return 'Proprietor or Partner Name (e.g., Last Name, First Name Middlename)'
      if (isCooperative.value) return 'Passcode'
      return 'Password'
    })

    const passcodeHint = computed(() => {
      if (isBusinessLegalTypeFirm.value) return 'Name as it appears on the Business Summary or the Statement of Registration'
      if (isCooperative.value) return 'Passcode must be exactly 9 digits'
      return 'Password must be 8 to 15 characters'
    })

    const passcodeMaxLength = computed(() => {
      if (isBusinessLegalTypeFirm.value) return 150
      if (isCooperative.value) return 9
      return 15
    })

    const proprietorPartnerNameRules = computed(() => {
      return [
        (v) => !!v || 'Proprietor or Partner Name is required',
        (v) => v.length <= 150 || 'Maximum 150 characters'
      ]
    })

    const passcodeRules = computed(() => {
      if (isBusinessLegalTypeFirm.value) {
        return [
          (v) => !!v || 'Proprietor or Partner Name is required',
          (v) => v.length <= 150 || 'Maximum 150 characters'
        ]
      }
      if (isCooperative.value) {
        return [
          (v) => !!v || 'Passcode is required, enter the passcode you have setup in Corporate Online',
          (v) => CommonUtils.validateCooperativePasscode(v) || 'Passcode must be exactly 9 digits'
        ]
      }
      return [
        (v) => !!v || 'Password is required',
        (v) => CommonUtils.validateCorporatePassword(v) || 'Password must be 8 to 15 characters'
      ]
    })

    const passwordText = computed(() => {
      return (isCooperative.value ? 'passcode' : 'password')
    })

    const helpDialogBlurb = computed(() => {
      if (isCooperative.value) {
        return 'If you have not received your Access Letter from BC Registries, or have lost your Passcode, ' +
          'please contact us at:'
      } else {
        const url = 'www.corporateonline.gov.bc.ca'
        return `If you have forgotten or lost your password, please visit <a href="https://${url}">${url}</a> ` +
          'and choose the option "Forgot Company Password", or contact us at:'
      }
    })

    const isFormValid = computed(() => {
      let isValid = false

      if (isBusinessLegalTypeCorporation.value || isBusinessLegalTypeCoOp.value) {
        isValid = !!businessIdentifier.value && !!passcode.value
      } else if (isBusinessLegalTypeFirm.value) {
        isValid = !!businessIdentifier.value && !!proprietorPartnerName.value && isCertified.value
      } else {
        isValid =
          !!businessIdentifier.value &&
          !!passcode.value &&
          (!isBusinessLegalTypeFirm.value || isCertified.value) &&
          (!(isBusinessIdentifierValid.value && isBusinessLegalTypeFirm.value) || !!certifiedBy.value) &&
          addBusinessForm.value.validate()
      }
      return isValid
    })

    const isDialogVisible = computed(() => {
      return props.showBusinessDialog
    })

    const businessContactEmail = computed(() => {
      return contactInfo.value?.email
    })

    const computedAddressType = computed(() => {
      return isBusinessLegalTypeCorporation.value || isBusinessLegalTypeCoOp.value ? 'registered office' : isBusinessLegalTypeFirm.value ? 'business' : ''
    })

    // Methods
    const resetForm = (emitCancel = false) => {
      passcode.value = ''
      proprietorPartnerName.value = ''
      authorizationName.value = ''
      passcodeOption.value = false
      emailOption.value = false
      nameOption.value = false
      requestAuthBusinessOption.value = false
      requestAuthRegistryOption.value = false
      // staff workflow, doesn't have this function defined
      addBusinessForm.value?.resetValidation()
      isLoading.value = false
      if (emitCancel) {
        emit('on-cancel')
      }
    }

    const onAuthorizationEmailSentClose = () => {
      showAuthorizationEmailSentDialog.value = false
      emit('on-cancel')
    }

    const handleException = (exception) => {
      if (exception.response?.status === StatusCodes.UNAUTHORIZED) {
        emit('add-failed-invalid-code', passcodeLabel.value)
      } else if (exception.response?.status === StatusCodes.NOT_FOUND) {
        emit('add-failed-no-entity')
      } else if (exception.response?.status === StatusCodes.NOT_ACCEPTABLE) {
        emit('add-failed-passcode-claimed')
      } else if (exception.response?.status === StatusCodes.BAD_REQUEST) {
        emit('business-already-added', { name: businessName.value, identifier: businessIdentifier.value })
      } else {
        emit('add-unknown-error')
      }
    }

    const manageBusiness = async () => {
      if (emailOption.value) {
        try {
          const payload: CreateAffiliationInvitation = {
            fromOrgId: Number(props.orgId),
            businessIdentifier: businessIdentifier.value
          }
          await AffiliationInvitationService.createInvitation(payload)
        } catch (err) {
          // eslint-disable-next-line no-console
          console.log(err)
        } finally {
          showAuthorizationEmailSentDialog.value = true
        }
        return
      }
      addBusinessForm.value.validate()
      if (isFormValid.value) {
        isLoading.value = true
        try {
          // try to add business
          let businessData: LoginPayload = { businessIdentifier: businessIdentifier.value }
          if (!props.isStaffOrSbcStaff) {
            businessData = {
              ...businessData,
              certifiedByName: authorizationName.value,
              passCode: isBusinessLegalTypeFirm.value ? proprietorPartnerName.value : passcode.value
            }
          }
          const addResponse = await addBusiness(businessData)
          // check if add didn't succeed
          if (addResponse?.status !== StatusCodes.CREATED) {
            emit('add-unknown-error')
          }
          // try to update business name
          const businessResponse = await updateBusinessName(businessIdentifier.value)
          // check if update didn't succeed
          if (businessResponse?.status !== StatusCodes.OK) {
            emit('add-unknown-error')
          }
          // let parent know that add was successful
          emit('add-success', businessIdentifier.value)
        } catch (exception) {
          handleException(exception)
        } finally {
          resetForm()
        }
      }
    }

    const formatBusinessIdentifier = () => {
      businessIdentifierRules.value = [
        (v) => !!v || 'Incorporation Number or Registration Number is required',
        (v) => CommonUtils.validateIncorporationNumber(v) ||
          'Incorporation Number or Registration Number is not valid'
      ]
      businessIdentifier.value = CommonUtils.formatIncorporationNumber(businessIdentifier.value)
    }

    const openHelp = () => {
      helpDialog.value.open()
    }

    const showHelp = computed(() => {
      return helpDialog.value?.isDialogOpen
    })

    watch(() => props.initialBusinessIdentifier, async (newBusinessIdentifier: string) => {
      if (businessIdentifier && newBusinessIdentifier) {
        businessIdentifier.value = newBusinessIdentifier
        businessName.value = props.initialBusinessName
        try {
          const contact = await BusinessService.getMaskedContacts(newBusinessIdentifier)
          contactInfo.value = contact?.data
        } catch (err) {
          contactInfo.value = ''
          // eslint-disable-next-line no-console
          console.error(err)
        }
      }
    })

    // Watchers
    watch(businessIdentifier, (newValue) => {
      emit('on-business-identifier', newValue)
    }, { immediate: true })

    // Return the setup data - These will be removed with script setup.
    return {
      requestAuthRegistryOption,
      requestAuthBusinessOption,
      emailOption,
      nameOption,
      passcodeOption,
      isDialogVisible,
      addBusinessForm,
      helpDialog,
      businessName,
      businessIdentifier,
      passcode,
      proprietorPartnerName,
      folioNumber,
      isLoading,
      isCertified,
      authorizationName,
      authorizationLabel,
      authorizationMaxLength,
      isBusinessLegalTypeFirm,
      computedAddressType,
      isBusinessLegalTypeCorporation,
      isBusinessLegalTypeCoOp,
      enableBusinessNrSearch,
      isBusinessIdentifierValid,
      isCooperative,
      showAuthorization,
      certifiedBy,
      authorizationRules,
      passcodeLabel,
      passcodeHint,
      passcodeMaxLength,
      passcodeRules,
      proprietorPartnerNameRules,
      passwordText,
      helpDialogBlurb,
      isFormValid,
      manageBusiness,
      resetForm,
      onAuthorizationEmailSentClose,
      formatBusinessIdentifier,
      openHelp,
      businessContactEmail,
      enableDelegationFeature,
      showHelp,
      showAuthorizationEmailSentDialog
    }
  }
})
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';
@import '@/assets/scss/ModalDialog.scss';

  #help-button {
    cursor: pointer;
    color: var(--v-primary-base) !important;
    .v-icon {
      transform: translate(0, -2px) !important;
      color: var(--v-primary-base) !important;
    }
  }
  .list-body {
    color:#313132;
  }

  .v-tooltip__content {
    background-color: RGBA(73, 80, 87, 0.95) !important;
    color: white !important;
    border-radius: 4px;
    font-size: 12px !important;
    line-height: 18px !important;
    padding: 15px !important;
    letter-spacing: 0;
    max-width: 270px !important;
  }

  .v-tooltip__content:after {
    content: "" !important;
    position: absolute !important;
    top: 50% !important;
    right: 100% !important;
    margin-top: -10px !important;
    border-top: 10px solid transparent !important;
    border-bottom: 10px solid transparent !important;
    border-right: 8px solid RGBA(73, 80, 87, .95) !important;
  }

  .top-tooltip:after {
    top: 100% !important;
    left: 45% !important;
    margin-top: 0 !important;
    border-right: 10px solid transparent !important;
    border-left: 10px solid transparent !important;
    border-top: 8px solid RGBA(73, 80, 87, 0.95) !important;
  }

  .add-business-unordered-list {
    list-style: none;
    padding-left: 1rem;

    li {
      margin-left: 1.5rem;

      &::before {
        content: "\2022";
        display: inline-block;
        width: 1.5em;
        color: $gray9;
        margin-left: -1.5em;
      }
    }
  }

  .underline-dotted {
    border-bottom: dotted;
    border-bottom-width: 2px;
  }

  dl {
    line-height: 2rem;
  }

  // pair up terms and definitions
  dt {
    float: left;
    clear: left;
  }

  .form__btns {
    display: flex;
    justify-content: flex-end;

    .v-btn + .v-btn {
      margin-left: 0.5rem;
    }

    #cancel-button,
    #add-button {
      min-width: 80px !important;
    }

    // override disabled button color
    .v-btn[disabled]:not(.v-btn--flat):not(.v-btn--text):not(.v-btn--outlined) {
      color: white !important;
      background-color: $app-blue !important;
      opacity: 0.4;
    }
  }

  // remove whitespace below error message
  .authorization {
    ::v-deep .v-text-field__details {
      margin-bottom: 0 !important;
    }
  }

  ::v-deep {
    .v-list-group{
      border-bottom: 1px solid rgb(228, 228, 228);
      &.top-of-list{
        border-top: 1px solid rgb(228, 228, 228);
      }
      .item-content{
        color: #000 !important;
      }
    }

    .v-list-item{
      background: $BCgovInputBG;
      height: 4rem !important;
      margin: 0 !important;
    }

    .v-list-item--link>
    .v-list-item__title {
      font-weight: 300 !important;
      margin-left:-1rem !important;
      color: var(--v-primary-base) !important;
      .subtitle {
        line-height: 1.5rem;
        font-size: 9pt;
        color: var(--v-primary-base) !important;
        font-weight: normal;
      }
    }

    .v-list-item--active>
    .v-list-item__title {
      font-weight: 600 !important;
      margin-left:-1rem !important;
      color: #000 !important;
      .subtitle {
        line-height: 1.5rem;
        font-size: 9pt;
        color: #000 !important;
        font-weight: normal;
      }
    }

    .v-list-item__content{
      color: #000 !important;
    }
  }
</style>
