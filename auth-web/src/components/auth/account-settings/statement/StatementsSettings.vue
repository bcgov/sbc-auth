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
            <div
              v-if="isEFT()"
              class="mt-2"
            >
              Statement for electronic funds transfer will be issued monthly.
            </div>
            <div
              v-else
              class="mt-2"
            >
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
                :disabled="isFrequencyLocked(frequency)"
              >
                <template #label>
                  <span
                    :class="{'radio-btn': !isFrequencyLocked(frequency), 'radio-btn-disabled': isFrequencyLocked(frequency)}"
                  >
                    {{ capitalizeLabel(frequency.frequency) }}
                  </span>
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
              class="mt-2 mb-0 check-box"
              @change="toggleStatementNotification"
            >
              <template #label>
                <span class="check-box">
                  Send email notifications when account statements are available
                </span>
              </template>
            </v-checkbox>
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
import { LDFlags, PaymentTypes } from '@/util/constants'
import { Member, MembershipType, OrgPaymentDetails, Organization } from '@/models/Organization'
import { StatementListItem, StatementNotificationSettings, StatementRecipient, StatementSettings } from '@/models/statement'
import { computed, reactive, toRefs } from '@vue/composition-api'
import CommonUtils from '@/util/common-util'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import { useOrgStore } from '@/stores/org'

