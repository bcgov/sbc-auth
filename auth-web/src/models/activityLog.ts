export interface ActivityLogs {
    activityLogs : ActivityLog[]
}
export interface ActivityLog {
    id?: number;
    action?:string
    actor?:string
    created?: Date;
    itemId?: string;
    itemName?: string;
    itemType?: string;
    modified?: Date;
    orgId?:number;
}

export interface ActivityLogsResponse {
    tasks: ActivityLog[]
    limit: number
    page: number
    total: number
}

export interface ActivityLogFilterParams {
    pageNumber?: number
    pageLimit?: number
    orgId?:number
  }
