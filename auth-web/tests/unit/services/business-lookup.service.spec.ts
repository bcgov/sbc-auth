import BusinessLookupServices from '@/services/business-lookup.services'
import { axios } from '@/util/http-util'
import sinon from 'sinon'

describe('Business Lookup Services', () => {
  it('returns a result when the business is found', async () => {
    const result = {
      bn: '701819922',
      identifier: 'FM1000002',
      legalType: 'SP',
      name: 'KK CONSTRUCTION',
      score: 10.642771,
      status: 'ACTIVE'
    }

    const url = BusinessLookupServices.registriesSearchApiUrl + 'businesses/search/facets?start=0&rows=20' +
      '&categories=legalType:A,BC,BEN,C,CC,CP,CUL,FI,GP,LL,LLC,LP,PA,S,SP,ULC,XCP,XL,XP,XS' +
      `&query=value:${encodeURIComponent('FM1000002')}`

    sinon.stub(axios, 'get').withArgs(url).returns(
      Promise.resolve({ data: { searchResults: { results: [result] } } })
    )

    // search and look at results
    const results = await BusinessLookupServices.search('FM1000002')
    expect(results.length).toBe(1)
    expect(results[0]).toEqual(result)

    sinon.restore()
  })

  it('does not return a result when the business is not found', async () => {
    // mock unsuccesssful search
    const url = BusinessLookupServices.registriesSearchApiUrl + 'businesses/search/facets?start=0&rows=20' +
      '&categories=legalType:A,BC,BEN,C,CC,CP,CUL,FI,GP,LL,LLC,LP,PA,S,SP,ULC,XCP,XL,XP,XS' +
      `&query=value:${encodeURIComponent('FM1000003')}`

    sinon.stub(axios, 'get').withArgs(url).returns(
      Promise.resolve({ data: { searchResults: { results: [] } } })
    )

    const results = await BusinessLookupServices.search('FM1000003')
    expect(results.length).toBe(0)

    sinon.restore()
  })
})
