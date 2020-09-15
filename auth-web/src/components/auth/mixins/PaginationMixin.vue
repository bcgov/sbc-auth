// You can declare a mixin as the same style as components.
<script lang="ts">
import Component from 'vue-class-component'
import ConfigHelper from '@/util/config-helper'
import { DataOptions } from 'vuetify'
import { SessionStorageKeys } from '@/util/constants'
import Vue from 'vue'

@Component({
})
export default class PaginationMixin extends Vue {
  protected readonly ITEMS_PER_PAGE = 10
  protected readonly PAGINATION_COUNTER_STEP = 4

  DEFAULT_DATA_OPTIONS:DataOptions = {
    page: 1,
    itemsPerPage: this.ITEMS_PER_PAGE,
    sortBy: [],
    sortDesc: [],
    groupBy: [],
    groupDesc: [],
    multiSort: false,
    mustSort: false
  }

  cachePageInfo (tableDataOptions: Partial<DataOptions>) {
    ConfigHelper.addToSession(SessionStorageKeys.PaginationOptions, JSON.stringify(tableDataOptions))
  }

  get hasCachedPageInfo ():boolean {
    const paginationOptions = JSON.parse(ConfigHelper.getFromSession(SessionStorageKeys.PaginationOptions) || '{}')
    return Object.keys(paginationOptions).length !== 0
  }

  getAndPruneCachedPageInfo ():Partial<DataOptions> |undefined {
    const paginationOptions = JSON.parse(sessionStorage.getItem('pagination_options') || '{}')
    if (Object.keys(paginationOptions).length !== 0) {
      // not ideal; but okay to do as long as signature conveys it
      ConfigHelper.removeFromSession(SessionStorageKeys.PaginationOptions)
      return paginationOptions
    } else {
      return undefined
    }
  }

  protected get getPaginationOptions () {
    return [...Array(this.PAGINATION_COUNTER_STEP)].map((value, index) => this.ITEMS_PER_PAGE * (index + 1))
  }

  private customSort (items, index, isDescending) {
    const isDesc = isDescending.length > 0 && isDescending[0]
    items.sort((a, b) => {
      if (isDesc) {
        return a[index[0]] < b[index[0]] ? -1 : 1
      } else {
        return b[index[0]] < a[index[0]] ? -1 : 1
      }
    })
    return items
  }
}
</script>
