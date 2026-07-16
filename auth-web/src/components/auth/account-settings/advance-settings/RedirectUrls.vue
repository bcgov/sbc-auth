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
      :disabled="isLoading"
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
          class="font-weight-bold"
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
          @click="$refs.editUrlDialog.close()"
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
          @click="$refs.removeUrlDialog.close()"
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
import { Action, State } from 'pinia-class'
import { Component, Mixins } from 'vue-property-decorator'
import { Member, MembershipType, OrgRedirectUrl, Organization } from '@/models/Organization'
import AccountChangeMixin from '@/components/auth/mixins/AccountChangeMixin.vue'
import CommonUtils from '@/util/common-util'
import { Event } from '@/models/event'
import { EventBus } from '@/event-bus'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import { normalizeError } from '@/util/error-util'
import { useOrgStore } from '@/stores/org'

export interface RedirectUrlItem {
  id: number
  url: string
  createdBy: string
  createdDate: string
}

@Component({
  components: {
    ModalDialog
  }
})
export default class RedirectUrls extends Mixins(AccountChangeMixin) {
  @State(useOrgStore) readonly currentOrganization!: Organization
  @State(useOrgStore) readonly currentMembership!: Member
  @Action(useOrgStore) readonly getOrgRedirectUrls!: (orgId: number) => Promise<{ redirectUrls: OrgRedirectUrl[] }>
  @Action(useOrgStore) readonly createOrgRedirectUrl!: (details: { orgId: number, redirectUrl: string }) => Promise<OrgRedirectUrl>
  @Action(useOrgStore) readonly updateOrgRedirectUrl!:
    (details: { orgId: number, urlId: number, redirectUrl: string }) => Promise<OrgRedirectUrl>
  @Action(useOrgStore) readonly deleteOrgRedirectUrl!: (details: { orgId: number, urlId: number }) => Promise<any>

  public isAddingUrl = false
  public isLoading = true
  public newUrl = ''
  public newUrlError = ''
  public editedUrl = ''
  public editedUrlError = ''
  public redirectUrls: RedirectUrlItem[] = []
  public editingId: number | null = null
  public removingId: number | null = null
  public recentlyAddedId: number | null = null
  public recentlyChangedId: number | null = null
  public readonly PAGE_LIMIT: number = 5

  $refs: {
    editUrlDialog: InstanceType<typeof ModalDialog>
    removeUrlDialog: InstanceType<typeof ModalDialog>
  }

  public formatDate = CommonUtils.formatDisplayDate

  // add/edit/remove is restricted to Admin/Coordinator
  // other roles get a read-only table
  public get canManageUrls (): boolean {
    return [MembershipType.Admin, MembershipType.Coordinator]
      .includes(this.currentMembership?.membershipTypeCode)
  }

