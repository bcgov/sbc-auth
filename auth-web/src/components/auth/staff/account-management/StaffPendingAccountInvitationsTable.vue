<template>
  <div>
    <v-data-table
      class="user-list"
      :headers="headerAccounts"
      :items="pendingInvitationOrgs"
      :items-per-page.sync="numberOfItems"
      :hide-default-footer="pendingInvitationOrgs.length <= tableDataOptions.itemsPerPage"
      :custom-sort="columnSort"
      :no-data-text="$t('noPendingAccountsLabel')"
      :footer-props="{
        itemsPerPageOptions: getPaginationOptions
      }"
      :options.sync="tableDataOptions"
      @update:items-per-page="saveItemsPerPage"
    >
      <template v-slot:loading>
        Loading...
      </template>
      <template v-slot:[`item.expires`]="{ item }">
        {{formatDate(item.invitations[0].expiresOn, 'MMM DD, YYYY')}}
      </template>
      <template v-slot:[`item.contactEmail`]="{ item }">
        <!-- {{item.invitations[0].recipientEmail}} -->
        <a v-bind:href="'mailto:' + item.invitations[0].recipientEmail">
          {{item.invitations[0].recipientEmail}}
        </a>
      </template>
      <template v-slot:[`item.action`]="{ item }">
        <div class="table-actions">
          <v-btn
            outlined
            color="primary"
            class="action-btn"
            :data-test="getIndexedTag('resend-invitation-button', item.id)"
            @click="resend(item.invitations[0])"
          >
            Resend
          </v-btn
          >
          <v-btn
            outlined
            color="primary"
            class="action-btn"
            @click="showConfirmRemoveInviteModal(item)"
          >
            Remove
          </v-btn>
        </div>
      </template>
    </v-data-table>
    <ModalDialog
      ref="confirmActionDialog"
      dialog-class="notify-dialog"
      max-width="640"
    >
      <template v-slot:title>
        <span>Remove Invitation</span>
      </template>
      <template v-slot:text>
        <span>This invitation for this account will be removed permanently. Are you sure you want to remove this invitation?</span>
      </template>
      <template v-slot:icon>
        <v-icon large color="error">mdi-alert-circle-outline</v-icon>
      </template>
      <template v-slot:actions>
        <v-btn large color="error" @click="deleteInvitation()">Yes</v-btn>
        <v-btn large color="default" @click="close()">No</v-btn>
      </template>
    </ModalDialog>
  </div>
</template>

<script lang="ts">
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import PaginationMixin from '@/components/auth/mixins/PaginationMixin.vue'
import { EventBus } from '@/event-bus'
import { Invitation } from '@/models/Invitation'
import { Organization } from '@/models/Organization'
import { Event } from '@/models/event'
import CommonUtils from '@/util/common-util'
import { Component, Mixins } from 'vue-property-decorator'
import { DataOptions } from 'vuetify'
import { mapActions, mapState } from 'vuex'

@Component({
  components: {
    ModalDialog
  },
  computed: {
    ...mapState('staff', [
      'pendingInvitationOrgs'
    ])
  },
  methods: {
    ...mapActions('staff', [
      'resendPendingOrgInvitation',
      'syncPendingInvitationOrgs',
      'deleteOrg'
    ])
  }
})
export default class StaffPendingAccountInvitationsTable extends Mixins(PaginationMixin) {
  $refs: {
    confirmActionDialog: ModalDialog
  }

  private readonly pendingInvitationOrgs!: Organization[]
  private readonly resendPendingOrgInvitation!: (invitation: Invitation) => void
  private readonly syncPendingInvitationOrgs!: () => Organization[]
  private readonly deleteOrg!: (org: Organization) => void
  private tableDataOptions : Partial<DataOptions> = {}

  private orgToBeRemoved: Organization = null

  private columnSort = CommonUtils.customSort

  mounted () {
    this.tableDataOptions = this.DEFAULT_DATA_OPTIONS
  }

  private readonly headerAccounts = [
    {
      text: 'Expiry Date',
      align: 'left',
      value: 'expires',
      sortable: false,
      width: '150'
    },
    {
      text: 'Name',
      align: 'left',
      sortable: false,
      value: 'name'
    },
    {
      text: 'Contact Email',
      align: 'left',
      sortable: false,
      value: 'contactEmail'
    },
    {
      text: 'Created By',
      align: 'left',
      sortable: false,
      value: 'createdBy'
    },
    {
      text: 'Actions',
      align: 'left',
      value: 'action',
      sortable: false,
      width: '210'
    }
  ]

  private formatDate = CommonUtils.formatDisplayDate

  private getIndexedTag (tag, index): string {
    return `${tag}-${index}`
  }

  private async resend (invitation: Invitation) {
    try {
      await this.resendPendingOrgInvitation(invitation)
      const event:Event = { message: `Invitation resent to ${invitation.recipientEmail}`, type: 'success', timeout: 1000 }
      EventBus.$emit('show-toast', event)
    } catch (err) {
      const event:Event = { message: 'Invitation resend failed', type: 'error', timeout: 1000 }
      EventBus.$emit('show-toast', event)
    }

    await this.syncPendingInvitationOrgs()
  }

  private async deleteInvitation () {
    try {
      await this.deleteOrg(this.orgToBeRemoved)
      this.close()
      const event:Event = { message: 'Invitation removed', type: 'success', timeout: 1000 }
      EventBus.$emit('show-toast', event)
      await this.syncPendingInvitationOrgs()
    } catch (err) {
      const event:Event = { message: 'Invitation remove failed', type: 'error', timeout: 1000 }
      EventBus.$emit('show-toast', event)
    }
  }

  private showConfirmRemoveInviteModal (org: Organization) {
    this.orgToBeRemoved = org
    this.$refs.confirmActionDialog.open()
  }

  private close () {
    this.$refs.confirmActionDialog.close()
  }
}
</script>

<style lang="scss" scoped>
::v-deep {
  table {
    table-layout: fixed;

    td {
      padding-top: 0.5rem;
      padding-bottom: 0.5rem;
    }
  }
}

.table-actions {
  .v-btn + .v-btn {
    margin-left: 0.25rem;
  }
}
</style>
