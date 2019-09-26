import { Contact } from './contact'

export interface User {
    firstname: string;
    lastname: string;
    username: string;
    contacts?: Contact[];
    modified?: Date
}

export interface SuccessEmitPayload {
    isResend: boolean,
    invitationCount: number
  }
