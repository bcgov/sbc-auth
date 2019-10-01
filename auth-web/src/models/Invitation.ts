export interface Invitation {
    id?: number;
    recipientEmail: string;
    sentDate?: Date;
    membership: InvitationMembership[];
    expiresOn?: Date;
}

export interface Invitations {
    invitations: Invitation []
}

export interface InvitationMembership {
    membershipType: string;
    orgId: number;
}
