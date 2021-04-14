
export interface Tasks {
    task : Task[]
}

export interface Task {
    created?: string;
    createdBy?: string;
    dateSubmitted?: string;
    id?: number;
    modified?: string;
    modifiedBy: string;
    name?: string;
    relationshipId?: number;
    relationshipType?: string;
    status?: string;
    type: string;
    user?: number;
}
