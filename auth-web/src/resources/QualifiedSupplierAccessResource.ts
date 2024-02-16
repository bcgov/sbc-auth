import { QualifiedSupplierRequirementsConfig } from '@/models/external'
import { TaskType } from '@/util/constants'

export const userAccessRequirements: Partial<Record<TaskType, QualifiedSupplierRequirementsConfig[]>> = {
  [TaskType.MHR_LAWYER_NOTARY]: [
    {
      boldText: `An active B.C. lawyer or notary in good standing will be on this account.`,
      regularText: `I understand that only a lawyer or notary, or someone who is being supervised by a lawyer or notary,
       is authorized to complete Restricted Transactions. `
    },
    {
      boldText: 'All filed documents will be stored for 7 years. ',
      regularText: `If requested, a copy or certified copy of filed documents (such as the Bill of Sale, or other signed
       forms), will be provided within 7 business days, at the fee level set by the Registrar.`
    }
  ],
  [TaskType.MHR_MANUFACTURERS]: [
    {
      boldText: `Have comprehensive general liability insurance `,
      regularText: `equal to or greater than $2,000,000.00.`
    },
    {
      boldText: `Manufactured homes built are CSA approved `,
      regularText: `(Z240 or A277).`
    },
    {
      boldText: `All filed documents will be stored for 7 years. `,
      regularText: `If requested, a copy or certified copy of filed documents (such as the Bill of Sale, or other 
        signed forms), will be provided within 7 business days, at the fee level set by the Registrar. `
    }
  ],
  [TaskType.MHR_DEALERS]: [
    {
      boldText: `Have comprehensive general liability insurance `,
      regularText: `equal to or greater than $2,000,000.00.`
    }
  ]
}

export const userAccessDisplayNames: Partial<Record<TaskType, string>> = {
  [TaskType.MHR_LAWYER_NOTARY]: 'Lawyers and Notaries',
  [TaskType.MHR_MANUFACTURERS]: 'Home Manufacturers',
  [TaskType.MHR_DEALERS]: 'Home Dealers'
}
