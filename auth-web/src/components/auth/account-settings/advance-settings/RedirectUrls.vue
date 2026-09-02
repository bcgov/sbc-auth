<template>
  <div class="pb-10">
    <header class="view-header mb-7">
      <h2 class="view-header__title">
        Redirect URLs
      </h2>
      <v-btn
        v-if="canManageUrls && !isAddingUrl"
        large
        depressed
        class="px-6"
        color="primary"
        aria-label="Add URL"
        data-test="add-url-button"
        :disabled="isLoading"
        @click="showAddUrlInput()"
      >
        <v-icon class="mr-1">
          mdi-plus
        </v-icon>
        Add URL
      </v-btn>
    </header>

    <template v-if="isAddingUrl">
      <p
        class="mb-5"
        data-test="add-url-helper-text"
      >
        {{ $t('redirectUrlHelperText') }}
      </p>
      <div class="add-url-row mb-7">
        <v-text-field
          v-model="newUrl"
          filled
          hide-details="auto"
          placeholder="Enter URL"
          aria-label="Enter URL"
          maxlength="250"
          data-test="url-input"
          :error-messages="newUrlError"
          @input="newUrlError = ''"
        />
        <v-btn
          outlined
          large
          depressed
          color="primary"
          class="ml-3 px-7"
          aria-label="Cancel"
          data-test="cancel-url-button"
          @click="cancelAddUrl()"
        >
          Cancel
        </v-btn>
        <v-btn
          large
          depressed
          color="primary"
          class="ml-3 px-8 font-weight-bold"
          aria-label="Add"
          data-test="confirm-add-url-button"
          :disabled="isLoading"
          :loading="isLoading"
          @click="addUrl()"
        >
          Add
        </v-btn>
      </div>
    </template>

    <v-data-table
      class="redirect-url-list"
      :headers="redirectUrlHeaders"
      :items="indexedRedirectUrls"
      :items-per-page="PAGE_LIMIT"
      :loading="isLoading"
      loading-text="Loading..."
      no-data-text="No Redirect URLs"
      :hide-default-footer="indexedRedirectUrls.length <= PAGE_LIMIT"
    >
      <template #loading>
        Loading...
      </template>
      <template #[`item.url`]="{ item }">
        <div
          class="font-weight-bold text-break"
          :data-test="`url-row-${item.index}`"
        >
          {{ item.url }}
        </div>
        <v-chip
          v-if="item.added"
          x-small
          label
          color="primary"
          class="font-weight-bold white--text mt-1"
          :data-test="`url-added-chip-${item.index}`"
        >
          ADDED
        </v-chip>
        <v-chip
          v-else-if="item.changed"
          x-small
          label
          color="primary"
          class="font-weight-bold white--text mt-1"
          :data-test="`url-changed-chip-${item.index}`"
        >
          CHANGED
        </v-chip>
      </template>
      <template #[`item.createdDate`]="{ item }">
        {{ formatDate(item.createdDate, 'MMM DD, YYYY') }}
      </template>
      <template #[`item.action`]="{ item }">
        <div class="url-actions">
          <v-btn
            depressed
            color="primary"
            class="remove-url-btn px-6"
            aria-label="Remove URL"
            :data-test="`remove-url-button-${item.index}`"
            @click="confirmRemoveUrl(item.id)"
          >
            Remove
          </v-btn>
          <v-menu
            offset-y
            left
          >
            <template #activator="{ on, value }">
              <v-btn
                depressed
                color="primary"
                class="more-actions-btn"
                aria-label="More Actions"
                :data-test="`more-actions-button-${item.index}`"
                v-on="on"
              >
                <v-icon>{{ value ? 'mdi-menu-up' : 'mdi-menu-down' }}</v-icon>
              </v-btn>
            </template>
            <v-list
              class="py-0"
            >
              <v-list-item
                :data-test="`edit-url-menu-item-${item.index}`"
                @click="editUrl(item.id)"
              >
                <v-list-item-subtitle
                  class="primary--text text-left"
                >
                  Edit URL
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-menu>
        </div>
      </template>
    </v-data-table>

    <!-- Edit URL Dialog -->
    <ModalDialog
      ref="editUrlDialog"
      title="Edit Redirect URL"
      dialog-class="info-dialog"
      max-width="720"
      :show-icon="false"
      show-close-icon
      data-test="edit-url-modal"
      @close-dialog="cancelEditUrl()"
    >
      <template #text>
        <p
          class="mb-7"
          data-test="edit-url-helper-text"
        >
          {{ $t('editRedirectUrlHelperText') }}
        </p>
        <p class="mb-2">
          Enter redirect URL:
        </p>
        <v-text-field
          v-model="editedUrl"
          filled
          hide-details="auto"
          aria-label="Enter redirect URL"
          maxlength="250"
          data-test="edit-url-input"
          :error-messages="editedUrlError"
          @input="editedUrlError = ''"
        />
      </template>
      <template #actions>
        <v-btn
          outlined
          large
          depressed
          color="primary"
          class="px-7"
          aria-label="Cancel"
          data-test="cancel-edit-url-button"
          @click="editUrlDialog.close()"
        >
          Cancel
        </v-btn>
        <v-btn
          large
          depressed
          color="primary"
          class="ml-3 px-8 font-weight-bold"
          aria-label="Save"
          data-test="save-edit-url-button"
          :disabled="isLoading"
          :loading="isLoading"
          @click="saveEditedUrl()"
        >
          Save
        </v-btn>
      </template>
    </ModalDialog>

    <!-- Remove URL Confirmation Dialog -->
    <ModalDialog
      ref="removeUrlDialog"
      title="Caution: Remove Redirect URL?"
      dialog-class="info-dialog"
      max-width="720"
      :show-icon="false"
      show-close-icon
      data-test="remove-url-modal"
      @close-dialog="removingId = null"
    >
      <template #text>
        <p data-test="remove-url-text">
          {{ $t('removeRedirectUrlText') }}
        </p>
      </template>
      <template #actions>
        <v-btn
          outlined
          large
          depressed
          color="primary"
          class="px-7"
          aria-label="Cancel"
          data-test="cancel-remove-url-button"
          @click="removeUrlDialog.close()"
        >
          Cancel
        </v-btn>
        <v-btn
          large
          depressed
          color="primary"
          class="ml-3 px-8 font-weight-bold"
          aria-label="Remove URL"
          data-test="confirm-remove-url-button"
          :disabled="isLoading"
          :loading="isLoading"
          @click="removeUrl()"
        >
          Remove URL
        </v-btn>
      </template>
    </ModalDialog>
  </div>
