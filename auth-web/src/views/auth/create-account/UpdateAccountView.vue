<template>
  <v-container class="view-container mt-10">
    <v-row justify="center">
      <v-col
        cols="12"
        sm="8"
        md="8"
        class="text-center pb-0"
      >
        <v-icon
          large
          color="info"
          class="font-weight-bold"
        >
          mdi-alert-circle-outline
        </v-icon>
        <h1 class="mt-2">
          Please Update Your Account Information
        </h1>
        <p
          v-sanitize="$t('updateAccountInformation' , {'name': currentOrganization.name })"
          class="text-center mt-8"
        />
      </v-col>
    </v-row>
    <v-row justify="center">
      <v-col
        cols="12"
        sm="9"
        md="8"
        class="text-center"
      >
        <v-card
          flat
          class="my-4 justify-space-between pa-8"
        >
          <v-card-title>
            <h2>Account Information</h2>
          </v-card-title>
          <v-card-text>
            <p style="text-align: justify">
              Do you want your account: <span class="font-weight-bold">{{ currentOrganization.name }}</span> associated
              with your personal name or business name?
            </p>
            <v-form
              ref="accountInformationForm"
              data-test="account-information-form"
            >
              <v-alert
                v-show="errorMessage"
                type="error"
                class="mb-6"
              >
                {{ errorMessage }}
              </v-alert>

              <v-radio-group
                v-model="isBusinessAccount"
                row
              >
                <v-row justify="space-between">
                  <v-col
                    md="12"
                    class="business-radio xs"
                  >
                    <v-radio
                      :key="false"
                      label="Individual Person Name"
                      :value="false"
                      data-test="radio-individual-account-type"
                      class="px-4 py-5"
                    />
                    <v-radio
                      :key="true"
                      label="Business Name"
                      :value="true"
                      data-test="radio-business-account-type"
                      class="px-4 py-5"
                    />
                  </v-col>
                </v-row>
              </v-radio-group>

              <div v-if="isBusinessAccount">
                <v-text-field
                  v-model="currentOrganization.name"
                  filled
                  label="Account Name"
                  disabled
                />
                <v-expand-transition class="branch-detail">
                  <v-text-field
                    v-model.trim="branchName"
                    filled
                    label="Branch/Division (Optional)"
                    data-test="input-branch-name"
                  />
                </v-expand-transition>
                <AccountBusinessTypePicker
                  @valid="checkOrgBusinessTypeValid"
                  @update:org-business-type="updateOrgBusinessType"
                />
              </div>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    <v-row justify="center">
      <v-col
        cols="12"
        sm="8"
        md="6"
        class="text-center"
      >
        <v-btn
          large
          color="primary"
          :disabled="!canSubmit"
          data-test="goto-create-account-button"
          @click="submit()"
        >
          Submit
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Action, State } from 'pinia-class'
import { Component, Vue, Watch } from 'vue-property-decorator'
import { CreateRequestBody, OrgBusinessType, Organization } from '@/models/Organization'
import AccountBusinessTypePicker from '@/components/auth/common/AccountBusinessTypePicker.vue'
import { Pages } from '@/util/constants'
import { useOrgStore } from '@/stores/org'

@Component({
  components: { AccountBusinessTypePicker }
})
export default class UpdateAccountView extends Vue {
  @State(useOrgStore) currentOrganization!: Organization
  @Action(useOrgStore) private updateOrg!: (requestBody: CreateRequestBody) => Promise<Organization>
  errorMessage: string = ''
  isBusinessAccount = null
  canSubmit = false
  branchName = ''
  orgBusinessType: OrgBusinessType = null

  private async mounted () {
    this.branchName = this.currentOrganization?.branchName
  }

  @Watch('isBusinessAccount')
  async onOrgBusinessTypeChange () {
    this.canSubmit = this.isBusinessAccount === false
  }

  checkOrgBusinessTypeValid (isValid) {
    this.canSubmit = isValid ? true : this.canSubmit
  }

  async submit () {
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
      await this.$router.push(`/${Pages.HOME}`)
    } catch (err) {
      switch (err.response.status) {
        case 409:
          this.errorMessage =
            'An account with this branch name already exists. Try a different branch name.'
          break
        case 400:
          this.errorMessage = 'Invalid account name'
          break
        default:
          this.errorMessage =
            'An error occurred while attempting to update your account.'
      }
    }
  }

  updateOrgBusinessType (orgBusinessType: OrgBusinessType) {
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
