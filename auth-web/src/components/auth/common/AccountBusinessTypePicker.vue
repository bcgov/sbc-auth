<template>
  <v-container class="view-container" v-can:EDIT_BUSINESS_INFO.disable.card>
    <v-fade-transition>
      <div v-if="isLoading" class="loading-inner-container">
        <v-progress-circular
          size="50"
          width="5"
          color="primary"
          :indeterminate="isLoading"
        />
      </div>
    </v-fade-transition>
    <div class="account-business-type-container" v-if="!isLoading">
      <v-form ref="accountInformationForm" data-test="account-information-form">
        <template>
          <v-expand-transition class="business-account-type-details">
            <v-row
              justify="space-between"
              data-test="business-account-type-details"
            >
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
                  :menu-props="{ auto: true, offsetY: true, maxHeight: 400 }"
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
                  :menu-props="{ auto: true, offsetY: true, maxHeight: 400 }"
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
import AccountChangeMixin from '@/components/auth/mixins/AccountChangeMixin.vue'
import { Code } from '@/models/Code'
import { OrgBusinessType, Organization } from '@/models/Organization'
import { Component, Emit, Mixins, Prop, Watch } from 'vue-property-decorator'
import { namespace } from 'vuex-class'

const OrgModule = namespace('org')
const CodesModule = namespace('codes')

@Component({
  components: {}
})
export default class AccountBusinessTypePicker extends Mixins(
  AccountChangeMixin
) {
  @Prop({ default: null }) errorMessage: string
  @Prop({ default: false }) saving: boolean

  @OrgModule.State('currentOrganization')
  public currentOrganization!: Organization

  @CodesModule.Action('getBusinessSizeCodes')
  private readonly getBusinessSizeCodes!: () => Promise<Code[]>
  @CodesModule.Action('getBusinessTypeCodes')
  private readonly getBusinessTypeCodes!: () => Promise<Code[]>
  @CodesModule.State('businessSizeCodes')
  private readonly businessSizeCodes!: Code[]
  @CodesModule.State('businessTypeCodes')
  private readonly businessTypeCodes!: Code[]

  private isLoading = false

  $refs: {
    businessType: HTMLFormElement
    businessSize: HTMLFormElement
  }

  private businessType = ''
  private businessSize = ''

  // Input field rules
  private readonly orgBusinessTypeRules = [
    v => !!v || 'A business type is required'
  ]
  private readonly orgBusinessSizeRules = [
    v => !!v || 'A business size is required'
  ]

  /** Emits an update message, so that we can sync with parent */
  @Emit('update:org-business-type')
  private emitUpdatedOrgBusinessType () {
    const orgBusinessType: OrgBusinessType = {
      businessType: this.businessType,
      businessSize: this.businessSize
    }
    return orgBusinessType
  }

  /** Emits the validity of the component. */
  @Emit('valid')
  private emitValid () {
    return (
      !this.$refs.businessType?.hasError && !this.$refs.businessSize?.hasError
    )
  }

  async mounted () {
    this.setAccountChangedHandler(this.setup)
    await this.setup()
  }
  public async setup () {
    try {
      // load business type and size codes
      this.isLoading = true
      await this.getBusinessSizeCodes()
      await this.getBusinessTypeCodes()
      // incase if the new account is a premium account, default business type to business account
      this.businessType = this.currentOrganization.businessType
      this.businessSize = this.currentOrganization.businessSize
    } catch (ex) {
      // eslint-disable-next-line no-console
      console.log(`error while loading account business type -  ${ex}`)
    } finally {
      this.isLoading = false
    }
  }

  @Watch('businessType')
  @Watch('businessSize')
  async onOrgBusinessTypeChange () {
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
</style>
