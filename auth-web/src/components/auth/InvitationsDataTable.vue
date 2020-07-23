<template>
  <v-data-table
    class="user-list"
    :headers="headerInvitations"
    :items="indexedInvitations"
    :items-per-page="5"
    :calculate-widths="true"
    :hide-default-footer="indexedInvitations.length <= 5"
    :no-data-text="$t('noPendingInvitesLabel')"
  >
    <template v-slot:item.recipientEmail="{ item }" >
      <span :data-test="getIndexedTag('invitation-email', item.index)"
      >
        {{ item.recipientEmail }}
      </span>
    </template>
    <template v-slot:item.sentDate="{ item }">
      <span
        :data-test="getIndexedTag('invitation-sent', item.index)"
      >
        {{ formatDate (item.sentDate) }}
      </span>
    </template>
    <template v-slot:item.expiresOn="{ item }">
      <span
        :data-test="getIndexedTag('invitation-expires', item.index)"
      >
        {{ formatDate (item.expiresOn) }}
      </span>
    </template>
    <template v-slot:item.action="{ item }">
      <v-btn
        outlined
        color="primary"
        class="mr-1"
        :data-test="getIndexedTag('resend-button', item.index)"
        @click="resend(item)"
      >
        Resend
      </v-btn>
      <v-btn
        outlined
        color="primary"
        :data-test="getIndexedTag('remove-button', item.index)"
        @click="confirmRemoveInvite(item)"
      >
        Remove
      </v-btn>
    </template>
  </v-data-table>
</template>

<script lang="ts">
import { Component, Emit, Vue } from 'vue-property-decorator'
import CommonUtils from '@/util/common-util'
import { Invitation } from '@/models/Invitation'
import { mapState } from 'vuex'

@Component({
  computed: {
    ...mapState('org', ['pendingOrgInvitations'])
  }
})
export default class InvitationsDataTable extends Vue {
  private readonly pendingOrgInvitations!: Invitation[]
  private readonly headerInvitations = [
    {
      text: 'Email',
      align: 'left',
      sortable: true,
      value: 'recipientEmail'
    },
    {
      text: 'Invitation Sent',
      align: 'left',
      sortable: true,
      value: 'sentDate',
      width: '160'
    },
    {
      text: 'Expires',
      align: 'left',
      sortable: true,
      value: 'expiresOn',
      width: '160'
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

  private get indexedInvitations () {
    return this.pendingOrgInvitations.map((item, index) => ({
      index,
      ...item
    }))
  }

  @Emit()
  private confirmRemoveInvite (invititation: Invitation) {}

  @Emit()
  private resend (invitation: Invitation) {}
}
</script>

<style lang="scss" scoped>
::v-deep {
  td {
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
    height: auto;
  }
}
</style>
