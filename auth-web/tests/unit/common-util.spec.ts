import CommonUtil from '@/util/common-util'

describe('Common Util Test', () => {
  it('Test isUrl works', () => {
    expect(CommonUtil.isUrl('abcd')).toBe(false)
    expect(CommonUtil.isUrl('http://localhost:8000')).toBe(true)
    expect(CommonUtil.isUrl('https://localhost:8000')).toBe(true)
    expect(CommonUtil.isUrl('localhost:8080')).toBe(false)
  })
})
