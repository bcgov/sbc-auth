<template>
  <v-form ref="createAccountInfoForm" lazy-validation>
      <v-row align="end">
        <v-col cols="12" align-self="end">
          <h4>BC Online Prime Contact Details
            <v-tooltip top>
              <template v-slot:activator="{ on }">
                <v-btn icon color="grey darken-2" small v-on="on" class="help-tooltip-btn">
                  <v-icon>mdi-help-circle-outline</v-icon>
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
                  v-model.trim="username"
                  :rules="usernameRules"
                  req
                  dense
          >
          </v-text-field>
        </v-col>
        <v-col cols="4" class="py-0 mb-4">
          <v-text-field
                  filled
                  label="Password"
                  v-model.trim="password"
                  type="password"
                  req
                  dense
                  :rules="passwordRules"
          >
          </v-text-field>
        </v-col>
        <v-col cols="4" class="py-0 mb-4">
          <v-btn
            x-large
            color="primary"
            @click="linkAccounts()"
            data-test="dialog-save-button"
            :loading="isLoading"
            :disabled='!isFormValid() || isLoading'
          >
            <strong>Link Accounts</strong>
          </v-btn>
        </v-col>
      </v-row>
    <v-alert type="error" class="mb-6"
             v-show="errorMessage">
      {{errorMessage}}
    </v-alert>
  </v-form>
</template>

<script lang="ts">
import { BcolAccountDetails, BcolProfile } from '@/models/bcol'
import { Component, Emit, Prop, Vue } from 'vue-property-decorator'
import { mapActions, mapState } from 'vuex'
@Component({
  name: 'BcolLogin',
  computed: {
    ...mapState('org', ['currentOrganization'])
  },
  methods: {
    ...mapActions('org', ['createOrg', 'syncMembership', 'syncOrganization', 'validateBcolAccount'])
  }
})
export default class BcolLogin extends Vue {
  private username: string = ''
  private password: string = ''
  private errorMessage: string = ''
  private isLoading: boolean = false
  private readonly validateBcolAccount!: (bcolProfile: BcolProfile) => Promise<BcolAccountDetails>

  private isFormValid (): boolean {
    return !!this.username && !!this.password
  }
  private usernameRules = [
    v => !!v.trim() || 'Username is required'
  ]

  private passwordRules = [
    value => !!value || 'Password is required'
  ]

  private async linkAccounts () {
    this.isLoading = true
    // Validate form, and then create an team with this user a member
    if (this.isFormValid()) {
      const bcolProfile: BcolProfile = {
        userId: this.username,
        password: this.password
      }
      try {
        const bcolAccountDetails = await this.validateBcolAccount(bcolProfile)
        this.isLoading = false
        if (bcolAccountDetails) { // TODO whats the success status
          this.$emit('account-link-successful', { bcolProfile, bcolAccountDetails })
        }
      } catch (err) {
        this.isLoading = false
        switch (err.response.status) {
          case 400:
            this.errorMessage = err.response.data.message
            break
          default:
            this.errorMessage = 'An error occurred while attempting to create your account.'
        }
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.help-tooltip-btn {
  margin-top: -8px;
}
</style>
