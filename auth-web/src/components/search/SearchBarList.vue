<template>
  <v-select
          id="search-select"
          class="search-bar-type-select"
          :class="{ 'wide-menu' : !isSingleSearchOption }"
          ref="searchSelect"
          :error-messages="categoryMessage ? categoryMessage : ''"
          filled
          :items="(displayItems.filter(item => displayGroup[item.group] || item.class === 'search-list-header'))"
          item-disabled="selectDisabled"
          item-text="searchTypeUI"
          item-value="searchTypeAPI"
          :label="searchTypeLabel"
          return-object
          v-model="selectedSearchType"
          @focus="updateSelections()"
          :menu-props="isSingleSearchOption ? { bottom: true, offsetY: true } : {}"
          attach=""
        >
        <template v-slot:item="{ item }">
          <template v-if="item.class === 'search-list-header'">
            <v-list-item-content style="padding: 9px 0;" :class="{ 'top-border' : item.icon === 'mdi-home' }">
              <v-row
                :id="`srch-type-drop-${item.group}`"
                style="width: 45rem; pointer-events: all;"
                @click="toggleGroup(item.group)"
              >
                <v-col class="py-0" align-self="center">
                  <span class="search-list-header"><v-icon class="menu-icon" :color="item.color">{{item.icon}}</v-icon>
                  {{ item.textLabel }}</span>
                </v-col>
                <v-col class="py-0" align-self="center" cols="auto">
                  <v-btn icon small style="pointer-events: all;">
                    <v-icon v-if="displayGroup[item.group]" class="expand-icon" color="primary">mdi-chevron-up</v-icon>
                    <v-icon v-else class="expand-icon" color="primary">mdi-chevron-down</v-icon>
                  </v-btn>
                </v-col>
              </v-row>
            </v-list-item-content>
          </template>
          <template v-else>
            <v-list-item
              :id="`list-${item.searchTypeAPI.toLowerCase().replaceAll('_','-')}`"
              class="copy-normal search-list"
              :class="{ 'select-menu-padding' : !isSingleSearchOption }"
              @click="selectSearchType(item)"
            >
              <v-list-item-title>
                {{ item.searchTypeUI }}
              </v-list-item-title>
            </v-list-item>
          </template>
        </template>
  </v-select>
