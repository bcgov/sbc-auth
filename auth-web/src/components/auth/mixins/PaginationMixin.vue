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
  protected readonly DEFAULT_ITEMS_PER_PAGE = 5
  protected readonly PAGINATION_COUNTER_STEP = 4

  DEFAULT_DATA_OPTIONS:DataOptions = {
    page: 1,
    itemsPerPage: this.numberOfItems,
    sortBy: [],
    sortDesc: [],
    groupBy: [],
    groupDesc: [],
    multiSort: false,
    mustSort: false
  }

  /**
   * returns the number of items for the paginator.
   * IF there is a value which user chosen, it takes preference
   */
  get numberOfItems () {
    return this.getNumberOfItemsFromSessionStorage() || this.DEFAULT_ITEMS_PER_PAGE
  }

  protected getNumberOfItemsFromSessionStorage (): number|undefined {
    let items = +ConfigHelper.getFromSession(SessionStorageKeys.PaginationNumberOfItems)
    return !isNaN(items) ? items : undefined
  }

  saveItemsPerPage (val) {
    ConfigHelper.addToSession(SessionStorageKeys.PaginationNumberOfItems, val)
  }

  cachePageInfo (tableDataOptions: Partial<DataOptions>) {
    ConfigHelper.addToSession(SessionStorageKeys.PaginationOptions, JSON.stringify(tableDataOptions))
  }

  /**
   * Helps to retain the current page information when the user went to detailed page and pressed refresh.
   */
  get hasCachedPageInfo ():boolean {
    const paginationOptions = JSON.parse(ConfigHelper.getFromSession(SessionStorageKeys.PaginationOptions) || '{}')
    return Object.keys(paginationOptions).length !== 0
  }

  /**
   * Helps to retain the current page information when the user went to detailed page and pressed refresh.
   */
  protected cachedPageInfo ():boolean {
    const paginationOptions = JSON.parse(ConfigHelper.getFromSession(SessionStorageKeys.PaginationOptions) || '{}')
    return Object.keys(paginationOptions).length !== 0
  }

  /**
   * Return the pagination option.
   * Removes from session storage ; b
   *    because the information should be used only once when user comes back from detail page to list view.
   */
  getAndPruneCachedPageInfo ():Partial<DataOptions> |undefined {
    const paginationOptions = JSON.parse(ConfigHelper.getFromSession(SessionStorageKeys.PaginationOptions) || '{}')
    if (Object.keys(paginationOptions).length !== 0) {
      // not ideal; but okay to do as long as signature conveys it
      ConfigHelper.removeFromSession(SessionStorageKeys.PaginationOptions)
      return paginationOptions
    } else {
      return undefined
    }
  }

  protected get getPaginationOptions () {
    return [...Array(this.PAGINATION_COUNTER_STEP)].map((value, index) => this.DEFAULT_ITEMS_PER_PAGE * (index + 1))
  }
}
</script>
