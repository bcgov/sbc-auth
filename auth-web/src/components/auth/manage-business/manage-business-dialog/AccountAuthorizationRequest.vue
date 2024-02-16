<template>
  <div class="pa-5">
    <div
      v-if="!!isLoading"
      class="loading-inner-container"
    >
      <v-progress-circular
        size="50"
        width="5"
        color="primary"
        :indeterminate="!!isLoading"
      />
    </div>

    <div v-else-if="!isLoading && accounts && accounts.length > 0">
      <span>Select an account:</span>
      <v-select
        id="account-authorization-request-request-account-select"
        v-model="selectedAccount"
        filled
        req
        persistent-hint
        validate-on-blur
        label="Select authorizing account"
        aria-label="Select Authorizing account"
        :disabled="accounts.length < 2"
        class="business-identifier mb-n2"
        :items="accounts"
        item-value="uuid"
        @change="emitSelected"
      >
        <template #selection="data">
          <!-- HTML that describe how select should render selected items -->
          <span
            v-if="data.item.branchName"
            data-test="account-authorization-request-selection"
          >{{ data.item.name }} - {{ data.item.branchName }}</span>
          <span
            v-else
            data-test="account-authorization-request-selection"
          >{{ data.item.name }}</span>
        </template>
        <template #item="data">
          <span
            v-if="data.item.branchName"
            data-test="account-authorization-request-option"
          >{{ data.item.name }} - {{ data.item.branchName }}</span>
          <span
            v-else
            data-test="account-authorization-request-option"
          >{{ data.item.name }}</span>
        </template>
      </v-select>
      <span>You can add a message that will be included as part of your authorization request. </span>
      <v-textarea
        id="account-authorization-request-additional-message-textarea"
        v-model.trim="requestAccessMessage"
        class="mb-n2"
        filled
        label="Request access additional message"
        aria-label="Request access additional message"
        maxlength="400"
        counter="400"
        @change="$emit('change-request-access-message', requestAccessMessage)"
      />
    </div>
    <div
      v-else
      id="no-accounts-found"
    >
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
import { defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import OrgService from '@/services/org.services'
import { OrgsDetails } from '@/models/affiliation-invitation'

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
  emits: ['change-request-access-message', 'select-account', 'unknown-error'],
  setup (props, { emit }) {
    const state = reactive({
      accounts: [] as OrgsDetails[],
      selectedAccount: '',
      requestAccessMessage: '',
      isLoading: true
    })

    const emitSelected = () => {
      const selectedAcc = state.accounts.find(acc => acc.uuid === state.selectedAccount)
      emit('select-account', selectedAcc)
    }

    const fetchData = async () => {
      const orgsDetails = await OrgService.getOrganizationsNameAndUuidByAffiliation(props.businessIdentifier)
      if (orgsDetails) {
        orgsDetails.sort((a, b) => (a.name.toLowerCase() > b.name.toLowerCase()) ? 1 : -1)
        state.accounts.splice(0, state.accounts.length)
        orgsDetails.forEach((el) => state.accounts.push(el))
        if (state.accounts.length === 1) {
          state.selectedAccount = state.accounts[0].uuid
          emitSelected()
        }
      } else {
        // Show a generic unknown error.
        emit('unknown-error')
      }
      state.isLoading = false
    }

    watch(() => props.businessIdentifier, (newValue: string) => {
      if (!newValue) {
        return
      }
      fetchData()
    },
    { immediate: true })

    return {
      ...toRefs(state),
      emitSelected
    }
  }
})
</script>