</template>
<script lang="ts">
import { computed, defineComponent, reactive, ref, toRefs } from '@vue/composition-api'
import { useGetters } from 'vuex-composition-helpers'
import { MHRSearchTypes, SearchTypes } from '@/resources'
import { APISearchTypes, UISearchTypes } from '@/enums'
import { SearchTypeIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { getFeatureFlag } from '@/utils'

export default defineComponent({
  name: 'SearchBarList',
  emits: ['selected'],
  props: {
    defaultSelectedSearchType: {
      type: Object as () => SearchTypeIF
    },
    defaultCategoryMessage: {
      type: String,
      default: ''
    }
  },
  setup (props, { emit }) {
    const {
      isRoleStaffReg,
      isRoleStaff,
      hasPprEnabled,
      hasMhrEnabled
    } = useGetters<any>([
      'isRoleStaffReg',
      'isRoleStaff',
      'hasPprEnabled',
      'hasMhrEnabled',
      'getUserProductSubscriptionsCodes'
    ])
    const searchSelect = ref(null)
    const localState = reactive({
      searchTypes: UISearchTypes,
      searchTypeValues: APISearchTypes,
      selectedSearchType: props.defaultSelectedSearchType,
      categoryMessage: computed((): string => {
        return props.defaultCategoryMessage
      }),
      searchTypeLabel: computed((): string => {
        if (!localState.selectedSearchType) {
          return 'Select a search category'
        }
        // display searchTypeUI label when both groups are collapsed
        if (Object.values(localState.displayGroup).every(group => group === false)) {
          return localState.selectedSearchType.searchTypeUI
        }
        // display searchTypeUI label even if other group is expanded
        if (!localState.displayGroup[localState.selectedSearchType.group]) {
          return localState.selectedSearchType.searchTypeUI
        }
        return ''
      }),
      origItems: computed((): Array<SearchTypeIF> => {
        const allSearchTypes = []

        // Staff Only Options
        if (isRoleStaff.value || isRoleStaffReg.value) {
          if (getFeatureFlag('mhr-ui-enabled')) {
            allSearchTypes.push(...SearchTypes, ...MHRSearchTypes)
            return allSearchTypes
          } else {
            allSearchTypes.push(...SearchTypes)
            return allSearchTypes.slice(1)
          }
        }

        // Client Only Blocks
        if (hasPprEnabled.value && hasMhrEnabled.value) {
          allSearchTypes.push(...SearchTypes, ...MHRSearchTypes)
          return allSearchTypes
        }

        if (hasPprEnabled.value) {
          allSearchTypes.push(...SearchTypes)
          return allSearchTypes.slice(1)
        }

        if (hasMhrEnabled.value) {
          allSearchTypes.push(...MHRSearchTypes)
          return allSearchTypes.slice(1)
        }
        return allSearchTypes
      }),
      isSingleSearchOption: computed((): boolean => {
        return ((hasPprEnabled.value && !hasMhrEnabled.value) || (!hasPprEnabled.value && hasMhrEnabled.value)) &&
          !(isRoleStaff.value || isRoleStaffReg.value)
      }),
      displayItems: [],
      displayGroup: {
        1: !(isRoleStaff.value || isRoleStaffReg.value)
          ? (hasPprEnabled.value && !hasMhrEnabled.value)
          : !hasMhrEnabled.value,
        2: !(isRoleStaff.value || isRoleStaffReg.value) && (!hasPprEnabled.value && hasMhrEnabled.value)
      },
      showMenu: false
    })

    const toggleGroup = (group: number) => {
      const initial = localState.displayGroup[group]
      // collapse both groups as only one group can be expanded at once
      localState.displayGroup = {
        1: false,
        2: false
      }
      // expand desired group
      localState.displayGroup[group] = !initial
      let newDisplayItems = [] as Array<SearchTypeIF>
      if (!localState.displayGroup[group]) {
        // remove elements from display
        for (let i = 0; i < localState.displayItems.length; i++) {
          const isHeader = localState.displayItems[i].selectDisabled || false
          // if item is not part of the group or is a header add to new list
          if (localState.displayItems[i].group !== group || isHeader) {
            newDisplayItems.push({ ...localState.displayItems[i] })
          }
        }
      } else {
        // add items to their proper spot in the display list
        newDisplayItems = [...localState.displayItems]
        // get the index of the group header
        let headerIdx = 0
        for (let i = 0; i < newDisplayItems.length; i++) {
          if (newDisplayItems[i].group === group) {
            headerIdx = i
            break
          }
        }
        // insert the items of that group after their header in the display list
        let offset = 1
        for (let i = 0; i < localState.origItems.length; i++) {
          const isHeader = localState.origItems[i].selectDisabled || false
          if (localState.origItems[i].group === group && !isHeader) {
            newDisplayItems.splice(headerIdx + offset, 0, { ...localState.origItems[i] })
            offset++
          }
        }
      }
      localState.displayItems = [...newDisplayItems]
    }
    const selectSearchType = (val: SearchTypeIF) => {
      emit('selected', val)
      localState.selectedSearchType = val
      searchSelect.value.blur()
    }
    const updateSelections = () => {
      localState.displayItems = localState.origItems
      if (hasPprEnabled.value && hasMhrEnabled.value) {
        localState.displayGroup = { 1: false, 2: false }
      }
    }

    return {
      updateSelections,
      searchSelect,
      selectSearchType,
      toggleGroup,
      ...toRefs(localState)
    }
  }
})
</script>
<style lang="scss" scoped>
@import "@/assets/styles/theme.scss";
::v-deep .theme--light.v-list-item.copy-normal {
  color: $gray7 !important;
}

::v-deep .select-menu-padding {
  padding-left: 49px;
}
.search-list-header {
  color: $gray9 !important;
  font-weight:bold;
}

.wide-menu > ::v-deep .v-menu__content {
  min-width: 427px !important;
}

::v-deep .v-menu__content {
  max-height: none !important;
  background-color: red;
  width: 80%;

  .top-border {
    border-top: 1px solid #E1E1E1;
  }
}

</style>
