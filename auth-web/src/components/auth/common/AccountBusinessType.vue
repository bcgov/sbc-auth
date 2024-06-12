<template>
  <v-container
    v-display-mode
    class="view-container"
  >
    <v-fade-transition>
      <div
        v-if="isLoading"
        class="loading-inner-container"
      >
        <v-progress-circular
          size="50"
          width="5"
          color="primary"
          :indeterminate="isLoading"
        />
      </div>
    </v-fade-transition>
    <div
      v-if="!isLoading"
      class="account-business-type-container"
    >
      <p
        v-if="!govmAccount"
        class="mb-9"
      >
        {{ $t('accountBusinessTypeText') }}
      </p>
      <v-form
        ref="accountInformationForm"
        data-test="account-information-form"
      >
        <v-radio-group
          v-if="!govmAccount"
          v-model="accessType"
          row
          mandatory
          @change="handleAccountTypeChange"
        >
          <v-row
            justify="space-between"
            no-gutters
          >
            <v-col
              cols="8"
              class="business-radio"
            >
              <v-radio
                label="Individual Person"
                :value="AccountType.INDIVIDUAL"
                data-test="radio-individual-account-type"
                class="px-4 py-5"
              />
              <v-radio
                label="Business"
                :value="AccountType.BUSINESS"
                data-test="radio-business-account-type"
                class="px-4 py-5"
              />
            </v-col>
            <v-col
              v-if="!isEditing && displayGovnType"
              cols="4"
              class="business-radio"
            >
              <v-tooltip
                top
                content-class="top-tooltip"
                transition="fade-transition"
              >
                <template #activator="{ on, attrs }">
                  <span
                    v-bind="attrs"
                    class="tooltip-activator"
                    v-on="on"
                  >
                    <v-radio
                      :value="AccountType.GOVN"
                      data-test="radio-government-account-type"
                      class="px-4 py-5 w-100"
                    >
                      <template #label>
                        <span class="tooltip-text">Government Agency</span>
                      </template>
                    </v-radio>
                  </span>
                </template>
                <span>Government agency includes: townships, cities, districts, municipalities, and federal government.</span>
              </v-tooltip>
            </v-col>
          </v-row>
        </v-radio-group>
        <fieldset
          class="auto-complete-relative account-name"
          data-test="account-name"
        >
          <legend
            v-if="govmAccount"
            class="mb-3"
          >
            Enter Ministry Information for this account
          </legend>
          <legend
            v-else-if="isGovnAccount"
            class="mb-3"
          >
            Government Agency Information
          </legend>
          <legend
            v-else-if="isIndividualAccount"
            class="mb-3"
          >
            Account Name
          </legend>
          <legend v-else />
          <v-slide-y-transition>
            <div v-show="errorMessage">
              <v-alert
                type="error"
                icon="mdi-alert-circle-outline"
              >
                {{ errorMessage }}
              </v-alert>
            </div>
          </v-slide-y-transition>
          <v-text-field
            v-model.trim="name"
            filled
            :label="getOrgNameLabel"
            :rules="orgNameRules"
            :disabled="saving || orgNameReadOnly"
            data-test="input-org-name"
            autocomplete="off"
            :readonly="govmAccount"
            :error-messages="bcolDuplicateNameErrorMessage"
            @keyup="onOrgNameChange"
          />
          <OrgNameAutoComplete
            v-if="isBusinessAccount"
            :searchValue="autoCompleteSearchValue"
            :setAutoCompleteIsActive="autoCompleteIsActive"
            @auto-complete-value="setAutoCompleteSearchValue"
          />
        </fieldset>
        <v-expand-transition class="branch-detail">
          <v-text-field
            v-show="govmAccount || isGovnAccount || isBusinessAccount"
            v-model.trim="branchName"
            filled
            label="Branch/Division (If applicable)"
            :disabled="saving"
            data-test="input-branch-name"
            :readonly="govmAccount"
            @keyup="onOrgBusinessTypeChange()"
          />
        </v-expand-transition>
        <v-expand-transition class="business-account-type-details">
          <v-row
            v-if="isGovnAccount || isBusinessAccount "
            justify="space-between"
            data-test="business-account-type-details"
          >
            <v-col
              cols="6"
              class="py-0"
            >
              <v-select
                v-model="businessType"
                filled
                :label="getOrgTypeDropdownLabel"
                item-text="desc"
                item-value="code"
                :items="typeCodesItems"
                data-test="select-business-type"
                :rules="orgBusinessTypeRules"
                :menu-props="{
                  bottom: true,
                  offsetY: true
                }"
                @change="onOrgBusinessTypeChange()"
              />
            </v-col>
            <v-col
              cols="6"
              class="py-0"
            >
              <v-select
                v-model="businessSize"
                filled
                :label="getOrgSizeDropdownLabel"
                item-text="desc"
                item-value="code"
                :items="businessSizeCodes"
                data-test="select-business-size"
                :rules="orgBusinessSizeRules"
                :menu-props="{
                  bottom: true,
                  offsetY: true
                }"
                @change="onOrgBusinessTypeChange()"
              />
            </v-col>
          </v-row>
        </v-expand-transition>
      </v-form>
    </div>
  </v-container>
