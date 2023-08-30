<template>
  <div
      :id="`action-menu-${index}`"
      class="new-actions mx-auto"
  >
    <!--  tech debt ticket to improve this piece of code. https://github.com/bcgov/entity/issues/17132 -->
    <span class="open-action">
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
      <!-- More Actions Menu -->
      <span class="more-actions">
        <v-menu
            v-model="isMoreActionsExpanded"
            :attach="`#action-menu-${index}`"
        >
          <template #activator="{ on }">
            <v-btn
                small
                color="primary"
                min-height="2rem"
                class="more-actions-btn"
                v-on="on"
            >
              <v-icon>{{ isMoreActionsExpanded ? 'mdi-menu-up' : 'mdi-menu-down' }}</v-icon>
            </v-btn>
          </template>
          <v-list>
            <v-list-item
                v-for="(action, index) in secondaryActionButtons"
                :key="index"
                class="actions-dropdown_item my-1"
                @click="action.actionHandler(business)"
            >
              <v-list-item-subtitle>
                <v-icon small>{{ action.buttonIcon }}</v-icon>
                <span class="pl-1"> {{ action.actionText }}</span>
              </v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </v-menu>
      </span>
    </span>
  </div>
</template>

<script lang="ts">
import { AffiliationInvitationStatus, AffiliationInvitationType, AffiliationInviteInfo } from '@/models/affiliation'
import { PropType, defineComponent, ref, computed } from '@vue/composition-api'
import { Business } from '@/models/business'
import { ActionButtonClickedEvent } from '@/models/ui-interfaces/manage-business'
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
  NrState, SessionStorageKeys
} from '@/util/constants'
import { NrRequestActionCodes } from '@bcrs-shared-components/enums'
import ConfigHelper from '@/util/config-helper'
import { appendAccountId } from 'sbc-common-components/src/util/common-util'
import { useOrgStore } from '@/stores'
import {
  goToCorpOnline,
  goToNameRequest,
  goToBusinessDashboard,
  goToSocieties
} from '@/util/entities-table/action-buttons-navigation'


interface ActionButtonInfo {
  actionText: string
  actionHandler: (business: Business) => Promise<void>
  tooltipText?: string
  hasExternalIcon?: boolean
  buttonIcon?: string // not an external icon, but button label icon
}

