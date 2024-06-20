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

const getNumberOfItemsFromSessionStorage = (key: SessionStorageKeys): number | undefined => {
  const items = +ConfigHelper.getFromSession(key)
  return !isNaN(items) ? items : undefined
}

export const numberOfItems = (key: SessionStorageKeys): number => {
  return getNumberOfItemsFromSessionStorage(key) || DEFAULT_ITEMS_PER_PAGE
}

export const saveItemsPerPage = (val: number, key: SessionStorageKeys): void => {
  ConfigHelper.addToSession(key, val)
}

export const cachePageInfo = (tableDataOptions: Partial<DataOptions>, key: SessionStorageKeys): void => {
  ConfigHelper.addToSession(key, JSON.stringify(tableDataOptions))
}

export const hasCachedPageInfo = (key: SessionStorageKeys): boolean => {
  const paginationOptions = JSON.parse(ConfigHelper.getFromSession(key) || '{}')
  return Object.keys(paginationOptions).length !== 0
}

export const getAndPruneCachedPageInfo = (key: SessionStorageKeys): Partial<DataOptions> | undefined => {
  const paginationOptions = JSON.parse(ConfigHelper.getFromSession(key) || '{}')
  if (Object.keys(paginationOptions).length !== 0) {
    return paginationOptions
  }
  return undefined
}

export const getPaginationOptions = (): number[] => {
  return [...Array(PAGINATION_COUNTER_STEP)].map((_, index) => DEFAULT_ITEMS_PER_PAGE * (index + 1))
}
