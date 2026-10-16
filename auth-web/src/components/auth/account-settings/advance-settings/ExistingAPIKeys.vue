<template>
  <div>
    <header class="view-header align-center mt-n1 mb-7">
      <div>
        <h2 class="view-header__title">
          API Keys
        </h2>
        <p
          class="mb-0 mt-1"
          data-test="api-key-counts"
        >
          <strong>{{ namedKeyCount }}/{{ maxNamedKeys }}</strong> Named Keys |
          <strong>{{ unnamedKeyCount }}</strong> Unnamed Keys
        </p>
      </div>
      <v-btn
        v-if="isCreateApiKeyEnabled"
        large
        depressed
        class="px-6"
        color="primary"
        aria-label="Create Key"
        data-test="create-api-key-button"
        :disabled="isCreateFormOpen || isNamedKeyLimitNoticeShown"
        @click="startCreateKey()"
      >
        <v-icon
          class="mr-2"
          size="18"
        >
          mdi-key-outline
        </v-icon>
        Create Key
      </v-btn>
    </header>

    <!-- Create key -->
    <div
      v-if="isCreateFormOpen"
      class="d-flex align-start mb-7"
      data-test="create-api-key-form"
    >
      <v-text-field
        v-model="newKeyName"
        filled
        dense
        class="key-name-input"
        hide-details="auto"
        placeholder="Enter an API Key Name (Optional)"
        aria-label="Enter an API Key Name (Optional)"
        maxlength="100"
        hint="This will help you identify the key in the list later"
        persistent-hint
        data-test="key-name-input"
        @keyup.enter="createKey()"
      />
      <v-btn
        outlined
        large
        depressed
        color="primary"
        class="ml-6 px-7"
        aria-label="Cancel"
        data-test="cancel-create-key-button"
        :disabled="isCreating"
        @click="closeCreateForm()"
      >
        Cancel
      </v-btn>
      <v-btn
        large
        depressed
        color="primary"
        class="ml-3 px-8 font-weight-bold"
        aria-label="Create"
        data-test="confirm-create-key-button"
        :loading="isCreating"
        :disabled="isCreating"
        @click="createKey()"
      >
        Create
      </v-btn>
    </div>

    <!-- Named key limit reached -->
    <div
      v-if="isNamedKeyLimitNoticeShown"
      class="mb-7"
      data-test="named-key-limit-notice"
    >
      <p class="mb-5">
        You have reached the maximum of {{ maxNamedKeys }} named API keys. To create another named key,
        delete one you no longer use. You can still create unnamed keys.
      </p>
      <div class="d-flex justify-end">
        <v-btn
          outlined
          large
          depressed
          color="primary"
          class="px-7"
          aria-label="Cancel"
          data-test="cancel-unnamed-key-button"
          :disabled="isCreating"
          @click="isNamedKeyLimitNoticeOpen = false"
        >
          Cancel
        </v-btn>
        <v-btn
          large
          depressed
          color="primary"
          class="ml-3 px-8 font-weight-bold"
          aria-label="Create"
          data-test="create-unnamed-key-button"
          :loading="isCreating"
          :disabled="isCreating"
          @click="createUnnamedKey()"
        >
          Create
        </v-btn>
      </div>
    </div>

    <div>
      <v-data-table
        class="apikey-list mb-10"
        :headers="activityHeader"
        :items="apiKeyList"
        item-key="apiKey"
        no-data-text="No API Keys"
        :loading="isLoading"
        loading-text="Loading..."
        sort-by="keyCreatedDate"
        :sort-desc="true"
        :items-per-page="PAGE_LIMIT"
        :hide-default-footer="apiKeyList.length <= PAGE_LIMIT"
      >
        <template #loading>
          Loading...
        </template>
        <template #[`item.apiKeyName`]="{ item }">
          <div class=" font-weight-bold">
            {{ getKeyName(item) }}
          </div>
          <v-chip
            v-if="item.isNewlyAdded"
            small
            label
            color="primary"
            text-color="white"
            class="font-weight-bold mt-1"
            data-test="new-api-key-chip"
          >
            ADDED
          </v-chip>
        </template>
        <template #[`item.environment`]="{ item }">
          <div class="text-capitalize">
            {{ item.environment }}
          </div>
        </template>
        <template #[`item.keyCreatedDate`]="{ item }">
          {{ item.keyCreatedDate ? formatDate(item.keyCreatedDate, 'MMMM DD, YYYY') : '-' }}
        </template>
        <template #[`item.apiKey`]="{ item }">
          <span>{{ maskApiKey(item.apiKey) }}</span>
        </template>
        <template #[`item.keyStatus`]="{ item }">
          <span data-test="key-status-chip">{{ getKeyStatusLabel(item) }}</span>
        </template>
        <template #[`item.action`]="{ item }">
          <!-- Revoke -->
          <v-btn
            v-if="isKeyActive(item)"
            depressed
            aria-label="Revoke"
            color="primary"
            :data-test="getIndexedTag('confirm-button', item.apiKey)"
            @click="confirmationModal(item)"
          >
            Revoke
          </v-btn>
          <!-- Delete, only revoked keys can be deleted -->
          <v-btn
            v-else-if="isKeyRevoked(item)"
            depressed
            aria-label="Delete"
            color="primary"
            :data-test="getIndexedTag('delete-button', item.apiKey)"
            @click="confirmDelete(item)"
          >
            Delete
          </v-btn>
        </template>
      </v-data-table>
    </div>

    <!-- Confirm Revoke Dialog -->
    <ModalDialog
      ref="confirmActionDialog"
      title="Revoke API Key?"
      dialog-class="info-dialog"
      max-width="650"
      :show-icon="false"
      show-close-icon
      data-test="confirmation-modal"
    >
      <template #text>
        <p class="mb-0">
          Revoking will immediately disable this API key. Are you sure you wish to revoke API Key:
          <strong>{{ getKeyName(selectedApi) }}</strong> ?
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
          data-test="cancel-revoke-key-button"
          :disabled="isLoading"
          @click="close($refs.confirmActionDialog)"
        >
          Cancel
        </v-btn>
        <v-btn
          large
          depressed
          color="primary"
          class="ml-3 px-8 font-weight-bold"
          aria-label="Revoke"
          data-test="confirm-revoke-key-button"
          :loading="isLoading"
          :disabled="isLoading"
          @click="revokeApi()"
        >
          Revoke
        </v-btn>
      </template>
    </ModalDialog>

    <!-- Confirm Delete Dialog -->
    <ModalDialog
      ref="confirmDeleteDialog"
      title="Delete API Key?"
      dialog-class="info-dialog"
      max-width="650"
      :show-icon="false"
      show-close-icon
      data-test="confirm-delete-modal"
    >
      <template #text>
        <p class="mb-0">
          Deleting this API key will permanently remove it. This action cannot be undone.
        </p>
        <p class="mb-0">
          Are you sure you want to delete API Key: <strong>{{ getKeyName(selectedApi) }}</strong> ?
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
          data-test="cancel-delete-key-button"
          :disabled="isLoading"
          @click="close($refs.confirmDeleteDialog)"
        >
          Cancel
        </v-btn>
        <v-btn
          large
          depressed
          color="error"
          class="ml-3 px-8 font-weight-bold"
          aria-label="Delete"
          data-test="confirm-delete-key-button"
          :loading="isLoading"
          :disabled="isLoading"
          @click="deleteApi()"
        >
          Delete
        </v-btn>
      </template>
    </ModalDialog>

    <!-- Revoke Success Dialog -->
    <ModalDialog
      ref="revokeSuccessDialog"
      dialog-class="info-dialog"
      max-width="650"
      :show-icon="false"
      show-close-icon
      data-test="revoke-success-modal"
    >
      <template #title>
        <v-icon
          color="success"
          class="mr-2"
        >
          mdi-check
        </v-icon>
        API Key Has Been Revoked
      </template>
      <template #text>
        <p class="mb-0">
          <strong>{{ revokedKeyName }}</strong> has been revoked.
        </p>
      </template>
      <template #actions>
        <v-btn
          large
          depressed
          color="primary"
          class="px-8 font-weight-bold"
          aria-label="Close"
          data-test="close-revoke-success-button"
          @click="close($refs.revokeSuccessDialog)"
        >
          Close
        </v-btn>
      </template>
    </ModalDialog>

    <!-- Alert Dialog (Success) -->
    <ModalDialog
      ref="successDialog"
      dialog-class="info-dialog"
      max-width="650"
      :show-icon="false"
      show-close-icon
      data-test="alert-modal"
    >
      <template #title>
        <v-icon
          :color="notificationColor"
          class="mr-2"
        >
          {{ alertIcon }}
        </v-icon>
        {{ alertTitle }}
      </template>
      <template #text>
        <p class="mb-0">
          <strong v-if="alertKeyName">{{ alertKeyName }}</strong> {{ alertText }}
        </p>
      </template>
      <template #actions>
        <v-btn
          large
          depressed
          color="primary"
          @click="close($refs.successDialog)"
        >
          Ok
        </v-btn>
      </template>
    </ModalDialog>

    <CreateApiKeySuccessModal
      ref="createKeySuccessModal"
      :api-key="generatedApiKey"
      :environment-label="createdKeyEnvLabel"
    />
  </div>
