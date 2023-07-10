<template>
  <div class="pa-5">
    <div v-if="isLoading" class="loading-inner-container">
      <v-progress-circular size="50" width="5" color="primary" :indeterminate="isLoading"/>
    </div>

    <div v-else-if="!isLoading && accounts && accounts.length > 0">
      <span>Select the account you want to perform Registries activities for <strong>{{ businessName }}</strong></span>
      <v-select
        id="account-authorization-request-request-account-select"
        filled req persistent-hint validate-on-blur
        label="Select authorizing account"
        aria-label="Select Authorizing account"
        v-model="selectedAccount"
        :disabled="accounts.length < 2"
        class="business-identifier mb-n2"
        :items="accounts"
        item-text="name"
        item-value="uuid"
        @change="emitSelected(selectedAccount)"
      />
      <span>You can add a message that will be included as part of your authorization request. </span>
      <v-textarea
        class="mb-n2"
        filled
        id="account-authorization-request-additional-message-textarea"
        label="Request access additional message"
        aria-label="Request access additional message"
        v-model.trim="requestAccessMessage"
        @change="$emit('changeRequestAccessMessage', requestAccessMessage)"
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
import { defineComponent, ref } from '@vue/composition-api'
import OrgService from '@/services/org.services'

export default defineComponent({
  name: 'AccountAuthorizationRequest',
  emits: ['changeRequestAccessMessage', 'selectAccount'],
  methods: {
    emitSelected: function (uuid) {
      const selectedAcc = this.accounts.find(acc => acc.uuid === uuid)
      this.emitSelectedAccount(selectedAcc)
    },
    emitSelectedAccount: function (selectedAcc) {
      this.$emit('selectAccount', selectedAcc)
    }

  },
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
  setup () {
    const accounts = ref([])
    const selectedAccount = ref(null)
    const requestAccessMessage = ref('')
    const isLoading = ref(true)

    return {
      selectedAccount,
      requestAccessMessage,

      accounts,
      isLoading
    }
  },
  mounted () {
    OrgService.getOrganizationsNameAndUuidByAffiliation(this.businessIdentifier).then(
      response => {
        if (response.data && response.data.orgsDetails) {
          this.accounts = response.data.orgsDetails

          if (this.accounts.length === 1) {
            this.selectedAccount = this.accounts[0]
            this.emitSelectedAccount(this.selectedAccount)
          }
        }
      }
    ).catch(
      err => {
        console.log(err)
      }
    ).finally(
      () => {
        this.isLoading = false
      }
    )
  }
})
</script>
