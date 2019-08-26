import { AffiliatedEntity } from './AffiliatedEntity'

export interface Organization {
  name: string;
  affiliatedEntities: AffiliatedEntity[];
}
