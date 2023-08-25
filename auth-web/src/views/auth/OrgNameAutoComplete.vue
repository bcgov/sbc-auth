<template>
  <v-card
    v-if="showAutoComplete"
    class="mt-0 auto-complete-card"
    elevation="5"
    data-test="auto-complete-card"
  >
    <v-row
      no-gutters
      justify="start"
      class="mx-0 pl-2 pr-5"
    >
      <v-col
        class="no-gutters"
        cols="12"
      >
        <div class="content px-2 pt-1">
          <v-list class="pt-0 content-list">
            <v-list-item-group v-model="autoCompleteSelectedIndex">
              <v-list-item
                v-for="(result, i) in autoCompleteResults"
                :key="i"
                class="pt-0 pb-0 pl-1 auto-complete-item"
              >
                <v-list-item-content class="pt-2 pb-2">
                  <v-list-item-title
                    :data-test="getIndexedTag('auto-complete-item', i)"
                    v-text="result.value"
                  />
                </v-list-item-content>
              </v-list-item>
            </v-list-item-group>
          </v-list>
          <v-btn
            append
            icon
            x-small
            right
            class="auto-complete-close-btn"
            data-test="auto-complete-close-btn"
            @click="autoCompleteIsActive=false"
          >
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </div>
      </v-col>
    </v-row>
  </v-card>
</template>

<script lang="ts">
import { AutoCompleteResponse, AutoCompleteResult } from '@/models/AutoComplete'
import { Component, Prop, Vue, Watch } from 'vue-property-decorator'
import { Action } from 'pinia-class'
import { ORG_AUTO_COMPLETE_MAX_RESULTS_COUNT } from '@/util/constants'
import { useOrgStore } from '@/stores/org'

@Component({})
export default class OrgNameAutoComplete extends Vue {
    @Action(useOrgStore) public getOrgNameAutoComplete!:(searchValue: string) => Promise<AutoCompleteResponse>
    @Prop({ default: false }) private setAutoCompleteIsActive: boolean
    @Prop({ default: '' }) private searchValue: string

    autoCompleteResults: AutoCompleteResult[] = []
    autoCompleteSelectedIndex : number = -1
    autoCompleteIsActive: boolean = false

    get showAutoComplete () {
      return this.autoCompleteResults.length > 0 && this.autoCompleteIsActive
    }

    @Watch('searchValue')
    async GetAutoCompleteResults (val, oldVal) {
      if (oldVal !== val && this.autoCompleteIsActive) {
        await this.getAutoCompleteResults(val)
      }
    }

    @Watch('setAutoCompleteIsActive')
    async AutoCompleteIsActive (val: boolean) {
      this.autoCompleteIsActive = val
    }

    @Watch('autoCompleteIsActive')
    updateAutoCompleteIsActive (val: boolean) {
      if (!val) {
        this.autoCompleteResults = []
      }
    }

    @Watch('autoCompleteSelectedIndex')
    async emitSelectedValue (val: number) {
      if (val >= 0) {
        const searchValue = this.autoCompleteResults[val]?.value
        this.autoCompleteIsActive = false
        this.$emit('auto-complete-value', searchValue)
      }
    }

    private async getAutoCompleteResults (searchValue: string) {
      try {
        const response: AutoCompleteResponse = await this.getOrgNameAutoComplete(searchValue)
        if (searchValue === this.searchValue && response?.results) {
        // will slice results and show distinct results by value - similar to PPR
          const autoCompleteResponse = response?.results
          const key = 'value'
          this.autoCompleteResults = [...new Map(autoCompleteResponse.map(item =>
            [item[key], item])).values()].slice(0, ORG_AUTO_COMPLETE_MAX_RESULTS_COUNT)
        }
      } catch (ex) {
        // eslint-disable-next-line no-console
        console.log('Error while auto complete...')
      }
    }

    getIndexedTag (tag, index): string {
      return `${tag}-${index}`
    }
}
</script>

<style lang="scss" scoped>
@import '../../assets/scss/theme.scss';

.auto-complete-close-btn {
  color: $gray5 !important;
  background-color: transparent !important;
  position: absolute;
  right: 10px;
  top: 5px;
}
.auto-complete-item {
  min-height: 0;
}
.auto-complete-card {
  position: absolute;
  z-index: 3;
  width: 100%;
  top:64px;
}
.content{
  display: flex;
  justify-content: space-between;
  & .content-list{
    width: 100%;
  }
}
.close-btn-row {
  height: 1rem;
}
</style>
