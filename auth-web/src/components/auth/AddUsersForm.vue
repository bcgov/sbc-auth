/* eslint-disable no-console */
<template>
  <div>
    <v-form ref="form" class="mt-9">
      <ul class="invite-list">
        <transition-group name="slide-y-transition">
          <li class="d-flex" v-for="(user, index) in users" v-bind:key="index + 1">
            <v-text-field
              filled
              label="Username"
              v-model="user.username"
              :data-test="getIndexedTag('username', index)"
            ></v-text-field>

            <v-text-field
              filled
              label="Temporary Password"
              v-model="user.password"
              :data-test="getIndexedTag('password', index)"
            ></v-text-field>

            <v-overflow-btn
              filled
              class="select-role-btn ml-2"
              v-model="user.selectedRole.name"
              item-text="name"
              item-value="name"
              :items="availableRoles"
              :value="availableRoles[0]"
              :data-test="getIndexedTag('role-selector', index)"
              menu-props="dense"
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
              @click="removeUser(index)">
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </li>
        </transition-group>
      </ul>
      <v-btn text small color="primary"
        @click="addUser()" data-test="add-another-button">
        <v-icon>mdi-plus-box</v-icon>
        <span>Add Another</span>
      </v-btn>
      <div class="form__btns">
        <v-btn large depressed color="primary"
                @click="addUsers"
                :loading="loading"
                :disabled="loading || !isFormValid()"
                data-test="add-users-button"
        >
          <span>Add</span>
        </v-btn>
        <v-btn large depressed class="ml-2" data-test="cancel-button"
          @click="cancel">
          <span>Cancel</span>
        </v-btn>
      </div>
    </v-form>
  </div>
</template>

<script lang="ts">
import { AddUserBody, AddUsersToOrgBody, Member, MembershipType, Organization, RoleInfo } from '@/models/Organization'
import { Component, Emit, Vue } from 'vue-property-decorator'
import { mapActions, mapMutations, mapState } from 'vuex'
import { Invitation } from '@/models/Invitation'
import OrgModule from '@/store/modules/org'
import { getModule } from 'vuex-module-decorators'

@Component({
  computed: {
    ...mapState('org', ['currentOrganization', 'currentMembership'])
  },
  methods: {
    // ...mapMutations('org', ['resetInvitations']),
    ...mapActions('org', ['createUsers'])
  }
})
export default class AddUsersForm extends Vue {
  private loading = false
  private readonly currentOrganization!: Organization
  private readonly currentMembership!: Member
  private readonly createUsers!: (AddUsersToOrgBody) => Promise<void>

  $refs: {
    form: HTMLFormElement
  }

  private get availableRoles () {
    if (this.currentMembership.membershipTypeCode !== MembershipType.Owner) {
      return this.roles.filter(role => role.name !== 'Owner')
    }
    return this.roles
  }

  private users: AddUserBody[] = []

  // Get the description from UX team
  private readonly roles: RoleInfo[] = [
    {
      icon: 'mdi-account',
      name: 'Member',
      desc: 'Can add businesses, and file for a business.'
    },
    {
      icon: 'mdi-settings',
      name: 'Admin',
      desc: 'Can add/remove team members, add businesses, and file for a business.'
    },
    {
      icon: 'mdi-shield-key',
      name: 'Owner',
      desc: 'Can add/remove team members and businesses, and file for a business.'
    }
  ]

  private getIndexedTag (tag, index): string {
    return `${tag}-${index}`
  }

  private created () {
    this.resetForm()
  }

  private getDefaultRow (): AddUserBody {
    return { username: '', password: '', selectedRole: { ...this.roles[0] }, membershipType: this.roles[0].name }
  }

  private hasDuplicates (): boolean {
    const users = this.users.filter(user => user.username)
    return new Set(users.map(user => user.username.toLowerCase())).size !== users.length
  }

  private isFormValid (): boolean {
    let isValid: boolean = true
    this.users.forEach(user => {
      if (user.username || user.password) {
        if (!user.username || !user.password) {
          isValid = false
        }
      }
    })
    return isValid && !this.hasDuplicates()
  }

  private removeUser (index: number) {
    this.users.splice(index, 1)
  }

  private addUser () {
    this.users.push(this.getDefaultRow())
  }

  private resetForm () {
    this.users = []
    for (let i = 0; i < 3; i++) {
      this.users.push(this.getDefaultRow())
    }
  }

  private async addUsers () {
    if (this.isFormValid()) {
      // set loading state
      this.loading = true
      // Doing a reverse loop to remove empty rows, not going with reduceRight atm
      for (let i = this.users.length - 1; i >= 0; i--) {
        const user = this.users[i]
        if (!user.username.trim() && !user.password.trim()) {
          this.users.splice(i, 1)
        } else {
          user.membershipType = user.selectedRole.name.toUpperCase()
        }
      }
      await this.createUsers({ orgId: this.currentOrganization.id, users: this.users })

      this.resetForm()

      // emit event to let parent know the invite sequence is complete
      this.addUsersComplete()
      this.loading = false
    }
  }

  @Emit()
  private addUsersComplete () {
  }

  @Emit()
  private cancel () {
    this.resetForm()
  }
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
    width: 20rem;

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

  .select-role-btn {
    ::v-deep .v-input__slot {
      padding-right: 0 !important
    }
  }
</style>
