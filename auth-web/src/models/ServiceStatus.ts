/*
 corresponds to the API call api/v1/status/PAYBC [https://status-api-dev.pathfinder.gov.bc.ca/api/v1/status/PAYBC]
 */

export interface ServiceStatus {
    currentStatus: boolean,
    nextUpTime: Date,
}
