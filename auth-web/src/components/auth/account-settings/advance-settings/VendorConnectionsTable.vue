<template>
  <div>
    <BaseVDataTable
      class="vendor-connections-list"
      item-key="id"
      :loading="isLoading"
      loading-text="Loading..."
      :no-data-text="noDataText"
      :set-items="connectionsList"
      :set-headers="tableHeaders"
      :total-items="connectionsList.length"
      page-hide
      hide-filters
      data-test="vendor-connections-table"
    >
      <template #item-slot-serviceProviderName="{ item }">
        <div class="font-weight-bold">
          {{ item.serviceProviderName }}
        </div>
        <span
          v-if="getConnectionStatus(item) === 'expiring'"
          class="label expiring mt-1 d-inline-block"
        >
          {{ $t('vendorConnectionsExpiresInDays', { days: getDaysUntilExpiry(item.expiryDate) }) }}
        </span>
        <span
          v-else-if="getConnectionStatus(item) === 'expired'"
          class="label expired mt-1 d-inline-block"
        >
          {{ $t('vendorConnectionsExpired') }}
        </span>
      </template>

      <template #item-slot-dateAdded="{ item }">
        {{ formatDateAdded(item.dateAdded) }}
      </template>

      <template #item-slot-expiryDate="{ item }">
        {{ formatExpiryDate(item.expiryDate) }}
      </template>

      <template #item-slot-action="{ item }">
        <div
          v-if="canManageConnections"
          class="action-buttons d-flex justify-end"
        >
          <v-btn
            v-if="getConnectionStatus(item) === 'active'"
            color="primary"
            depressed
            class="vendor-connection-action-btn vendor-connection-action-btn--standalone"
            aria-label="Remove connection"
            title="Remove connection"
            :data-test="getIndexedTag('remove-button', item.id)"
            @click="openRemoveModal(item)"
          >
            Remove
          </v-btn>

          <span
            v-else
            class="vendor-connection-split-actions d-inline-flex align-center"
          >
            <v-btn
              color="primary"
              depressed
              class="vendor-connection-action-btn vendor-connection-action-btn--split-main"
              aria-label="Extend connection"
              title="Extend connection"
              :data-test="getIndexedTag('extend-button', item.id)"
              @click="openExtendModal(item)"
            >
              Extend
            </v-btn>
            <v-menu
              v-model="actionMenuOpen[item.id]"
              offset-y
              left
            >
              <template #activator="{ on, attrs }">
                <v-btn
                  color="primary"
                  depressed
                  class="vendor-connection-action-btn vendor-connection-action-btn--split-menu"
                  aria-label="More actions"
                  title="More actions"
                  v-bind="attrs"
                  :data-test="getIndexedTag('actions-menu', item.id)"
                  v-on="on"
                >
                  <v-icon>{{ actionMenuOpen[item.id] ? 'mdi-menu-up' : 'mdi-menu-down' }}</v-icon>
                </v-btn>
              </template>
              <v-list>
                <v-list-item
                  :data-test="getIndexedTag('remove-menu-item', item.id)"
                  @click="openRemoveModal(item)"
                >
                  <v-list-item-title>Remove</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </span>
        </div>
      </template>
    </BaseVDataTable>

    <ModalDialog
      ref="removeDialog"
      :title="$t('vendorConnectionsRemoveTitle')"
      :text="$t('vendorConnectionsRemoveBody')"
      :show-icon="false"
      :show-close-icon="true"
      dialog-class="warning-dialog vendor-connection-dialog"
      max-width="650"
      data-test="vendor-connections-remove-modal"
    >
      <template #actions>
        <div class="vendor-connection-dialog__actions">
          <v-btn
            outlined
            large
            depressed
            color="primary"
            class="px-7"
            data-test="vendor-connections-remove-cancel"
            @click="closeDialog(removeDialog)"
          >
            Cancel
          </v-btn>
          <v-btn
            large
            color="primary"
            class="font-weight-bold px-8 ml-3"
            data-test="vendor-connections-remove-confirm"
            @click="confirmRemove()"
          >
            Remove Connection
          </v-btn>
        </div>
      </template>
    </ModalDialog>

    <ModalDialog
      ref="extendDialog"
      :title="$t('vendorConnectionsExtendTitle')"
      :text="$t('vendorConnectionsExtendBody')"
      :show-icon="false"
      :show-close-icon="true"
      dialog-class="warning-dialog vendor-connection-dialog"
      max-width="650"
      data-test="vendor-connections-extend-modal"
    >
      <template #actions>
        <div class="vendor-connection-dialog__actions">
          <v-btn
            outlined
            large
            depressed
            color="primary"
            class="px-7"
            data-test="vendor-connections-extend-cancel"
            @click="closeDialog(extendDialog)"
          >
            Cancel
          </v-btn>
          <v-btn
            large
            color="primary"
            class="font-weight-bold px-8 ml-3"
            data-test="vendor-connections-extend-confirm"
            @click="confirmExtend()"
          >
            Extend Connection
          </v-btn>
        </div>
      </template>
    </ModalDialog>
  </div>
