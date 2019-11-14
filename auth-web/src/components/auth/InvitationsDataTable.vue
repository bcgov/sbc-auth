<template>
  <v-data-table
    class="user-list__pending"
    :headers="headerInvitations"
    :items="pendingOrgInvitations"
    :items-per-page="5"
    :calculate-widths="true"
    :hide-default-footer="pendingOrgInvitations.length <= 5"
  >
    <template v-slot:item.sentDate="{ item }">
      {{ formatDate (item.sentDate) }}
    </template>
    <template v-slot:item.expiresOn="{ item }">
      {{ formatDate (item.expiresOn) }}
    </template>
    <template v-slot:item.action="{ item }">
      <v-btn depressed small class="mr-2" @click="resend(item)">Resend</v-btn>
      <v-btn depressed small @click="confirmRemoveInvite(item)">Remove</v-btn>
    </template>
  </v-data-table>
</template>

<script lang="ts">
import { Component, Emit, Vue } from 'vue-property-decorator'
import { mapActions, mapGetters, mapState } from 'vuex'
import { Invitation } from '@/models/Invitation'
import { Organization } from '@/models/Organization'
import moment from 'moment'

@Component({
  computed: {
    ...mapState('org', ['pendingOrgInvitations']),
    ...mapGetters('org', ['myOrg'])
  },
  methods: {
    ...mapActions('org', ['syncPendingOrgInvitations'])
  }
})
export default class InvitationsDataTable extends Vue {
  private readonly myOrg!: Organization
  private readonly pendingOrgInvitations!: Invitation[]
  private readonly syncPendingOrgInvitations!: () => Invitation[]
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
      value: 'sentDate'
    },
    {
      text: 'Expires',
      align: 'left',
      sortable: true,
      value: 'expiresOn'
    },
    {
      text: 'Actions',
      align: 'left',
      value: 'action',
      sortable: false,
      width: '195'
    }
  ]

  private async mounted () {
    await this.syncPendingOrgInvitations()
  }

  private formatDate (date: Date) {
    return moment(date).format('DD MMM, YYYY')
  }

  @Emit()
  private confirmRemoveInvite (invititation: Invitation) {}

  @Emit()
  private resend (invitation: Invitation) {}
}
</script>

<style lang="scss" scoped>

</style>
