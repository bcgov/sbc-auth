import { User } from '@/models/user';

export interface Organizations
{
  orgs : Organization []
}

export interface Organization {
  id?: string;
  name: string;
  affiliatedEntities: AffiliatedEntity[];
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
  membershipTypeCode: string
  user: User
}

export interface Members {
  members: Member []
}