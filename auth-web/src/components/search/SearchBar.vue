<template>
  <v-container fluid class="white search-bar-container no-gutters">
    <confirmation-dialog
      :setDisplay="confirmationDialog"
      :setOptions="dialogOptions"
      :setSettingOption="settingOption"
      @proceed="searchAction($event)"
    />
    <staff-payment-dialog
      attach=""
      class="mt-10"
      :setDisplay="staffPaymentDialogDisplay"
      :setOptions="staffPaymentDialog"
      :setShowCertifiedCheckbox="true"
      @proceed="onStaffPaymentChanges($event)"
    />

    <v-row>
      <v-col class="col-xl py-0">
        <v-row>
          <v-col class="search-info py-0">
            Select a search category and then enter a criteria to search.
          </v-col>
          <v-col align-self="end" cols="3" class="py-0">
            <folio-number
              :defaultFolioNumber="folioNumber"
              @folio-number="updateFolioNumber"
              @folio-error="folioError = $event"
            />
          </v-col>
        </v-row>
        <div v-if="typeOfSearch" v-html="typeOfSearch" class="font-weight-bold search-title pt-0 pb-1"></div>
        <v-row>
          <v-col class="pb-0" cols="4">
            <search-bar-list
              :defaultSelectedSearchType="selectedSearchType"
              :defaultCategoryMessage="categoryMessage"
              @selected="returnSearchSelection($event)"
            />
          </v-col>

          <!-- Business Name Lookup -->
          <v-col v-if="isBusinessDebtor" class="col-xl pb-0">
            <v-text-field
              filled
              id="txt-name-debtor"
              ref="debtorNameSearchField"
              label="Find or enter the Full Legal Name of the Business"
              v-model="searchValue"
              persistent-hint
              :hint="searchHint"
              :hide-details="hideDetails"
              :clearable="showClear"
              :disabled="!selectedSearchType"
              :error-messages="searchMessage ? searchMessage : ''"
              @click:clear="showClear = false"
            >
              <template v-slot:append>
                <v-progress-circular
                  v-if="loadingSearchResults"
                  indeterminate
                  color="primary"
                  class="mx-3"
                  :size="25"
                  :width="3"
                />
              </template>
            </v-text-field>

            <v-card flat>
              <BusinessSearchAutocomplete
                :searchValue="autoCompleteSearchValue"
                :setAutoCompleteIsActive="autoCompleteIsActive"
                v-click-outside="setCloseAutoComplete"
                @search-value="setSearchValue"
                @searching="loadingSearchResults = $event"
                :showDropdown="$refs.debtorNameSearchField && $refs.debtorNameSearchField.isFocused"
                isPPR
              />
            </v-card>
          </v-col>

          <v-col v-else-if="!isIndividual" class="col-xl pb-0">
            <v-tooltip
              content-class="bottom-tooltip"
              bottom
              :open-on-hover="false"
              :disabled="!searchPopUp"
              transition="fade-transition"
              :value="showSearchPopUp && searchPopUp"
            >
              <template v-slot:activator="scope">
                <v-text-field
                  id="search-bar-field"
                  class="search-bar-text-field"
                  autocomplete="off"
                  v-on="scope.on"
                  :disabled="!selectedSearchType"
                  :error-messages="searchMessage ? searchMessage : ''"
                  filled
                  :hint="searchHint"
                  :hide-details="hideDetails"
                  persistent-hint
                  :label="selectedSearchType ? selectedSearchType.textLabel : 'Select a category first'"
                  v-model="searchValue"
                  @keypress.enter="searchCheck()"
                />
              </template>
              <v-row v-for="(line, index) in searchPopUp" :key="index" class="pt-2 pl-3">
                {{ line }}
              </v-row>
            </v-tooltip>
            <auto-complete
              :searchValue="autoCompleteSearchValue"
              :setAutoCompleteIsActive="autoCompleteIsActive"
              v-click-outside="setCloseAutoComplete"
              @search-value="setSearchValue"
              @hide-details="setHideDetails"
            >
            </auto-complete>
          </v-col>

          <v-col v-else class="pl-3 col-xl pb-0">
            <v-row no-gutters>
              <v-col cols="4">
                <v-text-field
                  id="first-name-field"
                  :class="wrapClass"
                  autocomplete="off"
                  :error-messages="searchMessageFirst ? searchMessageFirst : ''"
                  filled
                  :hint="searchHintFirst"
                  persistent-hint
                  :label="optionFirst"
                  v-model="searchValueFirst"
                  @keypress.enter="searchCheck()"
                />
              </v-col>
              <v-col cols="4" class="pl-3">
                <v-text-field
                  id="second-name-field"
                  autocomplete="off"
                  :error-messages="searchMessageSecond ? searchMessageSecond : ''"
                  filled
                  :hint="searchHintSecond"
                  persistent-hint
                  label="Middle Name (Optional)"
                  v-model="searchValueSecond"
                  @keypress.enter="searchCheck()"
                />
              </v-col>
              <v-col cols="4" class="pl-3">
                <v-text-field
                  id="last-name-field"
                  autocomplete="off"
                  :error-messages="searchMessageLast ? searchMessageLast : ''"
                  filled
                  :hint="searchHintLast"
                  persistent-hint
                  label="Last Name"
                  v-model="searchValueLast"
                  @keypress.enter="searchCheck()"
                />
              </v-col>
            </v-row>
          </v-col>
        </v-row>
        <v-row>
          <v-col class="py-0">
            <div v-if="showPprFeeHint || showMhrHint" class="ppr-mhr-info mt-5 mb-7">
              <v-icon size="20">mdi-information-outline</v-icon>
              <span v-if="showPprFeeHint" data-test-id="ppr-search-info">
                Each Personal Property Registry search will incur a fee of ${{ fee }}, including searches that return
                no results.
              </span>
              <span v-else-if="showMhrHint" data-test-id="mhr-search-info">
                You will have the option to include a Personal Property Registry lien / encumbrance search
                as part of your Manufactured Home Registry search.
              </span>
            </div>
          </v-col>
        </v-row>
      </v-col>
      <v-col class="col-auto py-0">
        <v-row :style="typeOfSearch ? 'height: 115px' : 'height: 85px'" />
        <v-row>
          <v-col class="pb-0">
            <v-btn
            id="search-btn"
            class="search-bar-btn primary"
            :loading="searching"
            @click="searchCheck()"
            >
              <v-icon>mdi-magnify</v-icon>
            </v-btn>

          <v-menu v-if="(isStaffBcolReg || isRoleStaff) && !isStaffSbc" offset-y left nudge-bottom="4">
              <template v-slot:activator="{ on }">
                <v-btn
                  v-on="on"
                  id="client-search"
                  outlined
                  class="down-btn ml-3"
                  color="primary"
                  data-test-id="client-search-bar-btn"
                >
                  <v-icon color="primary">mdi-menu-down</v-icon>
                </v-btn>
              </template>
              <v-list class="actions__more-actions">
                <v-list-item @click="clientSearch()">
                  <v-list-item-subtitle>
                    <v-icon style="font-size: 18px;padding-bottom: 2px;">mdi-magnify</v-icon>
                    <span>
                      Client Search
                    </span>
                  </v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-menu>
          </v-col>
        </v-row>
        <v-row v-if="showPprFeeHint" no-gutters>
          <v-col>
            <span id="search-btn-info" class="fee-text"> ${{ fee }} fee </span>
          </v-col>
        </v-row>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import { useActions, useGetters } from 'vuex-composition-helpers'
