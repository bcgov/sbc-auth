export interface Tasks {
    task : Task[]
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
    relationshipType?: string;
    status?: string;
    type?: string;
    user?: number;
    dueDate?: Date
}
