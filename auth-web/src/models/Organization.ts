export interface Organizations
{
  orgs : Organization []
}

export interface Organization {
  name: string;
  affiliatedEntities: AffiliatedEntity[];
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
