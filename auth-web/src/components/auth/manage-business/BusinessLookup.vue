<template>
  <!-- once in Summary state, need to re-mount to reuse this component -->
  <div
    v-if="state !== States.SUMMARY"
    id="business-lookup"
  >
    <v-autocomplete
      :search-input.sync="searchField"
      :hide-no-data="state != States.NO_RESULTS"
      :items="searchResults"
      :loading="state === States.SEARCHING"
      :name="Math.random()"
      append-icon="mdi-magnify"
      autocomplete="chrome-off"
      autofocus
      class="mt-5 mb-n2"
      filled
      hint="For example: &quot;Joe's Plumbing Inc.&quot;, &quot;BC1234567&quot;, &quot;FM1234567&quot;"
      item-text="name"
      item-value="identifier"
      label="Business Name or Incorporation/Registration Number"
      no-filter
      persistent-hint
      return-object
      @input="onItemSelected($event)"
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

      <template #item="{ item }">
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
import { Component, Emit, Watch } from 'vue-property-decorator'
import { Action } from 'pinia-class'
import { BusinessLookupResultIF } from '@/models'
import BusinessLookupServices from '@/services/business-lookup.services'
import { Debounce } from 'vue-debounce-decorator'
import Vue from 'vue'
import { useBusinessStore } from '@/store/business'

enum States {
  INITIAL = 'initial',
  SEARCHING = 'searching',
  SHOW_RESULTS = 'show results',
  NO_RESULTS = 'no results',
  SUMMARY = 'summary'
}

/*
 * See PPR's BusinessSearchAutocomplete.vue for a Composition API example.
 */
@Component({})
export default class BusinessLookup extends Vue {
  // enum for template
  readonly States = States

  // action from business module
  @Action(useBusinessStore) private readonly isAffiliated!: (identifier: string) => Promise<boolean>

  /** V-model for search field. */
  searchField = ''

  /** Results from business lookup API. */
  searchResults = [] as Array<BusinessLookupResultIF>

  /** State of this component. */
  state = States.INITIAL

  /** Called when searchField property has changed. */
  @Watch('searchField')
  @Debounce(600)
  private async onSearchFieldChanged (): Promise<void> {
    // safety check
    if (this.searchField && this.searchField.length > 2) {
      this.state = States.SEARCHING
      const searchStatus = null // search all (ACTIVE + HISTORICAL)
      this.searchResults = await BusinessLookupServices.search(this.searchField, searchStatus).catch(() => [])

      // enable or disable items according to whether they have already been added
      for (const result of this.searchResults) {
        result.disabled = await this.isAffiliated(result.identifier)
      }

      // display appropriate section
      this.state = (this.searchResults.length > 0) ? States.SHOW_RESULTS : States.NO_RESULTS
    } else {
      // reset variables
      this.searchResults = []
      this.state = States.INITIAL
    }
  }

  /** When an item has been selected, emits event with business object. */
  @Emit('business')
  onItemSelected (input: BusinessLookupResultIF): void {
    // safety check
    if (input) {
      // change to summary state
      this.state = States.SUMMARY
    }
    // event data is automatically returned
  }
}
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
</style>
