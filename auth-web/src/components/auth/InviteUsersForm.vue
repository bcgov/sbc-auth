<template>
  <v-card>
    <v-card-title class="d-flex">
        Invite Team Members
        
        <v-btn large icon>
          <v-icon @click="cancel()">close</v-icon>
        </v-btn>
        
    </v-card-title>
    <v-card-text>
      <p>Enter email addresses to invite team members. Team members will be required to sign in with their <a href="https://www2.gov.bc.ca/gov/content/governments/government-id/bc-services-card" target="_blank">BC Services Card</a>.</p>
      <v-form ref="form" class="mt-8">
        <ul class="invite-list">
          <transition-group name="slide-y-transition">
            <li class="d-flex" v-for="(email, index) in inviteEmails" v-bind:key="index">
              <v-text-field
                filled
                label="Email Address"
                v-model="inviteEmails[index]"
                validate-on-blur="true"
                :rules="emailRules"
              ></v-text-field>
              <v-select class="select-role ml-1"
                filled
                label="Select Role"
              ></v-select>
              <v-btn icon class="mt-3 ml-1"
                @click="removeEmail(index)">
                <v-icon>close</v-icon>
              </v-btn>
            </li>
          </transition-group>
        </ul>
        <v-btn text small color="primary"
          @click="addEmail()">
          <v-icon>add_box</v-icon>
          <span>Add Another</span>
        </v-btn>
        <div class="form__btns">
          <v-btn large depressed color="primary"
                 @click="sendInvites"
                 :loading="loading"
                 :disabled="loading || !isFormValid()">
            <span>Send Invites</span>
          </v-btn>
          <v-btn large depressed class="ml-2"
            @click="cancel">
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
    v => !v || /.+@.+\..+/.test(v) || 'Enter a valid email address'
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
          await this.createInvitation({
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

<style lang="scss" scoped>
  @import '../../assets/scss/theme.scss';

  .v-card__title {
    justify-content: space-between;
  }

  .invite-list {
    margin: 0;
    padding: 0;
  }

  .invite-list .select-role {
    width: 8rem;
  }

  .form__btns {
    display: flex;
    flex-direction: row;
    justify-content: flex-end;
  }

</style>