  public get redirectUrlHeaders () {
    const headers = [
      {
        text: 'Redirect URL',
        align: 'left',
        sortable: false,
        value: 'url',
        class: 'bold-header'
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
    return this.canManageUrls ? headers : headers.filter(header => header.value !== 'action')
  }

  public async mounted () {
    this.setAccountChangedHandler(this.initialize)
    this.initialize()
  }

  public async initialize () {
    this.recentlyAddedId = null
    this.recentlyChangedId = null
    // an account switch invalidates any in-progress add/edit/remove state
    this.cancelAddUrl()
    this.$refs.editUrlDialog?.close()
    this.$refs.removeUrlDialog?.close()
    await this.loadRedirectUrls()
  }

  public async loadRedirectUrls () {
    this.isLoading = true
    try {
      const resp = await this.getOrgRedirectUrls(this.currentOrganization.id)
      this.redirectUrls = (resp?.redirectUrls || []).map(item => ({
        id: item.id,
        url: item.redirectUrl,
        createdBy: item.createdBy,
        createdDate: item.createdDate
      }))
    } catch (e) {
      this.showErrorToast()
      this.redirectUrls = []
    }
    this.isLoading = false
  }

  public get indexedRedirectUrls () {
    return this.redirectUrls.map((item, index) => ({
      index,
      ...item,
      added: item.id === this.recentlyAddedId,
      changed: item.id === this.recentlyChangedId
    }))
  }

  public showAddUrlInput () {
    this.isAddingUrl = true
  }

  public cancelAddUrl () {
    this.newUrl = ''
    this.newUrlError = ''
    this.isAddingUrl = false
  }

  public async addUrl () {
    const url = this.newUrl.trim().toLowerCase()
    this.newUrlError = this.validateUrl(url)
    if (this.newUrlError) {
      return
    }
    this.isLoading = true
    try {
      const created = await this.createOrgRedirectUrl({ orgId: this.currentOrganization.id, redirectUrl: url })
      this.recentlyAddedId = created.id
      this.recentlyChangedId = null
      this.newUrl = ''
      this.isAddingUrl = false
      await this.loadRedirectUrls()
      this.showToast('Redirect URL added.')
    } catch (e) {
      this.newUrlError = this.getServerErrorMessage(e)
      this.isLoading = false
    }
  }

  public editUrl (id: number) {
    const item = this.redirectUrls.find(item => item.id === id)
    if (!item) {
      return
    }
    this.editedUrl = item.url
    this.editedUrlError = ''
    this.editingId = id
    this.$refs.editUrlDialog.open()
  }

  public async saveEditedUrl () {
    const url = this.editedUrl.trim().toLowerCase()
    this.editedUrlError = this.validateUrl(url)
    if (this.editedUrlError) {
      return
    }
    const current = this.redirectUrls.find(item => item.id === this.editingId)
    // missing entry or unchanged value — close with no API call
    if (!current || url === current.url) {
      this.$refs.editUrlDialog.close()
      return
    }
    this.isLoading = true
    try {
      const updated = await this.updateOrgRedirectUrl({
        orgId: this.currentOrganization.id,
        urlId: current.id,
        redirectUrl: url
      })
      this.recentlyChangedId = updated.id
      this.recentlyAddedId = null
      this.$refs.editUrlDialog.close()
      await this.loadRedirectUrls()
      this.showToast('Redirect URL updated.')
    } catch (e) {
      this.isLoading = false
      this.showErrorToast()
    }
  }

  public cancelEditUrl () {
    this.editedUrl = ''
    this.editedUrlError = ''
    this.editingId = null
  }

  public confirmRemoveUrl (id: number) {
    this.removingId = id
    this.$refs.removeUrlDialog.open()
  }

  public async removeUrl () {
    const target = this.redirectUrls.find(item => item.id === this.removingId)
    if (!target) {
      this.$refs.removeUrlDialog.close()
      return
    }
    this.isLoading = true
    try {
      await this.deleteOrgRedirectUrl({ orgId: this.currentOrganization.id, urlId: target.id })
      this.$refs.removeUrlDialog.close()
      await this.loadRedirectUrls()
      this.showToast('Redirect URL removed.')
    } catch (e) {
      this.isLoading = false
      this.showErrorToast()
    }
  }

  private showToast (message: string) {
    const event: Event = { message, type: 'success', timeout: 3000 }
    EventBus.$emit('show-toast', event)
  }

  private showErrorToast () {
    const event: Event = { message: 'Something went wrong. Please try again.', type: 'error', timeout: 3000 }
    EventBus.$emit('show-toast', event)
  }

  private getServerErrorMessage (e: any): string {
    const normalized = normalizeError(e)
    if ((normalized.status === 400 || normalized.status === 409) && typeof normalized.message === 'string') {
      return normalized.message
    }
    return 'An error occurred while saving the redirect URL. Please try again.'
  }

  private validateUrl (url: string): string {
    if (!url) {
      return 'Enter a redirect URL.'
    }
    if (!CommonUtils.isValidHttpsUrl(url)) {
      return 'Enter a valid URL beginning with https://.'
    }
    if (this.redirectUrls.some(item => item.url.toLowerCase() === url && item.id !== this.editingId)) {
      return 'This URL has already been added.'
    }
    return ''
  }
}
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
  }

  .v-list-item__subtitle {
    width: 120px;
  }
}

</style>
