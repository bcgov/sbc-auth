// To handle Von autocomplete responses
export interface AutoCompleteResponse {
    total: number,
    results: Array<AutoCompleteResult>
}

export interface AutoCompleteResult {
    type: string
    value: string
    score: number
}
