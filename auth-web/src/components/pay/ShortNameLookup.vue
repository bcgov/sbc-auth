<template>
  <div id="short-name-lookup">
    <v-autocomplete
      item-disabled="linkedBy"
      :search-input.sync="searchField"
      :hide-no-data="state != LookupStates.NO_RESULTS"
      :items="searchResults"
      :loading="state === LookupStates.SEARCHING"
      :name="Math.random()"
      :clearable="state !== LookupStates.INITIAL && state !== LookupStates.SEARCHING"
      :clear-icon="'mdi-close'"
      :append-icon="state === LookupStates.INITIAL ? 'mdi-magnify':''"
      autocomplete="chrome-off"
      :class="`mt-5 mb-n2 ${state}`"
      filled
      hint=""
      :item-text="'accountName'"
      :item-value="'accountId'"
      dialog-class="short-name-lookup-dialog"
      :label="state !== LookupStates.SUMMARY ? 'Account ID or Account Name' : ''"
      no-filter
      persistent-hint
      return-object
      :readonly="state === LookupStates.SUMMARY"
      @input="onItemSelected"
      @keydown.enter.native.prevent
    >
      <template #selection="{ item }">
        <div>
          <span class="pr-8">{{ item.accountId }}</span> {{ item.accountName }}
        </div>
      </template>
      <template #append>
        <v-progress-circular
          v-if="state === LookupStates.SEARCHING"
          color="primary"
          indeterminate
          :size="24"
          :width="2"
        />
      </template>
      <template #prepend-item>
        <div
          class="d-flex"
          style="justify-content: space-between;"
        >
          <p
            class="pl-5 align-center item-row d-flex"
            style="flex-grow: 1;"
          >
            Accounts with EFT Payment Method Selected
          </p>
          <p
            class="pl- align-center item-row d-flex"
            style="flex-grow: 1; flex-basis: 19%;"
          >
            Amount Owing
          </p>
        </div>
      </template>
      <template #no-data>
        <p class="pl-5 d-flex align-center item-row">
          No accounts found
        </p>
      </template>
      <template #item="{ item }">
        <v-row class="short-name-lookup-result pt-1">
          <v-col
            cols="3"
            class="result-identifier d-inline-flex"
          >
            {{ item.accountId }}
          </v-col>
          <v-col
            cols="5"
            class="result-name flex-1-1"
          >
            {{ item.accountName }}
          </v-col>
          <v-col
            cols="2"
            class="amount-owing"
          >
            {{ formatCurrency(item.totalDue) }}
            <!-- {{ item.amountOwing }} -->
          </v-col>
          <v-col
            cols="2"
            class="result-action"
          >
            <span
              v-if="item.linkedBy"
              class="linked"
            >Linked</span>
            <span
              v-else
              class="select"
            >Select</span>
          </v-col>
        </v-row>
      </template>
    </v-autocomplete>
  </div>
</template>

