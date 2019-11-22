<template>
  <div>
    <p>Enter email addresses to invite team members. Team members will be required to sign in with their <a href="https://www2.gov.bc.ca/gov/content/governments/government-id/bc-services-card" target="_blank">BC Services Card</a>.</p>
    <v-form ref="form" class="mt-9">
      <ul class="invite-list">
        <transition-group name="slide-y-transition">
          <li class="d-flex" v-for="(invite, index) in invitations" v-bind:key="index + 1">
            <v-text-field
              filled
              label="Email Address"
              v-model="invitations[index].emailAddress"
              :rules="emailRules"
            ></v-text-field>
            <v-overflow-btn
              filled
              class="ml-3"
              :items="availableRoles"
              item-text="name"
              item-value="name"
              :value="availableRoles[2]"
            >
              <template v-slot:selection="{ item }">
                {{ item.name }}
              </template>

              <template v-slot:item="{ item }">
                <div class="role-container">
                  <v-list-item-icon>
                    <v-icon v-text="item.icon" />
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title>{{ item.name }}</v-list-item-title>
                    <v-list-item-subtitle>{{ item.desc }}</v-list-item-subtitle>
                  </v-list-item-content>
                </div>
              </template>
            </v-overflow-btn>

            <v-btn icon class="mt-3 ml-1"
              @click="removeEmail(index)">
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </li>
        </transition-group>
      </ul>
      <v-btn text small color="primary"
        @click="addEmail()">
        <v-icon>mdi-plus-box</v-icon>
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
  </div>
</template>

<script lang="ts">
import { Component, Emit, Vue } from 'vue-property-decorator'
import { mapActions, mapGetters, mapMutations, mapState } from 'vuex'
import { Invitation } from '@/models/Invitation'
import OrgModule from '@/store/modules/org'
import { Organization } from '@/models/Organization'
import { getModule } from 'vuex-module-decorators'

interface RoleInfo {
  icon: string
  name: string
  desc: string
}

interface InvitationInfo {
  emailAddress: string
  role: RoleInfo
}

@Component({
  computed: {
    ...mapGetters('org', ['myOrg'])
  },
  methods: {
    ...mapMutations('org', ['resetInvitations']),
    ...mapActions('org', ['createInvitation'])
  }
})
export default class InviteUsersForm extends Vue {
  private orgStore = getModule(OrgModule, this.$store)
  private loading = false
  private readonly myOrg!: Organization
  private readonly resetInvitations!: () => void
  private readonly createInvitation!: (Invitation) => Promise<void>

  $refs: {
    form: HTMLFormElement
  }

  private invitations: InvitationInfo[] = []

  private readonly emailRules = [
    v => !v || /.+@.+\..+/.test(v) || 'Enter a valid email address'
  ]

  private readonly availableRoles = [
    {
      icon: 'mdi-shield-key',
      name: 'Owner',
      desc: 'Can add/remove team members and businesses, and file for a business.'
    },
    {
      icon: 'mdi-settings',
      name: 'Admin',
      desc: 'Can add/remove team members, add businesses, and file for a business.'
    },
    {
      icon: 'mdi-account',
      name: 'Member',
      desc: 'Can add businesses, and file for a business.'
    }
  ]

  private created () {
    for (let i = 0; i < 3; i++) {
      this.invitations.push({ emailAddress: '', role: this.availableRoles[2] })
    }
  }

  private isFormValid (): boolean {
    return this.invitations && this.invitations.some(invite => invite.emailAddress) && this.$refs.form.validate()
  }

  private removeEmail (index: number) {
    this.invitations.splice(index, 1)
  }

  private addEmail () {
    this.invitations.push({ emailAddress: '', role: this.availableRoles[2] })
  }

  private async sendInvites () {
    if (this.isFormValid()) {
      // set loading state
      this.loading = true
      this.resetInvitations()
      for (let i = 0; i < this.invitations.length; i++) {
        const invite = this.invitations[i]
        if (invite && invite.emailAddress) {
          await this.createInvitation({
            recipientEmail: invite.emailAddress,
            sentDate: new Date(),
            membership: [{ membershipType: invite.role.name.toUpperCase(), orgId: this.myOrg.id }]
          })
        }
      }

      // emit event to let parent know the invite sequence is complete
      this.$emit('invites-complete')
      this.loading = false
    }
  }

  @Emit()
  private cancel () {}
}
</script>

<style lang="scss" scoped>
  @import '$assets/scss/theme.scss';
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

  .role-container {
    display: flex;
    max-width: 20rem;

    .v-list-item__title {
      letter-spacing: -0.02rem;
      font-size: 0.875rem;
      font-weight: 700;
    }

    .v-list-item__subtitle {
      white-space: normal;
      overflow: visible;
      line-height: 1.5;
      font-size: 0.875rem;
    }
  }

  .v-list-item.active {
    background: $BCgovBlue0;
  }
</style>
