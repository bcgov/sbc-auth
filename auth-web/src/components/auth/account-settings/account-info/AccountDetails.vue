<template>
  <div>
    <v-form ref="editAccountForm">
      <v-card elevation="0">
        <div class="account-label">
          <div class="nav-list-title font-weight-bold" data-test="title">Account Details</div>
          <div v-if="isLoading" class="loading-inner-container loading-center">
            <v-progress-circular
              size="50"
              width="5"
              color="primary"
              :indeterminate="isLoading"
            />
          </div>

          <div class="details" v-else>
            <div v-if="viewOnlyMode" class="view-only">
              <div class="with-change-icon">
                <div>
                  <span class="font-weight-bold">Account Name:</span>
                  {{ orgName }}
                </div>
                <div
                  v-can:CHANGE_ORG_NAME.disable
                  v-if="!nameChangeNotAllowed && viewOnlyMode"
                >
                  <span
                    class="primary--text cursor-pointer"
                    @click="
                      $emit('update:viewOnlyMode', {
                        component: 'account',
                        mode: false
                      })
                    "
                    data-test="btn-edit"
                  >
                    <v-icon color="primary" size="20"> mdi-pencil</v-icon>
                    Change
                  </span>
                </div>
              </div>
              <div v-if="accountTypeBusiness">
                <span class="font-weight-bold">Branch/Division:</span>
                {{ branchName != '' ? branchName : '-' }}
              </div>

              <div v-if="accountTypeBusiness">
                <span class="font-weight-bold">Business Type:</span>
                {{ getBusinessTypeLabel }}
              </div>

              <div v-if="accountTypeBusiness">
                <span class="font-weight-bold">Business Size:</span>
                {{ getBusinessSizeLabel }}
              </div>
            </div>
            <div v-else>
              <account-business-type
                :saving="false"
                @update:org-business-type="updateOrgBusinessType"
                @valid="checkOrgBusinessTypeValid"
                :isEditAccount="true"
              >
              </account-business-type>

              <v-card-actions class="pt-1 pr-0">
                <v-spacer></v-spacer>
                <v-btn
                  large
                  class="save-btn px-9"
                  color="primary"
                  :loading="false"
                  aria-label="Save Account Information"
                  @click="updateDetails()"
                >
                  <span class="save-btn__label">Save</span>
                </v-btn>
                <v-btn
                  outlined
                  large
                  depressed
                  class="ml-2 px-9"
                  color="primary"
                  aria-label="Cancel Account Information"
                  @click="cancelEdit()"
                  data-test="reset-button"
                  >Cancel</v-btn
                >
              </v-card-actions>
            </div>
          </div>
        </div>
      </v-card>
    </v-form>
  </div>
</template>

<script lang="ts">
import { Component, Emit, Mixins, Prop, Watch } from 'vue-property-decorator'
import AccountBusinessType from '@/components/auth/common/AccountBusinessType.vue'
import AccountChangeMixin from '@/components/auth/mixins/AccountChangeMixin.vue'

import { Code } from '@/models/Code'
import { OrgBusinessType } from '@/models/Organization'
import { namespace } from 'vuex-class'

const CodesModule = namespace('codes')

@Component({
  components: {
    AccountBusinessType
  }
})
export default class AccountDetails extends Mixins(AccountChangeMixin) {
  @Prop({ default: null }) accountDetails: OrgBusinessType
  @Prop({ default: true }) viewOnlyMode: boolean

  @Prop({ default: false }) isBusinessAccount: boolean
  @Prop({ default: false }) nameChangeNotAllowed: boolean

  // @Prop({ default: null }) updateOrgBusinessType: any
  @CodesModule.Action('getBusinessSizeCodes')
  private readonly getBusinessSizeCodes!: () => Promise<Code[]>
  @CodesModule.Action('getBusinessTypeCodes')
  private readonly getBusinessTypeCodes!: () => Promise<Code[]>
  @CodesModule.State('businessSizeCodes')
  private readonly businessSizeCodes!: Code[]
  @CodesModule.State('businessTypeCodes')
  private readonly businessTypeCodes!: Code[]

  public orgName = ''
  public branchName = ''
  public accountTypeBusiness = false
  private isOrgBusinessTypeValid = false
  public isLoading =false

  public orgBusinessType: OrgBusinessType = {
    businessType: '',
    businessSize: ''
  }

  $refs: {
    editAccountForm: HTMLFormElement
  }

  @Watch('accountDetails', { deep: true })
  onAccountDetailsChange () {
    this.updateAccountDetails()
  }
  @Watch('isBusinessAccount')
  onAccountTypeChange (businessType) {
    this.accountTypeBusiness = businessType
  }

  updateAccountDetails () {
    this.orgName = this.accountDetails?.name
    this.branchName = this.accountDetails?.branchName
    this.orgBusinessType.businessType = this.accountDetails?.businessType
    this.orgBusinessType.businessSize = this.accountDetails?.businessSize
    this.accountTypeBusiness = this.isBusinessAccount
  }

  get getBusinessTypeLabel () {
    return this.getCodeLabel(
      this.businessTypeCodes,
      this.orgBusinessType.businessType
    )
  }

  get getBusinessSizeLabel () {
    return this.getCodeLabel(
      this.businessSizeCodes,
      this.orgBusinessType.businessSize
    )
  }

  getCodeLabel (codeList, code) {
    const codeArray = codeList.filter(type => type.code === code)
    return (codeArray && codeArray[0] && codeArray[0]?.desc) || ''
  }

  @Emit('update:viewOnlyMode')
  cancelEdit () {
    this.updateAccountDetails()
    return {
      component: 'account',
      mode: true
    }
  }

  public updateOrgBusinessType (orgBusinessType: OrgBusinessType) {
    this.orgBusinessType = orgBusinessType
  }
  // emit to par3ent only on save click
  // taking account name  an dbrqanch from this and business type details from child component
  // arrange data and emit to parent on save click
  @Emit('update:updateAndSaveAccountDetails')
  public updateDetails () {
    if (this.isOrgBusinessTypeValid) {
      return this.orgBusinessType
    }
  }

  private checkOrgBusinessTypeValid (isValid) {
    this.isOrgBusinessTypeValid = !!isValid
  }

  private async mounted () {
    this.isLoading = true
    // to show businsss type valeu neeed to get all code
    await this.getBusinessTypeCodes()
    await this.getBusinessSizeCodes()
    this.updateAccountDetails()
    this.isLoading = false
  }
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';
.business-radio {
  display: flex;
  width: 90%;
  .v-radio {
    padding: 10px;
    background-color: rgba(0, 0, 0, 0.06);
    min-width: 50%;
    border: 1px rgba(0, 0, 0, 0.06) !important;
  }

  .v-radio.theme--light.v-item--active {
    border: 1px solid var(--v-primary-base) !important;
    background-color: $BCgovInputBG !important;
  }
}

</style>
