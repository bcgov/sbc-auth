<template>
  <v-tooltip
      top
      content-class="top-tooltip"
      :disabled="!mainActionButton.tooltipText.trim()"
  >
    <template #activator="{on}">
      <v-btn
          small
          color="primary"
          min-width="5rem"
          min-height="2rem"
          class="open-action-btn"
          v-on="on"
          @click="mainActionButton.actionHandler(business)"
      >
        {{ mainActionButton.actionText }}
        <v-icon
            v-if="mainActionButton.hasExternalIcon"
            class="external-icon pl-1"
            small
        >
          mdi-open-in-new
        </v-icon>
      </v-btn>
    </template>
    <span>{{ mainActionButton.tooltipText }}</span>
  </v-tooltip>
</template>

<script lang="ts">
import { AffiliationInvitationStatus, AffiliationInvitationType, AffiliationInviteInfo } from '@/models/affiliation'
import { PropType, defineComponent, ref } from '@vue/composition-api'
import { Business } from '@/models/business'
import { MainActionButtonClickedEvent } from '@/models/ui-interfaces/manage-business'
import OrgService from '@/services/org.services'
import { getFirstPendingAffiliationWithSmallestId } from '@/util/affiliation-invitation'
import {
  entityStatus, getType,
  isColinEntity, isForRestore,
  isModernizedEntity, isNameRequest,
  isOtherEntities, isSocieties, isSupportedRestorationEntities,
  isTemporaryBusiness
} from '@/util/business'
import {
  ActionButtonsEvents,
  ActionButtonsTexts,
  AffiliationTypes,
  BusinessState, CorpTypes,
  NrDisplayStates,
  NrState
} from '@/util/constants'
import { NrRequestActionCodes } from '@bcrs-shared-components/enums'
import CommonUtils from '@/util/common-util'

interface ActionButtonInfo {
  actionText: string
  actionHandler: (business: Business) => Promise<void>
  hasTooltip: boolean
  tooltipText: string
  hasExternalIcon: boolean
}

