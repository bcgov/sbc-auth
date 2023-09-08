import { QualifiedSupplierRequirementsConfig } from '@/models/external'
import { TaskType } from '@/util/constants'

export const userAccessRequirements: Record<TaskType | any, QualifiedSupplierRequirementsConfig[]> = {
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
  [TaskType.MHR_MANUFACTURERS]: [],
  [TaskType.MHR_DEALERS]: []
}
