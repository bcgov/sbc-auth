<template>
  <div>
    <v-fade-transition>
      <div v-if="isLoading" class="loading-container transparent">
        <v-progress-circular size="50" width="5" color="primary" :indeterminate="isLoading"/>
      </div>
    </v-fade-transition>
    <v-dialog
      v-model="isSettingsModalOpen"
      max-width="600"
    >
      <v-card >
        <v-card-title>
          Statement Settings
          <v-btn
            large
            icon
            aria-label="Close Dialog"
            title="Close Dialog"
            @click="closeSettings"
          >
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>

        <v-card-text>

          <!-- Statement Frequency-->
          <fieldset class="mb-5">
            <legend>Statement Period</legend>
            <div class="mt-1">Set how often you want to receive statements for this account.</div>
            <v-radio-group
              v-model="frequencySelected"
              @change="frequencyChanged"
            >
              <v-radio
                v-for="frequency in frequencies"
                :key="frequency.frequencyCode"
                :label="frequency.frequencyLabel"
                :value="frequency.frequencyCode"
              >
              </v-radio>
            </v-radio-group>
          </fieldset>

          <!-- Statement Notifications -->
          <fieldset class="mb-5">
            <legend>Statement Notifications</legend>
            <v-checkbox
              class="mt-2 mb-0"
              v-model="sendStatementNotifications"
              @change="toggleStatementNotification"
              label="Send email notifications when account statements are available"
            ></v-checkbox>
          </fieldset>

          <!-- Notification Recipients -->
          <v-expand-transition>
            <fieldset v-if="sendStatementNotifications">
              <legend>Notification Recipients</legend>
              <div class="mt-2 mb-6">Manage which team members will receive statement notifications.</div>

              <!-- Recipient List -->
              <v-expand-transition>
                <div v-if="emailRecipientList.length">
                  <v-divider></v-divider>
                  <v-simple-table>
                    <template v-slot:default>
                      <tbody>
                        <tr v-for="item in emailRecipientList" :key="item.authUserId">
                          <td>
                            {{item.firstname}} {{item.lastname}}
                          </td>
                          <td>
                            {{item.email}}
                          </td>
                          <td class="text-right">
                            <v-btn
                              icon
                              small
                              class="remove-user-btn"
                              aria-label="Remove Recipient"
                              title="Remove recipient from notifications list"
                              @click="removeEmailReceipient(item)"
                            >
                              <v-icon small>mdi-trash-can-outline</v-icon>
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
                append-icon="mdi-plus-box"
                v-model="emailRecipientInput"
                @click:append="addEmailReceipient"
                hide-details
                :items="recipientAutoCompleteList"
                no-data-text="No team members available"
                item-text="name"
                return-object
                filled
                label="Team Member Name"
                class="mt-3"
              >
              </v-autocomplete>
            </fieldset>
          </v-expand-transition>

          <!-- Alert -->
          <v-alert
            text
            dense
            class="mb-0"
            type="error"
            v-if="errorMessage"
          >
            {{errorMessage}}
          </v-alert>
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            large
            color="primary"
            width="90"
            aria-label="Save Settings"
            title="Save Statement Settings"
            @click="updateSettings"
            :disabled="!enableSaveBtn"
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
  </div>
</template>

<script lang="ts">
import { Component, Mixins, Prop, Vue, Watch } from 'vue-property-decorator'
import { Member, Organization } from '@/models/Organization'
import { StatementListItem, StatementNotificationSettings, StatementRecipient } from '@/models/statement'
import { mapActions, mapState } from 'vuex'

@Component({
  methods: {
    ...mapActions('org', [
      'getStatementSettings',
      'getStatementRecipients',
      'updateStatementSettings',
      'syncActiveOrgMembers',
      'updateStatementNotifications'
    ])
  },
  computed: {
    ...mapState('org', [
      'currentStatementSettings',
      'currentStatementNotificationSettings',
      'activeOrgMembers',
      'currentOrganization'
    ])
  }
})
export default class StatementsSettings extends Vue {
  private readonly getStatementSettings!: () => StatementListItem
  private readonly getStatementRecipients!: () => StatementNotificationSettings
  private readonly updateStatementSettings!: (statementFrequency: StatementListItem) => any
  private readonly updateStatementNotifications!: (statementNotification: StatementNotificationSettings) => any
  private readonly syncActiveOrgMembers!: () => Member[]
  private readonly currentStatementSettings!: StatementListItem
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
      const settings = await this.getStatementSettings()
      const statementRecipients = await this.getStatementRecipients()
      this.frequencySelected = settings?.frequency || this.frequencies[1].frequencyCode
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
      const recipientIndex = this.emailRecipientList.findIndex((emailRecipient) => (emailRecipient.authUserId === member.id))
      // add to auto complete only if the member is not already saved
      if (recipientIndex < 0) {
        this.recipientAutoCompleteList.push({
          authUserId: member.id,
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
          authAccountName: this.currentOrganization.name
        }
        await this.updateStatementNotifications(statementNotification)
      }
      this.isSettingsModalOpen = false
    } catch (error) {
      this.errorMessage = 'Failed to update the settings, please try again.'
    }
  }

  private frequencyChanged (frequency) {
    this.isFrequencyChanged = (frequency !== this.currentStatementSettings?.frequency)
  }

  private toggleStatementNotification (notification) {
    this.isNotificationChanged = (notification !== this.currentStatementNotificationSettings.statementNotificationEnabled)
  }

  private recipientListChanged () {
    this.isRecipientListChanged = (JSON.stringify(this.emailRecipientList) !== JSON.stringify(this.currentStatementNotificationSettings.recipients))
  }

  private get enableSaveBtn () {
    return (this.isFrequencyChanged || this.isNotificationChanged || this.isRecipientListChanged)
  }

  private addEmailReceipient () {
    if (this.emailRecipientInput.authUserId) {
      this.emailRecipientList.push({ ...this.emailRecipientInput })
      this.recipientListChanged()
      // remove the added receipient from autocomplete list
      const recipientIndex = this.recipientAutoCompleteList.findIndex((recipient) => recipient.authUserId === this.emailRecipientInput.authUserId)
      if (recipientIndex > -1) {
        this.recipientAutoCompleteList.splice(recipientIndex, 1)
      }
      this.emailRecipientInput = {} as StatementRecipient
    }
  }

  private removeEmailReceipient (item) {
    const index = this.emailRecipientList.indexOf(item)
    if (index > -1) {
      this.emailRecipientList.splice(index, 1)
    }
    this.recipientListChanged()
    // add the removed item back to auto complete list
    item.name = `${item.firstname || ''} ${item.lastname || ''}`
    this.recipientAutoCompleteList.push(item)
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

  .loading-transparent {
    background: #bdbdbd4d !important;
  }
</style>
