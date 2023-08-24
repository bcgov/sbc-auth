<template>
  <div id="add-business-dialog">
    <HelpDialog
      ref="helpDialog"
      :helpDialogBlurb="helpDialogBlurb"
    />

    <v-dialog
      v-model="dialog"
      attach="#entity-management"
      persistent
      scrollable
      max-width="50rem"
      data-test-tag="add-business"
      @keydown.esc="resetForm(true)"
    >
      <v-card>
        <v-card-title data-test="dialog-header">
          <span>Add an Existing Business</span>
        </v-card-title>

        <v-card-text class="py-2">
          <p>
            Add an existing business to your list by providing the following required pieces of information:
          </p>
          <v-tooltip
            top
            nudge-bottom="80"
            content-class="top-tooltip"
          >
            <template #activator="{ on, attrs }">
              <ul class="add-business-unordered-list">
                <li>For <strong>cooperatives</strong>, enter the incorporation number and the passcode.</li>
                <li>For <strong>benefit companies</strong>, enter the incorporation number and the password.</li>
                <li>
                  For <strong>sole proprietorships and general partnerships</strong>, enter the registration
                  number and either <span
                    v-bind="attrs"
                    activator
                    class="underline-dotted"
                    v-on="on"
                  >the name
                    of the proprietor or a partner</span>.
                </li>
              </ul>
            </template>
            <span>
              For individuals, it should be "Last Name, First Name Middlename".<br>
              E.g. Watson, John Hamish
            </span>
          </v-tooltip>

          <v-form
            ref="addBusinessForm"
            lazy-validation
            class="mt-6"
          >
            <template v-if="enableBusinessNrSearch">
              <!-- Search for business identifier or name -->
              <!-- NB: use v-if to re-mount component between instances -->
              <BusinessLookup
                v-if="dialog"
                @business="businessName = $event.name; businessIdentifier = $event.identifier"
              />

              <template v-if="businessIdentifier">
                <dl>
                  <dt class="font-weight-bold mr-2">
                    Business Name:
                  </dt>
                  <dd>{{ businessName }}</dd>

                  <dt class="font-weight-bold mr-2">
                    Incorporation Number:
                  </dt>
                  <dd>{{ businessIdentifier }}</dd>
                </dl>
              </template>
            </template>

            <template v-else>
              <!-- Business Identifier -->
              <v-text-field
                v-model="businessIdentifier"
                filled
                req
                persistent-hint
                validate-on-blur
                label="Incorporation Number or Registration Number"
                hint="Example: BC1234567, CP1234567 or FM1234567"
                :rules="businessIdentifierRules"
                class="business-identifier mb-n2"
                aria-label="Incorporation Number and Password or Passcode"
                autofocus
                @blur="formatBusinessIdentifier()"
              />
            </template>

            <template v-if="!isStaffOrSbcStaff">
              <!-- Passcode -->
              <v-expand-transition>
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
                  class="passcode mt-6 mb-n2"
                  :aria-label="passcodeLabel"
                />
              </v-expand-transition>

              <!-- Authorization Name -->
              <v-expand-transition>
                <section
                  v-if="isBusinessIdentifierValid && showAuthorization"
                  class="mt-6"
                >
                  <header class="font-weight-bold">
                    Authorization
                  </header>
                  <v-text-field
                    v-model="authorizationName"
                    filled
                    persistent-hint
                    :label="authorizationLabel"
                    :rules="authorizationRules"
                    :maxlength="authorizationMaxLength"
                    :aria-label="authorizationLabel"
                    autocomplete="off"
                    class="authorization mt-4 pb-1"
                    hide-details="auto"
                  />
                </section>
              </v-expand-transition>

              <!-- Certify (firms only) -->
              <v-expand-transition>
                <Certify
                  v-if="isBusinessIdentifierValid && isFirm"
                  :certifiedBy="certifiedBy"
                  entity="registered entity"
                  class="certify"
                  :class="(isBusinessIdentifierValid && showAuthorization) ? 'mt-4' : 'mt-6'"
                  @update:isCertified="isCertified = $event"
                />
              </v-expand-transition>

              <!-- Folio Number -->
              <v-expand-transition>
                <section
                  v-if="isBusinessIdentifierValid"
                  class="mt-6"
                >
                  <header class="font-weight-bold">
                    Folio / Reference Number
                  </header>
                  <p class="mt-4 mb-0">
                    If you file forms for a number of companies, you may want to enter a
                    folio or reference number to help you keep track of your transactions.
                  </p>
                  <v-text-field
                    v-model="folioNumber"
                    filled
                    hide-details
                    label="Folio or Reference Number (Optional)"
                    :maxlength="50"
                    class="folio-number mt-6"
                    aria-label="Folio or Reference Number (Optional)"
                  />
                </section>
              </v-expand-transition>
            </template>
          </v-form>
        </v-card-text>

        <v-card-actions class="form__btns">
          <v-btn
            v-if="isBusinessIdentifierValid && !isFirm"
            id="forgot-button"
            large
            text
            class="pl-2 pr-2 mr-auto"
            @click.stop="openHelp()"
          >
            <v-icon>mdi-help-circle-outline</v-icon>
            <span>{{ forgotButtonText }}</span>
          </v-btn>
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
            @click="add()"
          >
            <span>Add</span>
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, ref, watch } from '@vue/composition-api'
import BusinessLookup from './BusinessLookup.vue'
import Certify from './Certify.vue'
import CommonUtils from '@/util/common-util'
import HelpDialog from '@/components/auth/common/HelpDialog.vue'
import { LDFlags } from '@/util/constants'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import { LoginPayload } from '@/models/business'
import { StatusCodes } from 'http-status-codes'
import { useBusinessStore } from '@/stores/business'

