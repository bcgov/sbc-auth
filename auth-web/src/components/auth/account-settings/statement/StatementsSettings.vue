<template>
  <div>
    <v-fade-transition>
      <div
        v-if="isLoading"
        class="loading-container"
      >
        <v-progress-circular
          size="50"
          width="5"
          color="primary"
          :indeterminate="isLoading"
        />
      </div>
    </v-fade-transition>
    <v-dialog
      v-model="isSettingsModalOpen"
      :persistent="enableSaveBtn"
      max-width="640"
    >
      <v-card v-can:CHANGE_STATEMENT_SETTINGS.disable.card>
        <v-card-title>
          Statement Settings
          <v-btn
            large
            icon
            aria-label="Close Dialog"
            title="Close Dialog"
            :disabled="false"
            style="pointer-events: auto;"
            @click="closeSettings"
          >
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>

        <v-card-text>
          <!-- Statement Frequency-->
          <fieldset class="mb-5">
            <legend>Statement Period</legend>
            <div class="mt-2">
              Set how often statements are generated for this account.
            </div>
            <v-radio-group
              v-model="frequencySelected"
              @change="frequencyChanged"
            >
              <v-radio
                v-for="frequency in statementSettings.frequencies"
                :key="frequency.frequency"
                :value="frequency.frequency"
              >
                <template #label>
                  <span>{{ capitalizeLabel(frequency.frequency) }}</span>
                  <span
                    v-if="showFrequencyChangeDate(frequency)"
                    class="ml-1"
                  > - Frequency will change starting {{ formatDate(frequency.startDate) }}</span>
                </template>
              </v-radio>
            </v-radio-group>
          </fieldset>

          <!-- Statement Notifications -->
          <fieldset class="mb-5">
            <legend>Statement Notifications</legend>
            <v-checkbox
              v-model="sendStatementNotifications"
              class="mt-2 mb-0"
              label="Send email notifications when account statements are available"
              @change="toggleStatementNotification"
            />
          </fieldset>

          <!-- Notification Recipients -->
          <v-expand-transition>
            <fieldset v-if="sendStatementNotifications">
              <legend class="mb-4">
                Notification Recipients
              </legend>

              <!-- Recipient List -->
              <v-expand-transition>
                <div v-if="emailRecipientList.length">
                  <v-divider />
                  <v-simple-table>
                    <template #default>
                      <tbody>
                        <tr
                          v-for="item in emailRecipientList"
                          :key="item.authUserId"
                        >
                          <td>
                            {{ item.firstname }} {{ item.lastname }}
                          </td>
                          <td>
                            {{ item.email }}
                          </td>
                          <td class="text-right">
                            <v-btn
                              icon
                              class="remove-user-btn"
                              aria-label="Remove Recipient"
                              title="Remove recipient from notifications list"
                              @click="removeEmailReceipient(item)"
                            >
                              <v-icon>mdi-trash-can-outline</v-icon>
                            </v-btn>
                          </td>
                        </tr>
                      </tbody>
                    </template>
                  </v-simple-table>
                </div>
              </v-expand-transition>

              <!-- Recipient Input -->
              <v-autocomplete
                v-model="emailRecipientInput"
                filled
                hide-details
                label="Team Member Name"
                :items="recipientAutoCompleteList"
                no-data-text="No team members available"
                item-text="name"
                return-object
                :menu-props="{ closeOnContentClick: true }"
                @update:list-index="selectFromListUsingKey"
              >
                <template #item="{ item }">
                  <v-list-item-content @click="addEmailReceipient(item)">
                    <v-list-item-title v-text="item.name" />
                  </v-list-item-content>
                </template>
              </v-autocomplete>
            </fieldset>
          </v-expand-transition>

          <!-- Alert -->
          <v-alert
            v-if="errorMessage"
            text
            dense
            class="mb-0"
            type="error"
          >
            {{ errorMessage }}
          </v-alert>
        </v-card-text>

        <v-card-actions>
          <v-spacer />
          <v-btn
            v-can:CHANGE_STATEMENT_SETTINGS.disable
            large
            color="primary"
            width="90"
            aria-label="Save Settings"
            title="Save Statement Settings"
            :disabled="!enableSaveBtn"
            :loading="isSaving"
            @click="updateSettings"
          >
            Save
          </v-btn>

          <v-btn
            large
            depressed
            width="90"
            aria-label="Cancel"
            title="Cancel"
            @click="closeSettings"
          >
            Cancel
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-snackbar
      v-model="showStatementNotification"
      bottom
      multi-line
      :timeout="6000"
      class="mb-6"
    >
      Statement Settings updated
      <v-btn
        dark
        icon
        aria-label="Close Notification"
        title="Close Notification Message"
        @click="showStatementNotification = false"
      >
        <v-icon>mdi-close</v-icon>
      </v-btn>
    </v-snackbar>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import { Member, MembershipType, Organization } from '@/models/Organization'
