import { Contact } from '@/models/contact'

export interface AffidavitInformation {
  contacts: Contact[]
  documentId: string
  documentUrl: string
  issuer: string
  status: string
}