<script lang="ts">
import { PropType, defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import CommonUtils from '@/util/common-util'
import { EFTShortnameResponse } from '@/models/eft-transaction'
import { LookupType } from '@/models/business-nr-lookup'
import PaymentService from '@/services/payment.services'
import _ from 'lodash'
import { useOrgStore } from '@/stores/org'

enum LookupStates {
  INITIAL = 'initial',
  TYPING = 'typing',
  SEARCHING = 'searching',
  SHOW_RESULTS = 'show results',
  NO_RESULTS = 'no results',
  SUMMARY = 'summary'
}

export default defineComponent({
  name: 'ShortNameLookup',
  props: {
    lookupType: {
      type: String as PropType<LookupType>,
      default: LookupType.BUSINESS
    }
  },
  emits: ['account', 'reset'],
  setup (props, { emit }) {
    const orgStore = useOrgStore()
    const states = reactive({
      state: LookupStates.INITIAL,
      searchField: '',
      searchResults: [] as EFTShortnameResponse[]
    })

    const onSearchFieldChanged = _.debounce(async function () {
      if (states.state !== LookupStates.SUMMARY) {
        checkForTyping()
        await checkForSearching()
        checkForEmptySearch()
      }
    }, 600)

    function checkForTyping () {
      if (states.searchField?.length <= 2) {
        states.state = LookupStates.TYPING
      }
    }

    function checkForEmptySearch () {
      if (!states.searchField) {
        emit('account', {})
        states.searchResults = []
        states.state = LookupStates.INITIAL
      }
    }

    function onItemSelected (account: EFTShortnameResponse) {
      if (account) {
        emit('account', account)
        states.state = LookupStates.SUMMARY
      } else {
        emit('account', {})
        states.searchResults = []
        states.state = LookupStates.INITIAL
      }
    }

    function reset () {
      emit('reset')
      states.searchField = ''
      states.state = LookupStates.INITIAL
      states.searchResults = []
    }

    const getStatementsSummary = async (accountId): Promise<any> => {
      try {
        const data = await orgStore.getStatementsSummary(accountId)
        return data.totalDue
      } catch (error) {
        // eslint-disable-next-line no-console
        console.log(error)
      }
    }

    async function mapAccounts (query) {
      try {
        const eftAccountsResponse = await PaymentService.searchEFTAccounts(query)
        const eftAccounts = eftAccountsResponse.data.items

        if (!eftAccounts.length) {
          return []
        }

        const accountIds = eftAccounts.map((org) => org.accountId)

        const eftShortNamesResponse = await PaymentService.getEFTShortNames(
          { 'filterPayload': { 'accountIdList': accountIds.join(',') } }
        )

        const eftShortNames = eftShortNamesResponse.data.items

        const statementsSummaries = await Promise.all(
          accountIds.map(accountId => getStatementsSummary(accountId))
        )

        const mappedAccounts = eftAccounts.map((eftAccount, index) => {
          const eftShortName = eftShortNames.find((eftShortName) => eftShortName.accountId === eftAccount.accountId)
          const totalDue = statementsSummaries[index]
          return {
            ...eftAccount,
            ...eftShortName,
            totalDue
          }
        })

        return mappedAccounts
      } catch (error) {
        console.error('Error occurred while searching:', error)
        return []
      }
    }

    async function checkForSearching () {
      if (!states.searchField || states.searchField?.length <= 2) {
        return
      }
      states.state = LookupStates.SEARCHING

      const searchOrganizations = (query) => mapAccounts(query)

      try {
        states.searchResults = await searchOrganizations(states.searchField)
      } catch (error) {
        console.error('Error occurred while searching:', error)
        states.searchResults = []
      }
      states.state = (states.searchResults.length > 0) ? LookupStates.SHOW_RESULTS : LookupStates.NO_RESULTS
    }

    watch(() => states.searchField, onSearchFieldChanged)

    return {
      ...toRefs(states),
      formatCurrency: CommonUtils.formatAmount,
      onItemSelected,
      LookupStates,
      LookupType,
      reset
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

::v-deep .v-input__slot {
  background: red;
}

::v-deep .summary {
  .v-input__control {
    .v-input__slot {
      margin-bottom: 24px;
      color: red;
      &:before, &:after {
        color: #6f7780;
      }
    }
    .v-input__icon i {
      color: var(--v-primary-base) !important;
    }
    .v-select__selections {
      color: black;
    }
  }
}

.font-size-12 {
  font-size: 12px;
}

p {
  color: $gray7;
}

.short-name-lookup-result {
  pointer-events: none;
  font-size: $px-14;
  color: $gray7;

  &:hover {
    background-color: $gray1;
    color: $app-blue;
  }
}

.result-identifier {
  min-width: 120px;
}

.result-identifier,
.result-name {
  font-size: $px-16;
  max-width: 485px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.result-action {
  text-align: right;
  font-size: $px-14;

  .select {
    color: $app-blue;
  }

  .linked {
    color: $app-green;
  }
}

.item-row {
  height: 50px;
  margin: 0;
}

::v-deep .v-input__icon .mdi-magnify {
  -webkit-transform: none !important;
  transform: none !important;
}

::v-deep .v-list {
  padding: 0;
}

::v-deep .v-text-field__details {
  display: none;
}
</style>