import { StatementListItem, StatementNotificationSettings, StatementRecipient, StatementSettings } from '@/models/statement'
import { mapActions, mapState } from 'pinia'
import CommonUtils from '@/util/common-util'
/* eslint-disable-next-line @typescript-eslint/no-unused-vars */
import moment from 'moment'
import { useOrgStore } from '@/store/org'

@Component({
  methods: {
    ...mapActions(useOrgStore, [
      'fetchStatementSettings',
      'getStatementRecipients',
      'updateStatementSettings',
      'syncActiveOrgMembers',
      'updateStatementNotifications'
    ])
  },
  computed: {
    ...mapState(useOrgStore, [
      'statementSettings',
      'currentStatementNotificationSettings',
      'activeOrgMembers',
      'currentOrganization'
    ])
  }
})
export default class StatementsSettings extends Vue {
  private readonly fetchStatementSettings!: () => StatementSettings
  private readonly getStatementRecipients!: () => StatementNotificationSettings
  private readonly updateStatementSettings!: (statementFrequency: StatementListItem) => any
  private readonly updateStatementNotifications!: (statementNotification: StatementNotificationSettings) => any
  private readonly syncActiveOrgMembers!: () => Member[]
  private readonly statementSettings!: StatementSettings
  private readonly currentStatementNotificationSettings!: StatementNotificationSettings
  private readonly currentOrganization!: Organization
  private activeOrgMembers!: Member[]
  private isSettingsModalOpen: boolean = false
  private frequencySelected: string = ''
  private sendStatementNotifications: boolean = false
  private emailRecipientInput: StatementRecipient = {} as StatementRecipient
  private emailRecipientList: StatementRecipient[] = []
  private errorMessage: string = ''
  private isFrequencyChanged: boolean = false
  private isNotificationChanged: boolean = false
  private isRecipientListChanged: boolean = false
  private recipientAutoCompleteList: StatementRecipient[] = []
  private isLoading: boolean = false
  private isSaving: boolean = false
  private showStatementNotification: boolean = false

  private getIndexedTag (tag, index): string {
    return `${tag}-${index}`
  }

  public async openSettings () {
    this.isLoading = true
    try {
      this.errorMessage = ''
      this.isFrequencyChanged = false
      this.isNotificationChanged = false
      this.isRecipientListChanged = false
      await this.syncActiveOrgMembers()
      const settings = await this.fetchStatementSettings()
      const statementRecipients = await this.getStatementRecipients()
      this.frequencySelected = settings?.currentFrequency?.frequency || settings?.frequencies[0].frequency
      this.sendStatementNotifications = statementRecipients.statementNotificationEnabled
      this.emailRecipientList = [ ...statementRecipients.recipients ]
      await this.prepareAutoCompleteList()
      this.isLoading = false
      this.isSettingsModalOpen = true
    } catch (error) {
      this.isLoading = false
    }
  }

  // prepare list for org members as required for the auto complete component
  private async prepareAutoCompleteList () {
    this.activeOrgMembers.forEach((member) => {
      const recipientIndex = this.emailRecipientList.findIndex((emailRecipient) => (emailRecipient.authUserId === member?.user?.id))
      // add to auto complete only if the member is not already saved
      if ((recipientIndex < 0) && (member.membershipTypeCode !== MembershipType.User)) {
        this.recipientAutoCompleteList.push({
          authUserId: member.user?.id,
          firstname: member.user?.firstname,
          lastname: member.user?.lastname,
          name: `${member.user?.firstname || ''} ${member.user?.lastname || ''}`,
          email: member.user?.contacts[0]?.email
        })
      }
    })
  }

