<template>
  <div class="pa-5">
    <div v-if="!!componentState.isLoading" class="loading-inner-container">
      <v-progress-circular size="50" width="5" color="primary" :indeterminate="!!componentState.isLoading"/>
    </div>

    <div v-else-if="!componentState.isLoading && componentState.accounts && componentState.accounts.length > 0">
      <span>Select the account you want to perform Registries activities for <strong>{{ businessName }}</strong></span>
      <v-select
        id="account-authorization-request-request-account-select"
        filled req persistent-hint validate-on-blur
        label="Select authorizing account"
        aria-label="Select Authorizing account"
        v-model="componentState.selectedAccount"
        :disabled="componentState.accounts.length < 2"
        class="business-identifier mb-n2"
        :items="componentState.accounts"
        item-text="name"
        item-value="uuid"
        @change="emitSelected(componentState.selectedAccount)"
      />
      <span>You can add a message that will be included as part of your authorization request. </span>
      <v-textarea
        class="mb-n2"
        filled
        id="account-authorization-request-additional-message-textarea"
        label="Request access additional message"
        aria-label="Request access additional message"
        v-model.trim="componentState.requestAccessMessage"
        @change="$emit('changeRequestAccessMessage', componentState.requestAccessMessage)"
        maxlength="400"
        counter="400"
      />
    </div>
    <div v-else>
      <h3 class="text-center">No authorizing accounts found</h3>
    </div>
  </div>
</template>

<script lang='ts'>
import { defineComponent, getCurrentInstance, onMounted, reactive, ref } from '@vue/composition-api'
import OrgService from '@/services/org.services'

export default defineComponent({
  name: 'AccountAuthorizationRequest',
  emits: ['changeRequestAccessMessage', 'selectAccount'],
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
  setup (props, { emit }) {
    const componentState = reactive({
      accounts: [],
      selectedAccount: { },
      requestAccessMessage: '',
      isLoading: true
    })

    const emitSelectedAccount = (selectedAcc) => {
      emit('selectAccount', selectedAcc)
    }

    const emitSelected = (uuid) => {
      const selectedAcc = componentState.accounts.find(acc => acc.uuid === uuid)

      emitSelectedAccount(selectedAcc)
    }

    onMounted(async () => {
      const response = await OrgService.getOrganizationsNameAndUuidByAffiliation(props.businessIdentifier)
      if (response.data && response.data.orgsDetails) {
        componentState.accounts = response.data.orgsDetails

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
