<template>
  <v-card>
    <v-card-title>
      <v-layout class="header">
        <h2>Invite Team Members</h2>
        <v-btn icon>
          <v-icon @click="cancel()">close</v-icon>
        </v-btn>
      </v-layout>
    </v-card-title>
    <v-card-text>

      <p class="subtitle-1">
        Enter email addresses to invite team members. Team members will be required to sign in with their
        <a href="">BC Services Card</a>.
      </p>
      <v-form ref="form">
        <div class="d-flex" v-for="(email, index) in inviteEmails" v-bind:key="index">
          <v-text-field
            filled
            label="Email Address"
            persistent-hint
            v-model="inviteEmails[index]"
            :rules="emailRules"
          ></v-text-field>
          <v-btn icon @click="removeEmail(index)" class="mt-3 ml-1">
            <v-icon>close</v-icon>
          </v-btn>
        </div>
        <v-btn outlined @click="addEmail()">
          + Add Another
        </v-btn>

        <div class="invite-users-form__row invite-users-form__form-btns">
          <v-btn class="mr-3"
                 @click="sendInvites"
                 color="primary"
                 large
                 :loading="loading"
                 :disabled="loading || !isFormValid()">
            <span>Send Invites</span>
          </v-btn>
          <v-btn @click="cancel" color="secondary" large>
            <span>Cancel</span>
          </v-btn>
        </div>
      </v-form>

    </v-card-text>
  </v-card>
</template>

<script lang="ts">
import { Component, Vue, Emit } from 'vue-property-decorator'
import OrgModule from '@/store/modules/org'
import { mapState, mapActions, mapMutations } from 'vuex'
import { Organization } from '@/models/Organization'
import { Invitation } from '@/models/Invitation'
import { getModule } from 'vuex-module-decorators'

@Component({
  computed: {
    ...mapState('user', ['organizations'])
  },
  methods: {
    ...mapMutations('org', ['resetInvitations']),
    ...mapActions('org', ['createInvitation'])
  }
})
export default class InviteUsersForm extends Vue {
  orgStore = getModule(OrgModule, this.$store)
  readonly organizations!: Organization[]
  readonly resetInvitations!: () => void
  readonly createInvitation!: (Invitation) => Promise<void>
  private loading = false

  $refs: {
    form: HTMLFormElement
  }

  inviteEmails = ['', '', '']

  emailRules = [
    v => !v || /.+@.+\..+/.test(v) || 'E-mail must be valid'
  ]

  private isFormValid (): boolean {
    return this.inviteEmails.some(email => email) && this.$refs.form.validate()
  }

  removeEmail (index: number) {
    this.inviteEmails.splice(index, 1)
  }

  addEmail () {
    this.inviteEmails.push('')
  }

  async sendInvites () {
    if (this.isFormValid()) {
      // set loading state
      this.loading = true
      this.resetInvitations()
      for (let i = 0; i < this.inviteEmails.length; i++) {
        const email = this.inviteEmails[i]
        if (email) {
          this.createInvitation({
            recipientEmail: email,
            sentDate: new Date(),
            membership: this.organizations
              .filter(org => org.orgType === 'IMPLICIT')
              .map(org => { return { membershipType: 'MEMBER', orgId: org.id } })
          })
        }
      }

      // emit event to let parent know the invite sequence is complete
      this.$emit('invites-complete')
      this.loading = false
    }
  }

  @Emit()
  cancel () {}
}
</script>

<style lang="scss">
  .header {
    justify-content: space-between;
  }

  .invite-users-form__row {
    margin-top: 1rem;
    justify-content: right;
  }

  .invite-users-form__form-btns {
    margin-top: 2rem;
    display: flex;
  }
</style>
