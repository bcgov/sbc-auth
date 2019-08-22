/*
 corresponds to the API call api/v1/status/PAYBC [https://pay-api-dev.pathfinder.gov.bc.ca/api/v1/status/PAYBC]
 */

export interface PaySystemStatus {
    currentStatus: boolean,
    nextScheduleDate: Date,
    nextScheduleTime: Date
}