</template>

<script lang="ts">
import { MembershipType, OrgRedirectUrl, OrgRedirectUrls } from '@/models/Organization'
import { Ref, computed, defineComponent, onBeforeUnmount, onMounted, ref } from '@vue/composition-api'
import CommonUtils from '@/util/common-util'
import { Event } from '@/models/event'
import { EventBus } from '@/event-bus'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import { normalizeError } from '@/util/error-util'
import { useAccountChangeHandler } from '@/composables'
import { useOrgStore } from '@/stores/org'
import { useRedirectUrlsStore } from '@/stores/redirectUrls'

export interface RedirectUrlItem {
  id: number
  url: string
  createdBy: string
  createdDate: string
}

const PAGE_LIMIT = 5

// only lowercase the scheme and host name, the path and query are case-sensitive
// and the backend compares URLs as exact strings
const normalizeUrl = (value: string): string =>
  value.trim().replace(/^(https:\/\/[^/?#]*)/i, part => part.toLowerCase())

export default defineComponent({
  name: 'RedirectUrls',
  components: {
    ModalDialog
  },
  setup () {
    const orgStore = useOrgStore()
    const redirectUrlsStore = useRedirectUrlsStore()
    const { setAccountChangedHandler, beforeDestroy } = useAccountChangeHandler()

    const isAddingUrl = ref(false)
    const isLoading = ref(true)
    const newUrl = ref('')
    const newUrlError = ref('')
    const editedUrl = ref('')
    const editedUrlError = ref('')
    const redirectUrls = ref<RedirectUrlItem[]>([])
    const editingId = ref<number | null>(null)
    const removingId = ref<number | null>(null)
    const recentlyAddedId = ref<number | null>(null)
    const recentlyChangedId = ref<number | null>(null)
    const editUrlDialog: Ref<InstanceType<typeof ModalDialog>> = ref(null)
    const removeUrlDialog: Ref<InstanceType<typeof ModalDialog>> = ref(null)

    // add/edit/remove is restricted to Admin/Coordinator
    // other roles get a read-only table
    const canManageUrls = computed<boolean>(() => {
      return [MembershipType.Admin, MembershipType.Coordinator]
        .includes(orgStore.currentMembership?.membershipTypeCode)
    })

    const redirectUrlHeaders = computed(() => {
      const headers = [
        {
          text: 'Redirect URL',
          align: 'left',
          sortable: false,
          value: 'url',
          class: 'bold-header',
          width: '40%'
        },
        {
          text: 'Created By',
          align: 'left',
          sortable: false,
          value: 'createdBy',
          class: 'bold-header'
        },
        {
          text: 'Created Date',
          align: 'left',
          sortable: false,
          value: 'createdDate',
          class: 'bold-header'
        },
        {
          text: 'Action',
          align: 'left',
          sortable: false,
          value: 'action',
          class: 'bold-header',
          width: '150px'
        }
      ]
      // filter out action column for users that are not allowed to manage urls
      return canManageUrls.value ? headers : headers.filter(header => header.value !== 'action')
    })

    const indexedRedirectUrls = computed(() => {
      return redirectUrls.value.map((item, index) => ({
        index,
        ...item,
        added: item.id === recentlyAddedId.value,
        changed: item.id === recentlyChangedId.value
      }))
    })

    const showToast = (message: string) => {
      const event: Event = { message, type: 'success', timeout: 3000 }
      EventBus.$emit('show-toast', event)
    }

    const showErrorToast = () => {
      const event: Event = { message: 'Something went wrong. Please try again.', type: 'error', timeout: 3000 }
      EventBus.$emit('show-toast', event)
    }

    const getServerErrorMessage = (e: any): string => {
      const normalized = normalizeError(e)
      if ((normalized.status === 400 || normalized.status === 409) && typeof normalized.message === 'string') {
        return normalized.message
      }
      return 'An error occurred while saving the redirect URL. Please try again.'
    }

    const validateUrl = (url: string): string => {
      if (!url) {
        return 'Enter a redirect URL.'
      }
      if (!CommonUtils.isValidHttpsUrl(url)) {
        return 'Enter a valid URL beginning with https://.'
      }
      if (redirectUrls.value.some(item => item.url === url && item.id !== editingId.value)) {
        return 'This URL has already been added.'
      }
      return ''
    }

    const loadRedirectUrls = async () => {
      isLoading.value = true
      try {
        const resp = await redirectUrlsStore.getOrgRedirectUrls(orgStore.currentOrganization.id) as OrgRedirectUrls
        redirectUrls.value = (resp?.redirectUrls || []).map(item => ({
          id: item.id,
          url: item.redirectUrl,
          createdBy: item.createdBy,
          createdDate: item.createdDate
        }))
      } catch (e) {
        showErrorToast()
        redirectUrls.value = []
      }
      isLoading.value = false
    }

    const showAddUrlInput = () => {
      isAddingUrl.value = true
    }

    const cancelAddUrl = () => {
      newUrl.value = ''
      newUrlError.value = ''
      isAddingUrl.value = false
    }

    const initialize = async () => {
      recentlyAddedId.value = null
      recentlyChangedId.value = null
      // an account switch invalidates any in-progress add/edit/remove state
      cancelAddUrl()
      editUrlDialog.value?.close()
      removeUrlDialog.value?.close()
      await loadRedirectUrls()
    }

    const addUrl = async () => {
      const url = normalizeUrl(newUrl.value)
      newUrlError.value = validateUrl(url)
      if (newUrlError.value) {
        return
      }
      isLoading.value = true
      try {
        const created = await redirectUrlsStore.createOrgRedirectUrl({
          orgId: orgStore.currentOrganization.id,
          redirectUrl: url
        }) as OrgRedirectUrl
        recentlyAddedId.value = created.id
        recentlyChangedId.value = null
        newUrl.value = ''
        isAddingUrl.value = false
        await loadRedirectUrls()
        showToast('Redirect URL added.')
      } catch (e) {
        newUrlError.value = getServerErrorMessage(e)
        isLoading.value = false
      }
    }

    const editUrl = (id: number) => {
      const item = redirectUrls.value.find(item => item.id === id)
      if (!item) {
        return
      }
      editedUrl.value = item.url
      editedUrlError.value = ''
      editingId.value = id
      editUrlDialog.value.open()
    }

    const saveEditedUrl = async () => {
      const url = normalizeUrl(editedUrl.value)
      editedUrlError.value = validateUrl(url)
      if (editedUrlError.value) {
        return
      }
      const current = redirectUrls.value.find(item => item.id === editingId.value)
      // missing entry or unchanged value — close with no API call
      if (!current || url === current.url) {
        editUrlDialog.value.close()
        return
      }
      isLoading.value = true
      try {
        const updated = await redirectUrlsStore.updateOrgRedirectUrl({
          orgId: orgStore.currentOrganization.id,
          urlId: current.id,
          redirectUrl: url
        }) as OrgRedirectUrl
        recentlyChangedId.value = updated.id
        recentlyAddedId.value = null
        editUrlDialog.value.close()
        await loadRedirectUrls()
        showToast('Redirect URL updated.')
      } catch (e) {
        isLoading.value = false
        showErrorToast()
      }
    }

    const cancelEditUrl = () => {
      editedUrl.value = ''
      editedUrlError.value = ''
      editingId.value = null
    }

    const confirmRemoveUrl = (id: number) => {
      removingId.value = id
      removeUrlDialog.value.open()
    }

    const removeUrl = async () => {
      const target = redirectUrls.value.find(item => item.id === removingId.value)
      if (!target) {
        removeUrlDialog.value.close()
        return
      }
      isLoading.value = true
      try {
        await redirectUrlsStore.deleteOrgRedirectUrl({ orgId: orgStore.currentOrganization.id, urlId: target.id })
        removeUrlDialog.value.close()
        await loadRedirectUrls()
        showToast('Redirect URL removed.')
      } catch (e) {
        isLoading.value = false
        showErrorToast()
      }
    }

    onMounted(() => {
      setAccountChangedHandler(initialize)
      initialize()
    })

    onBeforeUnmount(() => {
      beforeDestroy()
    })

    return {
      PAGE_LIMIT,
      addUrl,
      canManageUrls,
      cancelAddUrl,
      cancelEditUrl,
      confirmRemoveUrl,
      editUrl,
      editUrlDialog,
      editedUrl,
      editedUrlError,
      editingId,
      formatDate: CommonUtils.formatDisplayDate,
      indexedRedirectUrls,
      isAddingUrl,
      isLoading,
      loadRedirectUrls,
      newUrl,
      newUrlError,
      recentlyAddedId,
      recentlyChangedId,
      redirectUrlHeaders,
      redirectUrls,
      removeUrl,
      removeUrlDialog,
      removingId,
      saveEditedUrl,
      showAddUrlInput
    }
  }
})
</script>

<style lang="scss" scoped>
.view-header {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}

.add-url-row {
  display: flex;
  align-items: flex-start;

  ::v-deep .v-input__slot {
    height: 44px !important;
    min-height: 44px !important;
  }
}

.url-actions {
  display: flex;

  .remove-url-btn {
    min-width: 5rem !important;
    border-top-right-radius: 0;
    border-bottom-right-radius: 0;
  }

  .more-actions-btn {
    padding: 0;
    min-width: 50px;
    margin-left: 1px;
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
  }
}

::v-deep {
  .v-data-table th {
    white-space: nowrap;
  }

  .v-data-table td {
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
    height: auto;
    vertical-align: top;
  }

  .v-list-item__subtitle {
    width: 120px;
  }
}

</style>