export default defineComponent({
  components: {
    BusinessLookup,
    Certify,
    HelpDialog
  },
  props: {
    dialog: {
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
    const businessStore = useBusinessStore()

    // Local variables
    const businessName = ref('')
    const businessIdentifier = ref('') // aka incorporation number of registration number
    const businessIdentifierRules = ref(null)
    const passcode = ref('') // aka password or proprietor/partner
    const folioNumber = ref('')
    const isLoading = ref(false)
    const isCertified = ref(false) // firms only
    const authorizationName = ref('')
    const addBusinessForm = ref<HTMLFormElement>()
    const helpDialog = ref<HelpDialog>()

    // Computed properties
    const authorizationLabel = 'Legal name of Authorized Person (e.g., Last Name, First Name)'
    const authorizationMaxLength = 100

    const enableBusinessNrSearch = computed(() => {
      return LaunchDarklyService.getFlag(LDFlags.EnableBusinessNrSearch) || false
    })

    const isBusinessIdentifierValid = computed(() => {
      return CommonUtils.validateIncorporationNumber(businessIdentifier.value)
    })

    const isCooperative = computed(() => {
      return CommonUtils.isCooperativeNumber(businessIdentifier.value)
    })

    const isFirm = computed(() => {
      return CommonUtils.isFirmNumber(businessIdentifier.value)
    })

    const showAuthorization = computed(() => {
      return isFirm.value && props.isStaffOrSbcStaff
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
      if (isFirm.value) return 'Proprietor or Partner Name (e.g., Last Name, First Name Middlename)'
      if (isCooperative.value) return 'Passcode'
      return 'Password'
    })

    const passcodeHint = computed(() => {
      if (isFirm.value) return 'Name as it appears on the Business Summary or the Statement of Registration'
      if (isCooperative.value) return 'Passcode must be exactly 9 digits'
      return 'Password must be 8 to 15 characters'
    })

    const passcodeMaxLength = computed(() => {
      if (isFirm.value) return 150
      if (isCooperative.value) return 9
      return 15
    })

    const passcodeRules = computed(() => {
      if (isFirm.value) {
        return [
          (v) => !!v || 'Proprietor or Partner Name is required',
          (v) => v.length <= 150 || 'Maximum 150 characters'
        ]
      }
      if (isCooperative.value) {
        return [
          (v) => !!v || 'Passcode is required',
          (v) => CommonUtils.validateCooperativePasscode(v) || 'Passcode must be exactly 9 digits'
        ]
      }
      return [
        (v) => !!v || 'Password is required',
        (v) => CommonUtils.validateCorporatePassword(v) || 'Password must be 8 to 15 characters'
      ]
    })

    const forgotButtonText = computed(() => {
      return 'I lost or forgot my ' + (isCooperative.value ? 'passcode' : 'password')
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
      // if user is a staff user or sbc staff user, then only require the business identifier
      if (props.isStaffOrSbcStaff && !!businessIdentifier.value) {
        return true
      }
      // business id is required
      // passcode is required
      // firms must accept certify clause
      // staff users must enter names
      // validate the form itself (according to the components' rules/state)
      return (
        !!businessIdentifier.value &&
        !!passcode.value &&
        (!isFirm.value || (isCertified.value && !!certifiedBy.value)) &&
        addBusinessForm.value.validate()
      )
    })

    // Methods
    const resetForm = (emitCancel = false) => {
      businessName.value = ''
      businessIdentifier.value = ''
      passcode.value = ''
      folioNumber.value = ''
      authorizationName.value = ''
      addBusinessForm.value.resetValidation()
      isLoading.value = false
      if (emitCancel) {
        emit('on-cancel')
      }
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

    const add = async () => {
      addBusinessForm.value.validate()
      if (isFormValid.value) {
        isLoading.value = true
        try {
          // try to add business
          let businessData: LoginPayload = { businessIdentifier: businessIdentifier.value }
          if (!props.isStaffOrSbcStaff) {
            businessData = { ...businessData, certifiedByName: authorizationName.value, passCode: passcode.value }
          }
          const addResponse = await businessStore.addBusiness(businessData)
          // check if add didn't succeed
          if (addResponse?.status !== StatusCodes.CREATED) {
            emit('add-unknown-error')
          }
          // try to update business name
          const businessResponse = await businessStore.updateBusinessName(businessIdentifier.value)
          // check if update didn't succeed
          if (businessResponse?.status !== StatusCodes.OK) {
            emit('add-unknown-error')
          }
          // update folio number
          await businessStore.updateFolioNumber({
            businessIdentifier: businessIdentifier.value,
            folioNumber: folioNumber.value
          })
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

    // Watchers
    watch(businessIdentifier, (newValue) => {
      emit('on-business-identifier', newValue)
    }, { immediate: true })

    // Return the setup data - These will be removed with script setup.
    return {
      addBusinessForm,
      helpDialog,
      businessName,
      businessIdentifier,
      passcode,
      folioNumber,
      isLoading,
      isCertified,
      authorizationName,
      authorizationLabel,
      authorizationMaxLength,
      enableBusinessNrSearch,
      isBusinessIdentifierValid,
      isCooperative,
      isFirm,
      showAuthorization,
      certifiedBy,
      authorizationRules,
      passcodeLabel,
      passcodeHint,
      passcodeMaxLength,
      passcodeRules,
      forgotButtonText,
      helpDialogBlurb,
      isFormValid,
      add,
      resetForm,
      formatBusinessIdentifier,
      openHelp
    }
  }
})
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';

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
    min-width: unset !important;
    width: 100px;
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
</style>
