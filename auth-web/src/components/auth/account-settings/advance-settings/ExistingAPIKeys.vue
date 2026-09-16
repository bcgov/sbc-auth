<template>
  <div>
    <header class="view-header align-center mt-n1 mb-7">
      <h2 class="view-header__title">
        Existing API Keys
      </h2>
      <v-btn
        v-if="isCreateApiKeyEnabled"
        large
        depressed
        class="px-6"
        color="primary"
        aria-label="Create API Key"
        data-test="create-api-key-button"
        @click="openCreateKeyDialog()"
      >
        <v-icon class="mr-1">
          mdi-plus
        </v-icon>
        Create API Key
      </v-btn>
    </header>

    <div>
      <v-data-table
        class="apikey-list mb-10"
        :headers="activityHeader"
        :items="apiKeyList"
        no-data-text="No API Keys"
        :loading="isLoading"
        loading-text="Loading..."
        disable-pagination
        hide-default-footer
      >
        <template #loading>
          Loading...
        </template>
        <template #[`item.apiKeyName`]="{ item }">
          <div class=" font-weight-bold">
            {{ item.apiKeyName }}
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
        <template #[`item.createdDate`]="{ item }">
          {{ item.createdDate ? formatDate(item.createdDate, 'MMMM DD, YYYY') : '-' }}
        </template>
        <template #[`item.apiKey`]="{ item }">
          <span>{{ maskApiKey(item.apiKey) }}</span>
        </template>
        <template #[`item.keyStatus`]="{ item }">
          <span data-test="key-status-chip">{{ isKeyActive(item) ? 'Active' : 'Revoked' }}</span>
        </template>
        <template #[`item.action`]="{ item }">
          <!-- Revoke -->
          <v-btn
            v-if="isKeyActive(item)"
            depressed
            aria-label="Revoke"
            color="primary"
            :data-test="getIndexedTag('confirm-button', item.apiKeyName)"
            @click="confirmationModal(item)"
          >
            Revoke
          </v-btn>
        </template>
      </v-data-table>
    </div>

    <!-- Confirm Action Dialog -->
    <ModalDialog
      ref="confirmActionDialog"
      :title="confirmActionTitle"
      dialog-class="notify-dialog"
      max-width="650"
      data-test="confirmation-modal"
    >
      <template #icon>
        <v-icon
          large
          color="error"
        >
          mdi-alert-circle-outline
        </v-icon>
      </template>
      <template #text>
        <p
          class="mb-0 px-6"
          v-html="confirmActionTextLine1"
        />
        <p
          class="mx-4 px-10 mb-0"
          v-html="confirmActionTextLine2"
        />
      </template>
      <template #actions>
        <div class="modal-class-override">
          <v-btn
            large
            color="primary"
            class="font-weight-bold px-8"
            :loading="isLoading"
            @click="revokeApi()"
          >
            Revoke
          </v-btn>
          <v-btn
            outlined
            large
            depressed
            color="primary"
            class="ml-3 px-7"
            @click="close($refs.confirmActionDialog)"
          >
            Cancel
          </v-btn>
        </div>
      </template>
    </ModalDialog>

    <!-- Alert Dialog (Success) -->
    <ModalDialog
      ref="successDialog"
      :title="alertTitle"
      :text="alertText"
      dialog-class="notify-dialog"
      max-width="600"
      data-test="alert-modal"
    >
      <template #icon>
        <v-icon
          large
          :color="notificationColor"
        >
          {{ alertIcon }}
        </v-icon>
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

    <CreateApiKeyModal
      ref="createKeyModal"
      @create="onCreateKey"
    />

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
import CommonUtils from '@/util/common-util'
import CreateApiKeyModal from '@/components/auth/account-settings/advance-settings/CreateApiKeyModal.vue'
import CreateApiKeySuccessModal from '@/components/auth/account-settings/advance-settings/CreateApiKeySuccessModal.vue'
import { LDFlags } from '@/util/constants'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import { Organization } from '@/models/Organization'
import { useOrgStore } from '@/stores/org'

@Component({
  components: {
    ModalDialog,
    CreateApiKeyModal,
    CreateApiKeySuccessModal
  }
})
export default class ExistingAPIKeys extends Mixins(AccountChangeMixin) {
  @State(useOrgStore) readonly currentOrganization!: Organization
  @Action(useOrgStore) readonly getOrgApiKeys!: (orgId: any) => Promise<any>
  @Action(useOrgStore) readonly revokeOrgApiKeys!: (orgId: any) => Promise<any>