</template>

<script lang="ts">
import { Account, AccountType, OrgNameLabel, SessionStorageKeys } from '@/util/constants'
import { computed, defineComponent, nextTick, onMounted, reactive, toRefs, watch } from '@vue/composition-api'
import ConfigHelper from '@/util/config-helper'
import { OrgBusinessType } from '@/models/Organization'
import OrgNameAutoComplete from '@/views/auth/OrgNameAutoComplete.vue'
import { storeToRefs } from 'pinia'
import { useCodesStore } from '@/stores/codes'
import { useOrgStore } from '@/stores/org'

export default defineComponent({
  name: 'AccountBusinessType',
  components: {
    OrgNameAutoComplete
  },
  props: {
    govmAccount: {
      type: Boolean,
      default: false
    },
    errorMessage: {
      type: String,
      default: null
    },
    saving: {
      type: Boolean,
      default: false
    },
    bcolDuplicateNameErrorMessage: {
      type: String,
      default: null
    },
    premiumLinkedAccount: {
      type: Boolean,
      default: false
    },
    orgNameReadOnly: {
      type: Boolean,
      default: false
    },
    isEditAccount: {
      type: Boolean,
      default: false
    }
  },
  setup (props, { emit }) {
    const codesStore = useCodesStore()
    const orgStore = useOrgStore()

    const {
      businessSizeCodes,
      businessTypeCodes,
      governmentTypeCodes
    } = storeToRefs(codesStore)

    const currentOrganization = computed(() => orgStore.currentOrganization)
    const displayGovnType = computed(() => orgStore.isGovnGovmOrg)

    const state = reactive({
      accountInformationForm: null,
      accessType: AccountType.INDIVIDUAL,
      autoCompleteIsActive: false,
      autoCompleteSearchValue: '',
      isLoading: false,
      isBusinessAccount: false,
      name: '',
      businessType: '',
      businessSize: '',
      governmentSize: '',
      branchName: '',
      isIndividualAccount: true,
      isGovnAccount: false,
      orgNameRules: [],
      orgBusinessTypeRules: [],
      orgBusinessSizeRules: [],
      typeCodesItems: []
    })

    const getOrgNameLabel = computed(() => {
      if (props.govmAccount) {
        return OrgNameLabel.GOVM
      } else if (state.isGovnAccount) {
        return OrgNameLabel.GOVN
      } else if (state.isBusinessAccount) {
        return OrgNameLabel.BUSINESS
      } else {
        return OrgNameLabel.REGULAR
      }
    })

    const getOrgTypeDropdownLabel = computed(() =>
      state.accessType === AccountType.GOVN ? 'Government Agency Type' : 'Business Type'
    )

    const getOrgSizeDropdownLabel = computed(() =>
      state.accessType === AccountType.GOVN ? 'Government Agency Size' : 'Business Size'
    )

    watch(() => state.accessType, () => {
      state.isBusinessAccount = state.accessType === AccountType.BUSINESS
      state.isGovnAccount = state.accessType === AccountType.GOVN
      state.isIndividualAccount = state.accessType === AccountType.INDIVIDUAL
      cleanOrgInfo()
    })

    function cleanOrgInfo () {
      state.name = ''
      state.branchName = ''
      state.businessType = ''
      state.businessSize = ''
      if (state.accountInformationForm) {
        state.accountInformationForm.resetValidation()
      }
      if (state.isGovnAccount) {
        state.orgNameRules = [v => !!v || 'A government agency name is required']
        state.orgBusinessTypeRules = [v => !!v || 'A government agency type is required']
        state.orgBusinessSizeRules = [v => !!v || 'A government agency size is required']
        state.typeCodesItems = governmentTypeCodes.value
      } else {
        state.orgNameRules = [v => !!v || 'An account name is required']
        state.orgBusinessTypeRules = [v => !!v || 'A business type is required']
        state.orgBusinessSizeRules = [v => !!v || 'A business size is required']
        state.typeCodesItems = businessTypeCodes.value
      }
    }

    async function handleAccountTypeChange (newValue) {
      state.accessType = newValue
      await onOrgBusinessTypeChange(!props.isEditAccount)
    }

    function emitUpdatedOrgBusinessType () {
      const orgBusinessType: OrgBusinessType = {
        name: state.name,
        isBusinessAccount: state.isBusinessAccount || state.isGovnAccount,
        ...((props.govmAccount || state.isBusinessAccount) && { branchName: state.branchName }),
        ...((state.isBusinessAccount || state.isGovnAccount) &&
          { businessType: state.businessType, businessSize: state.businessSize, branchName: state.branchName })
      }
      emit('update:org-business-type', orgBusinessType)
    }

    function updateAccessType () {
      if (state.isGovnAccount) {
        ConfigHelper.addToSession(SessionStorageKeys.GOVN_USER, 'true')
        return
      }
      ConfigHelper.removeFromSession(SessionStorageKeys.GOVN_USER)
    }

    function emitValid () {
      let isFormValid = true
      if (state.isBusinessAccount || state.isGovnAccount) {
        isFormValid = state.businessType !== '' && state.businessSize !== ''
      }
      isFormValid = isFormValid && state.name !== ''
      emit('valid', isFormValid)
    }

    onMounted(async () => {
      try {
        state.isLoading = true
        await codesStore.fetchAllBusinessTypeCodes()
        await codesStore.getGovernmentTypeCodes()
        await codesStore.getBusinessSizeCodes()
        await codesStore.getBusinessTypeCodes()
        if (currentOrganization.value?.name) {
          state.name = currentOrganization.value.name
          state.isBusinessAccount = currentOrganization.value.isBusinessAccount
          state.isIndividualAccount = false
          state.isGovnAccount = !currentOrganization.value.isBusinessAccount
          state.businessType = currentOrganization.value.businessType
          state.businessSize = currentOrganization.value.businessSize
          state.branchName = currentOrganization.value.branchName
        } else {
          state.isBusinessAccount = currentOrganization.value.orgType !== Account.BASIC
        }
        if (state.isBusinessAccount) {
          state.accessType = AccountType.BUSINESS
        }
        await onOrgBusinessTypeChange()
      } catch (ex) {
        console.error(`Error while loading account business type - ${ex}`)
      } finally {
        state.isLoading = false
      }
    })

    function setAutoCompleteSearchValue (value: string) {
      state.autoCompleteIsActive = false
      state.name = value
      emitUpdatedOrgBusinessType()
    }

    async function onOrgNameChange () {
      if (state.isBusinessAccount) {
        if (state.name) {
          state.autoCompleteSearchValue = state.name
        }
        state.autoCompleteIsActive = state.name !== ''
      }

      if (props.premiumLinkedAccount && props.bcolDuplicateNameErrorMessage) {
        emit('update:org-name-clear-errors')
      }

      await onOrgBusinessTypeChange()
    }

    async function onOrgBusinessTypeChange (clearOrgName = false) {
      if (clearOrgName) {
        state.name = ''
      }
      await nextTick()
      emitUpdatedOrgBusinessType()
      updateAccessType()
      emitValid()
    }

    return {
      ...toRefs(state),
      getOrgNameLabel,
      setAutoCompleteSearchValue,
      onOrgNameChange,
      onOrgBusinessTypeChange,
      businessSizeCodes,
      handleAccountTypeChange,
      AccountType,
      getOrgTypeDropdownLabel,
      getOrgSizeDropdownLabel,
      isEditing: props.isEditAccount,
      displayGovnType
    }
  }
})
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';
.view-container {
    padding: 0 !important;
}
.business-radio{
  display: flex;
  justify-content: center;
  .v-radio{
    background-color: rgba(0,0,0,.06);
    width: 100%;
    border: 1px rgba(0,0,0,.06) !important;
  }
  .v-radio.theme--light.v-item--active {
      border: 1px solid var(--v-primary-base) !important;
      background-color: $BCgovInputBG !important;
  }
}
.tooltip-activator {
  width: 100%;
}
.tooltip {
  background-color: transparent;
  opacity: 1 !important;

  .tooltip-content {
    min-width: 30rem;
    padding: 2rem;
  }
}
.tooltip-text {
  border-bottom: 2px dotted;
}
.tooltip-text:hover {
    cursor: pointer;
}
.v-tooltip__content {
  background-color: RGBA(73, 80, 87, 0.95) !important;
  color: white !important;
  border-radius: 4px;
  font-size: 14px !important;
  line-height: 18px !important;
  padding: 15px !important;
  letter-spacing: 0;
  max-width: 360px !important;
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

.right-tooltip:after {
  top: 50% !important;
  right: 100% !important;
  margin-top: -10px !important;
  border-bottom: 10px solid transparent !important;
  border-left: 10px solid transparent !important;
  border-top: 10px solid transparent !important;
  border-right: 8px solid RGBA(73, 80, 87, 0.95) !important;
}

.align-vertical {
  align-items: center;
}
</style>
