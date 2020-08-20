<template>
  <v-container>
    <header class="view-header mb-8">
      <h2 class="view-header__title">Statements</h2>
      <v-btn
        depressed
        color="grey lighten-3"
        @click.stop="openSettings"
      >
        <v-icon small class="mr-2">mdi-settings</v-icon>
        Statement Settings
      </v-btn>
    </header>
    <div>
      <v-data-table
        class="statement-list"
        :headers="headerStatements"
        :items="statementsList"
        :custom-sort="customSortActive"
        :no-data-text="$t('noStatementsList')"
        :server-items-length="totalStatementsCount"
        :options.sync="tableDataOptions"
        :loading="isDataLoading"
        loading-text="loading text"
        :footer-props="{
          itemsPerPageOptions: getPaginationOptions
        }"
      >
        <template v-slot:loading>
          Loading...
        </template>
        <template v-slot:[`item.dateRange`]="{ item }">
          <div class="font-weight-bold">
            {{formatDateRange(item.fromDate, item.toDate)}}
          </div>
        </template>
        <template v-slot:[`item.action`]="{ item }">
          <div class="btn-inline">
            <v-btn
              outlined
              small
              color="primary"
              class="font-weight-bold mr-2"
              :data-test="getIndexedTag('csv-button', item.id)"
              @click="downloadStatement(item, 'CSV')"
            >
              CSV
            </v-btn>
            <v-btn
              outlined
              small
              color="primary"
              class="font-weight-bold"
              :data-test="getIndexedTag('pdf-button', item.id)"
              @click="downloadStatement(item, 'PDF')"
            >
              PDF
            </v-btn>
          </div>
        </template>
      </v-data-table>
    </div>
    <v-dialog
      v-model="isSettingsModalOpen"
      max-width="600"
    >
      <v-card class="pa-2">
        <v-card-title class="headline">
          Configure Statements
          <v-btn
            icon
            @click="closeSettings"
          >
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>

        <v-card-text>
          <div class="mb-2">
            <h4 class="mb-2">Statement Frequency</h4>
            <p>Choose the frequency of your statements.</p>
            <v-radio-group
              v-model="frequencySelected"
            >
              <v-radio
                v-for="frequency in frequencies"
                :key="frequency.frequencyCode"
                :label="frequency.frequencyLabel"
                :value="frequency.frequencyCode"
                class="mb-3"
              >
              </v-radio>
            </v-radio-group>
          </div>
          <div class="mb-3">
            <h4 class="mb-2">Statement Notifications</h4>
            <v-checkbox
              v-model="sendStatementNotifications"
              label="Send email notifications when account statements are available"
            ></v-checkbox>
          </div>
          <div class="mb-1" v-if="sendStatementNotifications">
            <h4 class="mb-2">Notification Recipients</h4>
            <p>Enter the Team Members you want to receive statement notifications</p>
            <div
              class="mb-4"
              v-if="emailReceipientList.length">
              <v-divider></v-divider>
              <v-simple-table>
                <template v-slot:default>
                  <tbody>
                    <tr v-for="(item, index) in emailReceipientList" :key="index">
                      <td>
                        {{item}}
                      </td>
                      <td>
                        {{index}} some@some.com
                      </td>
                      <td class="text-right">
                        <v-btn
                          icon
                          @click="removeEmailReceipient(item)"
                        >
                          <v-icon>mdi-close</v-icon>
                        </v-btn>
                      </td>
                    </tr>
                  </tbody>
                </template>
              </v-simple-table>
            </div>
            <v-text-field
              v-model="emailReceipientInput"
              label="Team Member Name"
              filled
              append-icon="mdi-plus-box"
              @click:append="addEmailReceipient"
            ></v-text-field>
          </div>
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>

          <v-btn
            color="primary"
            width="90"
            @click="updateFrequency"
          >
            Save
          </v-btn>

          <v-btn
            color="primary"
            outlined
            width="90"
            @click="closeSettings"
          >
            Cancel
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script lang="ts">
import { Account, Pages } from '@/util/constants'
import { Component, Mixins, Prop, Vue, Watch } from 'vue-property-decorator'
import { Member, MembershipType, Organization } from '@/models/Organization'
import { StatementFilterParams, StatementListItem, StatementListResponse } from '@/models/statement'
import { mapActions, mapState } from 'vuex'
import AccountChangeMixin from '@/components/auth/mixins/AccountChangeMixin.vue'
import CommonUtils from '@/util/common-util'
import moment from 'moment'

@Component({
  methods: {
    ...mapActions('org', [
      'getStatementsList'
    ])
  },
  computed: {
    ...mapState('org', [
      'currentOrganization',
      'currentMembership'
    ])
  }
})
export default class Statements extends Mixins(AccountChangeMixin) {
  @Prop({ default: '' }) private orgId: string;
  private readonly currentMembership!: Member
  private readonly currentOrganization!: Organization
  private readonly getStatementsList!: (filterParams: StatementFilterParams) => StatementListResponse
  private readonly ITEMS_PER_PAGE = 5
  private readonly PAGINATION_COUNTER_STEP = 4
  private formatDate = CommonUtils.formatDisplayDate
  private totalStatementsCount: number = 0
  private tableDataOptions: any = {}
  private isDataLoading: boolean = false
  private statementsList: StatementListItem[] = []
  private isSettingsModalOpen: boolean = false
  private frequencySelected: string = ''
  private sendStatementNotifications: boolean = false
  private emailReceipientInput: string = ''
  private emailReceipientList = []