export default defineComponent({
  name: 'ActionButtons',
  props: {
    business: {
      type: Object as PropType<Business>,
      required: true
    }
  },
  emits: ['main-action-button-clicked'],
  setup (props, { emit }) {


    const mainActionButton: ActionButtonInfo = {
      actionText: 'Error',
      actionHandler: () => Promise.resolve(),
      hasTooltip: false,
      tooltipText: '',
      hasExternalIcon: false
    }

    const mainActionClickedEvent: MainActionButtonClickedEvent = {
      name: 'mainActionButtonClick',
      businessIdentifier: props.business.businessIdentifier,
      details: null,
      isError: false
    }

    const removeAffiliationInvitationHandler = async (business: Business) => {
      const affiliationInviteInfo = getFirstPendingAffiliationWithSmallestId(business.affiliationInvites)
      const resp = await OrgService.removeAffiliationInvitation(affiliationInviteInfo.id)

      if (resp.status === 200) {
        mainActionClickedEvent.details = {
          eventName: 'AffiliationInvitationRemoved',
          affiliationInvitation: affiliationInviteInfo
        }
      } else {
        mainActionClickedEvent.details = {
          errorName: 'AffiliationInvitationRemovalError',
          errorDescription: `Error removing affiliation invitation with id:${affiliationInviteInfo.id}`,
          errorSummary: 'Error removing affiliation invitation',
          errorSource: resp,
          errorCode: resp.status
        }
      }
      emit(ActionButtonsEvents.MAIN_BUTTON_CLICKED, mainActionClickedEvent)
    }

    const resendAffiliationInvitationHandler = async (business: Business) => {
      // todo:
      emit(ActionButtonsEvents.MAIN_BUTTON_CLICKED, mainActionClickedEvent) // todo: add consequence event
    }

    const openManageThisBusiness = async (business: Business) => {
      // todo:

      emit(ActionButtonsEvents.MAIN_BUTTON_CLICKED, mainActionClickedEvent) // todo: add consequence event
    }

    const openBusinessDashboard = async (business: Business) => {
      // todo:
      emit(ActionButtonsEvents.MAIN_BUTTON_CLICKED, mainActionClickedEvent) // todo: add consequence event
    }

    const openManageNR = async (business: Business) => {
      // todo:
    }

    const openIncorporationApplication = async (business: Business) => {
      // todo:
    }

    const redirectToColin = async (business: Business) => {
      // todo:
    }

    const redirectToSocietiesOnline = async (business: Business) => {
      // todo:
    }

    const redirectToFormsPage = async (business: Business) => {
      // todo:
    }

    const startRegularAmalgamation = async (business: Business) => {
      // MVP, will be done later
      await redirectToColin(business)
    }

    const openRestoreNow = async (business: Business) => {
      // MVP, will be done later
      await openBusinessDashboard(business)
    }

    const openReinstateNow = async (business: Business) => {
      // MVP, will be done later
      await openBusinessDashboard(business)
    }

    const openContinuationApplication = async (business: Business) => {
      // MVP, will be done later
      await redirectToColin(business)
    }

    const openChangeNameNow = async (business: Business) => {
      // MVP, will be done later
      await openBusinessDashboard(business)
    }

    const openConversionNameRequest = async (business: Business) => {
      // MVP, will be done later
      await openBusinessDashboard(business)
    }

    const removeNameRequestFromTable = async (business: Business) => {
      // todo:
    }

    const resumeDraft = async (business: Business) => {
      // todo:
    }

    const updateMainActionButton = (actionText: string,
                                    actionHandler: (business: Business) => Promise<void>,
                                    tooltipText?: string, // empty when not provided
                                    hasExternalIcon?: boolean // false when not provided
    ) => {
      mainActionButton.actionText = actionText
      mainActionButton.actionHandler = actionHandler
      mainActionButton.tooltipText = !!tooltipText ? tooltipText : ''
      mainActionButton.hasExternalIcon = !!hasExternalIcon
    }

    // resolve actions and texts
    const isTempAffiliationInvitationRow = props.business.affiliatedEntityTableViewData?.isTemporaryAffiliationInvitationRow
    if (isTempAffiliationInvitationRow) {
      // it is temporary affiliationInvitation row
      // it should have only one affiliation invitation for now, but we will add this for future proofing
      const affiliationInviteInfo = getFirstPendingAffiliationWithSmallestId(props.business.affiliationInvites)
      const isMagicLink = affiliationInviteInfo?.type === AffiliationInvitationType.MagicLink
      const isAccessRequest = affiliationInviteInfo?.type === AffiliationInvitationType.AccessRequest

      if (isAccessRequest && (affiliationInviteInfo.status === AffiliationInvitationStatus.Pending)) {
        updateMainActionButton(ActionButtonsTexts.Actions.CANCEL, removeAffiliationInvitationHandler)
        mainActionClickedEvent.name = ActionButtonsEvents.AFFILIATION_INVITATION_CANCEL

      } else if (isAccessRequest && (affiliationInviteInfo.status !== AffiliationInvitationStatus.Pending)) {
        updateMainActionButton(ActionButtonsTexts.Actions.REMOVE, removeAffiliationInvitationHandler)
        mainActionClickedEvent.name = ActionButtonsEvents.AFFILIATION_INVITATION_REMOVE

      } else if (isMagicLink &&
          [AffiliationInvitationStatus.Pending, AffiliationInvitationStatus.Expired].includes(affiliationInviteInfo.status)) {
        updateMainActionButton(ActionButtonsTexts.Actions.RESEND, resendAffiliationInvitationHandler)
        mainActionClickedEvent.name = ActionButtonsEvents.AFFILIATION_INVITATION_RESEND
      } else {
        // should not happen
        console.error('AffiliatedEntityTable.MainAction.isTempAffiliationInvitationRow',
            `unexpected code path, affiliation id:${affiliationInviteInfo.id}`
        )
      }
    } else if (isNameRequest(props.business)) {
      // handle name requests
      const nrRequestActionCd = props.business.nameRequest?.requestActionCd
      const status = entityStatus(props.business)
      const isApproved = status === NrDisplayStates.APPROVED
      const forRestore = (nrRequestActionCd === NrRequestActionCodes.RESTORE && isForRestore(props.business))
      const isForRemoval = [
        NrDisplayStates.REJECTED.toUpperCase(),
        NrDisplayStates.CONSUMED.toUpperCase(),
        NrDisplayStates.CANCELLED.toUpperCase(),
        NrDisplayStates.REFUND_REQUESTED.toUpperCase()
      ].includes(status.toUpperCase())

      mainActionClickedEvent.name = ActionButtonsEvents.DEFAULT_NAME_REQUEST_ACTION

      // resolve items based on types and statuses
      if (isForRemoval) {
        updateMainActionButton(ActionButtonsTexts.Actions.REMOVE_FROM_TABLE, removeNameRequestFromTable)

      } else if (isApproved && nrRequestActionCd === NrRequestActionCodes.AMALGAMATE) {
        // MVP redirect to COLIN
        updateMainActionButton(
            ActionButtonsTexts.Actions.AMALGAMATE_NOW,
            startRegularAmalgamation,
            ActionButtonsTexts.Tooltips.GO_TO_CORPORATE_ONLINE_ACCESS,  // mvp
            true // mvp
        )

      } else if (isApproved && nrRequestActionCd === NrRequestActionCodes.MOVE) {
        // MVP redirect to COLIN
        updateMainActionButton(
            ActionButtonsTexts.Actions.CONTINUE_IN_NOW,
            openContinuationApplication,
            ActionButtonsTexts.Tooltips.GO_TO_CORPORATE_ONLINE_ACCESS,  // mvp
            true // mvp
        )

      } else if (isApproved && (nrRequestActionCd === NrRequestActionCodes.RENEW || forRestore)) {
        // MVP redirect to COLIN4
        if (!isSupportedRestorationEntities(props.business)) {
          updateMainActionButton(
              ActionButtonsTexts.Actions.RESTORE_NOW,
              redirectToColin,
              ActionButtonsTexts.Tooltips.GO_TO_CORPORATE_ONLINE_ACCESS,
              true
          )
        } else {
          updateMainActionButton(
              ActionButtonsTexts.Actions.RESTORE_NOW,
              openBusinessDashboard
          )
        }

      } else if (isApproved && nrRequestActionCd === NrRequestActionCodes.RESTORE && !isForRestore(props.business)) {
        // MVP redirect to COLIN
        if (!isSupportedRestorationEntities(props.business)) {
          updateMainActionButton(
              ActionButtonsTexts.Actions.REINSTATE_NOW,
              redirectToColin,
              ActionButtonsTexts.Tooltips.GO_TO_CORPORATE_ONLINE_ACCESS,
              true
          )
        } else {
          updateMainActionButton(
              ActionButtonsTexts.Actions.REINSTATE_NOW,
              openBusinessDashboard
          )
        }

      } else if (isApproved && nrRequestActionCd === NrRequestActionCodes.CHANGE_NAME) {
        // MVP redirect to COLIN
        updateMainActionButton(isApproved && ActionButtonsTexts.Actions.CHANGE_NAME_NOW, openChangeNameNow)

      } else if (isApproved && nrRequestActionCd === NrRequestActionCodes.CONVERSION) {
        // MVP redirect to COLIN
        updateMainActionButton(ActionButtonsTexts.Actions.ALTER_NOW, openConversionNameRequest)

      } else if (isApproved && isModernizedEntity(props.business)) {
        updateMainActionButton(ActionButtonsTexts.Actions.REGISTER_NOW, openIncorporationApplication)

      } else if (isApproved && isColinEntity(props.business)) {
        updateMainActionButton(
            ActionButtonsTexts.Actions.REGISTER_NOW,
            redirectToColin,
            ActionButtonsTexts.Tooltips.GO_TO_CORPORATE_ONLINE_REGISTER,
            true
        )

      } else if (isApproved && isSocieties(props.business)) {
        updateMainActionButton(
            ActionButtonsTexts.Actions.REGISTER_NOW,
            redirectToSocietiesOnline,
            ActionButtonsTexts.Tooltips.GO_TO_SOCIETIES_ONLINE_REGISTER,
            true
        )

      } else if (isApproved && isOtherEntities(props.business)) {
        // MVP redirect to COLIN
        updateMainActionButton(
            ActionButtonsTexts.Actions.DOWNLOAD_FORM,
            redirectToFormsPage,
            ActionButtonsTexts.Tooltips.GO_TO_CORPORATE_ONLINE_REGISTER,
            true
        )

      } else {
        updateMainActionButton(ActionButtonsTexts.Actions.OPEN_NAME_REQUEST, openManageNR)

      }
    } else {
      // it is not invitation, nor name request ==> It is regular incorporation stuff
      const isDraft = isTemporaryBusiness(props.business)
      const isActive = entityStatus(props.business) === BusinessState.ACTIVE
      const isHistorical = props.business?.status?.toUpperCase() === BusinessState.HISTORICAL.toUpperCase() // is this OK check?
      const type = getType(props.business)
      mainActionClickedEvent.name = ActionButtonsEvents.DEFAULT_BUSINESS_ACTION

      if (
          // isDraft &&
          [AffiliationTypes.INCORPORATION_APPLICATION as string, CorpTypes.INCORPORATION_APPLICATION as string].includes(type)) {
        updateMainActionButton(ActionButtonsTexts.Actions.RESUME_DRAFT, resumeDraft)

      } else if (
          // isDraft &&
          [AffiliationTypes.REGISTRATION as string, CorpTypes.REGISTRATION as string].includes(type)) {
        updateMainActionButton(ActionButtonsTexts.Actions.RESUME_DRAFT, resumeDraft)

      } else if (isActive && isModernizedEntity(props.business)) {
        updateMainActionButton(ActionButtonsTexts.Actions.MANAGE_BUSINESS, openBusinessDashboard)

      } else if (isActive && !isModernizedEntity(props.business)) {
        updateMainActionButton(
            ActionButtonsTexts.Actions.MANAGE_BUSINESS,
            redirectToColin,
            ActionButtonsTexts.Tooltips.GO_TO_CORPORATE_ONLINE_ACCESS,
            true
        )

      } else if (isHistorical && isModernizedEntity(props.business)) {
        updateMainActionButton(ActionButtonsTexts.Actions.MANAGE_BUSINESS, openBusinessDashboard)

      } else if (isHistorical && !isModernizedEntity(props.business)) {
        updateMainActionButton(
            ActionButtonsTexts.Actions.MANAGE_BUSINESS,
            redirectToColin,
            ActionButtonsTexts.Tooltips.GO_TO_CORPORATE_ONLINE_ACCESS,
            true
        )

      } else if ((isHistorical || isActive) && isSocieties(props.business)) {
        updateMainActionButton(
            ActionButtonsTexts.Actions.MANAGE_BUSINESS,
            redirectToSocietiesOnline,
            ActionButtonsTexts.Tooltips.GO_TO_CORPORATE_ONLINE_ACCESS,
            true
        )

      } else if (isHistorical) {
        updateMainActionButton(
            ActionButtonsTexts.Actions.MANAGE_BUSINESS,
            redirectToColin,
            ActionButtonsTexts.Tooltips.GO_TO_CORPORATE_ONLINE_ACCESS,
            true
        )
      } else {
        //if all else fails ...
        updateMainActionButton(ActionButtonsTexts.Actions.MANAGE_BUSINESS, openBusinessDashboard)
      }
    }

    return {
      mainActionButton
    }
  }
})
</script>

<style scoped lang="scss">

// Tooltips
.v-tooltip__content {
  background-color: RGBA(73, 80, 87, 0.95) !important;
  color: white !important;
  border-radius: 4px;
  font-size: 12px !important;
  line-height: 18px !important;
  padding: 15px !important;
  letter-spacing: 0;
  max-width: 360px !important;
}

.v-tooltip__content:after {
  content: "" !important;
  position: absolute !important;
  top: 50% !important;
  right: 100% !important;
  margin-top: -10px !important;
  border-top: 10px solid transparent !important;
  border-bottom: 10px solid transparent !important;
  border-right: 8px solid RGBA(73, 80, 87, .95) !important;
}

.top-tooltip:after {
  top: 100% !important;
  left: 45% !important;
  margin-top: 0 !important;
  border-right: 10px solid transparent !important;
  border-left: 10px solid transparent !important;
  border-top: 8px solid RGBA(73, 80, 87, 0.95) !important;
}
</style>
