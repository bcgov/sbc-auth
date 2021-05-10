<template>
  <v-card v-if="showAutoComplete" :class="['mt-1', $style['auto-complete-card']]" elevation="5">
    <v-row no-gutters justify="end" :class="$style['close-btn-row']">
      <v-col cols="auto" justify="end" class="pt-0">
        <v-btn append
        icon
        x-small
        right
        :id="$style['auto-complete-close-btn']"
        class="auto-complete-close-btn"
        @click="autoCompleteIsActive=false">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-col>
    </v-row>
    <v-row no-gutters justify="center" class="pl-2 pr-5">
      <v-col no-gutters cols="auto">
        <v-list class="pt-0">
          <v-list-item-group v-model="autoCompleteSelected">
            <v-list-item v-for="(result, i) in autoCompleteResults"
            :key="i"
            :class="['pt-0', 'pb-0', 'pl-1', $style['auto-complete-item']]">
              <v-list-item-content class="pt-2 pb-2">
                <v-list-item-title v-text="result.value"></v-list-item-title>
              </v-list-item-content>
            </v-list-item>
          </v-list-item-group>
        </v-list>
      </v-col>
    </v-row>
  </v-card>
</template>

<script lang="ts">
import { AutoCompleteResponseIF, AutoCompleteResultIF } from '@/models/AutoComplete'
import { Component, Prop, Vue, Watch } from 'vue-property-decorator'
import { namespace } from 'vuex-class'

const OrgModule = namespace('org')

@Component({})
export default class AutoCompleteView extends Vue {
    @OrgModule.Action('getAutoComplete') public getAutoComplete!:(searchValue: string) =>Promise<AutoCompleteResponseIF>
    @Prop({ default: false }) private autoCompleteIsActive: boolean
    @Prop({ default: '' }) private searchValue: string

    private autoCompleteResults: AutoCompleteResultIF[] = []
    private autoCompletedSelected : number = -1

    private get showAutoComplete () {
      const value = this.autoCompleteResults.length > 0 && this.autoCompleteIsActive
      this.$emit('hide-auto-complete', value)
      return value
    }

    @Watch('searchValue', { deep: true })
    async updateAutoCompleteResults (val, oldVal) {
      if (oldVal !== val && this.autoCompleteIsActive) {
        await this.getAutoCompleteResults(val)
      }
    }

    @Watch('autoCompleteIsActive', { deep: true })
    updateAutoCompleteIsActive (val) {
      if (!val) {
        this.autoCompleteResults = []
      }
    }

    @Watch('autoCompletedSelected', { deep: true })
    async emitSelectedValue (val) {
      if (val >= 0) {
        const searchValue = this.autoCompleteResults[val]?.value
        this.autoCompleteIsActive = false
        this.$emit('auto-complete-value', searchValue)
      }
    }

    private async getAutoCompleteResults (searchValue: string) {
      try {
        const response: AutoCompleteResponseIF = await this.getAutoComplete(searchValue)
        if (searchValue === this.searchValue && response?.results) {
        // will take up to 5 results
          this.autoCompleteResults = response?.results.slice(0, 5)
        }
      } catch (ex) {
        // eslint-disable-next-line no-console
        console.log('Error while auto complete...')
      }
    }
}
</script>

<style lang="scss" scoped>
#auto-complete-close-btn {
  color: $gray5 !important;
  background-color: transparent !important;
}
.auto-complete-item {
  min-height: 0;
}
.auto-complete-card {
  max-width: 30rem;
  position: absolute;
  z-index: 3;
}
.close-btn-row {
  height: 1rem;
}
</style>
