<template>
  <v-card flat id="bn-request-manager">
        <ResubmitRequestDialog v-if="requestDetails"
          :dialog="resubmitRequestDialog"
          :xmlData="requestDetails.request"
          @resubmit="resubmitRequest($event)"
          @close="hideResubmitRequestDialog($event)"
          attach="#bn-request-manager"
        />

      <div class="table-header">
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
        <template v-slot:item="{ item, index }">
          <tr>
            <td>{{ item.requestType }}</td>
            <td>
              <v-icon v-if="item.isProcessed" color="green" class="names-text pr-1" small>mdi-check</v-icon>
              <v-icon v-else color="red" class="names-text pr-1" small>mdi-close</v-icon>
            </td>
            <td>
              <v-icon v-if="item.isAdmin" color="green" class="names-text pr-1" small>mdi-check</v-icon>
              <v-icon v-else color="red" class="names-text pr-1" small>mdi-close</v-icon>
            </td>
            <td class="action-cell">
              <div class="actions" :id="`action-menu-${index}`">
                <span class="open-action">
                  <v-btn
                    small
                    color="primary"
                    min-width="5rem"
                    min-height="2rem"
                    class="open-action-btn"
                    @click="showResubmitRequestDialog(item)"
                  >
                    Edit
                  </v-btn>
                </span>
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
import ResubmitRequestDialog from '@/components/auth/staff/admin/ResubmitRequestDialog.vue'
import Vue from 'vue'
import { namespace } from 'vuex-class'

const BusinessModule = namespace('business')

@Component({
  components: {
    ResubmitRequestDialog
  }
})
export default class BNRequestManager extends Vue {
  @BusinessModule.Action('getBNRequests')
  private readonly getBNRequests!: (businessIdentifier: string) => Promise<RequestTracker[]>

  @BusinessModule.Action('getRequestTracker')
  private readonly getRequestTracker!: (requestTrackerId: number) => Promise<RequestTracker>

  @BusinessModule.Action('resubmitBNRequest')
  private readonly resubmitBNRequest!: (resubmitBNRequest: ResubmitBNRequest) => Promise<boolean>

  @Prop({ default: undefined }) businessIdentifier: string

  protected headers = [
    { text: 'Request Type', align: 'start', value: 'requestType', sortable: false, show: true },
    { text: 'Processed', value: 'isProcessed', sortable: false, show: true },
    { text: 'Admin Request', value: 'isAdmin', sortable: false, show: true },
    { text: 'Actions', align: 'end', value: 'action', sortable: false, show: true }
  ]

  protected bnRequests: RequestTracker[] = []
  protected requestDetails: RequestTracker = null
  protected resubmitRequestDialog = false

  @Watch('businessIdentifier', { deep: true, immediate: true })
  async businessIdentifierChange () {
    this.bnRequests = await this.getBNRequests(this.businessIdentifier)
  }

  private async showResubmitRequestDialog (item: RequestTracker): Promise<void> {
    this.requestDetails = await this.getRequestTracker(item.id)
    this.resubmitRequestDialog = true
  }

  private async hideResubmitRequestDialog (): Promise<void> {
    this.resubmitRequestDialog = false
    this.requestDetails = null
  }

  private async resubmitRequest (xmlData): Promise<void> {
    const queued = await this.resubmitBNRequest({
      businessIdentifier: this.businessIdentifier,
      requestType: this.requestDetails.requestType,
      request: xmlData
    })
    if (queued) {
      this.resubmitRequestDialog = false
      this.requestDetails = null
      this.businessIdentifierChange()
    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';

.table-header {
  display: flex;
  background-color: $app-lt-blue;
  padding: .875rem;
}

.action-cell {
  max-width: 0;
  max-height: 30px !important;
  text-align: end !important;
  padding-right: 5;
}

::v-deep {
  .v-data-table--fixed-header thead th {
    z-index: 1;
  }
}
</style>
