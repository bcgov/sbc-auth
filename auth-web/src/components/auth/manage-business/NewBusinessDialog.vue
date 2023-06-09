<template>
  <div id="add-business-dialog">
    <HelpDialog
      :helpDialogBlurb="helpDialogBlurb"
      ref="helpDialog"
    />

    <v-dialog
      attach="#entity-management"
      v-model="dialog"
      persistent
      scrollable
      max-width="675"
      data-test-tag="add-business"
      @keydown.esc="resetForm(true)"
    >
      <v-card>
        <v-card-title data-test="dialog-header">
          <span>Manage a B.C Business</span>
        </v-card-title>

        <v-card-text class="py-2">
          <p>
           <strong>Business name:</strong> Dunder Mifflin Paper Company Inc.<br>
           <strong>Incorporation Number:</strong> BC0871349
          </p>
          <p>
            You must be authorised to manage this business. You can be authorised in one of the following ways:
          </p>

          <v-expansion-panels
            v-model="panel"
            class="bottom-border"
            accordion
          >
            <v-expansion-panel
              id="x-panel-1"
              class="mb-4"
              :disabled="isOneOption"
              @click="identifyForm(1)"
            >
              <v-expansion-panel-header :class="{'name-options-header': isOneOption}">
                <span class="names-option-title" color="primary">Request authorization from the business</span>
                <template #actions>
                  <v-icon color="primary">
                    mdi-menu-down
                  </v-icon>
                </template>
              </v-expansion-panel-header>

              <v-expansion-panel-content class="name-options-content pt-4">
                <p>
                  Select the account you want to authorise you to perform Registries activities for <strong>DUNDER MIFFLIN PAPER COMPANY INC.</strong>:
                </p>
                <div class="w-full">
                  <v-select
                    class="column-selections w-full"
                    dense
                    filled
                    hide-details
                    item-text="value"
                    :items="headerSelections"
                    :menu-props="{
                      bottom: true,
                      minWidth: '200px',
                      maxHeight: 'none',
                      offsetY: true,
                      width: '100%'
                    }"
                    multiple
                    return-object
                    v-model="headersSelected"
                  >
                    <template v-slot:selection="{ index }">
                      <span v-if="index === 0">Authorising Account</span>
                    </template>
                  </v-select>

                  <p class="pt-8">
                    You can add a message that will be included as part of your authorisation request.
                  </p>

                  <v-card-text class="pt-1 pb-1">
                    <div class="relative">
                      <v-textarea
                        ref="textarea"
                        hide-details
                        dense
                        filled
                        placeholder="Enter an optional message"
                        full-width
                        v-model="message"
                        :disabled="characterCount >= 4000 && message.length !== 4000"
                        @input="updateCharacterCount"
                      />
                      <div class="character-counter absolute top-0 right-0 text-right pr-2 pt-2">
                        <span :class="{'text-red-500': characterCount > 4000}">{{ characterCount }}/4000 characters</span>
                      </div>
                    </div>
                  </v-card-text>
                </div>
              </v-expansion-panel-content>
            </v-expansion-panel>
          </v-expansion-panels>
        </v-card-text>

        <v-card-actions class="form__btns">
          <v-btn
            v-if="isBusinessIdentifierValid && !isFirm"
            large text
            class="pl-2 pr-2 mr-auto"
            id="forgot-button"
            @click.stop="openHelp()"
          >
            <v-icon>mdi-help-circle-outline</v-icon>
            <span>{{forgotButtonText}}</span>
          </v-btn>
          <v-btn
            large outlined color="primary"
            id="cancel-button"
            @click="resetForm(true)"
          >
            <span>Cancel</span>
          </v-btn>
          <v-btn
            large
            color="primary"
            id="add-button"
            :loading="isLoading"
            style="width: auto; display: inline-block; white-space: nowrap"
            @click="add()"
          >
            <span>Manage this business</span>
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>

