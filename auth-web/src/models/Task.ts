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
}
export interface TaskFilterParams {
    status?: string;
    type?: string;
    pageNumber?: number;
    pageLimit?: number;
}

export interface TaskList {
    tasks: Task[]
    limit: number
    page: number
    total: number
}
