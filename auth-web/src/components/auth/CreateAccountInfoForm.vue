<template>
  <div>
    <div>
      <v-form ref="createAccountInfoForm">
        <v-radio-group class="mt-0 mb-4 pt-0" v-model="teamType" :mandatory="true">
          <v-radio color="primary" class="mb-3" label="I manage my own business" value="BASIC" data-test="select-manage-own-business" />
          <v-radio color="primary" label="I manage multiple businesses on behalf of my clients" value="PREMIUM" data-test="select-manage-multiple-business" />
        </v-radio-group>

        <v-alert type="error" v-show="errorMessage">{{errorMessage}}</v-alert>

        <v-text-field filled
          label="Account Name"
          v-model.trim="teamName"
          :rules="teamNameRules"
          persistent-hint
          :disabled="saving"
          :hint="teamType === 'BASIC' ? 'Example: Your Business Name' : 'Example: Your Management Company or Law Firm Name'"/>
        <v-row>
          <v-col cols="12" class="form__btns pb-0">
            <v-btn
              large
              color="primary"
              class="mr-2"
              :loading = "saving"
              :disabled="!isFormValid() || saving"
              @click="save"
              data-test="save-button">
              Save and Continue
            </v-btn>
            <v-btn large depressed color="default" :disable="saving" @click="cancel" data-test="cancel-button">
              Cancel
            </v-btn>
          </v-col>
        </v-row>
      </v-form>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import { CreateRequestBody, Member, Organization } from '@/models/Organization'
import { mapActions, mapState } from 'vuex'
import OrgModule from '@/store/modules/org'
import { getModule } from 'vuex-module-decorators'

@Component({
  computed: {
    ...mapState('org', ['currentOrganization', 'orgCreateMessage'])
  },
  methods: {
    ...mapActions('org', ['createOrg', 'syncMembership', 'syncOrganization'])
  }
})
export default class CreateAccountInfoForm extends Vue {
    private orgStore = getModule(OrgModule, this.$store)
    private teamName: string = ''
    private teamType: string = 'BASIC'
    private errorMessage: string = ''
    private saving = false
    private readonly createOrg!: (requestBody: CreateRequestBody) => Promise<Organization>
    private readonly syncMembership!: (orgId: number) => Promise<Member>
    private readonly syncOrganization!: (orgId: number) => Promise<Organization>
    private readonly orgCreateMessage: string
    private readonly currentOrganization!: Organization

    $refs: {
      createAccountInfoForm: HTMLFormElement
    }

    private readonly teamNameRules = [
      v => !!v || 'An account name is required']

    private isFormValid (): boolean {
      return !!this.teamName
    }

    private async save () {
      // Validate form, and then create an team with this user a member
      if (this.isFormValid()) {
        const createRequestBody: CreateRequestBody = {
          name: this.teamName,
          typeCode: this.teamType === 'BASIC' ? 'IMPLICIT' : 'EXPLICIT'
        }
        try {
          this.saving = true
          const organization = await this.createOrg(createRequestBody)
          await this.syncOrganization(organization.id)
          await this.syncMembership(organization.id)
          this.$store.commit('updateHeader')
          this.redirectToNext(organization)
        } catch (err) {
          this.saving = false
          switch (err.response.status) {
            case 409:
              this.errorMessage = 'An account with this name already exists. Try a different account name.'
              break
            case 400:
              if (err.response.data.code === 'MAX_NUMBER_OF_ORGS_LIMIT') {
                this.errorMessage = 'Maximum number of accounts reached'
              } else {
                this.errorMessage = 'Invalid account name'
              }
              break
            default:
              this.errorMessage = 'An error occurred while attempting to create your account.'
          }
        }
      }
    }

    private cancel () {
      this.$router.push({ path: '/home' })
    }

    private redirectToNext (organization?: Organization) {
      this.$router.push({ path: `/account/${organization.id}/` })
    }
}
</script>

<style lang="scss" scoped>
  @import '$assets/scss/theme.scss';

  // Tighten up some of the spacing between rows
  [class^="col"] {
    padding-top: 0;
    padding-bottom: 0;
  }

  .form__btns {
    display: flex;
    justify-content: flex-end;
  }
</style>
