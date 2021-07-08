<template>
  <v-container class="view-container mt-10">
    <v-row justify="center">
      <v-col cols="12" sm="8" md="8" class="text-center pb-0">
        <v-icon large color="info" class="font-weight-bold">mdi-alert-circle-outline</v-icon>
        <h1 class="mt-2">Please Update Your Account Information</h1>
        <p class="text-center mt-8"
           v-html="$t('updateAccountInformation' , {'name': currentOrganization.name })" />
      </v-col>
    </v-row>
    <v-row justify="center">
      <v-col cols="12" sm="9" md="8" class="text-center">
        <v-card flat class="my-4 justify-space-between pa-8">
          <v-card-title>
            <h2>Account Information</h2>
          </v-card-title>
          <v-card-text>
            <p style="text-align: justify">
              Do you want your account: <span class="font-weight-bold">{{ currentOrganization.name }}</span> associated
              with your personal name or business name?
            </p>
            <v-form ref="accountInformationForm" data-test="account-information-form">

              <v-alert type="error" class="mb-6" v-show="errorMessage">
                {{ errorMessage }}
              </v-alert>

              <v-radio-group
                row
                v-model="isBusinessAccount"
              >
                <v-row justify="space-between">
                  <v-col xs="12" md="12" class="business-radio">
                    <v-radio
                      label="Individual Person Name"
                      :key="false"
                      :value="false"
                      data-test="radio-individual-account-type"
                      class="px-4 py-5"
                      @change="onOrgBusinessTypeChange(true)"
                    ></v-radio>
                    <v-radio
                      label="Business Name"
                      :key="true"
                      :value="true"
                      data-test="radio-business-account-type"
                      class="px-4 py-5"
                      @change="onOrgBusinessTypeChange(true)"
                    ></v-radio>
                  </v-col>
                </v-row>
              </v-radio-group>

              <div v-if="isBusinessAccount">
                <v-text-field
                  filled
                  label="Account Name"
                  disabled
                  v-model="currentOrganization.name"
                >
                </v-text-field>
                <v-expand-transition class="branch-detail">
                  <v-text-field
                    filled
                    label="Branch/Division (Optional)"
                    v-model.trim="branchName"
                    data-test="input-branch-name"
                    v-on:keyup="onOrgBusinessTypeChange()"
                  />
                </v-expand-transition>
                <AccountBusinessTypePicker
                  @valid="checkOrgBusinessTypeValid"
                  @update:org-business-type="updateOrgBusinessType">

                </AccountBusinessTypePicker>
              </div>

            </v-form>
          </v-card-text>

        </v-card>
      </v-col>
    </v-row>
    <v-row justify="center">
      <v-col cols="12" sm="8" md="6" class="text-center">
        <v-btn large color="primary" :disabled="!canSubmit" data-test="goto-create-account-button" @click="submit()">
          Submit
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import { CreateRequestBody, OrgBusinessType, Organization } from '@/models/Organization'
import AccountBusinessType from '@/components/auth/common/AccountBusinessType.vue'
import AccountBusinessTypePicker from '@/components/auth/common/AccountBusinessTypePicker.vue'
import { namespace } from 'vuex-class'

const OrgModule = namespace('org')

@Component({
  components: { AccountBusinessTypePicker, AccountBusinessType }
})
export default class UpdateAccountView extends Vue {
  @OrgModule.State('currentOrganization') private currentOrganization!: Organization
  @OrgModule.Action('syncOrganization') private syncOrganization!: (orgId: number) => Promise<Organization>
  @OrgModule.Action('isOrgNameAvailable') private readonly isOrgNameAvailable!: (orgName: string) => Promise<boolean>
  @OrgModule.Action('updateOrg') private updateOrg!: (requestBody: CreateRequestBody) => Promise<Organization>
  private static readonly DUPL_ERROR_MESSAGE = 'An account with this name already exists. Try a different account name.'
  private errorMessage: string = ''
  private isBusinessAccount = null
  private canSubmit = false
  private branchName = ''
  private orgBusinessType: OrgBusinessType = null

  private async mounted () {
    if (this.currentOrganization?.branchName) {
      this.branchName = this.currentOrganization.branchName
    }
  }

  async onOrgBusinessTypeChange (clearOrgName: boolean = false) {
    await this.$nextTick()
    // eslint-disable-next-line no-console
    console.log('-------', this.isBusinessAccount)
    if (this.isBusinessAccount === false) {
      this.canSubmit = true
    } else {
      this.canSubmit = false
    }
  }

  private checkOrgBusinessTypeValid (isValid) {
    // eslint-disable-next-line no-console
    console.log('-----------isValid---', isValid)
    if (isValid) {
      this.canSubmit = true
    }
  }

  private async submit () {
    let createRequestBody: CreateRequestBody = {
      isBusinessAccount: this.isBusinessAccount
    }
    if (this.isBusinessAccount) {
      createRequestBody.branchName = this.branchName
      createRequestBody.businessSize = this.orgBusinessType.businessSize
      createRequestBody.businessType = this.orgBusinessType.businessType
    }
    try {
      await this.updateOrg(createRequestBody)
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error(error)
    }
  }

  private updateOrgBusinessType (orgBusinessType: OrgBusinessType) {
    // eslint-disable-next-line no-console
    console.log('---------', orgBusinessType)
    this.orgBusinessType = orgBusinessType
  }
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';

.view-container {
  padding: 0 !important;
}

.business-radio {
  display: flex;

  .v-radio {
    padding: 10px;
    background-color: rgba(0, 0, 0, .06);
    min-width: 50%;
    border: 1px rgba(0, 0, 0, .06) !important;
  }

  .v-radio.theme--light.v-item--active {
    border: 1px solid var(--v-primary-base) !important;
    background-color: $BCgovInputBG !important;
  }
}
</style>
