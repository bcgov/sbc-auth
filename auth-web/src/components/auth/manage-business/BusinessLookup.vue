<template>
  <!-- once in Summary state, need to re-mount to reuse this component -->
  <div id="business-lookup">
    <v-autocomplete
      :search-input.sync="searchField"
      :hide-no-data="state != States.NO_RESULTS"
      :items="searchResults"
      :loading="state === States.SEARCHING"
      :name="Math.random()"
      :clearable="state !== States.INITIAL && state !== States.SEARCHING"
      :append-icon="state === States.INITIAL ? 'mdi-magnify':''"
      autocomplete="chrome-off"
      class="mt-5 mb-n2"
      filled
      hint="For example: &quot;Joe's Plumbing Inc.&quot;, &quot;BC1234567&quot;, &quot;FM1234567&quot;"
      :item-text="lookupType === LookupType.NR ? 'nrNum' : 'name'"
      :item-value="lookupType === LookupType.NR ? 'nrNum' : 'identifier'"
      label="My business name, incorporation, or registration number"
      no-filter
      persistent-hint
      return-object
      @input="onItemSelected"
      @keydown.enter.native.prevent
    >
      <template #append>
        <v-progress-circular
          v-if="state === States.SEARCHING"
          color="primary"
          indeterminate
          :size="24"
          :width="2"
        />
      </template>

      <template #no-data>
        <p class="pl-5 font-weight-bold">
          No active B.C. business found
        </p>
        <p class="pl-5">
          Ensure you have entered the correct business name or number.
        </p>
      </template>

      <template
        v-if="lookupType === LookupType.BUSINESS"
        #item="{ item }"
      >
        <v-row class="business-lookup-result pt-1">
          <v-col
            cols="2"
            class="result-identifier"
          >
            {{ item.identifier }}
          </v-col>
          <v-col
            cols="8"
            class="result-name"
          >
            {{ item.name }}
          </v-col>
          <v-col
            cols="2"
            class="result-action"
          >
            <span
              v-if="item.disabled"
              class="added"
            >Added</span>
          </v-col>
        </v-row>
      </template>
      <template
        v-else
        #item="{ item }"
      >
        <v-row class="business-lookup-result pt-1">
          <v-col
            cols="2"
            class="result-identifier"
          >
            {{ item.nrNum }}
          </v-col>
          <v-col
            cols="8"
            class="result-name"
          >
            <div
              v-for="(name, index) in item.names"
              :key="index"
            >
              {{ name }}
            </div>
          </v-col>
          <v-col
            cols="2"
            class="result-action"
          >
            <span
              v-if="item.disabled"
              class="added"
            >Added</span>
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
import { LookupType, NameRequestLookupResultIF } from '@/models/business-nr-lookup'
import { Ref, defineComponent, ref, watch } from '@vue/composition-api'
import { BusinessLookupResultIF } from '@/models'
import BusinessLookupServices from '@/services/business-lookup.services'
import NameRequestLookupServices from '@/services/name-request-lookup.services'
import _ from 'lodash'
import { useStore } from 'vuex-composition-helpers'

enum States {
  INITIAL = 'initial',
  TYPING = 'typing',
  SEARCHING = 'searching',
  SHOW_RESULTS = 'show results',
  NO_RESULTS = 'no results',
  SUMMARY = 'summary'
}

/*
 * See PPR's BusinessSearchAutocomplete.vue for a Composition API example.
 */
// @Component({})
export default defineComponent({
  name: 'BusinessLookup',
  props: {
    lookupType: { type: String, default: LookupType.BUSINESS }
  },
  setup (props, { emit }) {
    // local variables
    const state = ref(States.INITIAL)
    const searchField = ref('')
    const searchResults: Ref<BusinessLookupResultIF[] | NameRequestLookupResultIF[]> = ref([])
    if (props.lookupType === LookupType.NR) {
      searchResults.value = [] as NameRequestLookupResultIF[]
    } else {
      searchResults.value = [] as BusinessLookupResultIF[]
    }

    // store
    const store = useStore()
    const isAffiliated = (businessIdentifier: string) => store.dispatch('business/isAffiliated', businessIdentifier)
    const isAffiliatedNR = (nrNum: string) => store.dispatch('business/isAffiliatedNR', nrNum)

    const onSearchFieldChanged = _.debounce(async () => {
      // safety check
      if (searchField.value && searchField.value?.length < 3) {
        state.value = States.TYPING
      } else if (searchField.value && searchField.value?.length > 2) {
        state.value = States.SEARCHING
        const searchStatus = null // search all (ACTIVE + HISTORICAL)

        // Use appropriate service based on lookupType
        if (props.lookupType === LookupType.NR) {
          searchResults.value = await NameRequestLookupServices.search(searchField.value).catch(() => [])
        } else {
          searchResults.value = await BusinessLookupServices.search(searchField.value, searchStatus).catch(() => [])
        }
        // enable or disable items according to whether they have already been added
        for (const result of searchResults.value) {
          if (props.lookupType === LookupType.NR && 'nrNum' in result) {
            result.disabled = await isAffiliatedNR(result.nrNum)
          } else if ('identifier' in result) {
            result.disabled = await isAffiliated(result.identifier)
          }
        }

        // display appropriate section
        state.value = (searchResults.value.length > 0) ? States.SHOW_RESULTS : States.NO_RESULTS
      } else {
        // reset variables
        searchResults.value = []
        state.value = States.INITIAL
      }
    }, 600)

    watch(searchField, onSearchFieldChanged)

    const onItemSelected = (input: BusinessLookupResultIF) => {
      if (input) {
        emit(props.lookupType, input)
      } else {
        // Clear button was clicked
        searchResults.value = []
        state.value = States.INITIAL
      }
    }

    return {
      searchField,
      searchResults,
      state,
      onItemSelected,
      States,
      LookupType
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

.font-size-12 {
  font-size: 12px;
}

p {
  color: $gray7;
}

.business-lookup-result {
  font-size: $px-14;
  color: $gray7;

  &:hover {
    background-color: $gray1;
    color: $app-blue;
  }
}

.result-identifier,
.result-name {
  font-size: $px-16;

  // limit col width and show an ellipsis for long names:
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

// prevent Magnify icon from being rotated when list is displayed
::v-deep .v-input__icon .mdi-magnify {
  -webkit-transform: none !important;
  transform: none !important;
}

// Background color of Busines Name or Incorporation/Registration Number field
::v-deep .v-input__slot {
  background: #fff !important;
}
</style>