</template>

<script lang="ts">
import { Action, State } from 'pinia-class'
import { Component, Mixins } from 'vue-property-decorator'
import AccountChangeMixin from '@/components/auth/mixins/AccountChangeMixin.vue'
import { ApiTermsStatus } from '@/models/ApiTermsStatus'
import CommonUtils from '@/util/common-util'
import CreateApiKeySuccessModal from '@/components/auth/account-settings/advance-settings/CreateApiKeySuccessModal.vue'
import { LDFlags } from '@/util/constants'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import { Organization } from '@/models/Organization'
import { useOrgStore } from '@/stores/org'

@Component({
  components: {
    ModalDialog,
    CreateApiKeySuccessModal
  }
})
export default class ExistingAPIKeys extends Mixins(AccountChangeMixin) {
  @State(useOrgStore) readonly currentOrganization!: Organization
  @Action(useOrgStore) readonly getOrgApiKeys!: (orgId: any, all?: boolean) => Promise<any>
  @Action(useOrgStore) readonly createOrgApiKey!: (orgId: any, payload: any) => Promise<any>
  @Action(useOrgStore) readonly revokeOrgApiKeys!: (orgId: any) => Promise<any>
  @Action(useOrgStore) readonly deleteOrgApiKey!: (apiDetails: any) => Promise<any>
  @Action(useOrgStore) readonly getApiTermsStatus!: (orgId: number) => Promise<ApiTermsStatus>