  public isLoading = true
  public confirmActionTitle = 'Revoke API Key?'
  public confirmActionTextLine1 = ''
  public confirmActionTextLine2 = ''
  public alertText = ''
  public alertTitle = ''
  public alertIcon = 'mdi-check'
  public notificationColor = 'success'
  public totalApiKeyCount: number = 0
  public selectedApi: any = {}
  public generatedApiKey = ''
  public createdKeyEnvLabel = ''

  get isCreateApiKeyEnabled (): boolean {
    return LaunchDarklyService.getFlag(LDFlags.EnableCreateApiKey)
  }

  private formatDate = CommonUtils.formatDisplayDate

  $refs: {
    successDialog: InstanceType<typeof ModalDialog>
    confirmActionDialog: InstanceType<typeof ModalDialog>
    createKeyModal: InstanceType<typeof CreateApiKeyModal>
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
      value: 'createdDate',
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
    this.initialize()
  }

  public async initialize () {
    await this.loadApiKeys()
  }

  public async loadApiKeys () {
    this.isLoading = true
    this.apiKeyList = []
    this.totalApiKeyCount = 0
    try {
      const resp: any = await this.getOrgApiKeys(this.currentOrganization.id)
      this.apiKeyList = resp?.consumer?.consumerKey || []
      this.totalApiKeyCount = resp?.consumer?.consumerKey.length || 0
      this.isLoading = false
    } catch (e) {
      this.isLoading = false
    }
  }

  public openCreateKeyDialog () {
    this.$refs.createKeyModal.open()
  }

  public onCreateKey ({ apiKeyName, environment }: { apiKeyName: string; environment: string }) {
    this.createdKeyEnvLabel = environment.charAt(0).toUpperCase() + environment.slice(1)

    // create a mock api key until backed in wired up in upcoming work
    this.generatedApiKey = this.generateMockApiKey()
    this.apiKeyList = [
      {
        apiKeyName,
        environment,
        apiKey: this.generatedApiKey,
        createdDate: new Date(),
        keyStatus: 'approved',
        isNewlyAdded: true
      },
      ...this.apiKeyList
    ]
    this.totalApiKeyCount = this.apiKeyList.length
    this.$refs.createKeyModal.close()
    this.$refs.createKeySuccessModal.open()
  }

  public generateMockApiKey (): string {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    const randomSegment = (length: number) => Array.from({ length }, () => chars[Math.floor(Math.random() * chars.length)]).join('')
    return [5, 6, 9, 16].map(randomSegment).join('-')
  }

  public isKeyActive (item: any): boolean {
    return item.keyStatus === 'approved'
  }

  // mask the key as it is only shown once in success dialog
  public maskApiKey (key: string): string {
    return !key ? '' : `${'*'.repeat(4)}${key.slice(-4)}`
  }

  public confirmationModal (apiKey) {
    this.selectedApi = apiKey
    const { apiKeyName } = apiKey
    // eslint-disable-next-line no-irregular-whitespace
    this.confirmActionTextLine1 = `Revoking an API key will immediately disable and remove this API key.`
    // eslint-disable-next-line no-irregular-whitespace
    this.confirmActionTextLine2 = `This action cannot be reversed. Are you sure you wish to remove <strong>${apiKeyName}</strong> API key?`
    this.$refs.confirmActionDialog.open()
  }

  public async revokeApi () {
    const orgId = this.currentOrganization.id
    const { apiKey, apiKeyName } = this.selectedApi
    const apiKeys = { orgId, apiKey }
    this.alertIcon = 'mdi-alert-circle-outline'
    this.alertTitle = 'API key has not been Revoked'
    this.alertText = `<strong>${apiKeyName}</strong> API Key has not been Revoked`
    this.notificationColor = 'error'
    this.isLoading = true
    try {
      const resp: any = await this.revokeOrgApiKeys(apiKeys)
      if (resp) {
        this.alertIcon = 'mdi-check'
        this.alertTitle = 'API key has been Revoked'
        this.alertText = `<strong>${apiKeyName}</strong> API Key has been Revoked`
        this.notificationColor = 'success'
      }
    } catch (e) {
      // eslint-disable-next-line no-console
      console.log('error', e)
    }
    this.isLoading = false
    await this.loadApiKeys()
    this.selectedApi = {}
    this.$refs.confirmActionDialog.close()
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
.modal-class-override{
  margin-top: -13px;
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
