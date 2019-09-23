export interface Invitation {
    recipientEmail: string;
    sentDate: Date;
    membership: InvitationMembership[]
}

export interface Invitations {
    invitations: Invitation []
}

export interface InvitationMembership {
    membershipType: string;
    orgId: string;
}