  public readonly PAGE_LIMIT = 5
  // the limit comes from the API with the key list, it's null until the keys are loaded
  public maxNamedKeys: number = null
  public isLoading = true
  public isCreating = false
  public isCreateFormOpen = false
  public newKeyName = ''
  public isNamedKeyLimitNoticeOpen = false
  public alertText = ''
  public alertKeyName = ''
  public alertTitle = ''
  public alertIcon = 'mdi-check'
  public notificationColor = 'success'
  public selectedApi: any = {}
  public revokedKeyName = ''
  public generatedApiKey = ''
  public createdKeyEnvLabel = ''

  get isCreateApiKeyEnabled (): boolean {
    return LaunchDarklyService.getFlag(LDFlags.EnableCreateApiKey)
  }

  // counts include revoked keys, as they are listed until deleted
  get namedKeyCount (): number {
    return this.apiKeyList.filter(key => this.isKeyNamed(key)).length
  }

  get unnamedKeyCount (): number {
    return this.apiKeyList.length - this.namedKeyCount
  }

  get isNamedKeyLimitReached (): boolean {
    return this.maxNamedKeys !== null && this.namedKeyCount >= this.maxNamedKeys
  }

  // the notice goes away once a named key is deleted
  get isNamedKeyLimitNoticeShown (): boolean {
    return this.isNamedKeyLimitNoticeOpen && this.isNamedKeyLimitReached
  }

  private formatDate = CommonUtils.formatDisplayDate

  $refs: {
    successDialog: InstanceType<typeof ModalDialog>
    confirmActionDialog: InstanceType<typeof ModalDialog>
    confirmDeleteDialog: InstanceType<typeof ModalDialog>
    revokeSuccessDialog: InstanceType<typeof ModalDialog>
    createKeySuccessModal: InstanceType<typeof CreateApiKeySuccessModal>
  }

  public apiKeyList = []

  public readonly activityHeader = [
    {
      text: 'Name',
      align: 'left',
      sortable: false,
      value: 'apiKeyName',
      class: 'bold-header'
    },

    {
      text: 'Environment',
      align: 'left',
      sortable: false,
      value: 'environment',
      class: 'bold-header'
    },
    {
      text: 'API Key',
      align: 'left',
      sortable: false,
      value: 'apiKey',
      class: 'bold-header'
    },
    {
      text: 'Created Date',
      align: 'left',
      sortable: false,
      value: 'keyCreatedDate',
      class: 'bold-header'
    },
    {
      text: 'Status',
      align: 'left',
      sortable: false,
      value: 'keyStatus',
      class: 'bold-header'
    },
    {
      text: 'Actions',
      align: 'right',
      sortable: false,
      value: 'action',
      class: 'bold-header'
    }
  ]