</template>

<script lang="ts">
import { Ref, computed, defineComponent, onBeforeUnmount, onMounted, reactive, ref } from '@vue/composition-api'
import {
  canAccessVendorConnections,
  getDaysUntilExpiry,
  getVendorConnectionStatus,
  mapLinkingKeyToVendorConnection
} from '@/util/vendor-connection-util'
import { BaseTableHeaderI } from '@/components/datatable/interfaces'
import { BaseVDataTable } from '@/components'
import CommonUtils from '@/util/common-util'
import { EventBus } from '@/event-bus'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import { VendorConnection } from '@/models/vendorConnection'
import moment from 'moment'
import { useAccountChangeHandler } from '@/composables'
import { useI18n } from 'vue-i18n-composable'
import { useLinkingKeysStore } from '@/stores/linkingKeys'
import { useOrgStore } from '@/stores/org'
import { useUserStore } from '@/stores/user'

const TABLE_HEADERS: BaseTableHeaderI[] = [
  {
    col: 'serviceProviderName',
    hasFilter: false,
    value: 'Service Provider Name',
    class: 'bold-header'
  },
  {
    col: 'dateAdded',
    hasFilter: false,
    value: 'Date Added',
    class: 'bold-header'
  },
  {
    col: 'createdBy',
    hasFilter: false,
    value: 'Created By',
    class: 'bold-header'
  },
  {
    col: 'expiryDate',
    hasFilter: false,
    value: 'Expiry Date',
    class: 'bold-header'
  },
  {
    col: 'action',
    hasFilter: false,
    value: 'Action',
    class: 'bold-header text-right',
    itemClass: 'text-right',
    width: '180px'
  }
]

export default defineComponent({
  name: 'VendorConnectionsTable',
  components: {
    BaseVDataTable,
    ModalDialog
  },
  setup () {
    const { t } = useI18n()
    const orgStore = useOrgStore()
    const linkingKeysStore = useLinkingKeysStore()
    const userStore = useUserStore()
    const { setAccountChangedHandler, beforeDestroy } = useAccountChangeHandler()

    const isLoading = ref(false)
    const connectionsList = ref<VendorConnection[]>([])
    const actionMenuOpen = reactive<Record<string, boolean>>({})
    const selectedConnection = ref<VendorConnection | null>(null)
    const removeDialog: Ref<InstanceType<typeof ModalDialog>> = ref(null)
    const extendDialog: Ref<InstanceType<typeof ModalDialog>> = ref(null)

    const currentMembership = computed(() => orgStore.currentMembership)

    const canManageConnections = computed(() => {
      return canAccessVendorConnections(
        currentMembership.value?.membershipTypeCode,
        userStore.currentUser?.roles
      )
    })

    const noDataText = computed(() => t('vendorConnectionsEmpty'))

    const loadConnections = async () => {
      isLoading.value = true
      connectionsList.value = []

      const orgId = orgStore.currentOrganization?.id
      if (!orgId) {
        isLoading.value = false
        return
      }

      try {
        const response = await linkingKeysStore.fetchLinkingKeys(orgId)
        connectionsList.value = (response?.linkingKeys || []).map(mapLinkingKeyToVendorConnection)
      } catch {
        connectionsList.value = []
      } finally {
        isLoading.value = false
      }
    }

    const initialize = () => {
      loadConnections()
    }

    const getConnectionStatus = (connection: VendorConnection) => {
      return getVendorConnectionStatus(connection.expiryDate)
    }

    const formatDateAdded = (dateAdded: string): string => {
      return CommonUtils.formatDisplayDate(moment.utc(dateAdded).toDate(), 'MMM D, YYYY h:mmA')
    }

    const formatExpiryDate = (expiryDate: string): string => {
      return CommonUtils.formatDisplayDate(expiryDate, 'MMM D, YYYY')
    }

    const openRemoveModal = (connection: VendorConnection) => {
      selectedConnection.value = connection
      removeDialog.value?.open?.()
    }

    const openExtendModal = (connection: VendorConnection) => {
      selectedConnection.value = connection
      extendDialog.value?.open?.()
    }

    const confirmRemove = () => {
      if (!selectedConnection.value) {
        return
      }

      const providerName = selectedConnection.value.serviceProviderName
      connectionsList.value = connectionsList.value
        .filter(connection => connection.id !== selectedConnection.value?.id)

      EventBus.$emit('show-toast', {
        message: t('vendorConnectionsRemovedToast', { providerName }),
        type: 'primary',
        timeout: 3000
      })

      selectedConnection.value = null
      removeDialog.value?.close?.()
    }

    const confirmExtend = async () => {
      if (!selectedConnection.value) {
        return
      }

      const providerName = selectedConnection.value.serviceProviderName
      const connectionId = selectedConnection.value.id
      const orgId = orgStore.currentOrganization?.id
      if (!orgId) {
        return
      }

      try {
        const updatedKey = await linkingKeysStore.extendLinkingKey({
          orgId,
          keyId: Number(connectionId)
        })
        connectionsList.value = connectionsList.value.map(connection => {
          if (connection.id !== connectionId) {
            return connection
          }
          return mapLinkingKeyToVendorConnection(updatedKey)
        })

        EventBus.$emit('show-toast', {
          message: t('vendorConnectionsExtendedToast', { providerName }),
          type: 'primary',
          timeout: 3000
        })
      } catch {
        return
      } finally {
        selectedConnection.value = null
        extendDialog.value?.close?.()
      }
    }

    const closeDialog = (dialog: InstanceType<typeof ModalDialog> | null) => {
      dialog?.close?.()
      selectedConnection.value = null
    }

    const getIndexedTag = (tag: string, idx: string): string => {
      return `${tag}-${idx}`
    }

    onMounted(() => {
      setAccountChangedHandler(initialize)
      initialize()
    })

    onBeforeUnmount(() => {
      beforeDestroy()
    })

    return {
      actionMenuOpen,
      canManageConnections,
      closeDialog,
      confirmExtend,
      confirmRemove,
      connectionsList,
      extendDialog,
      formatDateAdded,
      formatExpiryDate,
      getConnectionStatus,
      getDaysUntilExpiry,
      getIndexedTag,
      isLoading,
      noDataText,
      openExtendModal,
      openRemoveModal,
      removeDialog,
      tableHeaders: TABLE_HEADERS
    }
  }
})
</script>

