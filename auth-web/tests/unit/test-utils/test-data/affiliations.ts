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
  // Amalgamation Application
  {
    businessIdentifier: 'TC6weERhbH',
    corpType: {
      code: CorpTypes.AMALGAMATION
    },
    corpSubType: {
      code: CorpTypes.BENEFIT_COMPANY
    }
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

export const moreBusinesses: Business[] = [
  // BEN Name Request - Processing
  {
    businessIdentifier: 'NR 4045460',
    corpType: { code: CorpTypes.NAME_REQUEST },
    name: 'BEN NAME REQUEST - PROCESSING',
    nameRequest: {
      legalType: CorpTypes.BENEFIT_COMPANY,
      names: [{
        name: 'BEN NAME REQUEST - PROCESSING',
        decision_text: 'Decision text',
        name_type_cd: 'Name type code',
        designation: 'Designation',
        state: 'State'
      }],
      nrNumber: 'NR 4045460',
      state: 'PROCESSING',
      expirationDate: null,
      requestActionCd: 'CHG',
      corpNum: 'CorpNum'
    },
    status: 'PROCESSING'
  },
  // BEN Name Request - Pending Staff Review
  {
    businessIdentifier: 'NR 4045461',
    corpType: { code: CorpTypes.NAME_REQUEST },
    name: 'BEN NAME REQUEST - PENDING',
    nameRequest: {
      legalType: CorpTypes.BENEFIT_COMPANY,
      names: [{
        name: 'BEN NAME REQUEST - PENDING',
        decision_text: 'Decision text',
        name_type_cd: 'Name type code',
        designation: 'Designation',
        state: 'State'
      }],
      nrNumber: 'NR 4045461',
      state: 'DRAFT',
      expirationDate: null,
      requestActionCd: 'CHG',
      corpNum: 'corpNum'
    },
    status: 'DRAFT'
  },
  // BEN Name Request - Expired
  {
    businessIdentifier: 'NR 4045462',
    corpType: { code: CorpTypes.NAME_REQUEST },
    name: 'BEN NAME REQUEST - EXPIRED',
    nameRequest: {
      legalType: CorpTypes.BENEFIT_COMPANY,
      names: [{
        name: 'BEN NAME REQUEST - EXPIRED',
        decision_text: 'Decision text',
        name_type_cd: 'Name type code',
        designation: 'Designation',
        state: 'State'
      }],
      nrNumber: 'NR 4045462',
      state: 'EXPIRED',
      expirationDate: null,
      requestActionCd: 'CHG',
      corpNum: 'corpNum'
    },
    status: 'EXPIRED'
  },
  // BEN Name Request - Rejected
  {
    businessIdentifier: 'NR 4045463',
    corpType: { code: CorpTypes.NAME_REQUEST },
    name: 'BEN NAME REQUEST - REJECTED',
    nameRequest: {
      legalType: CorpTypes.BENEFIT_COMPANY,
      names: [{
        name: 'BEN NAME REQUEST - REJECTED',
        decision_text: 'Decision text',
        name_type_cd: 'Name type code',
        designation: 'Designation',
        state: 'State'
      }],
      nrNumber: 'NR 4045463',
      state: 'REJECTED',
      expirationDate: null,
      requestActionCd: 'CHG',
      corpNum: 'corpNum'
    },
    status: 'REJECTED'
  },
  // BEN Name Request - Consumed
  {
    businessIdentifier: 'NR 4045464',
    corpType: { code: CorpTypes.NAME_REQUEST },
    name: 'BEN NAME REQUEST - CONSUMED',
    nameRequest: {
      legalType: CorpTypes.BENEFIT_COMPANY,
      names: [{
        name: 'BEN NAME REQUEST - CONSUMED',
        decision_text: 'Decision text',
        name_type_cd: 'Name type code',
        designation: 'Designation',
        state: 'State'
      }],
      nrNumber: 'NR 4045464',
      state: 'CONSUMED',
      expirationDate: null,
      requestActionCd: 'CHG',
      corpNum: 'corpNum'
    },
    status: 'CONSUMED'
  },
  // BEN Name Request - Approved, Incorporation
  {
    businessIdentifier: 'NR 4045465',
    corpType: { code: CorpTypes.NAME_REQUEST },
    name: 'BEN NR INCORPORATION - APPROVED',
    nameRequest: {
      legalType: CorpTypes.BENEFIT_COMPANY,
      names: [{
        name: 'BEN NR INCORPORATION - APPROVED',
        decision_text: 'Decision text',
        name_type_cd: 'Name type code',
        designation: 'Designation',
        state: 'State'
      }],
      nrNumber: 'NR 4045465',
      state: 'APPROVED',
      expirationDate: new Date('2022-11-22T19:42:13+00:00'),
      requestActionCd: 'NEW',
      corpNum: 'corpNum'
    },
    status: 'APPROVED'
  },
  // LP Name Request - Approved, Incorporation
  {
    businessIdentifier: 'NR 4045466',
    corpType: { code: CorpTypes.NAME_REQUEST },
    name: 'LP NR INCORPORATION - APPROVED',
    nameRequest: {
      legalType: CorpTypes.LIM_PARTNERSHIP,
      names: [{
        name: 'LP NR INCORPORATION - APPROVED',
        decision_text: 'Decision text',
        name_type_cd: 'Name type code',
        designation: 'Designation',
        state: 'State'
      }],
      nrNumber: 'NR 4045466',
      state: 'APPROVED',
      expirationDate: new Date('2022-11-22T19:42:13+00:00'),
      requestActionCd: 'NEW',
      corpNum: 'corpNum'
    },
    status: 'APPROVED'
  },
  // FI Name Request - Approved, Incorporation
  {
    businessIdentifier: 'NR 4045467',
    corpType: { code: CorpTypes.NAME_REQUEST },
    name: 'FI NR INCORPORATION - APPROVED',
    nameRequest: {
      legalType: CorpTypes.FINANCIAL,
      names: [{
        name: 'FI NR INCORPORATION - APPROVED',
        decision_text: 'Decision text',
        name_type_cd: 'Name type code',
        designation: 'Designation',
        state: 'State'
      }],
      nrNumber: 'NR 4045467',
      state: 'APPROVED',
      expirationDate: new Date('2022-11-22T19:42:13+00:00'),
      requestActionCd: 'NEW',
      corpNum: 'corpNum'
    },
    status: 'APPROVED'
  },
  // BEN Name Request - Approved, Amalgamate
  {
    businessIdentifier: 'NR 4045468',
    corpType: { code: CorpTypes.NAME_REQUEST },
    name: 'BEN NR AMALGAMATE - APPROVED',
    nameRequest: {
      legalType: CorpTypes.BENEFIT_COMPANY,
      names: [{
        name: 'BEN NR AMALGAMATE - APPROVED',
        decision_text: 'Decision text',
        name_type_cd: 'Name type code',
        designation: 'Designation',
        state: 'State'
      }],
      nrNumber: 'NR 4045468',
      state: 'APPROVED',
      expirationDate: new Date('2022-11-22T19:42:13+00:00'),
      requestActionCd: 'AML',
      corpNum: 'corpNum'
    },
    status: 'APPROVED'
  },
  // BEN Name Request - Approved, Continue into
  {
    businessIdentifier: 'NR 4045469',
    corpType: { code: CorpTypes.NAME_REQUEST },
    name: 'BEN NR CONTINUE IN - APPROVED',
    nameRequest: {
      legalType: CorpTypes.BENEFIT_COMPANY,
      names: [{
        name: 'BEN NR CONTINUE IN - APPROVED',
        decision_text: 'Decision text',
        name_type_cd: 'Name type code',
        designation: 'Designation',
        state: 'State'
      }],
      nrNumber: 'NR 4045469',
      state: 'APPROVED',
      expirationDate: new Date('2022-11-22T19:42:13+00:00'),
      requestActionCd: 'MVE',
      corpNum: 'corpNum'
    },
    status: 'APPROVED'
  },
  // BEN Name Request - Approved, Restore
  {
    businessIdentifier: 'NR 4045470',
    corpType: { code: CorpTypes.NAME_REQUEST },
    name: 'BEN NR RESTORE - APPROVED',
    nameRequest: {
      legalType: CorpTypes.BENEFIT_COMPANY,
      names: [{
        name: 'BEN NR RESTORE - APPROVED',
        decision_text: 'Decision text',
        name_type_cd: 'Name type code',
        designation: 'Designation',
        state: 'State'
      }],
      nrNumber: 'NR 4045470',
      state: 'APPROVED',
      expirationDate: new Date('2022-11-22T19:42:13+00:00'),
      requestActionCd: 'REH',
      corpNum: 'corpNum'
    },
    status: 'APPROVED'
  },
  // XL Name Request - Approved, Reinstate
  {
    businessIdentifier: 'NR 4045471',
    corpType: { code: CorpTypes.NAME_REQUEST },
    name: 'XL NR REINSTATE - APPROVED',
    nameRequest: {
      legalType: CorpTypes.XPRO_LL_PARTNR,
      names: [{
        name: 'XL NR REINSTATE - APPROVED',
        decision_text: 'Decision text',
        name_type_cd: 'Name type code',
        designation: 'Designation',
        state: 'State'
      }],
      nrNumber: 'NR 4045471',
      state: 'APPROVED',
      expirationDate: new Date('2022-11-22T19:42:13+00:00'),
      requestActionCd: 'REH',
      corpNum: 'corpNum'
    },
    status: 'APPROVED'
  },
  // // BEN Name Request - Approved, Change Name
  {
    businessIdentifier: 'NR 4045472',
    corpType: { code: CorpTypes.NAME_REQUEST },
    name: 'BEN NR CHG NAME - APPROVED',
    nameRequest: {
      legalType: CorpTypes.BENEFIT_COMPANY,
      names: [{
        name: 'BEN NR CHG NAME - APPROVED',
        decision_text: 'Decision text',
        name_type_cd: 'Name type code',
        designation: 'Designation',
        state: 'State'
      }],
      nrNumber: 'NR 4045472',
      state: 'APPROVED',
      expirationDate: new Date('2022-11-22T19:42:13+00:00'),
      requestActionCd: 'CHG',
      corpNum: 'corpNum'
    },
    status: 'APPROVED'
  },
  // // BEN Name Request - Approved, Alter
  {
    businessIdentifier: 'NR 4045473',
    corpType: { code: CorpTypes.NAME_REQUEST },
    name: 'BEN NR ALTER - APPROVED',
    nameRequest: {
      legalType: CorpTypes.BENEFIT_COMPANY,
      names: [{
        name: 'BEN NR ALTER - APPROVED',
        decision_text: 'Decision text',
        name_type_cd: 'Name type code',
        designation: 'Designation',
        state: 'State'
      }],
      nrNumber: 'NR 4045473',
      state: 'APPROVED',
      expirationDate: new Date('2022-11-22T19:42:13+00:00'),
      requestActionCd: 'CNV',
      corpNum: 'corpNum'
    },
    status: 'APPROVED'
  },
  // // BEN Business - Active
  {
    adminFreeze: false,
    goodStanding: true,
    businessIdentifier: 'business identifier',
    corpType: {
      code: CorpTypes.BENEFIT_COMPANY
    },
    corpSubType: {
      code: CorpTypes.BENEFIT_COMPANY
    }
  },
  // // FI Business - Active
  {
    adminFreeze: false,
    goodStanding: true,
    businessIdentifier: 'business identifier',
    corpType: {
      code: CorpTypes.FINANCIAL
    },
    corpSubType: {
      code: CorpTypes.FINANCIAL
    }
  },
  // // BEN Incorporation Application
  {
    businessIdentifier: 'TCkK0ArEiL',
    corpType: {
      code: CorpTypes.INCORPORATION_APPLICATION
    },
    corpSubType: {
      code: CorpTypes.BENEFIT_COMPANY
    }
  },
  // // SP Registration
  {
    businessIdentifier: 'ToyBWY9chJ',
    corpType: { code: CorpTypes.REGISTRATION },
    nameRequest: {
      entityTypeCd: 'SP',
      expirationDate: new Date('2022-07-20T06:59:00+00:00'),
      id: 2264498,
      legalType: CorpTypes.SOLE_PROP,
      names: [
        {
          name: 'SP REGISTRATION',
          decision_text: 'Decision text',
          name_type_cd: 'Name type code',
          designation: 'Designation',
          state: 'APPROVED'
        }
      ],
      nrNumber: 'NR 1234567',
      state: 'APPROVED',
      target: NrTargetTypes.LEAR,
      requestActionCd: 'NEW',
      corpNum: 'corpNum'
    },
    nrNumber: 'NR 1234567'
  },
  // BEN Name Request - Cancelled
  {
    businessIdentifier: 'NR 4045474',
    corpType: { code: CorpTypes.NAME_REQUEST },
    name: 'BEN NAME REQUEST - CANCELLED',
    nameRequest: {
      legalType: CorpTypes.BENEFIT_COMPANY,
      names: [{
        name: 'BEN NAME REQUEST - CANCELLED',
        decision_text: 'Decision text',
        name_type_cd: 'Name type code',
        designation: 'Designation',
        state: 'State'
      }],
      nrNumber: 'NR 4045474',
      state: 'CANCELLED',
      expirationDate: null,
      requestActionCd: 'CHG',
      corpNum: 'corpNum'
    },
    status: 'CANCELLED'
  },
  // BEN Name Request - Cancelled, Refund Requested
  {
    businessIdentifier: 'NR 4045475',
    corpType: { code: CorpTypes.NAME_REQUEST },
    name: 'BEN NAME REQUEST - CANCELLED, REFUND',
    nameRequest: {
      legalType: CorpTypes.BENEFIT_COMPANY,
      names: [{
        name: 'BEN NAME REQUEST - CANCELLED, REFUND',
        decision_text: 'Decision text',
        name_type_cd: 'Name type code',
        designation: 'Designation',
        state: 'State'
      }],
      nrNumber: 'NR 4045475',
      state: 'REFUND_REQUESTED',
      expirationDate: null,
      requestActionCd: 'CHG',
      corpNum: 'corpNum'
    },
    status: 'REFUND_REQUESTED'
  },
  // LLP Name Request - Approved, Incorporation
  {
    businessIdentifier: 'NR 4045466',
    corpType: { code: CorpTypes.NAME_REQUEST },
    name: 'LLP NR INCORPORATION - APPROVED',
    nameRequest: {
      legalType: CorpTypes.LL_PARTNERSHIP,
      names: [{
        name: 'LLP NR INCORPORATION - APPROVED',
        decision_text: 'Decision text',
        name_type_cd: 'Name type code',
        designation: 'Designation',
        state: 'State'
      }],
      nrNumber: 'NR 4045476',
      state: 'APPROVED',
      expirationDate: new Date('2022-11-22T19:42:13+00:00'),
      requestActionCd: 'NEW',
      corpNum: 'corpNum'
    },
    status: 'APPROVED'
  },
  // XLP Name Request - Approved, Incorporation
  {
    businessIdentifier: 'NR 4045466',
    corpType: { code: CorpTypes.NAME_REQUEST },
    name: 'XLP NR INCORPORATION - APPROVED',
    nameRequest: {
      legalType: CorpTypes.XPRO_LIM_PARTNR,
      names: [{
        name: 'XLP NR INCORPORATION - APPROVED',
        decision_text: 'Decision text',
        name_type_cd: 'Name type code',
        designation: 'Designation',
        state: 'State'
      }],
      nrNumber: 'NR 4045477',
      state: 'APPROVED',
      expirationDate: new Date('2022-11-22T19:42:13+00:00'),
      requestActionCd: 'NEW',
      corpNum: 'corpNum'
    },
    status: 'APPROVED'
  }
]

export const actions = [
  {
    'primary': 'Open Name Request',
    'secondary': ['Remove From Table'],
    'external': false
  },
  {
    'primary': 'Open Name Request',
    'secondary': ['Remove From Table'],
    'external': false
  },
  {
    'primary': 'Open Name Request',
    'secondary': ['Remove From Table'],
    'external': false
  },
  {
    'primary': 'Remove From Table',
    'secondary': ['Open Name Request'],
    'external': false
  },
  {
    'primary': 'Remove From Table',
    'secondary': ['Open Name Request'],
    'external': false
  },
  {
    'primary': 'Register Now',
    'secondary': ['Open Name Request', 'Remove From Table'],
    'external': false
  },
  {
    'primary': 'Download Form',
    'secondary': ['Open Name Request', 'Remove From Table'],
    'external': true
  },
  {
    'primary': 'Download Form',
    'secondary': ['Open Name Request', 'Remove From Table'],
    'external': true
  },
  {
    'primary': 'Amalgamate Now',
    'secondary': ['Open Name Request', 'Remove From Table'],
    'external': true
  },
  {
    'primary': 'Continue In Now',
    'secondary': ['Open Name Request', 'Remove From Table'],
    'external': true
  },
  {
    'primary': 'Restore Now',
    'secondary': ['Open Name Request', 'Remove From Table'],
    'external': false
  },
  {
    'primary': 'Reinstate Now',
    'secondary': ['Open Name Request', 'Remove From Table'],
    'external': true
  },
  {
    'primary': 'Change Name Now',
    'secondary': ['Open Name Request', 'Remove From Table'],
    'external': false
  },
  {
    'primary': 'Alter Now',
    'secondary': ['Open Name Request', 'Remove From Table'],
    'external': false
  },
  {
    'primary': 'Manage Business',
    'secondary': ['Remove From Table'],
    'external': false
  },
  {
    'primary': 'Manage Business',
    'secondary': ['Remove From Table'],
    'external': true
  },
  {
    'primary': 'Resume Draft',
    'secondary': ['Delete Incorporation Application'],
    'external': false
  },
  {
    'primary': 'Resume Draft',
    'secondary': ['Delete Registration'],
    'external': false
  },
  {
    'primary': 'Remove From Table',
    'secondary': ['Open Name Request'],
    'external': false
  },
  {
    'primary': 'Remove From Table',
    'secondary': ['Open Name Request'],
    'external': false
  },
  {
    'primary': 'Download Form',
    'secondary': ['Open Name Request', 'Remove From Table'],
    'external': true
  },
  {
    'primary': 'Download Form',
    'secondary': ['Open Name Request', 'Remove From Table'],
    'external': true
  }
]