  public async mounted () {
    this.setAccountChangedHandler(this.initialize)
    // keys are loaded first so we know the named key limit
    await this.initialize()
    // user is routed back with openCreateKey param after accepting the API terms of use
    if (this.$route?.params?.openCreateKey === 'true' && this.isCreateApiKeyEnabled) {
      await this.$nextTick()
      this.openCreateKeyForm()
    }
  }

  public async initialize () {
    await this.loadApiKeys()
  }

  public async loadApiKeys () {
    this.isLoading = true
    this.apiKeyList = []
    try {
      const resp: any = await this.getOrgApiKeys(this.currentOrganization.id, true)
      this.apiKeyList = resp?.consumer?.consumerKey || []
      this.maxNamedKeys = resp?.maxNamedKeys ?? null
      this.isLoading = false
    } catch (e) {
      this.isLoading = false
    }
  }

  // skip the terms page when the latest API terms already accepted
  public async startCreateKey () {
    try {
      const status = await this.getApiTermsStatus(this.currentOrganization.id)
      if (status?.isAccepted) {
        this.openCreateKeyForm()
        return
      }
    } catch (e) {
      // the API enforces acceptance when creating a key
      // eslint-disable-next-line no-console
      console.error(e)
    }
    this.goToApiTerms()
  }

  public goToApiTerms () {
    this.$router.push({ name: 'api-terms-of-use', params: { orgId: String(this.currentOrganization.id) } })
  }

  public openCreateKeyForm () {
    // only unnamed keys can be created once the named key limit is reached
    if (this.isNamedKeyLimitReached) {
      this.isNamedKeyLimitNoticeOpen = true
      return
    }
    this.newKeyName = ''
    this.isCreateFormOpen = true
  }

  public closeCreateForm () {
    this.isCreateFormOpen = false
    this.newKeyName = ''
  }

  // the name is optional - a key created without it is an unnamed key
  public async createKey () {
    if (this.isCreating) return
    await this.onCreateKey({ apiKeyName: this.newKeyName.trim() || undefined })
  }

  public async createUnnamedKey () {
    await this.onCreateKey({})
    this.isNamedKeyLimitNoticeOpen = false
  }

  public async onCreateKey ({ apiKeyName }: { apiKeyName?: string }) {
    this.isCreating = true
    const existingKeys = this.apiKeyList
    try {
      // the env is not sent - the API gets it from the env the user logged into
      const resp: any = await this.createOrgApiKey(this.currentOrganization.id, { apiKeyName })
      const [newKey] = resp?.consumer?.consumerKey ?? []
      if (!newKey) {
        this.closeCreateForm()
        await this.loadApiKeys()
        this.alertIcon = 'mdi-alert-outline'
        this.alertTitle = 'API key has been created'
        this.alertKeyName = ''
        this.alertText = 'The key value could not be displayed. If you need it, revoke this key and create a new one.'
        this.notificationColor = 'warning'
        this.$refs.successDialog.open()
        return
      }

      newKey.isNewlyAdded = true
      // the create response may not have the date, it's needed to sort the new key to the top
      newKey.keyCreatedDate ??= new Date().toISOString()
      this.apiKeyList = [newKey, ...existingKeys]
      this.generatedApiKey = newKey.apiKey
      const environmentLabel = newKey.environment || ''
      this.createdKeyEnvLabel = environmentLabel.charAt(0).toUpperCase() + environmentLabel.slice(1)

      this.closeCreateForm()
      await this.$nextTick()
      this.$refs.createKeySuccessModal.open()
    } catch (e) {
      // eslint-disable-next-line no-console
      console.error(e)
      const errorCode = e?.response?.data?.code
      if (errorCode === 'API_TERMS_NOT_ACCEPTED') {
        // e.g. a new terms version was published since the terms page was shown
        this.closeCreateForm()
        this.goToApiTerms()
        return
      }
      this.closeCreateForm()
      if (errorCode === 'API_KEY_NAMED_LIMIT_REACHED') {
        // eg: if a named key was created in another tab
        await this.loadApiKeys()
        if (this.isNamedKeyLimitReached) {
          this.isNamedKeyLimitNoticeOpen = true
          return
        }
      }
      this.alertIcon = 'mdi-alert-circle-outline'
      this.alertTitle = 'API key has not been created'
      this.alertKeyName = ''
      this.alertText = this.getErrorMessage(e, ['API_TERMS_NOT_FOUND', 'API_KEY_NAMED_LIMIT_REACHED'])
      this.notificationColor = 'error'
      this.$refs.successDialog.open()
    } finally {
      this.isCreating = false
    }
  }

