import { User } from '@/models/user';

export interface Organizations
{
  orgs : Organization []
}

export interface Organization {
  id?: string;
  name: string;
  affiliatedEntities?: AffiliatedEntity[];
  orgType?: string;
}

export interface AffiliatedEntity {
  businessIdentifier: string;
  businessNumber: string;
  name: string;
}

export interface RemoveBusinessPayload {
  orgIdentifier: string
  incorporationNumber: string
}

export interface Member {
  id: number
  membershipTypeCode: string
  user: User
}

export interface Members {
  members: Member []
}

export interface ActiveUserRecord {
  username: string
  name: string
  role: string
  lastActive: string
}

export interface PendingUserRecord {
  invitationId: number
  email: string
  invitationSent: string
  invitationExpires?: string
}