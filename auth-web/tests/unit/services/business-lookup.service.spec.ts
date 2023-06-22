import BusinessLookupServices from '@/services/business-lookup.services'
import { axios } from '@/util/http-util'
import sinon from 'sinon'

const BUSINESS_SEARCH_URL = 'https://bcregistry-dev.apigee.net/registry-search/api/v1/'

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

    // mock successsful search
    const args = `${BUSINESS_SEARCH_URL}businesses/search/facets?start=0&rows=20&categories=legalType:` +
      `BC,A,ULC,C,S,XP,GP,LP,CUL,XS,LLC,LL,BEN,CP,CC,XL,FI,XCP,PA&query=value:FM1000002`
    sinon.stub(axios, 'get').withArgs(args).returns(
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
    const args = `${BUSINESS_SEARCH_URL}businesses/search/facets?start=0&rows=20&categories=legalType` +
      `:BC,A,ULC,C,S,XP,GP,LP,CUL,XS,LLC,LL,BEN,CP,CC,XL,FI,XCP,PA&query=value:FM1000003`
    sinon.stub(axios, 'get').withArgs(args).returns(
      Promise.resolve({ data: { searchResults: { results: [] } } })
    )

    // search and look at results
    const results = await BusinessLookupServices.search('FM1000003')
    expect(results.length).toBe(0)

    sinon.restore()
  })
})
