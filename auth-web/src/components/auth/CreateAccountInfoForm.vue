<template>
      <v-form ref="createAccountInfoForm" lazy-validation>
        <div class="view-container">
            <h1 class="mb-5">Account Settings</h1>
            <p class="intro-text">You must be the Prime Contact to link this account with your existing BC Online account.</p>
        </div>
        <div>
        <v-row>
          <v-col cols="12">
            <h4 class="mb-5">BC Online Prime Contact Details
              <v-tooltip v-model="show" top>
                <template v-slot:activator="{ on }">
                  <v-btn icon v-on="on">
                    <v-icon color="grey lighten-1">mdi-help-circle-outline</v-icon>
                  </v-btn>
                </template>
                <span>BC Online Prime Contacts are users who have authority to manage account settings for a BC Online Account.</span>
              </v-tooltip></h4>
          </v-col>
        </v-row>

        <v-row>
          <v-col cols="4" class="py-0 mb-4">
            <v-text-field
                    filled
                    label="User ID"
                    req
            >
            </v-text-field>
          </v-col>
          <v-col cols="4" class="py-0 mb-4">
            <v-text-field
                    filled
                    label="Password"
            >
            </v-text-field>
          </v-col>
          <v-col cols="4" class="py-0 mb-4">
            <v-btn large color="primary" @click="close()" data-test="dialog-ok-button">Link Accounts</v-btn>
          </v-col>
        </v-row>
        </div></div>
      </v-form>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import { CreateRequestBody, Member, Organization } from '@/models/Organization'
import { mapActions, mapState } from 'vuex'
import OrgModule from '@/store/modules/org'
import { getModule } from 'vuex-module-decorators'

@Component({
  computed: {
    ...mapState('org', ['currentOrganization'])
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
    private readonly currentOrganization!: Organization
    @Prop() stepForward!: () => void
    @Prop() stepBack!: () => void

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
          if (!this.stepForward) {
            this.redirectToNext(organization)
          } else {
            this.stepForward()
          }
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
      if (this.stepBack) {
        this.stepBack()
      } else {
        this.$router.push({ path: '/home' })
      }
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
