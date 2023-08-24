<template>
  <div>
    <header class="view-header align-center mt-n1 mb-7">
      <h2 class="view-header__title">
        Existing API Keys
      </h2>
    </header>

    <div>
      <v-data-table
        class="apikey-list"
        :headers="activityHeader"
        :items="apliKeyList"
        no-data-text="No API Keys"
        :loading="isLoading"
        loading-text="loading text"
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
        </template>
        <template #[`item.environment`]="{ item }">
          <div class="text-capitalize">
            {{ item.environment }}
          </div>
        </template>
        <template #[`item.action`]="{ item }">
          <!-- Revoke -->
          <v-btn
            outlined
            aria-label="Revoke"
            title="Revoke"
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
  </div>
</template>

<script lang="ts">
import { Action, State } from 'pinia-class'
import { Component, Mixins } from 'vue-property-decorator'
import AccountChangeMixin from '@/components/auth/mixins/AccountChangeMixin.vue'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import { Organization } from '@/models/Organization'
import { useOrgStore } from '@/stores/org'

@Component({
  components: {
    ModalDialog
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

  $refs: {
    successDialog: ModalDialog
    confirmActionDialog: ModalDialog
  }

  public apliKeyList = []

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
    this.apliKeyList = []
    this.totalApiKeyCount = 0
    try {
      const resp: any = await this.getOrgApiKeys(this.currentOrganization.id)
      this.apliKeyList = resp?.consumer?.consumerKey || []
      this.totalApiKeyCount = resp?.consumer?.consumerKey.length || 0
      this.isLoading = false
    } catch (e) {
      this.isLoading = false
    }
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
    height: 71px;
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
