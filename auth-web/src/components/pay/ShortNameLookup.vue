<template>
  <div id="short-name-lookup">
    <v-autocomplete
      :search-input.sync="searchField"
      :hide-no-data="state != LookupStates.NO_RESULTS"
      :items="searchResults"
      :loading="state === LookupStates.SEARCHING"
      :name="Math.random()"
      :clearable="state !== LookupStates.INITIAL && state !== LookupStates.SEARCHING"
      :clear-icon="state === LookupStates.SUMMARY ? 'mdi-undo': 'mdi-close'"
      :append-icon="state === LookupStates.INITIAL ? 'mdi-magnify':''"
      autocomplete="chrome-off"
      :class="`mt-5 mb-n2 ${state === LookupStates.SUMMARY ? 'summary' : ''}`"
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
          {{ item.accountId }} {{ item.accountName }}
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
        <p
          v-if="state === LookupStates.SUMMARY"
          class="d-flex justify-center align-center ma-0 pa-0 cursor-pointer undo"
        >
          Undo
        </p>
      </template>
      <template #prepend-item>
        <p class="pl-5">
          Accounts with EFT Payment Method Selected
        </p>
      </template>
      <template #no-data>
        <p class="pl-5">
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
            cols="7"
            class="result-name flex-1-1"
          >
            {{ item.accountName }}
          </v-col>
          <v-col
            cols="2"
            class="result-action"
          >
            <span
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
import { EFTShortnameResponse } from '@/models/eft-transaction'
import { LookupType } from '@/models/business-nr-lookup'
import OrgService from '@/services/org.services'
import PaymentService from '@/services/payment.services'
import _ from 'lodash'

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
  emits: ['account'],
  setup (props, { emit }) {
    const states = reactive({
      state: LookupStates.INITIAL,
      searchField: '',
      searchResults: [] as EFTShortnameResponse[]
    })

    const checkForTyping = () => {
      if (states.searchField?.length <= 2) {
        states.state = LookupStates.TYPING
      }
    }

    async function mapAccounts (query) {
      const organizations = await OrgService.getOrganizationsSimple(query)
      const accountIds = organizations.map((org) => org.id)
      const eftShortNamesResponse = await PaymentService.getEFTShortNames(
        { 'filterPayload': { 'accountIdList': accountIds.join(',') } })
      const eftShortNames = eftShortNamesResponse.data.items
      const matchedAccounts = eftShortNames.filter(eft => organizations.some(org => org.id.toString() === eft.accountId))
      return matchedAccounts
    }

    const checkForSearching = async () => {
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

    const checkForEmptySearch = () => {
      if (!states.searchField) {
        emit('account', {})
        states.searchResults = []
        states.state = LookupStates.INITIAL
      }
    }
    const onSearchFieldChanged = _.debounce(async () => {
      if (states.state !== LookupStates.SUMMARY) {
        checkForTyping()
        await checkForSearching()
        checkForEmptySearch()
      }
    }, 600)

    watch(() => states.searchField, onSearchFieldChanged)

    const onItemSelected = (account: EFTShortnameResponse) => {
      if (account) {
        emit('account', account)
        states.state = LookupStates.SUMMARY
      } else {
        emit('account', {})
        states.searchResults = []
        states.state = LookupStates.INITIAL
      }
    }
    return {
      ...toRefs(states),
      onItemSelected,
      LookupStates,
      LookupType
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

::v-deep .summary {
  .v-input__control {
    .v-input__slot {
      background: transparent !important;
      &:before, &:after {
        opacity: 0;
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

.undo {
  height: 22px;
  color: var(--v-primary-base) !important;
}

.font-size-12 {
  font-size: 12px;
}

p {
  color: $gray7;
}

.short-name-lookup-result {
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

  .added {
    color: $app-green;
  }
}

::v-deep .v-input__icon .mdi-magnify {
  -webkit-transform: none !important;
  transform: none !important;
}
</style>
