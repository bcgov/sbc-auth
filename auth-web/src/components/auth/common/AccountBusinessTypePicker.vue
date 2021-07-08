<template>
    <v-container class="view-container" >
      <v-fade-transition>
      <div v-if="isLoading" class="loading-inner-container">
        <v-progress-circular size="50" width="5" color="primary" :indeterminate="isLoading"/>
      </div>
      </v-fade-transition>
      <div class="account-business-type-container" v-if="!isLoading">
        <v-form ref="accountInformationForm" data-test="account-information-form">
            <template >
              <v-expand-transition class="business-account-type-details">
                <v-row justify="space-between" data-test="business-account-type-details">
                    <v-col cols="6" >
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
export default class AccountBusinessTypePicker extends Vue {
  @Prop({ default: null }) errorMessage: string
  @Prop({ default: false }) saving: boolean

  @OrgModule.State('currentOrganization') public currentOrganization!: Organization

  @CodesModule.Action('getBusinessSizeCodes') private readonly getBusinessSizeCodes!: () => Promise<Code[]>
  @CodesModule.Action('getBusinessTypeCodes') private readonly getBusinessTypeCodes!: () => Promise<Code[]>
  @CodesModule.State('businessSizeCodes') private readonly businessSizeCodes!: Code[]
  @CodesModule.State('businessTypeCodes') private readonly businessTypeCodes!: Code[]

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
  private readonly orgBusinessTypeRules = [v => !!v || 'A business type is required']
  private readonly orgBusinessSizeRules = [v => !!v || 'A business size is required']

  /** Emits an update message, so that we can sync with parent */
  @Emit('update:org-business-type')
  private emitUpdatedOrgBusinessType () {
    const orgBusinessType: OrgBusinessType = { businessType: this.businessType, businessSize: this.businessSize }
    return orgBusinessType
  }

  /** Emits the validity of the component. */
  @Emit('valid')
  private emitValid () {
    return !this.$refs.businessType?.hasError && !this.$refs.businessSize?.hasError
  }

  async mounted () {
    try {
    // load business type and size codes
      this.isLoading = true
      await this.getBusinessSizeCodes()
      await this.getBusinessTypeCodes()
      if (this.currentOrganization.name) {
        // incase if the new account is a premium account, default business type to business account
        this.isBusinessAccount = this.currentOrganization.isBusinessAccount
        this.businessType = this.currentOrganization.businessType
        this.businessSize = this.currentOrganization.businessSize
        this.branchName = this.currentOrganization.branchName
      } else {
        this.isBusinessAccount = this.currentOrganization.orgType !== Account.BASIC
      }
    } catch (ex) {
      // eslint-disable-next-line no-console
      console.log(`error while loading account business type -  ${ex}`)
    } finally {
      this.isLoading = false
    }
  }

  async onOrgBusinessTypeChange () {
    // eslint-disable-next-line no-console
    console.log('-------value--------')
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
