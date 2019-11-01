import { Organization } from '@/models/Organization'

export interface CreateRequestBody {
    recipientEmail: string;
    sentDate: Date;
    membership: InvitationMembership[];
}

export interface Invitation {
    id: number;
    recipientEmail: string;
    sentDate: Date;
    membership: InvitationMembership[];
    expiresOn?: Date;
    status: string;
}

export interface Invitations {
    invitations: Invitation []
}

export interface InvitationMembership {
    membershipType: string;
    org: Organization;
}
