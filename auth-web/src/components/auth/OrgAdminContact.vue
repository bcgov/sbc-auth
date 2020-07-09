<template>
    <div class="value__title">
      <p  v-for="(member, index) in getActiveAdmins()" v-bind:key="index + 1">
        <span> {{ member.user.firstname }} {{ member.user.lastname }} </span>
        <span>( </span>
        <span>{{ member.user.contacts[0].email }} </span>
        <span v-if="member.user.contacts[0].phone">, {{ member.user.contacts[0].phone }} </span>
        <span v-if="member.user.contacts[0].phoneExtension"> - {{ member.user.contacts[0].phoneExtension }} </span>
        <span> )</span>
      </p>
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

@Component({
  computed: {
    ...mapState('org', [
      'activeOrgMembers'
    ])
  },
  methods: {
    ...mapActions('org', ['syncActiveOrgMembers'])
  }

})
export default class OrgAdminContact extends Vue {
  private activeOrgMembers!: Member[]
  private readonly syncActiveOrgMembers!: () => Member[]

  private async mounted () {
    this.syncActiveOrgMembers()
  }

  private getActiveAdmins (): Member[] {
    return this.activeOrgMembers.filter(member => member.membershipTypeCode === MembershipType.Admin)
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
