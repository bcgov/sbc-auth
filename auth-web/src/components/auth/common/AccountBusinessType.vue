<template>
    <v-container class="view-container" v-display-mode>
      <v-fade-transition>
      <div v-if="isLoading" class="loading-inner-container">
        <v-progress-circular size="50" width="5" color="primary" :indeterminate="isLoading"/>
      </div>
      </v-fade-transition>

      <div class="account-business-type-container" v-if="!isLoading">
        <p class="mb-9" v-if="!govmAccount">
                {{ $t('accountBusinessTypeText') }}
        </p>
        <v-form ref="accountInformationForm" data-test="account-information-form">
          <v-radio-group
            row
            v-model="isBusinessAccount"
            ref="isBusinessAccount"
            mandatory
            >
                <v-row justify="space-between">
                    <v-col  xs="12" md="9" class="business-radio">
                        <v-radio
                        label="Individual Person Name"
                        :key="false"
                        :value="false"
                        data-test="radio-individual-account-type"
                        class="px-4 py-5"
                        @change="onOrgBusinessTypeChange(!isEditAccount)"
                        ></v-radio>
                        <v-radio
                        label="Business Name"
                        :key="true"
                        :value="true"
                        data-test="radio-business-account-type"
                        class="px-4 py-5"
                        @change="onOrgBusinessTypeChange(!isEditAccount)"
                        ></v-radio>
                    </v-col>
                </v-row>
            </v-radio-group>
            <fieldset class="auto-complete-relative account-name" data-test="account-name">
                <legend class="mb-3"  v-if="govmAccount">Enter Ministry Information for this account</legend>
                <legend class="mb-3"  v-else-if="!isBusinessAccount">Account Name</legend>
                <v-slide-y-transition>
                    <div v-show="errorMessage">
                    <v-alert type="error" icon="mdi-alert-circle-outline">{{ errorMessage }}</v-alert>
                    </div>
                </v-slide-y-transition>
                <v-text-field
                filled
                :label="getOrgNameLabel"
                v-model.trim="name"
                :rules="orgNameRules"
                :disabled="saving || orgNameReadOnly"
                data-test="input-org-name"
                :readonly="govmAccount"
                autocomplete="off"
                :error-messages="bcolDuplicateNameErrorMessage"
                v-on:keyup="onOrgNameChange"
                ref="name"
                />
                <org-name-auto-complete
                v-if="enableOrgNameAutoComplete && isBusinessAccount"
                :searchValue="autoCompleteSearchValue"
                :setAutoCompleteIsActive="autoCompleteIsActive"
                @auto-complete-value="setAutoCompleteSearchValue">
                </org-name-auto-complete>
            </fieldset>
              <v-expand-transition class="branch-detail">
                <v-text-field
                filled
                label="Branch/Division (If applicable)"
                v-model.trim="branchName"
                :disabled="saving"
                data-test="input-branch-name"
                :readonly="govmAccount"
                v-on:keyup="onOrgBusinessTypeChange()"
                v-show="govmAccount || isBusinessAccount"
                />
              </v-expand-transition>
            <template >
              <v-expand-transition class="business-account-type-details">
                <v-row justify="space-between" data-test="business-account-type-details" v-if="isBusinessAccount">
                    <v-col cols="6" class="py-0">
                        <v-select
                        filled
                        label="Business Type"
                        item-text="desc"
                        item-value="code"
                        :items="businessTypeCodes"
                        v-model="businessType"
                        data-test="select-business-type"
                        :rules="orgBusinessTypeRules"
                        @change="onOrgBusinessTypeChange()"
                        :menu-props="{ auto:true, offsetY: true, maxHeight: 400 }"
                        ref="businessType"
                        />
                    </v-col>
                    <v-col cols="6" class="py-0">
                        <v-select
                        filled
                        label="Business Size"
                        item-text="desc"
                        item-value="code"
                        :items="businessSizeCodes"
                        v-model="businessSize"
                        data-test="select-business-size"
                        :rules="orgBusinessSizeRules"
                        @change="onOrgBusinessTypeChange()"
                        :menu-props="{ auto:true, offsetY: true, maxHeight: 400 }"
                        ref="businessSize"
                        />
                    </v-col>
                </v-row>
              </v-expand-transition>
            </template>
        </v-form>
      </div>
    </v-container>
</template>

<script lang="ts">
import { Account, LDFlags } from '@/util/constants'
import { Component, Emit, Prop, Vue } from 'vue-property-decorator'
import { OrgBusinessType, Organization } from '@/models/Organization'
import { Code } from '@/models/Code'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import OrgNameAutoComplete from '@/views/auth/OrgNameAutoComplete.vue'
import { namespace } from 'vuex-class'

const OrgModule = namespace('org')
const CodesModule = namespace('codes')

@Component({
  components: {
    OrgNameAutoComplete
  }
})
export default class AccountBusinessType extends Vue {
  @Prop({ default: false }) govmAccount: boolean
  @Prop({ default: null }) errorMessage: string
  @Prop({ default: false }) saving: boolean
  @Prop({ default: null }) bcolDuplicateNameErrorMessage: string
  @Prop({ default: false }) premiumLinkedAccount: boolean
  @Prop({ default: false }) orgNameReadOnly: boolean
  @Prop({ default: false }) isEditAccount: boolean // hide some details for update account

