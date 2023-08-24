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
        @change="emitSelected(componentState.selectedAccount)"
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
        @change="$emit('changeRequestAccessMessage', componentState.requestAccessMessage)"
      />
    </div>
    <div v-else>
      <h3 class="text-center">
        No authorizing accounts found
      </h3>
    </div>
  </div>
</template>

<script lang='ts'>
import { defineComponent, onMounted, reactive } from '@vue/composition-api'
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
  emits: ['changeRequestAccessMessage', 'selectAccount'],
  setup (props, { emit }) {
    // Will remove this after Vue upgrade.
    interface ComponentState {
      accounts: any[];
      selectedAccount: any;
      requestAccessMessage: string;
      isLoading: boolean;
    }

    const componentState = reactive({
      accounts: [],
      selectedAccount: {},
      requestAccessMessage: '',
      isLoading: true
    }) as ComponentState

    const emitSelectedAccount = (selectedAcc) => {
      emit('selectAccount', selectedAcc)
    }

    const emitSelected = (uuid) => {
      const selectedAcc = componentState.accounts.find(acc => acc.uuid === uuid)

      emitSelectedAccount(selectedAcc)
    }

    onMounted(async () => {
      const response = await OrgService.getOrganizationsNameAndUuidByAffiliation(props.businessIdentifier)
      if (response?.data?.orgsDetails) {
        const orgsDetails = response.data.orgsDetails
        orgsDetails.sort((a, b) => (a.name.toLowerCase() > b.name.toLowerCase()) ? 1 : -1)
        componentState.accounts = orgsDetails

        if (componentState.accounts.length === 1) {
          Object.assign(componentState.selectedAccount, componentState.accounts[0])
          emitSelectedAccount(componentState.selectedAccount)
        }
      } else {
        console.error('OrgService.getOrganizationsNameAndUuidByAffiliation', response.status)
      }
      componentState.isLoading = false
    })

    return {
      emitSelected,
      componentState
    }
  }
})
</script>
