// To handle codes tables such as SuspensionReasonCode, etc
export interface Code {
    code: string;
    default?: boolean;
    desc: string;
    isBusiness?: boolean;
    isGovernmentAgency?: boolean;
}
