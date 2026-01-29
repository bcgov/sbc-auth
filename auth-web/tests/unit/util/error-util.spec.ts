import { describe, expect, it } from 'vitest'
import { getErrorMessage, getErrorTitle, isErrorType, normalizeError } from '@/util/error-util'

describe('error-util', () => {
  describe('normalizeError', () => {
    it('extracts status and rootCause fields from gateway errors', () => {
      const error = {
        response: {
          status: 400,
          data: {
            errorMessage: 'Gateway error',
            rootCause: { type: 'SOME_ERROR', title: 'Title', detail: 'Detail' }
          }
        }
      }

      const normalized = normalizeError(error)

      expect(normalized.status).toBe(400)
      expect(normalized.type).toBe('SOME_ERROR')
      expect(normalized.title).toBe('Title')
      expect(normalized.detail).toBe('Detail')
      expect(normalized.errorMessage).toBe('Gateway error')
    })

    it('extracts fields from non-gateway errors', () => {
      const error = {
        response: {
          status: 409,
          data: { type: 'CONFLICT', code: 'ERR_001', message: 'Already exists' }
        }
      }

      const normalized = normalizeError(error)

      expect(normalized.status).toBe(409)
      expect(normalized.type).toBe('CONFLICT')
      expect(normalized.code).toBe('ERR_001')
      expect(normalized.message).toBe('Already exists')
    })

    it('handles errors without response data', () => {
      expect(normalizeError({ message: 'Network Error' }).message).toBe('Network Error')
      expect(normalizeError({}).message).toBe('An unexpected error occurred')
    })
  })

  describe('getErrorMessage', () => {
    it('returns detail > message > errorMessage > default', () => {
      expect(getErrorMessage({ detail: 'D', message: 'M' })).toBe('D')
      expect(getErrorMessage({ message: 'M', errorMessage: 'E' })).toBe('M')
      expect(getErrorMessage({ errorMessage: 'E' })).toBe('E')
      expect(getErrorMessage({})).toBe('An error occurred')
    })
  })

  describe('getErrorTitle', () => {
    it('returns title > message > default', () => {
      expect(getErrorTitle({ title: 'T', message: 'M' })).toBe('T')
      expect(getErrorTitle({ message: 'M' })).toBe('M')
      expect(getErrorTitle({})).toBe('Error')
    })
  })

  describe('isErrorType', () => {
    it('matches by type or code', () => {
      expect(isErrorType({ type: 'ERR' }, 'ERR')).toBe(true)
      expect(isErrorType({ code: 'ERR' }, 'ERR')).toBe(true)
      expect(isErrorType({ type: 'ERR' }, 'OTHER')).toBe(false)
      expect(isErrorType({}, 'ERR')).toBe(false)
    })
  })
})
