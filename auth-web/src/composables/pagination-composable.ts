import { computed, ref } from 'vue'
import ConfigHelper from '@/util/config-helper'
import { DataOptions } from 'vuetify'
import { SessionStorageKeys } from '@/util/constants'

export default function usePagination () {
  const DEFAULT_ITEMS_PER_PAGE = 5
  const PAGINATION_COUNTER_STEP = 4

  const numberOfItems = ref(getNumberOfItemsFromSessionStorage() || DEFAULT_ITEMS_PER_PAGE)

  function getNumberOfItemsFromSessionStorage (): number | undefined {
    const items = +ConfigHelper.getFromSession(SessionStorageKeys.PaginationNumberOfItems)
    return !isNaN(items) ? items : undefined
  }

  function saveItemsPerPage (val: number) {
    ConfigHelper.addToSession(SessionStorageKeys.PaginationNumberOfItems, val.toString())
  }

  function cachePageInfo (tableDataOptions: Partial<DataOptions>) {
    ConfigHelper.addToSession(SessionStorageKeys.PaginationOptions, JSON.stringify(tableDataOptions))
  }

  const hasCachedPageInfo = computed((): boolean => {
    const paginationOptions = JSON.parse(ConfigHelper.getFromSession(SessionStorageKeys.PaginationOptions) || '{}')
    return Object.keys(paginationOptions).length !== 0
  })

  function getAndPruneCachedPageInfo (): Partial<DataOptions> | undefined {
    const paginationOptions = JSON.parse(ConfigHelper.getFromSession(SessionStorageKeys.PaginationOptions) || '{}')
    if (Object.keys(paginationOptions).length !== 0) {
      ConfigHelper.removeFromSession(SessionStorageKeys.PaginationOptions)
      return paginationOptions
    }
    return undefined
  }

  const getPaginationOptions = computed(() =>
    Array.from({ length: PAGINATION_COUNTER_STEP }, (_, index) => DEFAULT_ITEMS_PER_PAGE * (index + 1))
  )

  return {
    numberOfItems,
    saveItemsPerPage,
    cachePageInfo,
    hasCachedPageInfo,
    getAndPruneCachedPageInfo,
    getPaginationOptions
  }
}