export default {
  name: 'StatementSettings',
  setup () {
    const orgStore = useOrgStore()

    const state = reactive({
      isSettingsModalOpen: false,
      frequencySelected: '',
      sendStatementNotifications: false,
      emailRecipientInput: {} as StatementRecipient,
      emailRecipientList: [] as StatementRecipient[],
      errorMessage: '',
      isFrequencyChanged: false,
      isNotificationChanged: false,
      isRecipientListChanged: false,
      recipientAutoCompleteList: [] as StatementRecipient[],
      isLoading: false,
      isSaving: false,
      showStatementNotification: false,
      activeOrgMembers: computed<Member[]>(() => orgStore.activeOrgMembers),
      statementSettings: computed<StatementSettings>(() => orgStore.statementSettings),
      currentStatementNotificationSettings: computed<StatementNotificationSettings>(() => orgStore.currentStatementNotificationSettings),
      currentOrganization: computed<Organization>(() => orgStore.currentOrganization),
      currentOrgPaymentDetails: computed<OrgPaymentDetails>(() => orgStore.currentOrgPaymentDetails),
      isEFTPaymentMethod: computed<boolean>(() => orgStore.currentOrgPaymentDetails?.paymentMethod === PaymentTypes.EFT)
    })

    const isEFT = () => {
      const enableEFTPaymentMethod: boolean = LaunchDarklyService.getFlag(LDFlags.EnableEFTPaymentMethod, false)
      return enableEFTPaymentMethod && state.isEFTPaymentMethod
    }
    const isFrequencyLocked = (frequency: StatementListItem) => {
      return isEFT() && frequency.frequency !== state.frequencySelected
    }

    const prepareAutoCompleteList = async () => {
      state.activeOrgMembers.forEach((member) => {
        const recipientIndex = state.emailRecipientList.findIndex((emailRecipient) => (emailRecipient.authUserId === member?.user?.id))
        if ((recipientIndex < 0) && (member.membershipTypeCode !== MembershipType.User)) {
          state.recipientAutoCompleteList.push({
            authUserId: member.user?.id,
            firstname: member.user?.firstname,
            lastname: member.user?.lastname,
            name: `${member.user?.firstname || ''} ${member.user?.lastname || ''}`,
            email: member.user?.contacts[0]?.email
          })
        }
      })
    }

    const openSettings = async (): Promise<any> => {
      state.isLoading = true
      try {
        state.errorMessage = ''
        state.isFrequencyChanged = false
        state.isNotificationChanged = false
        state.isRecipientListChanged = false
        await orgStore.syncActiveOrgMembers()
        await orgStore.fetchStatementSettings()
        await orgStore.getStatementRecipients()
        state.frequencySelected = state.statementSettings?.currentFrequency?.frequency || state.statementSettings?.frequencies[0].frequency
        state.sendStatementNotifications = state.currentStatementNotificationSettings.statementNotificationEnabled
        state.emailRecipientList = [...state.currentStatementNotificationSettings.recipients]
        await prepareAutoCompleteList()
        state.isLoading = false
        state.isSettingsModalOpen = true
      } catch (error) {
        state.isLoading = false
      }
    }

    const closeSettings = () => {
      state.isSettingsModalOpen = false
    }

    const updateSettings = async () => {
      state.errorMessage = ''
      try {
        state.isSaving = true
        if (state.isFrequencyChanged) {
          await orgStore.updateStatementSettings({ 'frequency': state.frequencySelected })
        }
        if (state.isNotificationChanged || state.isRecipientListChanged) {
          const recipientList = state.emailRecipientList.map((recipient) => {
            return {
              authUserId: recipient.authUserId,
              email: recipient.email,
              firstname: recipient.firstname,
              lastname: recipient.lastname
            }
          })
          const statementNotification: StatementNotificationSettings = {
            statementNotificationEnabled: state.sendStatementNotifications,
            recipients: recipientList,
            accountName: state.currentOrganization.name
          }
          await orgStore.updateStatementNotifications(statementNotification)
        }
        state.showStatementNotification = true
        state.isSaving = false
        state.isSettingsModalOpen = false
      } catch (error) {
        state.errorMessage = 'Failed to update the settings, please try again.'
        state.isSaving = false
      }
    }

    const frequencyChanged = (frequency: string) => {
      state.isFrequencyChanged = (frequency !== state.statementSettings?.currentFrequency?.frequency)
    }

    const toggleStatementNotification = (notification) => {
      state.isNotificationChanged = (notification !== state.currentStatementNotificationSettings.statementNotificationEnabled)
    }

    const setRecipientListChanged = () => {
      state.isRecipientListChanged = (
        JSON.stringify(state.emailRecipientList) !==
        JSON.stringify(state.currentStatementNotificationSettings.recipients)
      )
    }

    const enableSaveBtn = computed(() => {
      return (state.isFrequencyChanged || state.isNotificationChanged || state.isRecipientListChanged)
    })

    const formatDate = (value) => {
      return CommonUtils.formatDisplayDate(new Date(value))
    }

    const showFrequencyChangeDate = (frequency: StatementListItem) => {
      return (frequency.frequency === state.frequencySelected) && (frequency.frequency !== state.statementSettings?.currentFrequency?.frequency)
    }

    const capitalizeLabel = (value) => {
      return (typeof value === 'string') ? `${value.charAt(0)}${value.slice(1).toLowerCase()}` : ''
    }

    const addEmailReceipient = (item) => {
      if (item.authUserId) {
        state.emailRecipientList.push({ ...item })
        setRecipientListChanged()
        const recipientIndex = state.recipientAutoCompleteList.findIndex((recipient) => recipient.authUserId === item.authUserId)
        if (recipientIndex > -1) {
          state.recipientAutoCompleteList.splice(recipientIndex, 1)
        }
        setTimeout(() => {
          state.emailRecipientInput = {} as StatementRecipient
        }, 100)
      }
    }

    const removeEmailReceipient = (item) => {
      const index = state.emailRecipientList.indexOf(item)
      if (index > -1) {
        state.emailRecipientList.splice(index, 1)
      }
      setRecipientListChanged()
      item.name = `${item.firstname || ''} ${item.lastname || ''}`
      state.recipientAutoCompleteList.push(item)
    }

    const selectFromListUsingKey = (itemIndex) => {
      if (itemIndex > -1) {
        addEmailReceipient(state.emailRecipientInput)
      }
    }

    return {
      ...toRefs(state),
      isFrequencyLocked,
      isEFT,
      prepareAutoCompleteList,
      openSettings,
      closeSettings,
      updateSettings,
      frequencyChanged,
      toggleStatementNotification,
      setRecipientListChanged,
      enableSaveBtn,
      formatDate,
      showFrequencyChangeDate,
      capitalizeLabel,
      addEmailReceipient,
      removeEmailReceipient,
      selectFromListUsingKey
    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
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

  .radio-btn {
    color: $gray7;
    opacity: 1;
  }

  .radio-btn-disabled {
    color: $gray7;
    opacity: .4;
  }

  .check-box {
    color: $gray7;
  }

</style>
