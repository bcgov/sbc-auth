<template>
    <div class="value__title">
      <div  v-for="(member, index) in getActiveAdmins()" v-bind:key="index + 1">
        <p v-if="!anonAccount">
          <span> {{ member.user.firstname }} {{ member.user.lastname }} </span>
          <span>( </span>
          <span v-if="member.user.contacts[0].email">{{ member.user.contacts[0].email }} </span>
          <span v-if="member.user.contacts[0].phone">, {{ member.user.contacts[0].phone }} </span>
          <span v-if="member.user.contacts[0].phoneExtension"> - {{ member.user.contacts[0].phoneExtension }} </span>
          <span> )</span>
        </p>
        <p v-else>
          <span> {{ member.user.username }} </span>
        </p>
      </div>
    </div>
</template>

<script lang="ts">
import { Component, Emit, Vue } from 'vue-property-decorator'
import {
  Member,
  MembershipStatus,
  MembershipType,
  Organization,
  RoleInfo
} from '@/models/Organization'
import { mapActions, mapState } from 'vuex'
import { AccessType } from '@/util/constants'

@Component({
  computed: {
    ...mapState('org', [
      'activeOrgMembers',
      'currentOrganization'
    ])
  },
  methods: {
    ...mapActions('org', ['syncActiveOrgMembers'])
  }

})
export default class OrgAdminContact extends Vue {
  private activeOrgMembers!: Member[]
  private readonly syncActiveOrgMembers!: () => Member[]
  private readonly currentOrganization!: Organization

  private async mounted () {
    this.syncActiveOrgMembers()
  }

  private getActiveAdmins (): Member[] {
    return this.activeOrgMembers.filter(member => member.membershipTypeCode === MembershipType.Admin)
  }

  get anonAccount (): boolean {
    return this.currentOrganization?.accessType === AccessType.ANONYMOUS
  }

}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';

.v-list--dense {
  .v-list-item .v-list-item__title {
    margin-bottom: 0.25rem;
    font-weight: 700;
  }
}

.role-list {
  width: 20rem;
}
.btn-inline {
  white-space: nowrap;
}

.user-role-desc {
  white-space: normal !important;
}
</style>
