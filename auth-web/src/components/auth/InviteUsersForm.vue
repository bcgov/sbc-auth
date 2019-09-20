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
          <v-btn class="mr-3" @click="sendInvites" color="primary" large>
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
import { SuccessEmitPayload } from '@/models/user'

@Component({})
export default class InviteUsersForm extends Vue {

  $refs: {
    form: HTMLFormElement
  }

  inviteEmails = ['', '', '']

  emailRules = [
        v => !v || /.+@.+\..+/.test(v) || 'E-mail must be valid',
      ]

  private isFormValid (): boolean {
    return this.$refs.form.validate()
  }

  removeEmail (index: number) {
    this.inviteEmails.splice(index, 1)
  }

  addEmail () {
    this.inviteEmails.push('')
  }

  sendInvites () {
    if (this.isFormValid()) {
      try {
        // send invites to each specified email

        // emit success event
        this.$emit('invite-success', { isResend: false, invitationCount: this.inviteEmails.length } as SuccessEmitPayload)
      } catch (exception) {
        this.$emit('invite-error')
      }
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
