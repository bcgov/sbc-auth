import { Invitation } from '@/models/Invitation'
import { User } from '@/models/user'

export interface CreateRequestBody {
  name: string
}

export interface Organizations
{
  orgs : Organization[]
}

export interface Organization {
  id?: number;
  name: string;
  affiliatedEntities?: AffiliatedEntity[];
  orgType?: string;
  members?: Member[];
  invitations?: Invitation[];
}

export interface AffiliatedEntity {
  businessIdentifier: string;
  businessNumber: string;
  name: string;
}

export interface UpdateMemberPayload {
  orgIdentifier: number
  memberId: number
  role?: string
}

export interface RemoveBusinessPayload {
  orgIdentifier: number
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
  member: Member
}

export interface PendingUserRecord {
  email: string
  invitationSent: string
  invitationExpires?: string
  invitation: Invitation
}
