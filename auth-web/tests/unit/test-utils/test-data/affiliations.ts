import { CorpTypes, NrTargetTypes } from '@/util/constants'
import { Business } from '@/models/business'
import moment from 'moment'

export const businesses: Business[] = [
  // BEN Name Request - Processing
  {
    businessIdentifier: 'NR 4045467',
    corpType: { code: CorpTypes.NAME_REQUEST },
    name: 'BEN NAME REQUEST LIMITED - PROCESSING',
    nameRequest: {
      legalType: CorpTypes.BENEFIT_COMPANY,
      names: [{
        name: 'BEN NAME REQUEST LIMITED - PROCESSING',
        decision_text: 'Decision text',
        name_type_cd: 'Name type code',
        designation: 'Designation',
        state: 'State'
      }],
      nrNumber: 'NR 4045467',
      state: 'Processing',
      expirationDate: null
    },
    status: 'Processing'
  },
  // BEN Name Request
  {
    businessIdentifier: undefined,
    nrNumber: 'NR 4045466',
    corpType: { code: CorpTypes.NAME_REQUEST },
    name: 'BEN NAME REQUEST LIMITED',
    nameRequest: {
      legalType: CorpTypes.BENEFIT_COMPANY,
      names:
      [{
        name: 'BEN NAME REQUEST LIMITED',
        decision_text: 'Decision text',
        name_type_cd: 'Name type code',
        designation: 'Designation',
        state: 'State'
      }],
      nrNumber: 'NR 4045466',
      state: 'APPROVED',
      expirationDate: moment.utc('2022-11-02T19:42:13+00:00').toDate()
    },
    status: 'APPROVED'
  },
  // BEN Name Request DRAFT with expiration date
  {
    businessIdentifier: undefined,
    corpType: {
      code: CorpTypes.NAME_REQUEST
    },
    nameRequest: {
      legalType: CorpTypes.BENEFIT_COMPANY,
      names:
      [{
        name: 'BEN NAME REQUEST LIMITED',
        decision_text: 'Decision text',
        name_type_cd: 'Name type code',
        designation: 'Designation',
        state: 'State'
      }],
      nrNumber: 'NR 4045468',
      state: 'DRAFT',
      expirationDate: new Date('2022-11-22T19:42:13+00:00')
    },
    status: 'DRAFT'
  },
  // BEN Incorporation Application (numbered)
  {
    businessIdentifier: 'TIQcIs5qvA',
    corpType: {
      code: CorpTypes.REGISTRATION
    },
    corpSubType: {
      code: CorpTypes.BENEFIT_COMPANY
    }
  },
  // SP Registration
  {
    businessIdentifier: 'TKmp4A16B1',
    corpType: { code: CorpTypes.NAME_REQUEST },
    nameRequest: {
      entityTypeCd: 'FR',
      expirationDate: new Date('2022-07-20T06:59:00+00:00'),
      id: 2264498,
      legalType: CorpTypes.SOLE_PROP,
      names: [
        {
          name: 'AC SP 2022.MAY.25 15.38 TEST',
          decision_text: 'Decision text',
          name_type_cd: 'Name type code',
          designation: 'Designation',
          state: 'APPROVED'
        }
      ],
      natureBusinessInfo: 'asdf',
      nrNumber: 'NR 2821990',
      state: 'CONSUMED',
      target: NrTargetTypes.LEAR
    },
    nrNumber: 'NR 2821990'
  },
  // alert icons
  {
    adminFreeze: true,
    goodStanding: false,
    businessIdentifier: 'TIQcIs5sss',
    corpType: {
      code: CorpTypes.INCORPORATION_APPLICATION
    },
    corpSubType: {
      code: CorpTypes.BENEFIT_COMPANY
    }
  },
  {
    adminFreeze: false,
    goodStanding: true,
    businessIdentifier: 'BC0871095',
    name: '0871095 B.C. LTD.',
    corpType: { code: CorpTypes.BENEFIT_COMPANY },
    status: 'HISTORICAL'
  },
  // request access (invitations)
  // single
  {
    businessIdentifier: 'RequestAccessSingleTest111',
    corpType: { code: CorpTypes.BC_COMPANY },
    name: 'Request Access Single LTD.',
    status: 'ACTIVE',
    affiliationInvites: [
      {
        id: 11,
        type: 'RequestAccess',
        status: 'ACTIVE',
        business: {
          businessIdentifier: 'RequestAccessSingleTest111',
          name: 'Request Access Single LTD.',
          corpType: { code: CorpTypes.BC_COMPANY }
        },
        toOrg: { name: 'Org Z', id: 3113 },
        fromOrg: { name: 'Org B', id: 1114 }
      }
    ]
  },
  // request access (invitations)
  // multiple
  {
    businessIdentifier: 'RequestAccessMultiTest111',
    corpType: { code: CorpTypes.BC_COMPANY },
    name: 'Request Access Multi LTD.',
    status: 'ACTIVE',
    affiliationInvites: [
      {
        id: 12,
        type: 'RequestAccess',
        status: 'ACTIVE',
        business: {
          businessIdentifier: 'RequestAccessMultiTest111',
          name: 'Request Access Multi LTD.',
          corpType: { code: CorpTypes.BC_COMPANY }
        },
        toOrg: { name: 'Org Z', id: 3113 },
        fromOrg: { name: 'Org B', id: 1114 }
      },
      {
        id: 13,
        type: 'RequestAccess',
        status: 'ACTIVE',
        business: {
          businessIdentifier: 'RequestAccessMultiTest111',
          name: 'Request Access Multi LTD.',
          corpType: { code: CorpTypes.BC_COMPANY }
        },
        toOrg: { name: 'Org Z', id: 3113 },
        fromOrg: { name: 'Org C', id: 1112 }
      },
      {
        id: 14,
        type: 'RequestAccess',
        status: 'ACTIVE',
        business: {
          businessIdentifier: 'RequestAccessMultiTest111',
          name: 'Request Access Multi LTD.',
          corpType: { code: CorpTypes.BC_COMPANY }
        },
        toOrg: { name: 'Org Z', id: 3113 },
        fromOrg: { name: 'Org D', id: 1111 }
      }
    ]
  }
]
