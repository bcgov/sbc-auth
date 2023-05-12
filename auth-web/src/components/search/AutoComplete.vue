<template>
  <v-card v-if="showAutoComplete" :class="['mt-1', $style['auto-complete-card']]" elevation="5">
    <v-row no-gutters justify="center">
      <v-col class="no-gutters" cols="12">
        <v-list class="pt-0">
          <v-list-item-group v-model="autoCompleteSelected">
            <v-list-item v-for="(result, i) in autoCompleteResults"
                         :key="i"
                         :class="['pt-0', 'pb-0', 'pl-3', $style['auto-complete-item']]">
              <v-list-item-content class="pt-2 pb-2">
                <v-list-item-subtitle>
                  <v-row :class="$style['auto-complete-row']">
                    <v-col cols="12" :class="$style['title-size']">
                      {{ result.value }}
                    </v-col>
                  </v-row>
                </v-list-item-subtitle>
                <!--<v-list-item-title v-text="result.value"></v-list-item-title>-->
              </v-list-item-content>
            </v-list-item>
          </v-list-item-group>
        </v-list>
      </v-col>
    </v-row>
  </v-card>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import { getAutoComplete } from '@/utils'
import { AutoCompleteResponseIF } from '@/interfaces' // eslint-disable-line no-unused-vars

export default defineComponent({
  name: 'AutoComplete',
  props: {
    setAutoCompleteIsActive: {
      type: Boolean
    },
    searchValue: {
      type: String,
      default: ''
    }
  },
  setup (props, { emit }) {
    const localState = reactive({
      autoCompleteIsActive: props.setAutoCompleteIsActive,
      autoCompleteResults: [],
      autoCompleteSelected: -1,
      showAutoComplete: computed((): boolean => {
        const value = localState.autoCompleteResults?.length > 0 && localState.autoCompleteIsActive
        emit('hide-details', value)
        return value
      })
    })
    const updateAutoCompleteResults = async (searchValue: string) => {
      const response: AutoCompleteResponseIF = await getAutoComplete(searchValue)
      // check if results are still relevant before updating list
      if (searchValue === props.searchValue && response?.results) {
        // will take up to 5 results
        localState.autoCompleteResults = response?.results.slice(0, 5)
      }
    }
    watch(() => localState.autoCompleteSelected, (val: number) => {
      if (val >= 0) {
        const serchValue = localState.autoCompleteResults[val]?.value
        localState.autoCompleteIsActive = false
        emit('search-value', serchValue)
      }
    })
    watch(() => localState.autoCompleteIsActive, (val: boolean) => {
      if (!val) localState.autoCompleteResults = []
    })
    watch(() => props.setAutoCompleteIsActive, (val: boolean) => {
      localState.autoCompleteIsActive = val
    })
    watch(() => props.searchValue, (val: string) => {
      if (localState.autoCompleteIsActive) {
        updateAutoCompleteResults(val)
      }
    })

    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
#auto-complete-close-btn {
  color: $gray5 !important;
  background-color: transparent !important;
}
.auto-complete-item {
  min-height: 0;
}

@media (min-width: 960px) {
  .auto-complete-card {
    width: 700px;
  }
}

.auto-complete-card {
  position: absolute;
  z-index: 3;
}
.close-btn-row {
  height: 1rem;
}

.auto-complete-item:hover {
  color: $primary-blue !important;
  background-color: $gray1 !important;
}

.auto-complete-item[aria-selected='true'] {
  color: $primary-blue !important;
  background-color: $blueSelected !important;
}

.auto-complete-item:focus {
  background-color: $gray3 !important;
}

.auto-complete-row {
  width: 35rem;
  color: $gray7 !important;
}
.auto-complete-row:hover {
  color: $primary-blue !important;
}

.title-size {
  font-size: 1rem;
}

</style>