  @OrgModule.State('currentOrganization') public currentOrganization!: Organization

  @CodesModule.Action('getBusinessSizeCodes') private readonly getBusinessSizeCodes!: () => Promise<Code[]>
  @CodesModule.Action('getBusinessTypeCodes') private readonly getBusinessTypeCodes!: () => Promise<Code[]>
  @CodesModule.State('businessSizeCodes') private readonly businessSizeCodes!: Code[]
  @CodesModule.State('businessTypeCodes') private readonly businessTypeCodes!: Code[]

  private autoCompleteIsActive: boolean = false
  private autoCompleteSearchValue: string = ''
  private isLoading = false

  $refs: {
    accountInformationForm: HTMLFormElement,
    name: HTMLFormElement,
    businessType: HTMLFormElement,
    businessSize: HTMLFormElement,
    isBusinessAccount: HTMLFormElement
  }

  // input fields
  private isBusinessAccount = false
  private name = ''
  private businessType = ''
  private businessSize = ''
  private branchName = ''

  // Input field rules
  private readonly orgNameRules = [v => !!v || 'An account name is required']
  private readonly orgBusinessTypeRules = [v => !!v || 'A business type is required']
  private readonly orgBusinessSizeRules = [v => !!v || 'A business size is required']

  /** Emits an update message, so that we can sync with parent */
  @Emit('update:org-business-type')
  private emitUpdatedOrgBusinessType () {
    const orgBusinessType: OrgBusinessType = {
      name: this.name,
      isBusinessAccount: this.isBusinessAccount,
      ...((this.govmAccount || this.isBusinessAccount) && { branchName: this.branchName }),
      ...(this.isBusinessAccount && { businessType: this.businessType, businessSize: this.businessSize, branchName: this.branchName })
    }
    return orgBusinessType
  }

  /** Emits the validity of the component. */
  @Emit('valid')
  private emitValid () {
    let isFormValid = false
    isFormValid = !this.$refs.isBusinessAccount?.hasError && !this.$refs.name?.hasError
    if (this.isBusinessAccount && isFormValid) {
      isFormValid = isFormValid && !this.$refs.businessType?.hasError && !this.$refs.businessSize?.hasError
    }
    return isFormValid
  }

  async mounted () {
    try {
    // load business type and size codes
      this.isLoading = true
      await this.getBusinessSizeCodes()
      await this.getBusinessTypeCodes()
      if (this.currentOrganization.name) {
        this.name = this.currentOrganization.name
        // incase if the new account is a premium account, default business type to business account
        this.isBusinessAccount = this.currentOrganization.isBusinessAccount
        this.businessType = this.currentOrganization.businessType
        this.businessSize = this.currentOrganization.businessSize
        this.branchName = this.currentOrganization.branchName
      } else {
        this.isBusinessAccount = this.currentOrganization.orgType !== Account.BASIC
      }
      // sync with parent tracking object on mount and remove validation errors
      await this.onOrgBusinessTypeChange()
    } catch (ex) {
      // eslint-disable-next-line no-console
      console.log(`error while loading account business type -  ${ex}`)
    } finally {
      this.isLoading = false
    }
  }

  private get enableOrgNameAutoComplete (): boolean {
    return LaunchDarklyService.getFlag(LDFlags.EnableOrgNameAutoComplete) || false
  }

  private get getOrgNameLabel (): string {
    return this.govmAccount ? 'Ministry Name' : this.isBusinessAccount ? 'Legal Business Name' : 'Account Name'
  }

  private setAutoCompleteSearchValue (autoCompleteSearchValue: string): void {
    if (this.enableOrgNameAutoComplete) {
      this.autoCompleteIsActive = false
      this.name = autoCompleteSearchValue
    }
    // emit the update value to the parent
    this.emitUpdatedOrgBusinessType()
  }

  // watches name and suggests auto completed names if it is a business account.
  // similar to PPR - watch logic
  async onOrgNameChange () {
    // suggest auto complete values
    if (this.enableOrgNameAutoComplete && this.isBusinessAccount) {
      if (this.name) {
        this.autoCompleteSearchValue = this.name
      }
      this.autoCompleteIsActive = this.name !== ''
    }

    // Incase it is a premium linked account, we need to update org name and clear parent duplicate name error (exclusive for linked premium sceanrio)
    /** Emits a clear errors event to parent (exclusive for premium linked account scenario). */
    if (this.premiumLinkedAccount && this.bcolDuplicateNameErrorMessage) {
      this.$emit('update:org-name-clear-errors')
    }

    // emit the update value to the parent
    await this.onOrgBusinessTypeChange()
  }

  async onOrgBusinessTypeChange (clearOrgName: boolean = false) {
    if (clearOrgName) {
      // Case for isBusinessAccount - when toggling between individual and business accounts, we ought to reset org name
      this.name = ''
    }
    await this.$nextTick()
    this.emitUpdatedOrgBusinessType()
    this.emitValid()
  }
}
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
