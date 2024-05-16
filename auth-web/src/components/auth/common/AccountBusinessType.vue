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
          v-model="orgType"
          row
          mandatory
          @change="handleAccountTypeChange"
        >
          <v-row justify="space-between">
            <v-col md="7" class="business-radio xs">
              <v-radio
                label="Individual Person"
                :value="AccountType.INDIVIDUAL"
                data-test="radio-individual-account-type"
                class="px-4 py-5"
              />
              <v-radio
                label="Business Name"
                :value="AccountType.BUSINESS"
                data-test="radio-business-account-type"
                class="px-4 py-5"
              />
              <v-radio
                v-if="!isEditing"
                label="Government Agency"
                :value="AccountType.GOVN"
                data-test="radio-government-account-type"
                class="px-4 py-5"
              />
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
            v-else-if="isGovnAccount && onOrgBusinessTypeChange"
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
          <org-name-auto-complete
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
                :items="businessTypeCodes"
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
import { defineComponent, ref, computed, onMounted, nextTick } from '@vue/composition-api'
import { useCodesStore } from '@/stores/codes'
import { useOrgStore } from '@/stores/org'
import OrgNameAutoComplete from '@/views/auth/OrgNameAutoComplete.vue'
import { OrgBusinessType, Organization } from '@/models/Organization'
import { Account, AccountType } from '@/util/constants'
import { Code } from '@/models/Code'

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

    const currentOrganization = computed(() => orgStore.currentOrganization)
    const businessSizeCodes = computed(() => codesStore.businessSizeCodes)
    const businessTypeCodes = computed(() => codesStore.businessTypeCodes)

    const orgType = ref(AccountType.INDIVIDUAL)
    const autoCompleteIsActive = ref(false)
    const autoCompleteSearchValue = ref('')
    const isLoading = ref(false)
    const isBusinessAccount = ref(false)
    const name = ref('')
    const businessType = ref('')
    const businessSize = ref('')
    const governmentSize = ref('')
    const branchName = ref('')
    const isIndividualAccount = ref(false)
    const isGovnAccount = ref(false)

    const orgNameRules = [v => !!v || 'An account name is required']
    const orgBusinessTypeRules = [v => !!v || 'A business type is required']
    const orgBusinessSizeRules = [v => !!v || 'A business size is required']

    const getOrgNameLabel = computed(() => {
      if (props.govmAccount) {
        return 'Ministry Name'
      } else if (isGovnAccount.value) {
        return 'Government Agency Name'
      } else if (isBusinessAccount.value) {
        return 'Legal Business Name'
      } else {
        return 'Account Name'
      }
    })

    const getOrgTypeDropdownLabel = computed(() => 
      orgType.value === AccountType.GOVN ? 'Government Agency Type' : 'Business Type'
    )

    const getOrgSizeDropdownLabel = computed(() => 
      orgType.value === AccountType.GOVN ? 'Government Agency Size' : 'Business Size'
    )

    function cleanOrgInfo() {
      name.value = ''
      branchName.value = ''
      businessType.value = ''
      businessSize.value = ''
    }

    async function handleAccountTypeChange(newValue) {
      orgType.value = newValue
      isBusinessAccount.value = (orgType.value === AccountType.BUSINESS)
      isGovnAccount.value = (orgType.value === AccountType.GOVN)
      isIndividualAccount.value = (orgType.value === AccountType.INDIVIDUAL)
      cleanOrgInfo()
      await onOrgBusinessTypeChange(!props.isEditAccount)
    }

    function emitUpdatedOrgBusinessType() {
      const orgBusinessType: OrgBusinessType = {
        name: name.value,
        isBusinessAccount: isBusinessAccount.value || isGovnAccount.value,
        ...((props.govmAccount || isBusinessAccount.value) && { branchName: branchName.value }),
        ...((isBusinessAccount.value || isGovnAccount.value) && { businessType: businessType.value, businessSize: businessSize.value, branchName: branchName.value })
      }
      emit('update:org-business-type', orgBusinessType)
    }

    function emitValid() {
      let isFormValid = true
      if (isBusinessAccount.value || isGovnAccount.value) {
        isFormValid = businessType.value !== '' && businessSize.value !== ''
      }
      isFormValid = isFormValid && name.value !== ''
      emit('valid', isFormValid)
    }

    onMounted(async () => {
      try {
        isLoading.value = true
        await codesStore.fetchAllBusinessTypeCodes()
        await codesStore.getGovernmentTypeCodes()
        await codesStore.getBusinessSizeCodes()
        await codesStore.getBusinessTypeCodes()
        if (currentOrganization.value.name) {
          name.value = currentOrganization.value.name
          isBusinessAccount.value = currentOrganization.value.isBusinessAccount
          businessType.value = currentOrganization.value.businessType
          businessSize.value = currentOrganization.value.businessSize
          branchName.value = currentOrganization.value.branchName
        } else {
          isBusinessAccount.value = currentOrganization.value.orgType !== Account.BASIC
          orgType.value = AccountType.BUSINESS
        }
        await onOrgBusinessTypeChange()
      } catch (ex) {
        console.error(`Error while loading account business type - ${ex}`)
      } finally {
        isLoading.value = false
      }
    })

    function setAutoCompleteSearchValue(value: string) {
      autoCompleteIsActive.value = false
      name.value = value
      emitUpdatedOrgBusinessType()
    }

    async function onOrgNameChange() {
      if (isBusinessAccount.value) {
        if (name.value) {
          autoCompleteSearchValue.value = name.value
        }
        autoCompleteIsActive.value = name.value !== ''
      }

      if (props.premiumLinkedAccount && props.bcolDuplicateNameErrorMessage) {
        emit('update:org-name-clear-errors')
      }

      await onOrgBusinessTypeChange()
    }

    async function onOrgBusinessTypeChange(clearOrgName = false) {
      if (clearOrgName) {
        name.value = ''
      }
      await nextTick()
      emitUpdatedOrgBusinessType()
      emitValid()
    }

    return {
      orgType,
      isLoading,
      isBusinessAccount,
      name,
      businessType,
      businessSize,
      branchName,
      autoCompleteIsActive,
      autoCompleteSearchValue,
      getOrgNameLabel,
      orgNameRules,
      orgBusinessTypeRules,
      orgBusinessSizeRules,
      setAutoCompleteSearchValue,
      onOrgNameChange,
      onOrgBusinessTypeChange,
      businessSizeCodes,
      businessTypeCodes,
      isGovnAccount,
      isIndividualAccount,
      governmentSize,
      handleAccountTypeChange,
      AccountType,
      getOrgTypeDropdownLabel,
      getOrgSizeDropdownLabel,
      isEditing: props.isEditAccount
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
  .v-radio{
     padding: 10px;
    background-color: rgba(0,0,0,.06);
    min-width: 50%;
    border: 1px rgba(0,0,0,.06) !important;
  }
  .v-radio.theme--light.v-item--active {
      border: 1px solid var(--v-primary-base) !important;
      background-color: $BCgovInputBG !important;
  }
}
</style>
