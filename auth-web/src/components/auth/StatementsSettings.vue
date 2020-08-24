<template>
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
            @change="frequencyChanged"
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
        <v-alert
          class="mb-0"
          dense
          text
          type="error"
          v-if="errorMessage"
        >
          {{errorMessage}}
        </v-alert>
      </v-card-text>

      <v-card-actions>
        <v-spacer></v-spacer>

        <v-btn
          color="primary"
          width="90"
          @click="updateSettings"
          :disabled="isSaveButtonDisabled"
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
</style>
