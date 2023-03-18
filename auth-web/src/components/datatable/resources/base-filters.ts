export const BaseTextFilter = (colVal: string, filterVal: string) => {
  return colVal.toUpperCase().includes(filterVal.toUpperCase())
}

export const BaseSelectFilter = (colVal: string, filterVal: string) => {
  if (filterVal) return colVal.toUpperCase() === filterVal.toUpperCase()
  return true
}