import _ from 'lodash'

import { mhrSearch, search, staffSearch, validateSearchAction, validateSearchRealTime } from '@/utils'
import { MHRSearchTypes, SearchTypes } from '@/resources'
import { paymentConfirmaionDialog, staffPaymentDialog } from '@/resources/dialogOptions'
/* eslint-disable no-unused-vars */
import {
  DialogOptionsIF,
  IndividualNameIF,
  SearchCriteriaIF,
  SearchTypeIF,
  SearchValidationIF,
  UserSettingsIF
} from '@/interfaces'
/* eslint-enable no-unused-vars */
import { APIMHRMapSearchTypes, APISearchTypes, SettingOptions } from '@/enums'
// won't render properly from @/components/search
import AutoComplete from '@/components/search/AutoComplete.vue'
import SearchBarList from '@/components/search/SearchBarList.vue'
import BusinessSearchAutocomplete from '@/components/search/BusinessSearchAutocomplete.vue'
import { FolioNumber } from '@/components/common'
import { ConfirmationDialog, StaffPaymentDialog } from '@/components/dialogs'
import { useSearch } from '@/composables/useSearch'

export default defineComponent({
  components: {
    AutoComplete,
    BusinessSearchAutocomplete,
    ConfirmationDialog,
    StaffPaymentDialog,
    FolioNumber,
    SearchBarList
  },
  props: {
    defaultDebtor: {
      type: Object as () => IndividualNameIF
    },
    defaultFolioNumber: {
      type: String,
      default: ''
    },
    defaultSelectedSearchType: {
      type: Object as () => SearchTypeIF
    },
    defaultSearchValue: {
      type: String
    },
    isNonBillable: { default: false },
    serviceFee: { default: 1.50 }
  },
  setup (props, { emit }) {
    const {
      setIsStaffClientPayment,
      setSearching,
      setStaffPayment,
      setFolioOrReferenceNumber,
      setSelectedManufacturedHomes
    } = useActions<any>([
      'setIsStaffClientPayment',
      'setSearching',
      'setStaffPayment',
      'setFolioOrReferenceNumber',
      'setSelectedManufacturedHomes'
    ])
    const {
      getUserSettings,
      isSearching,
      isRoleStaff,
      isRoleStaffBcol,
      isRoleStaffReg,
      isRoleStaffSbc,
      isSearchCertified,
      getStaffPayment,
      hasPprEnabled,
      hasMhrEnabled
    } = useGetters<any>([
      'getUserSettings',
      'isSearching',
      'isRoleStaff',
      'isRoleStaffBcol',
      'isRoleStaffReg',
      'isRoleStaffSbc',
      'isSearchCertified',
      'getStaffPayment',
      'hasPprEnabled',
      'hasMhrEnabled'
    ])
    const { isMHRSearchType, isPPRSearchType, mapMhrSearchType } = useSearch()
    const localState = reactive({
      autoCompleteIsActive: true,
      autoCompleteSearchValue: '',
      confirmationDialog: false,
      folioNumber: props.defaultFolioNumber,
      folioError: false,
      hideDetails: false,
      loadingSearchResults: false,
      showClear: false,
      searchValue: props.defaultSearchValue,
      searchValueFirst: props.defaultDebtor?.first,
      searchValueSecond: props.defaultDebtor?.second,
      searchValueLast: props.defaultDebtor?.last,
      selectedSearchType: props.defaultSelectedSearchType,
      settingOption: SettingOptions.PAYMENT_CONFIRMATION_DIALOG,
      showSearchPopUp: true,
      staffPaymentDialogDisplay: false,
      staffPaymentDialog: staffPaymentDialog,
      validations: Object as SearchValidationIF,
      categoryMessage: computed((): string => {
        return localState.validations?.category?.message || ''
      }),
      showPprFeeHint: computed((): boolean => {
        return !(isRoleStaffBcol.value || isRoleStaffReg.value) && ((hasPprEnabled.value && !hasMhrEnabled.value) ||
          isPPRSearchType(localState.selectedSearchType?.searchTypeAPI))
      }),
      showMhrHint: computed((): boolean => {
        return !(isRoleStaffBcol.value || isRoleStaffReg.value) && ((hasMhrEnabled.value && !hasPprEnabled.value) ||
          isMHRSearchType(localState.selectedSearchType?.searchTypeAPI))
      }),
      dialogOptions: computed((): DialogOptionsIF => {
        const options = { ...paymentConfirmaionDialog }
        options.text = options.text.replace('8.50', localState.fee)
        return options
      }),
      fee: computed((): string => {
        if (isRoleStaffSbc.value) return '10.00'
        if (props.isNonBillable) {
          const serviceFee = `${props.serviceFee}`
          if (serviceFee.includes('.')) {
            // the right side of the decimal
            const decimalStr = serviceFee.substring(serviceFee.indexOf('.') + 1)
            if (decimalStr.length === 2) return serviceFee
            // else add zero
            return serviceFee + '0'
          }
          // add decimal
          return serviceFee + '.00'
        }
        return '8.50'
      }),
      isIndividual: computed((): boolean => {
        return (localState.selectedSearchType?.searchTypeAPI === APISearchTypes.INDIVIDUAL_DEBTOR) ||
          (localState.selectedSearchType?.searchTypeAPI === APIMHRMapSearchTypes.MHROWNER_NAME)
      }),
      isBusinessDebtor: computed((): boolean => {
        return localState.selectedSearchType?.searchTypeAPI === APISearchTypes.BUSINESS_DEBTOR
      }),
      wrapClass: computed(() => {
        // Add wrap css class only to MHR Home Owner search fields
        if (localState.selectedSearchType?.searchTypeAPI !== APIMHRMapSearchTypes.MHROWNER_NAME) return ''
        return localState.searchMessageFirst || localState.searchMessageSecond ? 'hint-wrap' : 'hint-no-wrap'
      }),
      personalPropertySearchFee: computed((): string => {
        return localState.isRoleStaff || localState.isStaffSbc ? '10.00' : '8.50'
      }),
      manHomeSearchFee: computed((): string => {
        return localState.isRoleStaff || localState.isStaffSbc ? '10.00' : '7.00'
      }),
      comboSearchFee: computed((): string => {
        return localState.isRoleStaff || localState.isStaffSbc ? '15.00' : '12.00'
      }),
      isRoleStaff: computed((): boolean => {
        return isRoleStaff.value
      }),
      isStaffBcolReg: computed((): boolean => {
        return isRoleStaffBcol.value || isRoleStaffReg.value
      }),
      isRoleStaffReg: computed((): boolean => {
        return isRoleStaffReg.value
      }),
      isStaffSbc: computed((): boolean => {
        return isRoleStaffSbc.value
      }),
      searching: computed((): boolean => {
        return isSearching.value
      }),
      searchMessage: computed((): string => {
        return localState.validations?.searchValue?.message || ''
      }),
      optionFirst: computed((): string => {
        return isRoleStaffReg.value && isMHRSearchType(localState.selectedSearchType?.searchTypeAPI)
          ? 'First Name (Optional)' : 'First Name'
      }),
      typeOfSearch: computed((): string => {
        // only show the type of search if authorized to both types
        if (((hasPprEnabled.value && hasMhrEnabled.value) || isRoleStaff.value || localState.isStaffBcolReg)) {
          if (localState.selectedSearchType) {
            if (isPPRSearchType(localState.selectedSearchType.searchTypeAPI)) {
              return '<i aria-hidden="true" class="v-icon notranslate menu-icon mdi ' + SearchTypes[0].icon +
                '"></i>' + SearchTypes[0].textLabel
            }
            if (isMHRSearchType(localState.selectedSearchType.searchTypeAPI)) {
              return '<i aria-hidden="true" class="v-icon notranslate menu-icon mdi ' + MHRSearchTypes[0].icon +
                '"></i>' + MHRSearchTypes[0].textLabel
            }
          }
        }
        return ''
      }),
      searchMessageFirst: computed((): string => {
        return localState.validations?.searchValue?.messageFirst || ''
      }),
      searchMessageSecond: computed((): string => {
        return localState.validations?.searchValue?.messageSecond || ''
      }),
      searchMessageLast: computed((): string => {
        return localState.validations?.searchValue?.messageLast || ''
      }),
      searchHint: computed((): string => {
        if (localState.searchMessage) return ''
        else return localState.selectedSearchType?.hints?.searchValue || ''
      }),
      searchHintFirst: computed((): string => {
        if (localState.searchMessageFirst) return ''
        else return localState.selectedSearchType?.hints?.searchValueFirst || ''
      }),
      searchHintSecond: computed((): string => {
        if (localState.searchMessageSecond) return ''
        else return localState.selectedSearchType?.hints?.searchValueSecond || ''
      }),
      searchHintLast: computed((): string => {
        if (localState.searchMessageLast) return ''
        else return localState.selectedSearchType?.hints?.searchValueLast || ''
      }),
      searchPopUp: computed((): Array<string> | boolean => {
        return localState.validations?.searchValue?.popUp || false
      }),
      showConfirmationDialog: computed((): boolean => {
        // don't show confirmation dialog if bcol or reg staff
        if (localState.isStaffBcolReg || isMHRSearchType(localState.selectedSearchType?.searchTypeAPI)) return false

        const settings: UserSettingsIF = getUserSettings.value
        return settings?.paymentConfirmationDialog
      })
    })

    /**
     * the function take a string and remove all the zero-width space characters
     * and replace all smart quotes (closing single quote also used as apostrophe) to its corresponding straight quotes
     * @param dirtyValue the string we want to clean
     * @return the cleaned up string
     */
    const cleanUpInput = (dirtyValue: string|undefined) => {
      if (dirtyValue === undefined) {
        return undefined
      }
      return dirtyValue
        .trim()
        .replaceAll(/[\u200B-\u200D\uFEFF\u200E\u200F]|(?:&#x200E;)/g, '')
        .replaceAll(/[\u2018\u2019]/g, "'")
        .replaceAll(/[\u201C\u201D]/g, '"')
    }

    const getCriteria = () => {
      if (localState.isIndividual) {
        const first = cleanUpInput(localState.searchValueFirst)
        const second = cleanUpInput(localState.searchValueSecond) // Also used for middle name in MHR searches
        const last = cleanUpInput(localState.searchValueLast)

        if (isPPRSearchType(localState.selectedSearchType.searchTypeAPI)) {
          return { debtorName: { first: first, second: second, last: last } }
        }
        if (isMHRSearchType(localState.selectedSearchType.searchTypeAPI)) {
          return { ownerName: { first: first, middle: second, last: last } }
        }
      } else if (localState.selectedSearchType.searchTypeAPI === APISearchTypes.BUSINESS_DEBTOR) {
        return { debtorName: { business: cleanUpInput(localState.searchValue) } }
      } else {
        const cleanedSearchValue = cleanUpInput(localState.searchValue)
        return { value: cleanedSearchValue }
      }
    }
    const getSearchApiParams = (): SearchCriteriaIF => {
      const searchTypeApi = localState.selectedSearchType.searchTypeAPI
      const type = isMHRSearchType(searchTypeApi) ? mapMhrSearchType(searchTypeApi) : searchTypeApi

      return {
        type: type,
        criteria: getCriteria(),
        clientReferenceId: localState.folioNumber
      }
    }
    const searchAction = _.throttle(async (proceed: boolean) => {
      localState.confirmationDialog = false
      if (proceed) {
        // pad mhr number with 0s
        if ((localState.selectedSearchType?.searchTypeAPI === APISearchTypes.MHR_NUMBER) ||
          (localState.selectedSearchType?.searchTypeAPI === APIMHRMapSearchTypes.MHRMHR_NUMBER)) {
          localState.searchValue.padStart(6, '0')
        }
        setSearching(true)
        emit('search-data', null) // clear any current results
        let resp
        if (isRoleStaffReg.value) {
          if (isPPRSearchType(localState.selectedSearchType?.searchTypeAPI)) {
            resp = await staffSearch(
              getSearchApiParams(),
              getStaffPayment.value,
              isSearchCertified.value)
            setStaffPayment(null)
          }
          if (isMHRSearchType(localState.selectedSearchType.searchTypeAPI)) {
            setSelectedManufacturedHomes([])
            setFolioOrReferenceNumber(localState.folioNumber)
            resp = await mhrSearch(getSearchApiParams(), '')
          }
        } else {
          if (isPPRSearchType(localState.selectedSearchType?.searchTypeAPI)) {
            resp = await search(getSearchApiParams(), '')
          }
          if (isMHRSearchType(localState.selectedSearchType.searchTypeAPI)) {
            // If SBC Staff - is always a search on clients behalf
            if (localState.isStaffSbc) setIsStaffClientPayment(true)

            setSelectedManufacturedHomes([])
            setFolioOrReferenceNumber(localState.folioNumber)
            resp = await mhrSearch(getSearchApiParams(), '')
          }
        }
        if (resp?.error) emit('search-error', resp.error)
        else {
          emit('searched-type', localState.selectedSearchType)
          if (localState.isIndividual) {
            emit('debtor-name', {
              first: localState.searchValueFirst,
              second: localState.searchValueSecond,
              last: localState.searchValueLast
            })
          } else emit('searched-value', localState.searchValue)
          emit('search-data', resp)
        }
        setSearching(false)
      }
    }, 2000, { trailing: false })
    const searchCheck = async () => {
      if (localState.folioError) {
        return
      }
      localState.validations = validateSearchAction(localState)
      if (localState.validations) {
        localState.autoCompleteIsActive = false
      } else if (localState.showConfirmationDialog) {
        localState.confirmationDialog = true
      } else {
        searchAction(true)
      }
    }
    const setHideDetails = (hideDetails: boolean) => {
      localState.hideDetails = hideDetails
    }
    const returnSearchSelection = (selection: SearchTypeIF) => {
      localState.selectedSearchType = selection
    }
    const setSearchValue = (searchValue: string) => {
      localState.autoCompleteIsActive = false
      localState.searchValue = searchValue
      localState.showClear = true
      if (document.getElementById('search-bar-field')) {
        document.getElementById('search-bar-field').focus()
      }
    }
    const togglePaymentConfirmation = (showDialog: boolean) => {
      emit('togglePaymentDialog', showDialog)
    }
    const updateFolioNumber = (folioNumber: string) => {
      localState.folioNumber = folioNumber
    }

    const setCloseAutoComplete = () => {
      localState.autoCompleteIsActive = false
    }

    const onStaffPaymentChanges = (search: boolean): void => {
      if (search) {
        searchAction(true)
      }
      localState.staffPaymentDialogDisplay = false
    }

    const clientSearch = async () => {
      localState.validations = validateSearchAction(localState)
      if (localState.validations) {
        localState.autoCompleteIsActive = false
      } else if (isMHRSearchType(localState.selectedSearchType?.searchTypeAPI)) {
        setIsStaffClientPayment(true)
        searchAction(true)
      } else {
        localState.staffPaymentDialogDisplay = true
      }
    }

    watch(() => localState.searchValue, (val: string) => {
      if (!val) localState.validations = null
      else localState.validations = validateSearchRealTime(localState)
      if (localState.selectedSearchType?.searchTypeAPI === APISearchTypes.BUSINESS_DEBTOR &&
          localState.autoCompleteIsActive) {
        localState.autoCompleteSearchValue = val
      }
      // show autocomplete results when there is a searchValue and if no error messages
      localState.autoCompleteIsActive = !localState.validations && val !== ''
    })
    watch(() => localState.searchValueFirst, (val: string) => {
      if (!val) localState.validations = null
      else localState.validations = validateSearchRealTime(localState)
    })
    watch(() => localState.searchValueSecond, (val: string) => {
      if (!val) localState.validations = null
      else localState.validations = validateSearchRealTime(localState)
    })
    watch(() => localState.searchValueLast, (val: string) => {
      if (!val) localState.validations = null
      else localState.validations = validateSearchRealTime(localState)
    })
    watch(() => localState.selectedSearchType, (val: SearchTypeIF) => {
      localState.validations = null
      localState.searchValue = null
      if (val.searchTypeAPI !== APISearchTypes.BUSINESS_DEBTOR) localState.autoCompleteIsActive = false
      else localState.autoCompleteIsActive = true
    })

    return {
      ...toRefs(localState),
      isMHRSearchType,
      getSearchApiParams,
      onStaffPaymentChanges,
      searchAction,
      searchCheck,
      setHideDetails,
      setSearchValue,
      setCloseAutoComplete,
      clientSearch,
      togglePaymentConfirmation,
      returnSearchSelection,
      updateFolioNumber
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
::v-deep .theme--light.v-icon.mdi-close {
  color: $primary-blue !important;
}

.hint-no-wrap {
  white-space: nowrap;
  div {
    overflow: unset;
  }
}

.hint-wrap {
  white-space: normal;
}

#search-btn, #client-search {
  height: 2.85rem;
  min-width: 0 !important;
  width: 3rem;
}
#search-btn-info {
  color: $gray7;
  font-size: 0.725rem;
}
.search-info {
  color: $gray7;
  font-size: 1rem;
  line-height: 3.5em;
}
.search-title {
  color: $gray9;
  font-weight: bold;
}

.ppr-mhr-info {
  font-size: 14px;
  line-height: 1em;

  i {
    color: $gray7;
  }
}
.fee-info {
  border-bottom: 1px dotted $gray9;
}
.folio-btn {
  background-color: transparent !important;
  color: $primary-blue !important;
  font-size: 0.825rem !important;
}
.folio-btn::before {
  background-color: transparent !important;
  color: $primary-blue !important;
}
.folio-close-btn {
  background-color: transparent !important;
  color: $primary-blue !important;
  position: absolute;
}
.folio-close-btn::before {
  background-color: transparent !important;
  color: $primary-blue !important;
}
.folio-edit-card {
  width: 15rem;
  position: absolute;
  z-index: 3;
}
.folio-header {
  color: $gray9;
}
.folio-info {
  color: $gray7;
  font-size: 0.875rem;
}

.search-bar-container::v-deep {
  padding: 30px 30px 22px 24px;
}
::v-deep .auto-complete-card {
  width: 100%!important;
}
</style>
