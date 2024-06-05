import ConfigHelper from '@/util/config-helper'
import { DataOptions } from 'vuetify'
import { SessionStorageKeys } from '@/util/constants'

export const DEFAULT_ITEMS_PER_PAGE = 5
export const PAGINATION_COUNTER_STEP = 4

export const DEFAULT_DATA_OPTIONS: DataOptions = {
  page: 1,
  itemsPerPage: DEFAULT_ITEMS_PER_PAGE,
  sortBy: [],
  sortDesc: [],
  groupBy: [],
  groupDesc: [],
  multiSort: false,
  mustSort: false
}

const getNumberOfItemsFromSessionStorage = (): number | undefined => {
  const items = +ConfigHelper.getFromSession(SessionStorageKeys.PaginationNumberOfItems)
  return !isNaN(items) ? items : undefined
}

export const numberOfItems = (): number => {
  return getNumberOfItemsFromSessionStorage() || DEFAULT_ITEMS_PER_PAGE
}

export const saveItemsPerPage = (val: number): void => {
  ConfigHelper.addToSession(SessionStorageKeys.PaginationNumberOfItems, val)
}

export const cachePageInfo = (tableDataOptions: Partial<DataOptions>): void => {
  ConfigHelper.addToSession(SessionStorageKeys.PaginationOptions, JSON.stringify(tableDataOptions))
}

export const hasCachedPageInfo = (): boolean => {
  const paginationOptions = JSON.parse(ConfigHelper.getFromSession(SessionStorageKeys.PaginationOptions) || '{}')
  return Object.keys(paginationOptions).length !== 0
}

export const getAndPruneCachedPageInfo = (): Partial<DataOptions> | undefined => {
  const paginationOptions = JSON.parse(ConfigHelper.getFromSession(SessionStorageKeys.PaginationOptions) || '{}')
  if (Object.keys(paginationOptions).length !== 0) {
    ConfigHelper.removeFromSession(SessionStorageKeys.PaginationOptions)
    return paginationOptions
  }
  return undefined
}

export const getPaginationOptions = (): number[] => {
  return [...Array(PAGINATION_COUNTER_STEP)].map((_, index) => DEFAULT_ITEMS_PER_PAGE * (index + 1))
}
