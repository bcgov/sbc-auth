<template>
    <v-container class="view-container">
        <p class="mb-9" v-if="!govmAccount">
                {{ $t('accountBusinessTypeText') }}
        </p>
        <v-form ref="accountInformationForm" data-test="account-information-form">
            <v-radio-group
            row
            v-model="isBusinessAccount"
            @change="onOrgBusinessTypeChange"
            mandatory
            >
                <v-row justify="space-between">
                    <v-col cols="6">
                        <v-radio
                        label="Individual Person Name"
                        :key="false"
                        :value="false"
                        data-test="radio-individual-account-type"
                        ></v-radio>
                    </v-col>
                    <v-col cols="6">
                        <v-radio
                        label="Business Name"
                        :key="true"
                        :value="true"
                        data-test="radio-business-account-type"
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
                :label="govmAccount ? 'Ministry Name' : isBusinessAccount ? 'Legal Business Name' : 'Account Name'"
                v-model.trim="name"
                :rules="orgNameRules"
                :disabled="saving || orgNameReadOnly"
                data-test="input-org-name"
                :readonly="govmAccount"
                autocomplete="off"
                :error-messages="bcolDuplicateNameErrorMessage"
                v-on:keyup="onOrgNameChange"
                />
                <org-name-auto-complete
                v-if="enableOrgNameAutoComplete && isBusinessAccount"
                :searchValue="autoCompleteSearchValue"
                :setAutoCompleteIsActive="autoCompleteIsActive"
                @auto-complete-value="setAutoCompleteSearchValue">
                </org-name-auto-complete>
            </fieldset>
            <template v-if="govmAccount || isBusinessAccount">
              <v-expand-transition class="branch-detail" data-test="branch-detail">
                <v-text-field
                filled
                :label="govmAccount ? 'Branch/Division (If applicable)' : 'Branch/Division (If optional)'"
                v-model.trim="branchName"
                :disabled="saving"
                data-test="input-branch-name"
                :readonly="govmAccount"
                v-on:keyup="onOrgBusinessTypeChange"
                />
              </v-expand-transition>
            </template>
            <template v-if="isBusinessAccount">
              <v-expand-transition class="business-account-type-details"  data-test="business-account-type-details" >
                <v-row justify="space-between">
                    <v-col cols="6">
                        <v-select
                        filled
                        label="Business Type"
                        item-text="desc"
                        item-value="code"
                        :items="businessTypeCodes"
                        v-model="businessType"
                        data-test="select-business-type"
                        :rules="orgBusinessTypeRules"
                        @change="onOrgBusinessTypeChange"
                        />
                    </v-col>
                    <v-col cols="6">
                        <v-select
                        filled
                        label="Business Size"
                        item-text="desc"
                        item-value="code"
                        :items="businessSizeCodes"
                        v-model="businessSize"
                        data-test="select-business-size"
                        :rules="orgBusinessSizeRules"
                        @change="onOrgBusinessTypeChange"
                        />
                    </v-col>
                </v-row>
              </v-expand-transition>
            </template>
        </v-form>
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

  @OrgModule.State('currentOrganization') public currentOrganization!: Organization

  @CodesModule.Action('getBusinessSizeCodes') private readonly getBusinessSizeCodes!: () => Promise<Code[]>
  @CodesModule.Action('getBusinessTypeCodes') private readonly getBusinessTypeCodes!: () => Promise<Code[]>
  @CodesModule.State('businessSizeCodes') private readonly businessSizeCodes!: Code[]
  @CodesModule.State('businessTypeCodes') private readonly businessTypeCodes!: Code[]

  private autoCompleteIsActive: boolean = false
  private autoCompleteSearchValue: string = ''

  $refs: {
    accountInformationForm: HTMLFormElement
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

  /*   @Watch('currentOrganization')
  oncurrentOrganizationChange (value: Organization, oldValue: Organization) {
    if (value.name !== oldValue.name && this.) {
      this.name = value.name
    }
  } */

  /** Emits an update message, so that the caller can ".sync" with it. */
  @Emit('update:org-business-type')
  private emitUpdatedOrgBusinessType () {
    const orgBusinessType: OrgBusinessType = {
      name: this.name,
      isBusinessAccount: this.isBusinessAccount,
      ...((this.govmAccount || this.isBusinessAccount) && { branchName: this.branchName }),
      ...(this.isBusinessAccount && { businessType: this.businessType, businessSize: this.businessSize, branchName: this.branchName })
    }
    const isFormValid = this.$refs.accountInformationForm?.validate()
    this.emitValid(isFormValid)
    return orgBusinessType
  }

  /** Emits the validity of the component. */
  /* tslint:disable:no-empty */
  @Emit('valid')
  private emitValid (valid: boolean): void { }

  /** Emits a clear errors event to parent (exclusive for premium linked account scenario). */
  /* tslint:disable:no-empty */
  @Emit('update:org-name-clear-errors')
  private clearErrors (): void { }

  async mounted () {
    try {
    // load business type and size codes
      await this.getBusinessSizeCodes()
      await this.getBusinessTypeCodes()
      if (this.currentOrganization) {
        this.name = this.currentOrganization.name
        // incase if the new account is a premium account, default business type to business account
        this.isBusinessAccount = this.currentOrganization.isBusinessAccount || this.currentOrganization.orgType !== Account.BASIC
        this.businessType = this.currentOrganization.businessType
        this.businessSize = this.currentOrganization.businessSize
        this.branchName = this.currentOrganization.branchName
      }
      // sync with parent tracking object on mount
      this.onOrgBusinessTypeChange()
    } catch (ex) {
      // eslint-disable-next-line no-console
      console.log(`error while loading account business type -  ${ex}`)
    }
  }

  private get enableOrgNameAutoComplete (): boolean {
    return LaunchDarklyService.getFlag(LDFlags.EnableOrgNameAutoComplete) || false
  }

  private setAutoCompleteSearchValue (autoCompleteSearchValue: string): void {
    if (this.enableOrgNameAutoComplete) {
      this.autoCompleteIsActive = false
      this.name = autoCompleteSearchValue
    }
  }

  // watches name and suggests auto completed names if it is a business account.
  // similar to PPR - watch logic
  onOrgNameChange () {
    // suggest auto complete values
    if (this.enableOrgNameAutoComplete && this.isBusinessAccount) {
      if (this.name) {
        this.autoCompleteSearchValue = this.name
      }
      this.autoCompleteIsActive = this.name !== ''
    }

    // Incase it is a premium linked account, we need to update org name and clear parent duplicate name error (exclusive for linked premium sceanrio)
    if (this.premiumLinkedAccount && this.bcolDuplicateNameErrorMessage) {
      this.clearErrors()
    }

    // emit the update value to the parent
    this.onOrgBusinessTypeChange()
  }

  onOrgBusinessTypeChange () {
    this.$nextTick(() => {
      this.emitUpdatedOrgBusinessType()
    })
  }
}
</script>

<style lang="scss" scoped>

.view-container {
    padding: 0 !important;
}
</style>