import { Ref, computed, defineComponent, onBeforeUnmount, onMounted, ref, watch } from '@vue/composition-api'
import CommonUtils from '@/util/common-util'
import HelpDialog from '@/components/auth/common/HelpDialog.vue'
import { StatusCodes } from 'http-status-codes'
import { useStore } from 'vuex-composition-helpers'

export default defineComponent({
  name: 'AddBusinessDialog',
  components: {
    HelpDialog
  },
  props: {
    dialog: { default: false }
  },
  setup (props, { emit }) {
    const store = useStore()

    const isGovStaffAccount = ref(false)
    const userFirstName = ref('')
    const userLastName = ref('')

    const addBusiness = async () => {

    }

    const updateBusinessName = async (businessNumber) => {

    }

    const updateFolioNumber = async (folioNumberload) => {

    }

    // local variables
    const businessIdentifier = ref('')
    const passcode = ref('')
    const folioNumber = ref('')
    const isLoading = ref(false)
    const isCertified = ref(false) // firms only
    let businessIdentifierRules = []
    const authorizationName = ref('')

    const authorizationLabel = 'Legal name of Authorized Person (e.g., Last Name, First Name)'
    const authorizationMaxLength = 100

    const characterCount = ref(0)
    const message = ref('')

    const updateCharacterCount = () => {
      if (message.value.length > 4000) {
        message.value = message.value.substring(0, 4000)
      }
      characterCount.value = message.value.length
    }

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
      return isFirm.value && isGovStaffAccount.value
    })

    const certifiedBy = computed(() => {
      if (isGovStaffAccount.value) return authorizationName.value
      else return `${userLastName.value}, ${userFirstName.value}`
    })

    const authorizationRules = [
      (v) => !!v || 'Authorization is required'
    ]

    const helpDialogBlurb = computed(() => {
      if (isCooperative.value) {
        return 'If you have not received your Access Letter from BC Registries, or have lost your Passcode, please contact us at:'
      } else {
        const url = 'www.corporateonline.gov.bc.ca'
        return `If you have forgotten or lost your password, please visit <a href="https://${url}">${url}</a> and choose the option "Forgot Company Password", or contact us at:`
      }
    })

    const isFormValid = computed(() => {
      return (
        !!businessIdentifier.value &&
        !!passcode.value &&
        (!isFirm.value || isCertified.value) &&
        !!certifiedBy.value &&
        true // validate the form itself (according to the components' rules/state)
      )
    })

    const add = async () => {
      // Implementation here
    }

    const resetForm = (emitCancel = false) => {
      businessIdentifier.value = ''
      passcode.value = ''
      folioNumber.value = ''
      authorizationName.value = ''
      isLoading.value = false
      emitCancel && console.log('Emit cancel')
      if (emitCancel) {
        emit('on-cancel')
      }
    }

    const formatBusinessIdentifier = () => {
      businessIdentifierRules = [
        (v) => !!v || 'Incorporation Number or Registration Number is required',
        (v) =>
          CommonUtils.validateIncorporationNumber(v) ||
          'Incorporation Number or Registration Number is not valid'
      ]
      businessIdentifier.value = CommonUtils.formatIncorporationNumber(
        businessIdentifier.value
      )
    }

    const openHelp = () => {
      console.log('Open help')
    }

    // Emits event to parent initially and when business identifier changes.
    watch(businessIdentifier, () => {
      console.log('Business identifier changed')
    })

    return {
      isGovStaffAccount,
      userFirstName,
      userLastName,
      addBusiness,
      updateBusinessName,
      updateFolioNumber,
      businessIdentifier,
      passcode,
      folioNumber,
      isLoading,
      isCertified,
      businessIdentifierRules,
      authorizationName,
      authorizationLabel,
      authorizationMaxLength,
      characterCount,
      message,
      updateCharacterCount,
      isBusinessIdentifierValid,
      isCooperative,
      isFirm,
      showAuthorization,
      certifiedBy,
      authorizationRules,
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
