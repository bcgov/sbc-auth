<template>
  <v-tooltip
      top
      content-class="top-tooltip"
      :disabled="!hasToolTip"
  >
    <template #activator="{on}">
      <v-btn
          small
          color="primary"
          min-width="5rem"
          min-height="2rem"
          class="open-action-btn"
          v-on="on"
          @click="mainActionHandler(business)"
      >
        {{ mainActionText }}
        <v-icon
            v-if="hasExternalIcon"
            class="external-icon pl-1"
            small
        >
          mdi-open-in-new
        </v-icon>
      </v-btn>
    </template>
    <span>{{ tooltipText }}</span>
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
  entityStatus,
  isColinEntity, isForRestore,
  isModernizedEntity,
  isNameRequest,
  isOtherEntities,
  isSocieties
} from '@/util/business'
import { NrDisplayStates } from '@/util/constants'
import { NrRequestActionCodes } from '@bcrs-shared-components/enums'

export default defineComponent({
  name: 'MainActionButton',
  props: {
    business: {
      type: Object as PropType<Business>,
      required: true
    }
  },
  emits: ['main-action-button-clicked'],
  setup (props, { emit }) {

    interface ActionButtonInfo {
      actionText: string
      actionHandler: (business: Business) => Promise<void>
      hasTooltip: boolean
      tooltipText: string
      hasExternalIcon: boolean
    }

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
      emit('main-action-button-clicked', mainActionClickedEvent)
    }

    const resendAffiliationInvitationHandler = async (business: Business) => {
      // todo:
      emit('main-action-button-clicked', mainActionClickedEvent) // todo: add consequence event
    }

    const openManageThisBusiness = async (business: Business) => {
      // todo:

      emit('main-action-button-clicked', mainActionClickedEvent) // todo: add consequence event
    }

    const openBusinessDashboard = async (business: Business) => {
      // todo:
      emit('main-action-button-clicked', mainActionClickedEvent) // todo: add consequence event
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

    const updateMainActionButton = (actionText: string,
                                    actionHandler: (business: Business) => Promise<void>,
                                    hasTooltip?: boolean, // false when not provided
                                    tooltipText?: string, // empty when not provided
                                    hasExternalIcon?: boolean // false when not provided
    ) => {
      mainActionButton.actionText = actionText
      mainActionButton.actionHandler = actionHandler
      mainActionButton.hasTooltip = !!hasTooltip
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
        updateMainActionButton('Cancel', removeAffiliationInvitationHandler)
        mainActionClickedEvent.name = 'AffiliationInvitation-Cancel'

      } else if (isAccessRequest && (affiliationInviteInfo.status !== AffiliationInvitationStatus.Pending)) {
        updateMainActionButton('Remove', removeAffiliationInvitationHandler)
        mainActionClickedEvent.name = 'AffiliationInvitation-Remove'

      } else if (isMagicLink &&
          [AffiliationInvitationStatus.Pending, AffiliationInvitationStatus.Expired].includes(affiliationInviteInfo.status)) {
        updateMainActionButton('Resend', resendAffiliationInvitationHandler)
        mainActionClickedEvent.name = 'AffiliationInvitation-Resend'
      } else {
        // should not happen
        console.error('AffiliatedEntityTable.MainAction.isTempAffiliationInvitationRow',
            `unexpected code path, affiliation id:${affiliationInviteInfo.id}`
        )
      }
    } else if (isNameRequest(props.business)) {
      // handle name requests
      const nrRequestActionCd = props.business.nameRequest?.requestActionCd
      const isApproved = entityStatus(props.business) === NrDisplayStates.APPROVED

      // resolve items based on types and statuses
      if (entityStatus(props.business) === NrDisplayStates.CONSUMED) {
        updateMainActionButton('Remove from table', removeNameRequestFromTable)
        mainActionClickedEvent.name = 'HandleNameRequestAction'

      } else if (isModernizedEntity(props.business) && isApproved) {
        updateMainActionButton( 'Register Now', openIncorporationApplication)
        mainActionClickedEvent.name = 'HandleNameRequestAction'

      } else if (isColinEntity(props.business) && isApproved) {
        updateMainActionButton('Register Now',
            redirectToColin,
            true,
            'Go to Corporate Online to register this business',
            false
        )
        mainActionClickedEvent.name = 'HandleNameRequestAction'

      } else if (isSocieties(props.business) && isApproved) {
        updateMainActionButton('Register Now',
            redirectToSocietiesOnline,
            true,
            'Go to Societies Online to register this business',
            false
        )
        mainActionClickedEvent.name = 'HandleNameRequestAction'

      } else if (isOtherEntities(props.business) && isApproved) {
        // MVP redirect to COLIN
        updateMainActionButton('Download Form',
            redirectToColin,
            true,
            'Go to Corporate Online to register this business',
            false
        )
        mainActionClickedEvent.name = 'HandleNameRequestAction'

      } else if (nrRequestActionCd === NrRequestActionCodes.AMALGAMATE) {
        // MVP redirect to COLIN
        updateMainActionButton('Amalgamate Now', startRegularAmalgamation)
        mainActionClickedEvent.name = 'HandleNameRequestAction'

      } else if (nrRequestActionCd === NrRequestActionCodes.MOVE) {
        // MVP redirect to COLIN
        updateMainActionButton('Continue In Now', openContinuationApplication)
        mainActionClickedEvent.name = 'HandleNameRequestAction'

      } else if (nrRequestActionCd === NrRequestActionCodes.RENEW ||
          (nrRequestActionCd === NrRequestActionCodes.RESTORE && isForRestore(props.business))) {
        // MVP redirect to COLIN
        updateMainActionButton('Restore Now', openRestoreNow, null, null, true)
        mainActionClickedEvent.name = 'HandleNameRequestAction'

      } else if (nrRequestActionCd === NrRequestActionCodes.RESTORE && !isForRestore(props.business)) {
        // MVP redirect to COLIN
        updateMainActionButton( 'Reinstate Now', openReinstateNow)
        mainActionClickedEvent.name = 'HandleNameRequestAction'

      } else if (nrRequestActionCd === NrRequestActionCodes.CHANGE_NAME) {
        // MVP redirect to COLIN
        updateMainActionButton('Change Name Now', openChangeNameNow)
        mainActionClickedEvent.name = 'HandleNameRequestAction'

      } else if (nrRequestActionCd === NrRequestActionCodes.CONVERSION) {
        // MVP redirect to COLIN
        updateMainActionButton('Alter Now', openConversionNameRequest)
        mainActionClickedEvent.name = 'HandleNameRequestAction'

      } else {
        updateMainActionButton('Open Name Request', openManageNR)
        mainActionClickedEvent.name = 'HandleNameRequestAction'
      }
    } else {
      // it is not invitation, nor name request

    }

    return {
      hasExternalIcon,
      hasToolTip,
      tooltipText,
      mainActionText,
      mainActionHandler
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