  public getErrorMessage (e: any, codes: string[]): string {
    const data = e?.response?.data
    return codes.includes(data?.code) ? data.message : ''
  }

  public isKeyActive (item: any): boolean {
    return item.keyStatus === 'approved'
  }

  public isKeyRevoked (item: any): boolean {
    return item.keyStatus === 'revoked'
  }

  public getKeyStatusLabel (item: any): string {
    if (this.isKeyActive(item)) return 'Active'
    if (this.isKeyRevoked(item)) return 'Revoked'
    const status = item.keyStatus || ''
    return status.charAt(0).toUpperCase() + status.slice(1)
  }

  public isKeyNamed (item: any): boolean {
    return !!item?.apiKeyName?.trim()
  }

  public getKeyName (item: any): string {
    return this.isKeyNamed(item) ? item.apiKeyName.trim() : 'Unnamed Key'
  }

  // mask the key as it is only shown once in success dialog
  public maskApiKey (key: string): string {
    return !key ? '' : `${'*'.repeat(4)}${key.slice(-4)}`
  }

  public confirmationModal (apiKey) {
    this.selectedApi = apiKey
    this.$refs.confirmActionDialog.open()
  }

  public confirmDelete (apiKey) {
    this.selectedApi = apiKey
    this.$refs.confirmDeleteDialog.open()
  }

  public async revokeApi () {
    await this.runKeyAction(this.revokeOrgApiKeys, 'Revoked', this.$refs.confirmActionDialog)
  }

  public async deleteApi () {
    await this.runKeyAction(this.deleteOrgApiKey, 'Deleted', this.$refs.confirmDeleteDialog)
  }

  private async runKeyAction (
    keyAction: (apiDetails: any) => Promise<any>, result: 'Revoked' | 'Deleted', confirmDialog: any
  ) {
    const orgId = this.currentOrganization.id
    const { apiKey } = this.selectedApi
    const apiKeyName = this.getKeyName(this.selectedApi)
    const apiKeys = { orgId, apiKey }
    this.alertIcon = 'mdi-alert-circle-outline'
    this.alertTitle = `API key has not been ${result}`
    this.alertKeyName = apiKeyName
    this.alertText = `API Key has not been ${result}`
    this.notificationColor = 'error'
    this.isLoading = true
    let isSuccess = false
    try {
      const resp: any = await keyAction(apiKeys)
      if (resp) {
        isSuccess = true
        this.alertIcon = 'mdi-check'
        this.alertTitle = `API key has been ${result}`
        this.alertText = `API Key has been ${result}`
        this.notificationColor = 'success'
      }
    } catch (e) {
      // eslint-disable-next-line no-console
      console.log('error', e)
      this.alertText = this.getErrorMessage(e, ['API_KEY_NOT_REVOKED', 'DATA_NOT_FOUND']) || this.alertText
    }
    this.isLoading = false
    await this.loadApiKeys()
    this.selectedApi = {}
    confirmDialog.close()
    // a revoked key has its own success dialog
    if (isSuccess && result === 'Revoked') {
      this.revokedKeyName = apiKeyName
      this.$refs.revokeSuccessDialog.open()
      return
    }
    this.$refs.successDialog.open()
  }

  public close (dialog) {
    dialog.close()
  }

  public getIndexedTag (tag, idx) {
    return `${tag}-${idx}`
  }
}
</script>

<style lang="scss" scoped>
.view-header {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
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

  .v-badge--inline .v-badge__wrapper {
    margin-left: 0;

    .v-badge__badge {
      margin-right: -0.25rem;
      margin-left: 0.25rem;
    }
  }
}
// match the height of the large buttons (44px) next to the input
.key-name-input ::v-deep .v-input__slot {
  min-height: 44px;
}
.notify-checkbox {
  justify-content: center;

  ::v-deep {
    .v-input__slot {
      margin-bottom: 0 !important;
    }
  }
}
</style>
