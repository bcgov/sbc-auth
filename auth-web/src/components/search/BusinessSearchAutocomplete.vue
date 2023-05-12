<template>
  <v-card
    v-if="searchValue && searchValue.length >= 3 && !searching"
    id="business-search-autocomplete"
    class="auto-complete-card"
    elevation="5"
  >
    <v-row no-gutters justify="center">
      <v-col class="no-gutters" cols="12">
        <v-list v-if="autoCompleteResults && autoCompleteResults.length > 0" class="pt-0 results-list">
          <v-list-item disabled>
            <v-row class="auto-complete-sticky-row">
              <v-col cols="24"><span v-if="!isPPR">Active </span>B.C. Businesses:</v-col>
            </v-row>
          </v-list-item>
          <v-list-item-group v-model="autoCompleteSelected">
            <div v-for="(result, i) in autoCompleteResults" :key="i">
              <div class="info-tooltip" v-if="isBusinessTypeSPGP(result.legalType)">
                <v-tooltip right nudge-right="3" content-class="right-tooltip pa-5" transition="fade-transition">
                  <template v-slot:activator="{ on }">
                    <v-icon class="mt-n1" color="primary" v-on="on">
                      mdi-information-outline
                    </v-icon>
                  </template>
                  Registered owners of a manufactured home cannot be a sole proprietorship, partnership or limited
                  partnership. The home must be registered in the name of the sole proprietor or partner (person or
                  business).
                </v-tooltip>
              </div>

              <v-list-item
                class="auto-complete-item"
                :disabled="isBusinessTypeSPGP(result.legalType)"
                :class="{ disabled: isBusinessTypeSPGP(result.legalType) }"
              >
                <v-list-item-content class="py-2">
                  <v-list-item-subtitle>
                    <v-row class="auto-complete-row">
                      <v-col cols="2">{{ result.identifier }}</v-col>
                      <v-col cols="8" class="org-name">{{ result.name }}</v-col>
                      <v-col cols="2" v-if="!isBusinessTypeSPGP(result.legalType)" class="selectable">
                        Select
                      </v-col>
                    </v-row>
                  </v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </div>
          </v-list-item-group>
        </v-list>
        <div v-else-if="hasNoMatches" id="no-party-matches" class="pa-5">
          <p class="auto-complete-sticky-row">
            <span v-if="!isPPR">Active </span>B.C. Businesses:
          </p>
          <p>
            <strong>
              No <span v-if="!isPPR">active </span>B.C. businesses found.
            </strong>
          </p>
          <p>
            Ensure you have entered the correct, full legal name of the organization before entering the phone number
            and mailing address.
          </p>
        </div>
      </v-col>
    </v-row>
  </v-card>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs, watch, computed } from '@vue/composition-api'
import { SearchResponseI } from '@/interfaces' // eslint-disable-line no-unused-vars
import { useSearch } from '@/composables/useSearch'
import { BusinessTypes } from '@/enums/business-types'
import { debounce } from 'lodash'

export default defineComponent({
  name: 'BusinessSearchAutocomplete',
  props: {
    setAutoCompleteIsActive: {
      type: Boolean
    },
    searchValue: {
      type: String,
      default: ''
    },
    showDropdown: {
      type: Boolean
    },
    isPPR: {
      type: Boolean,
      default: false
    }
  },
  setup (props, { emit }) {
    const { searchBusiness } = useSearch()

    const localState = reactive({
      autoCompleteIsActive: props.setAutoCompleteIsActive,
      autoCompleteResults: null,
      autoCompleteSelected: null,
      searching: false,
      isSearchResultSelected: false,
      hasNoMatches: computed(
        (): boolean =>
          !localState.isSearchResultSelected &&
          localState.autoCompleteIsActive &&
          !localState.searching &&
          localState.autoCompleteResults &&
          localState.autoCompleteResults.length === 0
      )
    })

    const updateAutoCompleteResults = async (searchValue: string) => {
      localState.searching = true
      const response: SearchResponseI = await searchBusiness(searchValue, props.isPPR)
      // check if results are still relevant before updating list
      if (searchValue === props.searchValue && response?.searchResults.results) {
        localState.autoCompleteResults = response?.searchResults.results
      }
      localState.searching = false
    }

    const isBusinessTypeSPGP = (businessType: BusinessTypes): boolean => {
      // include all business types for PPR business searches
      return [BusinessTypes.GENERAL_PARTNERSHIP, BusinessTypes.SOLE_PROPRIETOR].includes(businessType) && !props.isPPR
    }

    watch(
      () => localState.autoCompleteSelected,
      (val: number) => {
        if (val >= 0) {
          const searchValue = localState.autoCompleteResults[val]?.name
          localState.autoCompleteIsActive = false
          localState.isSearchResultSelected = true
          emit('search-value', searchValue)
        }
      }
    )
    watch(
      () => localState.autoCompleteIsActive,
      (val: boolean) => {
        if (!val) localState.autoCompleteResults = null
      }
    )
    watch(
      () => props.setAutoCompleteIsActive,
      (val: boolean) => {
        localState.autoCompleteIsActive = val
      }
    )
    watch(
      () => props.searchValue,
      debounce((val: string) => {
        if (localState.autoCompleteIsActive) {
          updateAutoCompleteResults(val)
          localState.isSearchResultSelected = false
        }
      }, 1000) // add a one second delay before triggering the search, as per UXA
    )
    watch(
      () => localState.searching,
      (val: boolean) => {
        emit('searching', val)
      }
    )

    return {
      isBusinessTypeSPGP,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.auto-complete-item {
  min-height: 0;
}

strong, p {
  color: $gray7 !important;
}

.auto-complete-sticky-row{
  color: #465057 !important;
  font-size: 14px;
}
.auto-complete-row {
  color: $gray7 !important;
  font-size: 16px;

  .org-name {
    text-overflow: ellipsis;
    overflow: hidden;
  }
}

.auto-complete-card {
  position: absolute;
  z-index: 3;
  margin-top: -25px;
  width: 70%;
  p {
    white-space: pre-line;
  }

  .results-list {
    max-height: 400px;
    overflow-y: scroll;
  }
}
.auto-complete-item:hover {
  .auto-complete-row {
    color: $primary-blue !important;
  }
  background-color: #f1f3f5 !important;
}

.auto-complete-item[aria-selected='true'] {
  color: $primary-blue !important;
}

.auto-complete-item:focus {
  background-color: $gray3 !important;
}

.info-tooltip {
  position: relative;
  float: right;
  top: 15px;
  right: 40px;
  width: 0px;
}

.selectable {
  color: $primary-blue !important;
  text-align: right;
  font-size: 14px;
}

.auto-complete-item.disabled::v-deep {
  opacity: 0.6;
}
</style>
