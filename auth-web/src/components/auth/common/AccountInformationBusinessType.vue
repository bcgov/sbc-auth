<template>
    <v-container class="view-container">
        <p class="mb-9" v-if="!govmAccount">
                {{ $t('accountBusinessTypeText') }}
        </p>
        <v-form ref="accountInformationForm" data-test="account-information-form">
            <v-radio-group
            row
            v-model="orgBusinessTypeLocal.isBusinessAccount"
            mandatory
            >
                <v-row justify="space-between">
                    <v-col cols="6">
                        <v-radio
                        :label=AccountBusinessType.INDIVIDUAL_PERSON_NAME
                        :value=false
                        data-test="radio-individual-account-type"
                        ></v-radio>
                    </v-col>
                    <v-col cols="6">
                        <v-radio
                        :label=AccountBusinessType.BUSINESS_NAME
                        :value=true
                        data-test="radio-business-account-type"
                        ></v-radio>
                    </v-col>
                </v-row>
            </v-radio-group>
            <fieldset class="auto-complete-relative account-name" data-test="account-name">
                <legend class="mb-3"  v-if="govmAccount">Enter Ministry Information for this account</legend>
                <legend class="mb-3"  v-else-if="!orgBusinessTypeLocal.isBusinessAccount">Account Name</legend>
                <v-slide-y-transition>
                    <div v-show="errorMessage">
                    <v-alert type="error" icon="mdi-alert-circle-outline">{{ errorMessage }}</v-alert>
                    </div>
                </v-slide-y-transition>
                <v-text-field
                filled
                :label="govmAccount ? 'Ministry Name' : orgBusinessTypeLocal.isBusinessAccount ? 'Legal Business Name' : 'Account Name'"
                v-model.trim="orgBusinessTypeLocal.name"
                :rules="orgNameRules"
                :disabled="saving"
                data-test="input-org-name"
                :readonly="govmAccount"
                autocomplete="off"
                />
                <org-name-auto-complete
                v-if="enableOrgNameAutoComplete && orgBusinessTypeLocal.isBusinessAccount"
                :searchValue="autoCompleteSearchValue"
                :setAutoCompleteIsActive="autoCompleteIsActive"
                @auto-complete-value="setAutoCompleteSearchValue">
                </org-name-auto-complete>
            </fieldset>
            <fieldset class="branch-detail" data-test="branch-detail" v-if="govmAccount || orgBusinessTypeLocal.isBusinessAccount">
                <v-text-field
                filled
                :label="govmAccount ? 'Branch/Division (If applicable)' : 'Branch/Division (If optional)'"
                v-model.trim="orgBusinessTypeLocal.branchName"
                :disabled="saving"
                data-test="input-branch-name"
                :readonly="govmAccount"
                />
            </fieldset>
            <fieldset class="business-account-type-details"  data-test="business-account-type-details" v-if="orgBusinessTypeLocal.isBusinessAccount">
                <v-row justify="space-between">
                    <v-col cols="6">
                        <v-select
                        filled
                        label="Business Type"
                        item-text="text"
                        item-value="value"
                        :items="BusinessType"
                        v-model="orgBusinessTypeLocal.businessType"
                        data-test="select-business-type"
                        :rules="orgBusinessTypeRules"
                        />
                    </v-col>
                    <v-col cols="6">
                        <v-select
                        filled
                        label="Business Size"
                        item-text="text"
                        item-value="value"
                        :items="BusinessType"
                        v-model="orgBusinessTypeLocal.businessSize"
                        data-test="select-business-size"
                        :rules="orgBusinessSizeRules"
                        />
                    </v-col>
                </v-row>
            </fieldset>
        </v-form>
    </v-container>
</template>

<script lang="ts">
import { AccountBusinessType, LDFlags } from '@/util/constants'
import { Component, Emit, Prop, Vue, Watch } from 'vue-property-decorator'
import { OrgBusinessType, Organization } from '@/models/Organization'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import OrgNameAutoComplete from '@/views/auth/OrgNameAutoComplete.vue'
import { namespace } from 'vuex-class'

const OrgModule = namespace('org')

@Component({
  components: {
    OrgNameAutoComplete
  }
})
export default class AccountInformationBusinessType extends Vue {
  @Prop({ default: false }) govmAccount: boolean
  @Prop({ default: null }) errorMessage: string
  @Prop({ default: false }) saving: boolean

  @OrgModule.State('currentOrganization') public currentOrganization!: Organization

  private autoCompleteIsActive: boolean = false
  private autoCompleteSearchValue: string = ''
  private AccountBusinessType= AccountBusinessType

  $refs: {
    accountInformationForm: HTMLFormElement
  }

  // A local (working) copy of the address, to contain the fields edited by the component (ie, the model).
  private orgBusinessTypeLocal : OrgBusinessType = {
    name: '',
    isBusinessAccount: '',
    branchName: '',
    businessType: '',
    businessSize: ''
  }

  // Input field rules
  private orgNameRules = [v => !!v || 'An account name is required']
  private orgBusinessTypeRules = [v => !!v || 'A business type is required']
  private orgBusinessSizeRules = [v => !!v || 'A business size is required']

  private BusinessType = [
    {
      text: 'text1',
      value: 1
    },
    {
      text: 'text2',
      value: 2
    }
  ]

  mounted () {
    if (this.currentOrganization) {
      this.orgBusinessTypeLocal = { ...this.currentOrganization }
    }
  }

  /** Emits an update message, so that the caller can ".sync" with it. */
  @Emit('update:org-business-type')
  private emitAccountInfo (address: object): void { }

  /** Emits the validity of the component. */
  @Emit('valid')
  private emitValid (valid: boolean): void { }

  private get enableOrgNameAutoComplete (): boolean {
    return LaunchDarklyService.getFlag(LDFlags.EnableOrgNameAutoComplete) || false
  }

  private setAutoCompleteSearchValue (autoCompleteSearchValue: string): void {
    if (this.enableOrgNameAutoComplete) {
      this.autoCompleteIsActive = false
      this.orgBusinessTypeLocal['name'] = autoCompleteSearchValue
    }
  }

  @Watch('orgBusinessTypeLocal.name')
  getAutoCompleteValues (val: string) {
    if (this.enableOrgNameAutoComplete) {
      if (val) {
        this.autoCompleteSearchValue = val
      }
      this.autoCompleteIsActive = val !== ''
    }
  }

  @Watch('orgBusinessTypeLocal', { deep: true })
  getLocalOrganization (newVal, oldVal) {
    this.emitAccountInfo(this.orgBusinessTypeLocal)
    if (oldVal.name) {
      this.emitValid(this.$refs.accountInformationForm?.validate())
    }
  }

  public validateNow () {
    const isFormValid = this.$refs.accountInformationForm?.validate()
    this.emitValid(isFormValid)
  }
}
</script>

<style lang="scss" scoped>

.view-container {
    padding: 0 !important;
}
</style>
