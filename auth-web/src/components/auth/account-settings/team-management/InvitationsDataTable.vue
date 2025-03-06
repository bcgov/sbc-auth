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
    <template #[`item.recipientEmail`]="{ item }">
      <span :data-test="getIndexedTag('invitation-email', item.index)">
        {{ item.recipientEmail }}
      </span>
    </template>
    <template #[`item.sentDate`]="{ item }">
      <span
        :data-test="getIndexedTag('invitation-sent', item.index)"
      >
        {{ formatDate (item.sentDate, 'MMMM DD, YYYY') }}
      </span>
    </template>
    <template #[`item.expiresOn`]="{ item }">
      <span
        :data-test="getIndexedTag('invitation-expires', item.index)"
      >
        {{ formatDate (item.expiresOn, 'MMMM DD, YYYY') }}
      </span>
    </template>
    <template #[`item.action`]="{ item }">
      <!-- Resend Invitation -->
      <v-btn
        v-can:EDIT_USER.hide
        icon
        class="mr-1"
        aria-label="Resend invitation"
        title="Resend Invitation"
        :data-test="getIndexedTag('resend-button', item.index)"
        @click="resend(item)"
      >
        <v-icon>mdi-email-send-outline</v-icon>
      </v-btn>

      <!-- Remove Invitation -->
      <v-btn
        v-can:EDIT_USER.hide
        icon
        aria-label="Remove Invitation"
        title="Remove Invitation"
        :data-test="getIndexedTag('remove-button', item.index)"
        @click="confirmRemoveInvite(item)"
      >
        <v-icon>mdi-trash-can-outline</v-icon>
      </v-btn>
    </template>
  </v-data-table>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, ref, toRefs } from '@vue/composition-api'
import { storeToRefs } from 'pinia'
import CommonUtils from '@/util/common-util'
import { Invitation } from '@/models/Invitation'
import { useOrgStore } from '@/stores/org'
import { useUserStore } from '@/stores/user'

export default defineComponent({
  name: 'InvitationsDataTable',
  emits: ['confirmRemoveInvite', 'resend'],
  setup (props, { emit }) {
    const orgStore = useOrgStore()
    const userStore = useUserStore()

    const { pendingOrgInvitations, currentMembership } = storeToRefs(orgStore)
    const { currentUser } = storeToRefs(userStore)

    const headerInvitations = [
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
        align: 'right',
        value: 'action',
        sortable: false
      }
    ]

    const state = reactive({
      indexedInvitations: computed(() =>
        pendingOrgInvitations.value.map((item: Invitation, index: number) => ({
          index,
          ...item
        })))
    })

    function getIndexedTag (tag: string, index: number): string {
      return `${tag}-${index}`
    }

    function confirmRemoveInvite (invitation) {
      emit('confirm-remove-invite', invitation)
    }

    function resend (invitation) {
      emit('resend', invitation)
    }

    return {
      headerInvitations,
      ...toRefs(state),
      formatDate: CommonUtils.formatDisplayDate,
      getIndexedTag,
      confirmRemoveInvite,
      resend
    }
  }
})
</script>

<style lang="scss" scoped>
::v-deep {
  td {
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
    height: auto;
  }

  .v-tooltip__content {
    font-size: 10px !important;
  }
}
</style>
