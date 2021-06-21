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
    user?: number;
    dueDate?: Date;
    accountId?:number;
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
