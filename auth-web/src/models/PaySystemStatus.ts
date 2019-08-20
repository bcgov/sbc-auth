/*
 corresponds to the API call api/v1/status/PAYBC [https://pay-api-dev.pathfinder.gov.bc.ca/api/v1/status/PAYBC]
 */

export interface PaySystemStatus {
    current_status: boolean,
    next_schedule_date: Date,
    next_schedule_time: Date
}