export default defineComponent({
  name: 'ActionButtons',
  props: {
    index: {
      // todo: fixme: replace this with business identifier ?
      type: Number,
      required: true
    },
    business: {
      type: Object as PropType<Business>,
      required: true
    }
  },
  emits: [ActionButtonsEvents.ACTION_CLICKED],
  setup (props, { emit }) {
    const orgStore = useOrgStore()
    const currentOrganization = computed(() => orgStore.currentOrganization)
    const isMoreActionsExpanded = ref(false)
    const secondaryActionButtons: ActionButtonInfo[] = []
    const mainActionButton: ActionButtonInfo = {
      actionText: 'Error',
      actionHandler: () => Promise.resolve(),
      tooltipText: '',
      hasExternalIcon: false
    }

    const mainActionClickedEvent: ActionButtonClickedEvent = {
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
          eventName: ActionButtonsEvents.AFFILIATION_INVITATION_REMOVE,
          affiliationInvitation: affiliationInviteInfo
        }
      } else {
        mainActionClickedEvent.details = {
          errorName: ActionButtonsEvents.AFFILIATION_INVITATION_REMOVE,
          errorDescription: `Error removing affiliation invitation with id:${affiliationInviteInfo.id}`,
          errorSummary: 'Error removing affiliation invitation',
          errorSource: resp,
          errorCode: resp.status
        }
      }
      emit(ActionButtonsEvents.ACTION_CLICKED, mainActionClickedEvent)
    }

    const resendAffiliationInvitationHandler = async (business: Business) => {
      const affiliationInviteInfo = getFirstPendingAffiliationWithSmallestId(business.affiliationInvites)
      mainActionClickedEvent.details = {
        eventName: ActionButtonsEvents.AFFILIATION_INVITATION_RESEND,
        affiliationInvitation: affiliationInviteInfo
      }
      emit(ActionButtonsEvents.ACTION_CLICKED, mainActionClickedEvent)
    }

    const removeActionHandler = async (business: Business) => {
      mainActionClickedEvent.details = {
        eventName: ActionButtonsEvents.REMOVE_FROM_TABLE,
        entity: business
      }
      emit(ActionButtonsEvents.ACTION_CLICKED, mainActionClickedEvent)
    }

    const updateMainActionButton = (actionText: string,
                                    actionHandler: (business: Business) => Promise<void>,
                                    tooltipText?: string, // empty when not provided
                                    hasExternalIcon?: boolean // false when not provided
    ) => {
      mainActionButton.actionText = actionText
      mainActionButton.actionHandler = actionHandler
      mainActionButton.tooltipText = tooltipText || ''
      mainActionButton.hasExternalIcon = !!hasExternalIcon
    }

    const secondaryButtonOpenNameRequest = (): ActionButtonInfo => {
      return {
        actionHandler: (business) => goToNameRequest(business.nameRequest),
        actionText: ActionButtonsTexts.Actions.OPEN_NAME_REQUEST
      }
    }

    const removeFromTableButton = (isHardDelete?: boolean): ActionButtonInfo => {
      return {
        actionHandler: removeActionHandler,
        actionText: ActionButtonsTexts.Actions.REMOVE_FROM_TABLE,
        buttonIcon: isHardDelete ? 'mdi-delete-forever' : 'mdi-delete'
      }
    }

    const manageBusinessRedirectToColinExternal = () => {
      updateMainActionButton(
          ActionButtonsTexts.Actions.MANAGE_BUSINESS,
          goToCorpOnline,
          ActionButtonsTexts.Tooltips.GO_TO_CORPORATE_ONLINE_ACCESS,
          true
      )
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
        updateMainActionButton(ActionButtonsTexts.Actions.REMOVE_FROM_TABLE, removeActionHandler)
        secondaryActionButtons.push(secondaryButtonOpenNameRequest())

      } else if (isApproved && nrRequestActionCd === NrRequestActionCodes.AMALGAMATE) {
        // MVP redirect to COLIN
        updateMainActionButton(
            ActionButtonsTexts.Actions.AMALGAMATE_NOW,
            goToCorpOnline,
            ActionButtonsTexts.Tooltips.GO_TO_CORPORATE_ONLINE_ACCESS,  // mvp
            true // mvp
        )
        secondaryActionButtons.push(secondaryButtonOpenNameRequest(), removeFromTableButton())

      } else if (isApproved && nrRequestActionCd === NrRequestActionCodes.MOVE) {
        // MVP redirect to COLIN
        updateMainActionButton(
            ActionButtonsTexts.Actions.CONTINUE_IN_NOW,
            goToCorpOnline,
            ActionButtonsTexts.Tooltips.GO_TO_CORPORATE_ONLINE_ACCESS,  // mvp
            true // mvp
        )
        secondaryActionButtons.push(secondaryButtonOpenNameRequest(), removeFromTableButton())

      } else if (isApproved && (nrRequestActionCd === NrRequestActionCodes.RENEW || forRestore)) {
        // MVP redirect to COLIN
        if (!isSupportedRestorationEntities(props.business)) {
          updateMainActionButton(
              ActionButtonsTexts.Actions.RESTORE_NOW,
              goToCorpOnline,
              ActionButtonsTexts.Tooltips.GO_TO_CORPORATE_ONLINE_ACCESS,
              true
          )
        } else {
          updateMainActionButton(
              ActionButtonsTexts.Actions.RESTORE_NOW,
              goToBusinessDashboard
          )
        }
        secondaryActionButtons.push(secondaryButtonOpenNameRequest(), removeFromTableButton())

      } else if (isApproved && nrRequestActionCd === NrRequestActionCodes.RESTORE && !isForRestore(props.business)) {
        // MVP redirect to COLIN
        if (!isSupportedRestorationEntities(props.business)) {
          updateMainActionButton(
              ActionButtonsTexts.Actions.REINSTATE_NOW,
              goToCorpOnline,
              ActionButtonsTexts.Tooltips.GO_TO_CORPORATE_ONLINE_ACCESS,
              true
          )
        } else {
          updateMainActionButton(
              ActionButtonsTexts.Actions.REINSTATE_NOW,
              goToBusinessDashboard
          )
        }
        secondaryActionButtons.push(secondaryButtonOpenNameRequest(), removeFromTableButton())

      } else if (isApproved && nrRequestActionCd === NrRequestActionCodes.CHANGE_NAME) {
        // MVP redirect to dashboard
        updateMainActionButton(ActionButtonsTexts.Actions.CHANGE_NAME_NOW, goToBusinessDashboard)
        secondaryActionButtons.push(secondaryButtonOpenNameRequest(), removeFromTableButton())

      } else if (isApproved && nrRequestActionCd === NrRequestActionCodes.CONVERSION) {
        // MVP redirect to dashboard
        updateMainActionButton(ActionButtonsTexts.Actions.ALTER_NOW, goToBusinessDashboard)
        secondaryActionButtons.push(secondaryButtonOpenNameRequest(), removeFromTableButton())

      } else if (isApproved && isModernizedEntity(props.business)) {
        updateMainActionButton(ActionButtonsTexts.Actions.REGISTER_NOW, goToBusinessDashboard)
        secondaryActionButtons.push(secondaryButtonOpenNameRequest(), removeFromTableButton())

      } else if (isApproved && isColinEntity(props.business)) {
        updateMainActionButton(
            ActionButtonsTexts.Actions.REGISTER_NOW,
            goToCorpOnline,
            ActionButtonsTexts.Tooltips.GO_TO_CORPORATE_ONLINE_REGISTER,
            true
        )
        secondaryActionButtons.push(secondaryButtonOpenNameRequest(), removeFromTableButton())

      } else if (isApproved && isSocieties(props.business)) {
        updateMainActionButton(
            ActionButtonsTexts.Actions.REGISTER_NOW,
            goToSocieties,
            ActionButtonsTexts.Tooltips.GO_TO_SOCIETIES_ONLINE_REGISTER,
            true
        )
        secondaryActionButtons.push(secondaryButtonOpenNameRequest(), removeFromTableButton())

      } else if (isApproved && isOtherEntities(props.business)) {
        // MVP redirect to COLIN
        updateMainActionButton(
            ActionButtonsTexts.Actions.DOWNLOAD_FORM,
            goToCorpOnline,
            ActionButtonsTexts.Tooltips.GO_TO_CORPORATE_ONLINE_REGISTER,
            true
        )
        secondaryActionButtons.push(secondaryButtonOpenNameRequest(), removeFromTableButton())

      } else {
        updateMainActionButton('Open Name Request', (business) => goToNameRequest(business.nameRequest))
        secondaryActionButtons.push(removeFromTableButton())
      }
    } else {
      // it is not invitation, nor name request ==> It is regular incorporation stuff
      const isActive = entityStatus(props.business) === BusinessState.ACTIVE
      const isHistorical = props.business?.status?.toUpperCase() === BusinessState.HISTORICAL.toUpperCase() // is this OK check?
      const type = getType(props.business)
      mainActionClickedEvent.name = ActionButtonsEvents.DEFAULT_BUSINESS_ACTION

      if ([AffiliationTypes.INCORPORATION_APPLICATION as string, CorpTypes.INCORPORATION_APPLICATION as string].includes(type)) {
        // MVP redirect to dashboard
        updateMainActionButton(ActionButtonsTexts.Actions.RESUME_DRAFT, goToBusinessDashboard)
        secondaryActionButtons.push({
          actionHandler: removeActionHandler,
          actionText: ActionButtonsTexts.Actions.DELETE_INCORPORATION_REGISTRATION,
          buttonIcon: 'mdi-delete-forever'
        })

      } else if ([AffiliationTypes.REGISTRATION as string, CorpTypes.REGISTRATION as string].includes(type)) {
        // MVP redirect to dashboard
        updateMainActionButton(ActionButtonsTexts.Actions.RESUME_DRAFT, goToBusinessDashboard)
        secondaryActionButtons.push(
            {
              actionHandler: removeActionHandler,
              actionText: ActionButtonsTexts.Actions.DELETE_REGISTRATION,
              buttonIcon: 'mdi-delete-forever'
            }
        )

      } else if (isActive && isModernizedEntity(props.business)) {
        updateMainActionButton(ActionButtonsTexts.Actions.MANAGE_BUSINESS, goToBusinessDashboard)
        secondaryActionButtons.push(removeFromTableButton())

      } else if (isActive && !isModernizedEntity(props.business)) {
        manageBusinessRedirectToColinExternal()
        secondaryActionButtons.push(removeFromTableButton())

      } else if (isHistorical && isModernizedEntity(props.business)) {
        updateMainActionButton(ActionButtonsTexts.Actions.MANAGE_BUSINESS, goToBusinessDashboard)
        secondaryActionButtons.push(removeFromTableButton())

      } else if (isHistorical && !isModernizedEntity(props.business)) {
        manageBusinessRedirectToColinExternal()
        secondaryActionButtons.push(removeFromTableButton())

      } else if ((isHistorical || isActive) && isSocieties(props.business)) {
        updateMainActionButton(
            ActionButtonsTexts.Actions.MANAGE_BUSINESS,
            goToSocieties,
            ActionButtonsTexts.Tooltips.GO_TO_CORPORATE_ONLINE_ACCESS,
            true
        )
        secondaryActionButtons.push(removeFromTableButton())

      } else if (isHistorical) {
        manageBusinessRedirectToColinExternal()
        secondaryActionButtons.push(removeFromTableButton())

      } else {
        //if all else fails ...
        updateMainActionButton(ActionButtonsTexts.Actions.MANAGE_BUSINESS, goToBusinessDashboard)
        secondaryActionButtons.push(removeFromTableButton())
      }
    }


    return {
      isMoreActionsExpanded,
      mainActionButton,
      secondaryActionButtons
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
