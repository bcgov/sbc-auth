<template>
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
              <div v-if="emailReceipientList.length">
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
                            small
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
            <v-text-field
              filled
              hide-details
              label="Team Member Name"
              append-icon="mdi-plus-box"
              v-model="emailReceipientInput"
              @click:append="addEmailReceipient"
            ></v-text-field>
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
          :disabled="isSaveButtonDisabled"
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
</template>

<script lang="ts">
import { Component, Mixins, Prop, Vue, Watch } from 'vue-property-decorator'
import { mapActions, mapState } from 'vuex'
import { StatementListItem } from '@/models/statement'

@Component({
  methods: {
    ...mapActions('org', [
      'getStatementSettings',
      'updateStatementSettings'
    ])
  },
  computed: {
    ...mapState('org', [
      'currentStatementSettings'
    ])
  }
})
export default class StatementsSettings extends Vue {
  private readonly getStatementSettings!: () => any
  private readonly updateStatementSettings!: (statementFrequency: StatementListItem) => any
  private readonly currentStatementSettings!: StatementListItem
  private isSettingsModalOpen: boolean = false
  private frequencySelected: string = ''
  private sendStatementNotifications: boolean = false
  private emailReceipientInput: string = ''
  private emailReceipientList = []
  private errorMessage: string = ''
  private isSaveButtonDisabled: boolean = true

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
    this.errorMessage = ''
    this.isSaveButtonDisabled = true
    const settings = await this.getStatementSettings()
    this.frequencySelected = settings?.frequency || this.frequencies[1].frequencyCode
    this.isSettingsModalOpen = true
  }

  private closeSettings () {
    this.isSettingsModalOpen = false
  }

  private async updateSettings () {
    this.errorMessage = ''
    try {
      const update = await this.updateStatementSettings({ 'frequency': this.frequencySelected })
      this.isSettingsModalOpen = false
    } catch (error) {
      this.errorMessage = 'Failed to update the settings, please try again.'
    }
  }

  private frequencyChanged (frequency) {
    this.isSaveButtonDisabled = (frequency === this.currentStatementSettings?.frequency)
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
  .remove-user-btn {
    margin-right: -6px;
  }

  table tr:hover {
    background: transparent !important;
  }
</style>