  private readonly headerStatements = [
    {
      text: 'Date',
      align: 'left',
      sortable: false,
      value: 'dateRange',
      width: '270'
    },
    {
      text: 'Frequency',
      align: 'left',
      sortable: false,
      value: 'frequency',
      width: '140'
    },
    {
      text: 'Downloads',
      align: 'right',
      sortable: false,
      value: 'action'
    }
  ]

  private readonly frequencies = [
    {
      frequencyLabel: 'Daily',
      frequencyCode: 'DAILY'
    },
    {
      frequencyLabel: 'Weekly',
      frequencyCode: 'WEEKLY'
    },
    {
      frequencyLabel: 'Monthly',
      frequencyCode: 'MONTHLY'
    }
  ]

  private get getPaginationOptions () {
    return [...Array(this.PAGINATION_COUNTER_STEP)].map((value, index) => this.ITEMS_PER_PAGE * (index + 1))
  }

  private async mounted () {
    this.setAccountChangedHandler(this.initialize)
    this.initialize()
  }

  private async initialize () {
    if (!this.isStatementsAllowed) {
      // if the account switing happening when the user is already in the statements page,
      // redirect to account info if its a basic account
      this.$router.push(`/${Pages.MAIN}/${this.currentOrganization.id}/settings/account-info`)
    }
  }

  formatDateRange (date1, date2) {
    let displayDate = ''
    let dateObj1 = this.getMomentDateObj(date1)
    let dateObj2 = this.getMomentDateObj(date2)
    let year = (dateObj1.year() === dateObj2.year()) ? dateObj1.year() : ''
    let month = (dateObj1.month() === dateObj2.month()) ? dateObj1.format('MMMM') : ''
    if (date1 === date2) {
      return dateObj1.format('MMMM DD, YYYY')
    } else if (year && !month) {
      return `${dateObj1.format('MMMM DD')} - ${dateObj2.format('MMMM DD')}, ${year}`
    } else if (year && month) {
      return `${month} ${dateObj1.date()} - ${dateObj2.date()}, ${year}`
    } else {
      return `${dateObj1.format('MMMM DD, YYYY')} - ${dateObj2.format('MMMM DD, YYYY')}`
    }
  }

  getMomentDateObj (dateStr) {
    return moment(dateStr, 'YYYY-MM-DD')
  }

  @Watch('tableDataOptions', { deep: true })
  async getTransactions (val, oldVal) {
    const pageNumber = val.page || 1
    const itemsPerPage = val.itemsPerPage
    await this.loadStatementsList(pageNumber, itemsPerPage)
  }

  private async loadStatementsList (pageNumber?: number, itemsPerPage?: number) {
    this.isDataLoading = true
    const filterParams: StatementFilterParams = {
      pageNumber: pageNumber,
      pageLimit: itemsPerPage
    }
    const resp = await this.getStatementsList(filterParams)
    this.statementsList = resp?.items || []
    this.totalStatementsCount = resp?.total || 0
    this.isDataLoading = false
  }

  private get isStatementsAllowed (): boolean {
    return (this.currentOrganization?.orgType === Account.PREMIUM) &&
      [MembershipType.Admin, MembershipType.Coordinator].includes(this.currentMembership.membershipTypeCode)
  }

  private customSortActive (items, index, isDescending) {
    const isDesc = isDescending.length > 0 && isDescending[0]
    items.sort((a, b) => {
      return (isDesc) ? (a[index[0]] < b[index[0]] ? -1 : 1) : (b[index[0]] < a[index[0]] ? -1 : 1)
    })
    return items
  }

  private getIndexedTag (tag, index): string {
    return `${tag}-${index}`
  }

  private downloadStatement (item, type) {
    // eslint-disable-next-line no-console
    console.log(item, type)
  }

  private openSettings () {
    this.frequencySelected = this.frequencies[1].frequencyCode
    this.isSettingsModalOpen = true
  }

  private closeSettings () {
    this.isSettingsModalOpen = false
  }

  private updateFrequency () {
    // update frequency
    this.isSettingsModalOpen = false
  }

  private addEmailReceipient () {
    // add Email Receipient
    this.emailReceipientList.push(this.emailReceipientInput)
    this.emailReceipientInput = ''
  }

  private removeEmailReceipient (item) {
    const index = this.emailReceipientList.indexOf(item)
    if (index > -1) {
      this.emailReceipientList.splice(index, 1)
    }
  }
}
</script>

<style lang="scss" scoped>
.view-header {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}

.statement-list {
    .v-data-table-header {
      margin-bottom: -2px;
    }
}
</style>