  private closeSettings () {
    this.isSettingsModalOpen = false
  }

  private async updateSettings () {
    this.errorMessage = ''
    try {
      this.isSaving = true
      if (this.isFrequencyChanged) {
        await this.updateStatementSettings({ 'frequency': this.frequencySelected })
      }
      if (this.isNotificationChanged || this.isRecipientListChanged) {
        // map only required values for api
        const recipientList = this.emailRecipientList.map((recipient) => {
          return {
            authUserId: recipient.authUserId,
            email: recipient.email,
            firstname: recipient.firstname,
            lastname: recipient.lastname
          }
        })
        const statementNotification: StatementNotificationSettings = {
          statementNotificationEnabled: this.sendStatementNotifications,
          recipients: recipientList,
          accountName: this.currentOrganization.name
        }
        await this.updateStatementNotifications(statementNotification)
      }
      this.showStatementNotification = true
      this.isSaving = false
      this.isSettingsModalOpen = false
    } catch (error) {
      this.errorMessage = 'Failed to update the settings, please try again.'
      this.isSaving = false
    }
  }

  private frequencyChanged (frequency) {
    this.isFrequencyChanged = (frequency !== this.statementSettings?.currentFrequency?.frequency)
  }

  private toggleStatementNotification (notification) {
    this.isNotificationChanged = (notification !== this.currentStatementNotificationSettings.statementNotificationEnabled)
  }

  private setRecipientListChanged () {
    this.isRecipientListChanged = (JSON.stringify(this.emailRecipientList) !== JSON.stringify(this.currentStatementNotificationSettings.recipients))
  }

  private get enableSaveBtn () {
    return (this.isFrequencyChanged || this.isNotificationChanged || this.isRecipientListChanged)
  }

  private formatDate (value) {
    return CommonUtils.formatDisplayDate(new Date(value))
  }

  private showFrequencyChangeDate (frequency) {
    return (frequency.frequency === this.frequencySelected) && (frequency.frequency !== this.statementSettings?.currentFrequency?.frequency)
  }

  private capitalizeLabel (value) {
    return (typeof value === 'string') ? `${value.charAt(0)}${value.slice(1).toLowerCase()}` : ''
  }

  private addEmailReceipient (item) {
    if (item.authUserId) {
      this.emailRecipientList.push({ ...item })
      this.setRecipientListChanged()
      // remove the added receipient from autocomplete list
      const recipientIndex = this.recipientAutoCompleteList.findIndex((recipient) => recipient.authUserId === item.authUserId)
      if (recipientIndex > -1) {
        this.recipientAutoCompleteList.splice(recipientIndex, 1)
      }
      // required this delay to clear the selected item from input field
      setTimeout(() => {
        this.emailRecipientInput = {} as StatementRecipient
      }, 100)
    }
  }

  private removeEmailReceipient (item) {
    const index = this.emailRecipientList.indexOf(item)
    if (index > -1) {
      this.emailRecipientList.splice(index, 1)
    }
    this.setRecipientListChanged()
    // add the removed item back to auto complete list
    item.name = `${item.firstname || ''} ${item.lastname || ''}`
    this.recipientAutoCompleteList.push(item)
  }

  // for selecting the receipient from the list using keyboard
  private selectFromListUsingKey (itemIndex) {
    if (itemIndex > -1) {
      this.addEmailReceipient(this.emailRecipientInput)
    }
  }
}
</script>

<style lang="scss" scoped>
  .remove-user-btn {
    margin-right: -6px;
  }

  table tr:hover {
    background: transparent !important;
  }

  .loading-container {
    background: rgba(255,255,255, 0.8);
  }

  .add-recipient-btn {
    margin-top: -5px;
    margin-right: 10px;
  }
</style>
