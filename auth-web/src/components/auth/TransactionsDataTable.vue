<template>
  <v-data-table
    class="user-list"
    :headers="headerTranscations"
    :items="transactionList"
    :items-per-page="5"
    :hide-default-footer="transactionList.length <= 5"
    :custom-sort="customSortActive"
    :no-data-text="$t('noActiveUsersLabel')"
  >
    <template v-slot:loading>
      Loading...
    </template>
    <template v-slot:item.transactionNames="{ item }">
      <v-list-item-title
        class="user-name"
        :data-test="getIndexedTag('transaction-name', item.index)"
        >
        <div
          v-for="(name, nameIndex) in item.transactionNames"
          :key="nameIndex">
          {{ name }}
        </div>
      </v-list-item-title>
      <v-list-item-subtitle
        :data-test="getIndexedTag('transaction-sub', item.index)"
      >Business Registry</v-list-item-subtitle>
    </template>
    <template v-slot:item.transactionDate="{ item }">
      {{formatDate(item.transactionDate)}}
    </template>
  </v-data-table>
</template>

<script lang="ts">
import { Component, Emit, Prop, Vue } from 'vue-property-decorator'
import { Member, MembershipStatus, MembershipType, Organization, RoleInfo } from '@/models/Organization'
import { Transaction, TransactionListResponse, TransactionTableList, TransactionTableRow } from '@/models/transaction'
import { mapActions, mapState } from 'vuex'
import { Account } from '@/util/constants'
import { Business } from '@/models/business'
import CommonUtils from '@/util/common-util'

export interface ChangeRolePayload {
  member: Member
  targetRole: string
}

@Component({
  computed: {
    ...mapState('business', ['businesses']),
    ...mapState('org', [
      'activeOrgMembers',
      'currentMembership',
      'currentOrganization'
    ])
  },
  methods: {
    ...mapActions('org', [
      'getTransactionList'
    ])
  }
})
export default class TransactionsDataTable extends Vue {
  private readonly businesses!: Business[]
  private readonly activeOrgMembers!: Member[]
  private readonly currentMembership!: Member
  private readonly currentOrganization!: Organization
  private readonly getTransactionList!: () => TransactionTableList

  private transactionList: TransactionTableRow[] = [];
  private formatDate = CommonUtils.formatDisplayDate

  private readonly headerTranscations = [
    {
      text: 'Transaction',
      align: 'left',
      sortable: true,
      value: 'transactionNames'
    },
    {
      text: 'Folio #',
      align: 'left',
      sortable: true,
      value: 'folioNumber'
    },
    {
      text: 'Initiated By',
      align: 'left',
      sortable: true,
      value: 'initiatedBy'
    },
    {
      text: 'Date',
      align: 'left',
      value: 'transactionDate',
      sortable: true
    },
    {
      text: 'Total Amount',
      align: 'left',
      value: 'totalAmount',
      sortable: true
    },
    {
      text: 'Status',
      align: 'left',
      value: 'status',
      sortable: true
    }
  ]

  private async mounted () {
    this.loadTransactionList()
  }

  private async loadTransactionList () {
    const resp = await this.getTransactionList()
    this.transactionList = resp?.transactionsList || []
    // eslint-disable-next-line no-console
    console.log(this.transactionList)
  }

  private getIndexedTag (tag, index): string {
    return `${tag}-${index}`
  }

  private get indexedOrgMembers () {
    return this.activeOrgMembers.map((item, index) => ({
      index,
      ...item
    }))
  }

  private isRoleEnabled (role: RoleInfo): boolean {
    switch (this.currentMembership.membershipTypeCode) {
      case MembershipType.Owner:
        return true
      case MembershipType.Admin:
        if (role.name !== 'Owner') {
          return true
        }
        return false
      default:
        return false
    }
  }

