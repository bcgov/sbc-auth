<template>
  <div class="pa-5">
    <div
      v-if="!!componentState.isLoading"
      class="loading-inner-container"
    >
      <v-progress-circular
        size="50"
        width="5"
        color="primary"
        :indeterminate="!!componentState.isLoading"
      />
    </div>

    <div v-else-if="!componentState.isLoading && componentState.accounts && componentState.accounts.length > 0">
      <span>Select the account you want to perform Registries activities for <strong>{{ businessName }}</strong></span>
      <v-select
        id="account-authorization-request-request-account-select"
        v-model="componentState.selectedAccount"
        filled
        req
        persistent-hint
        validate-on-blur
        label="Select authorizing account"
        aria-label="Select Authorizing account"
        :disabled="componentState.accounts.length < 2"
        class="business-identifier mb-n2"
        :items="componentState.accounts"
        item-text="name"
        item-value="uuid"
        @change="emitSelected"
      />
      <span>You can add a message that will be included as part of your authorization request. </span>
      <v-textarea
        id="account-authorization-request-additional-message-textarea"
        v-model.trim="componentState.requestAccessMessage"
        class="mb-n2"
        filled
        label="Request access additional message"
        aria-label="Request access additional message"
        maxlength="400"
        counter="400"
        @change="$emit('change-request-access-message', componentState.requestAccessMessage)"
      />
    </div>
    <div v-else id="no-accounts-found">
      <p>An error occurred retrieving the list of authorizing accounts for this business.</p>
      <p>If this error persists, please contact the help desk:</p>
      <p>Service BC Help Desk:</p>
      <p>Toll-free: 1-800-663-6102 (Canada and USA only)</p>
      <p>Fax: (250) 952-6115</p>
      <p>Email: bcolhelp@gov.bc.ca</p>
    </div>
  </div>
</template>

<script lang='ts'>
import { defineComponent, reactive, watch } from '@vue/composition-api'
import OrgService from '@/services/org.services'

export default defineComponent({
  name: 'AccountAuthorizationRequest',
  props: {
    businessName: {
      type: String,
      required: true
    },
    businessIdentifier: {
      type: String,
      required: true
    }
  },
  emits: ['change-request-access-message', 'select-account'],
  setup (props, { emit }) {
    // Will remove this after Vue upgrade.
    interface ComponentState {
      accounts: any[];
      selectedAccount: string;
      requestAccessMessage: string;
      isLoading: boolean;
    }

    const componentState = reactive({
      accounts: [],
      selectedAccount: '',
      requestAccessMessage: '',
      isLoading: true
    }) as ComponentState

    const emitSelected = () => {
      const selectedAcc = componentState.accounts.find(acc => acc.uuid === componentState.selectedAccount)
      emit('select-account', selectedAcc)
      // emitSelectedAccount(selectedAcc)
    }

    const fetchData = async () => {
      const response = await OrgService.getOrganizationsNameAndUuidByAffiliation(props.businessIdentifier)
      if (response?.data?.orgsDetails) {
        const orgsDetails = response.data.orgsDetails
        orgsDetails.sort((a, b) => (a.name.toLowerCase() > b.name.toLowerCase()) ? 1 : -1)
        componentState.accounts.splice(0, componentState.accounts.length)
        orgsDetails.forEach((el: string) => componentState.accounts.push(el))

        if (componentState.accounts.length === 1) {
          componentState.selectedAccount = componentState.accounts[0].uuid
          emitSelected()
        }
      } else {
        console.error('OrgService.getOrganizationsNameAndUuidByAffiliation', response.status)
      }
      componentState.isLoading = false
    }

    watch(() => props.businessIdentifier, (newValue: string) => {
      if (!newValue) {
        return
      }
      fetchData()
    },
    { immediate: true })

    return {
      emitSelected,
      componentState
    }
  }
})
</script>
