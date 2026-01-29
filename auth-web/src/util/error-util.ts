export interface NormalizedError {
  status?: number
  type?: string
  code?: string
  title?: string
  detail?: string
  message?: string
  errorMessage?: string
}

export function normalizeError (error: any): NormalizedError {
  const status = error?.response?.status
  const data = error?.response?.data

  if (!data) {
    return { status, message: error?.message || 'An unexpected error occurred' }
  }

  const source = data.rootCause && typeof data.rootCause !== 'string' ? data.rootCause : data

  return {
    status,
    type: source.type,
    code: source.code,
    title: source.title || data.message?.title || data.title,
    detail: source.detail || data.message?.detail || data.detail,
    message: typeof data.rootCause === 'string'
      ? data.rootCause
      : source.message || (typeof data.message === 'string' ? data.message : undefined),
    errorMessage: data.rootCause ? data.errorMessage : undefined
  }
}

export function getErrorMessage (normalizedError: NormalizedError): string {
  return normalizedError.detail ||
         normalizedError.message ||
         normalizedError.errorMessage ||
         'An error occurred'
}

export function getErrorTitle (normalizedError: NormalizedError): string {
  return normalizedError.title ||
         normalizedError.message ||
         'Error'
}

export function isErrorType (normalizedError: NormalizedError, ...types: string[]): boolean {
  return !!(normalizedError?.type && types.includes(normalizedError.type)) ||
         !!(normalizedError?.code && types.includes(normalizedError.code))
}