  private canChangeRole (memberBeingChanged: Member): boolean {
    if (this.currentMembership.membershipStatus !== MembershipStatus.Active) {
      return false
    }

    switch (this.currentMembership.membershipTypeCode) {
      case MembershipType.Owner:
        // Owners can change roles of other users who are not owners
        if (!this.isOwnMembership(memberBeingChanged) && memberBeingChanged.membershipTypeCode !== MembershipType.Owner) {
          return true
        }
        // And they can downgrade their own role if there is another owner on the team
        if (this.isOwnMembership(memberBeingChanged) && this.ownerCount() > 1) {
          return true
        }
        return false
      case MembershipType.Admin:
        // Admins can change roles of their own
        return this.isOwnMembership(memberBeingChanged)
      default:
        return false
    }
  }

  private canRemove (memberToRemove: Member): boolean {
    // Can't remove yourself
    if (this.currentMembership.user.username === memberToRemove.user.username) {
      return false
    }

    // Can't remove unless Admin/Owner
    if (this.currentMembership.membershipTypeCode === MembershipType.Member) {
      return false
    }

    // Can't remove Admin unless Owner
    if (this.currentMembership.membershipTypeCode === MembershipType.Admin &&
      memberToRemove.membershipTypeCode === MembershipType.Admin) {
      return false
    }

    // No one can change an OWNER's status, only option is OWNER to leave the team. #2319
    if (memberToRemove.membershipTypeCode === MembershipType.Owner) {
      return false
    }

    return true
  }

  private canLeave (member: Member): boolean {
    if (this.currentMembership.user.username !== member.user.username) {
      return false
    }
    return true
  }

  private ownerCount (): number {
    return this.activeOrgMembers.filter(member => member.membershipTypeCode === MembershipType.Owner).length
  }

  private customSortActive (items, index, isDescending) {
    const isDesc = isDescending.length > 0 && isDescending[0]
    switch (index[0]) {
      case 'name':
        items.sort((a, b) => {
          if (isDesc) {
            return a.user.firstname < b.user.firstname ? -1 : 1
          } else {
            return b.user.firstname < a.user.firstname ? -1 : 1
          }
        })
        break
      case 'role':
        items.sort((a, b) => {
          if (isDesc) {
            return a.membershipTypeCode < b.membershipTypeCode ? -1 : 1
          } else {
            return b.membershipTypeCode < a.membershipTypeCode ? -1 : 1
          }
        })
        break
      case 'lastActive':
        items.sort((a, b) => {
          if (isDesc) {
            return a.user.modified < b.user.modified ? -1 : 1
          } else {
            return b.user.modified < a.user.modified ? -1 : 1
          }
        })
    }
    return items
  }

  private canDissolve (): boolean {
    if (this.activeOrgMembers.length === 1 && this.businesses.length === 0 && !this.isAnonymousAccount()) {
      return true
    }
    return false
  }

  private isAnonymousAccount (): boolean {
    return this.currentOrganization &&
            this.currentOrganization.accessType === Account.ANONYMOUS
  }

  @Emit()
  private confirmRemoveMember (member: Member) { }

  @Emit()
  private confirmChangeRole (member: Member, targetRole: string): ChangeRolePayload {
    return {
      member,
      targetRole
    }
  }

  private confirmLeaveTeam (member: Member) {
    if (member.membershipTypeCode === MembershipType.Owner &&
      this.ownerCount() === 1 &&
      !this.canDissolve()) {
      this.$emit('single-owner-error')
    } else {
      if (this.canDissolve()) {
        this.$emit('confirm-dissolve-team')
      } else {
        this.$emit('confirm-leave-team')
      }
    }
  }

  private isOwnMembership (member: Member) {
    return this.currentMembership?.user?.username === member.user.username || false
  }
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';

.v-list--dense {
  .v-list-item {
    padding-top: 0.25rem;
    padding-bottom: 0.25rem;
  }

  .v-list-item .v-list-item__title {
    margin-bottom: 0.25rem;
    font-weight: 700;
  }
}

.role-list {
  width: 20rem;
}
</style>
