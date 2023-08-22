<template>
  <v-container
    v-can:EDIT_BUSINESS_INFO.disable.card
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
      <v-form
        ref="accountInformationForm"
        data-test="account-information-form"
      >
        <v-expand-transition class="business-account-type-details">
          <v-row
            justify="space-between"
            data-test="business-account-type-details"
          >
            <v-col cols="6">
              <v-select
                ref="businessType"
                v-model="businessType"
                filled
                label="Business Type"
                item-text="desc"
                item-value="code"
                :items="businessTypeCodes"
                data-test="select-business-type"
                :rules="orgBusinessTypeRules"
                :menu-props="{ auto: true, offsetY: true, maxHeight: 400 }"
              />
            </v-col>
            <v-col cols="6">
              <v-select
                ref="businessSize"
                v-model="businessSize"
                filled
                label="Business Size"
                item-text="desc"
                item-value="code"
                :items="businessSizeCodes"
                data-test="select-business-size"
                :rules="orgBusinessSizeRules"
                :menu-props="{ auto: true, offsetY: true, maxHeight: 400 }"
              />
            </v-col>
          </v-row>
        </v-expand-transition>
      </v-form>
    </div>
  </v-container>
</template>

<script lang="ts">
import { Action, State } from 'pinia-class'
import {
  Component,
  Emit,
  Mixins,
  Prop,
  Watch
} from 'vue-property-decorator'
import { OrgBusinessType, Organization } from '@/models/Organization'
import AccountChangeMixin from '@/components/auth/mixins/AccountChangeMixin.vue'
import { Code } from '@/models/Code'
import { useCodesStore } from '@/store/codes'
import { useOrgStore } from '@/store/org'

@Component({
  components: {}
})
export default class AccountBusinessTypePicker extends Mixins(
  AccountChangeMixin
) {
  @Prop({ default: null }) errorMessage: string
  @Prop({ default: false }) saving: boolean

  @State(useOrgStore) public currentOrganization!: Organization

  @Action(useCodesStore) readonly getBusinessSizeCodes!: () => Promise<Code[]>
  @Action(useCodesStore) readonly getBusinessTypeCodes!: () => Promise<Code[]>
  @State(useCodesStore) readonly businessSizeCodes!: Code[]
  @State(useCodesStore) readonly businessTypeCodes!: Code[]

  isLoading = false

  $refs: {
    businessType: HTMLFormElement
    businessSize: HTMLFormElement
  }

  businessType = ''
  businessSize = ''

  // Input field rules
  readonly orgBusinessTypeRules = [
    v => !!v || 'A business type is required'
  ]
  readonly orgBusinessSizeRules = [
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
