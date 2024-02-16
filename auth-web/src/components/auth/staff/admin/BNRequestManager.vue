<template>
  <v-card
    id="bn-request-manager"
    flat
  >
    <ResubmitRequestDialog
      v-if="requestDetails && resubmitRequestDialog"
      :dialog="resubmitRequestDialog"
      :xmlData="requestDetails.request"
      attach="#bn-request-manager"
      @resubmit="resubmitRequest($event)"
      @close="hideResubmitRequestDialog()"
    />
    <v-dialog
      v-if="requestDetails && responseDialog"
      v-model="responseDialog"
      scrollable
      attach="#bn-request-manager"
    >
      <v-card>
        <v-card-title>BN Hub Response</v-card-title>
        <v-divider />
        <v-card-text class="pt-1 pb-1">
          <v-textarea
            id="response-textarea"
            ref="textarea"
            auto-grow
            outlined
            readonly
            hide-details
            :value="requestDetails.response"
          />
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn
            id="response-cancel-button"
            large
            depressed
            class="ml-2"
            @click="responseDialog = false"
          >
            Close
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <div class="table-header d-flex">
      <label>BN Request History</label>
    </div>
    <v-data-table
      id="bn-request-table"
      :headers="headers"
      :items="bnRequests"
      fixed-header
      disable-pagination
      hide-default-footer
    >
      <template #item="{ item, index }">
        <tr>
          <td>{{ requestTypeText(item.requestType) }}</td>
          <td>
            <v-icon
              v-if="item.isProcessed"
              color="green"
              class="names-text pr-1"
              small
            >
              mdi-check
            </v-icon>
            <v-icon
              v-else
              color="red"
              class="names-text pr-1"
              small
            >
              mdi-close
            </v-icon>
          </td>
          <td>
            <v-icon
              v-if="item.isAdmin"
              color="green"
              class="names-text pr-1"
              small
            >
              mdi-check
            </v-icon>
            <v-icon
              v-else
              color="red"
              class="names-text pr-1"
              small
            >
              mdi-close
            </v-icon>
          </td>
          <td>{{ formatDate(item.creationDate) }}</td>
          <td class="action-cell">
            <div
              :id="`action-menu-${index}`"
              class="actions"
            >
              <v-btn
                small
                color="primary"
                min-width="5rem"
                min-height="2rem"
                class="mr-1"
                @click="showResubmitRequestDialog(item)"
              >
                Edit
              </v-btn>
              <v-btn
                small
                color="primary"
                min-height="2rem"
                @click="showReponseDialog(item)"
              >
                View Response
              </v-btn>
            </div>
          </td>
        </tr>
      </template>
    </v-data-table>
  </v-card>
</template>

<script lang="ts">
import { Component, Prop, Watch } from 'vue-property-decorator'
import { RequestTracker, ResubmitBNRequest } from '@/models/request-tracker'
import { Action } from 'pinia-class'
import { RequestTrackerType } from '@/util/constants'
import ResubmitRequestDialog from '@/components/auth/staff/admin/ResubmitRequestDialog.vue'
import Vue from 'vue'
import { useBusinessStore } from '@/stores/business'

@Component({
  components: {
    ResubmitRequestDialog
  }
})
export default class BNRequestManager extends Vue {
  @Action(useBusinessStore) readonly getBNRequests!: (businessIdentifier: string) => Promise<RequestTracker[]>
  @Action(useBusinessStore) readonly getRequestTracker!: (requestTrackerId: number) => Promise<RequestTracker>
  @Action(useBusinessStore) readonly resubmitBNRequest!: (resubmitBNRequest: ResubmitBNRequest) => Promise<boolean>

  @Prop({ default: undefined }) businessIdentifier: string

  readonly headers = [
    { text: 'Request Type', align: 'start', value: 'requestType', sortable: false, show: true },
    { text: 'Processed', value: 'isProcessed', sortable: false, show: true },
    { text: 'Admin Request', value: 'isAdmin', sortable: false, show: true },
    { text: 'Creation Date', value: 'creationDate', sortable: false, show: true },
    { text: 'Actions', align: 'end', value: 'action', sortable: false, show: true }
  ]

  bnRequests: RequestTracker[] = []
  requestDetails: RequestTracker = null
  resubmitRequestDialog = false
  responseDialog = false

  @Watch('businessIdentifier', { deep: true, immediate: true })
  async businessIdentifierChange () {
    this.bnRequests = await this.getBNRequests(this.businessIdentifier)
  }

  requestTypeText (requestType: string) {
    switch (requestType) {
      case RequestTrackerType.InformCRA:
        return 'CreateProgramAccountRequest'
      case RequestTrackerType.ChangeDeliveryAddress:
      case RequestTrackerType.ChangeMailingAddress:
        return 'ChangeAddress'
      case RequestTrackerType.ChangeName:
      case RequestTrackerType.ChangeParty:
        return 'ChangeName'
      case RequestTrackerType.ChangeStatus:
        return 'ChangeStatus'
    }
  }

  formatDate (date: string) {
    return date ? date.substring(0, 10) : ''
  }

  async showReponseDialog (item: RequestTracker): Promise<void> {
    this.requestDetails = await this.getRequestTracker(item.id)
    this.responseDialog = true
  }

  async showResubmitRequestDialog (item: RequestTracker): Promise<void> {
    this.requestDetails = await this.getRequestTracker(item.id)
    this.resubmitRequestDialog = true
  }

  async hideResubmitRequestDialog (): Promise<void> {
    this.resubmitRequestDialog = false
    this.requestDetails = null
  }

  async resubmitRequest (xmlData): Promise<void> {
    const queued = await this.resubmitBNRequest({
      businessIdentifier: this.businessIdentifier,
      requestType: this.requestDetails.requestType,
      request: xmlData
    })
    if (queued) {
      this.resubmitRequestDialog = false
      this.requestDetails = null
      await this.businessIdentifierChange()
    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';

.table-header {
  background-color: $app-lt-blue;
  padding: .875rem;
}

.action-cell {
  white-space: nowrap;
  max-height: 30px !important;
  text-align: end !important;
}

// table header overlaps with appHeader. setting z-index from 2 -> 1
::v-deep {
  .v-data-table--fixed-header thead th {
    z-index: 1;
  }
}
</style>
