import { User } from './user'

export interface Tasks {
    tasks : Task[]
}
export interface Task {
    created?: Date;
    createdBy?: string;
    dateSubmitted?: Date;
    id?: number;
    modified?: Date;
    modifiedBy?: string;
    name?: string;
    relationshipId?: number;
    relationshipStatus?: string;
    relationshipType?: string;
    status?: string;
    type?: string;
    user?: User;
    dueDate?: Date;
    accountId?:number;
    remarks?: string;
    action?: string;
}
export interface TaskFilterParams {
    statuses?: string[];
    type?: string;
    relationshipStatus?: string;
    pageNumber?: number;
    pageLimit?: number;
}

export interface TaskList {
    tasks: Task[]
    limit: number
    page: number
    total: number
}

export interface SyncAccountPayload {
    organizationIdentifier: number
    isBCeIDAdminReview: boolean
    relatedBCeIDUser: User
}