<style lang="scss" scoped>
.label {
  border-radius: 4px;
  color: white;
  font-size: 10px;
  font-weight: bold;
  letter-spacing: 0.04em;
  padding: 2px 6px;

  &.expiring {
    background: $gray7;
  }

  &.expired {
    background: $gray7;
  }
}

::v-deep {
  .base-table__header__title {
    white-space: nowrap;
  }

  .base-table__item-cell {
    height: 71px;
  }
}

.vendor-connection-dialog__actions {
  display: flex;
  justify-content: flex-end;
  width: 100%;
}

.action-buttons {
  $vendor-action-main-width: 6.25rem;
  $vendor-action-menu-width: 36px;
  $vendor-action-group-width: calc(#{$vendor-action-main-width} + #{$vendor-action-menu-width} + 1px);

  ::v-deep .vendor-connection-action-btn {
    box-shadow: 0 1px 1px 0 rgb(0 0 0 / 20%), 0 2px 2px 0 rgb(0 0 0 / 14%), 0 1px 5px 0 rgb(0 0 0 / 12%) !important;
    font-weight: 700 !important;
    height: 36px !important;
    letter-spacing: normal;
    min-height: 36px !important;
    text-transform: none !important;
  }

  ::v-deep .vendor-connection-action-btn--split-main {
    border-bottom-right-radius: 0 !important;
    border-top-right-radius: 0 !important;
    max-width: $vendor-action-main-width !important;
    min-width: $vendor-action-main-width !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
    width: $vendor-action-main-width !important;
  }

  ::v-deep .vendor-connection-action-btn--standalone {
    max-width: $vendor-action-group-width !important;
    min-width: $vendor-action-group-width !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
    width: $vendor-action-group-width !important;
  }
}

.vendor-connection-split-actions {
  ::v-deep .vendor-connection-action-btn--split-menu {
    border-bottom-left-radius: 0 !important;
    border-top-left-radius: 0 !important;
    margin-left: 1px;
    max-width: 36px !important;
    min-width: 36px !important;
    padding: 0 !important;
    width: 36px !important;

    .v-icon {
      font-size: 20px;
    }
  }
}
</style>

<style lang="scss">
// Figma spacing for vendor connection confirmation dialogs only.
.v-dialog.vendor-connection-dialog {
  .v-card__title {
    align-items: flex-start;
    padding: 32px 40px 0 !important;
  }

  .v-card__text {
    padding: 8px 40px 0 !important;

    .modal-dialog-text {
      line-height: 1.5;
      margin-bottom: 0;
      text-align: left;
    }
  }

  .vendor-connection-dialog__prompt {
    display: block;
    margin-top: 16px;
  }

  .v-card__actions {
    justify-content: flex-end;
    padding: 24px 40px 32px !important;
  }
}
</style>
