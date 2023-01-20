export interface BaseTableFilterI {
  clearable: boolean
  items?: { text: string, value: any }[]
  filterApiFn?: (val: string) => Promise<void>
  filterFn?: (colVal: any, filterVal: string) => boolean
  label?: string
  type: 'select' | 'text'
  value: string
}

export interface BaseTableHeaderI {
  class?: string  // must be accessible in base table (i.e. large-cell pt-3)
  col: string  // item value
  customFilter?: BaseTableFilterI
  hasFilter: boolean
  itemClass?: string
  itemFn?: (val: any) => string
  minWidth?: string // 150px
  value: string  // display text (v-html)
  width?: string
}
