<template>
  <div class="value__title">
    <div
      v-for="(member, index) in getActiveAdmins"
      :key="index"
    >
      <div v-if="!anonAccount">
        <div>
          {{ member.user.firstname }} {{ member.user.lastname }}
        </div>
        <div v-if="member.user.contacts && member.user.contacts[0]">
          <div v-if="member.user.contacts[0].email">
            {{ member.user.contacts[0].email }}
          </div>
          <div v-if="member.user.contacts[0].phone">
            {{ member.user.contacts[0].phone }}
            <span v-if="member.user.contacts[0].phoneExtension">ext. {{ member.user.contacts[0].phoneExtension }}</span>
          </div>
        </div>
      </div>
      <div v-else>
        {{ member.user.username }}
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import {
  Member,
  MembershipType,
  Organization
} from '@/models/Organization'
import { mapActions, mapState } from 'pinia'
import { AccessType } from '@/util/constants'
import { useOrgStore } from '@/store/org'

@Component({
  computed: {
    ...mapState(useOrgStore, [
      'activeOrgMembers',
      'currentOrganization'
    ])
  },
  methods: {
    ...mapActions(useOrgStore, ['syncActiveOrgMembers'])
  }

})
export default class OrgAdminContact extends Vue {
  private activeOrgMembers!: Member[]
  private readonly syncActiveOrgMembers!: () => Member[]
  private readonly currentOrganization!: Organization

  private async mounted () {
    this.syncActiveOrgMembers()
  }

  private get getActiveAdmins (): Member[] {
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
