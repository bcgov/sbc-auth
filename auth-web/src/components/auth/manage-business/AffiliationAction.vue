<template>
  <div
    :id="`action-menu-${index}`"
    class="new-actions mx-auto"
  >
    <span class="open-action">
      <v-tooltip
        top
        content-class="top-tooltip"
        :disabled="disableTooltip(item)"
      >
        <template #activator="{on}">
          <v-btn
            small
            color="primary"
            min-width="5rem"
            min-height="2rem"
            class="open-action-btn"
            v-on="on"
            @click="action(item)"
          >
            {{ getPrimaryAction(item) }}
            <v-icon
              v-if="isOpenExternal(item)"
              class="external-icon pl-1"
              small
            >mdi-open-in-new</v-icon>
          </v-btn>
        </template>
        <span>Go to {{ getTooltipTargetDescription(item) }} to access this business</span>
      </v-tooltip>
      <!-- More Actions Menu -->
      <span class="more-actions">
        <v-menu
          v-model="actionDropdown[index]"
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
              <v-icon>{{ actionDropdown[index] ? 'mdi-menu-up' : 'mdi-menu-down' }}</v-icon>
            </v-btn>
          </template>
          <v-list>
            <v-list-item
              v-if="showAffiliationInvitationNewRequestButton(item)"
              class="actions-dropdown_item my-1"
              @click="openNewAffiliationInvite(item)"
            >
              <v-list-item-subtitle>
                <v-icon small>mdi-refresh</v-icon>
                <span class="pl-1">New Request</span>
              </v-list-item-subtitle>
            </v-list-item>
            <v-list-item
              v-if="showOpenButton(item)"
              class="actions-dropdown_item my-1"
              data-test="use-name-request-button"
              @click="goToNameRequest(item.nameRequest)"
            >
              <v-list-item-subtitle>
                <v-icon small>mdi-format-list-bulleted-square</v-icon>
                <span class="pl-1">Open Name Request</span>
              </v-list-item-subtitle>
            </v-list-item>
            <v-list-item
              v-if="showRemoveButton(item)"
              v-can:REMOVE_BUSINESS.disable
              class="actions-dropdown_item my-1"
              data-test="remove-button"
              @click="removeAffiliationOrInvitation(item)"
            >
              <v-list-item-subtitle v-if="isTemporaryBusiness(item)">
                <v-icon small>mdi-delete-forever</v-icon>
                <span class="pl-1">Delete {{ tempDescription(item) }}</span>
              </v-list-item-subtitle>
              <v-list-item-subtitle v-else-if="showAffiliationInvitationCancelRequestButton(item)">
                <v-icon small>mdi-window-close</v-icon>
                <span class="pl-1">Cancel Request</span>
              </v-list-item-subtitle>
              <v-list-item-subtitle v-else>
                <v-icon small>mdi-delete</v-icon>
                <span class="pl-1">Remove From Table</span>
              </v-list-item-subtitle>
            </v-list-item>
            <v-list-item
              v-if="showAmalgamateShortForm(item)"
              class="actions-dropdown_item my-1"
              data-test="use-name-request-button"
            >
              <v-list-item-subtitle>
                <v-icon small>mdi-checkbox-multiple-blank-outline</v-icon>
                <span class="pl-1">Amalgamate Now (Short Form)</span>
              </v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </v-menu>
      </span>
    </span>
  </div>
</template>

<script lang='ts'>
import { AffiliationInvitationStatus, AffiliationInvitationType, CorpTypes, FilingTypes, LDFlags,
  NrDisplayStates, NrTargetTypes } from '@/util/constants'
import { PropType, defineComponent } from '@vue/composition-api'
import { goToCorpOnline, goToDashboard, goToFormPage, goToNameRequest,
  goToOneStop, goToSocieties } from '@/util/navigation'
import { useBusinessStore, useOrgStore } from '@/stores'
import AffiliationInvitationService from '@/services/affiliation-invitation.services'
import { Business } from '@/models/business'
import { NrRequestActionCodes } from '@bcrs-shared-components/enums'
import launchdarklyServices from 'sbc-common-components/src/services/launchdarkly.services'
import { useAffiliations } from '@/composables'

export default defineComponent({
  name: 'AffiliationAction',
  props: {
    item: { type: Object as PropType<Business>, required: true },
    index: { type: Number, required: true }
  },
  emits: ['show-manage-business-dialog', 'unknown-error', 'remove-affiliation-invitation',
    'remove-business', 'business-unavailable-error', 'resend-affiliation-invitation'],
  setup (props, context) {
    const orgStore = useOrgStore()
    const businessStore = useBusinessStore()

    const { affiliations, status, isBusinessAffiliated, isNameRequest,
      isTemporaryBusiness, getEntityType, tempDescription, actionDropdown } = useAffiliations()

    /** Create a business record in LEAR. */
    const createBusinessRecord = async (business: Business): Promise<string> => {
      const regTypes = [CorpTypes.SOLE_PROP, CorpTypes.PARTNERSHIP]
      const iaTypes = [CorpTypes.BENEFIT_COMPANY, CorpTypes.COOP, CorpTypes.BC_CCC, CorpTypes.BC_COMPANY,
        CorpTypes.BC_ULC_COMPANY]

      let filingResponse = null
      if (regTypes.includes(business.nameRequest?.legalType)) {
        filingResponse = await businessStore.createNamedBusiness({ filingType: FilingTypes.REGISTRATION, business })
      } else if (iaTypes.includes(business.nameRequest?.legalType)) {
        filingResponse = await businessStore.createNamedBusiness({
          filingType: FilingTypes.INCORPORATION_APPLICATION, business })
      }

      if (filingResponse?.errorMsg) {
        context.emit('unknown-error')
        return ''
      }
      return filingResponse.data.filing.business.identifier
    }

    /** Handler for open action */
    const open = (item: Business): void => {
      if ((item.corpType?.code || item.corpType) === CorpTypes.NAME_REQUEST) {
        goToNameRequest(item.nameRequest)
      } else {
        goToDashboard(item.businessIdentifier)
      }
    }

    const isOtherEntities = (item: Business): boolean => {
      return [CorpTypes.FINANCIAL, CorpTypes.PRIVATE_ACT, CorpTypes.PARISHES].includes(getEntityType(item))
    }

    const isForRestore = (item: Business): boolean => {
      return [CorpTypes.BC_COMPANY, CorpTypes.BC_CCC, CorpTypes.BC_ULC_COMPANY,
        CorpTypes.COOP, CorpTypes.BENEFIT_COMPANY].includes(getEntityType(item))
    }

    const isSocieties = (item: Business): boolean => {
      return [CorpTypes.CONT_IN_SOCIETY, CorpTypes.SOCIETY, CorpTypes.XPRO_SOCIETY].includes(getEntityType(item))
    }

    const isModernizedEntity = (item: Business): boolean => {
      const entityType = getEntityType(item)
      const supportedEntityFlags = launchdarklyServices.getFlag(LDFlags.IaSupportedEntities)?.split(' ') || []
      return supportedEntityFlags.includes(entityType)
    }

    const isSupportedRestorationEntities = (item: Business): boolean => {
      const entityType = getEntityType(item)
      const supportedEntityFlags = launchdarklyServices.getFlag(LDFlags.SupportRestorationEntities)?.split(' ') || []
      return supportedEntityFlags.includes(entityType)
    }

    const isOpenExternal = (item: Business): boolean => {
      const invitationStatus = item?.affiliationInvites?.[0]?.status
      if ([AffiliationInvitationStatus.Pending, AffiliationInvitationStatus.Expired].includes(invitationStatus)) {
        return false
      }

      if (isTemporaryBusiness(item)) {
        return false
      }

      if (isNameRequest(item)) {
        const nrState = status(item)
        if (nrState !== NrDisplayStates.APPROVED) {
          return false
        }
        const nrRequestActionCd = item.nameRequest?.requestActionCd
        if (nrRequestActionCd === NrRequestActionCodes.NEW_BUSINESS) {
          return !isModernizedEntity(item)
        }
        // temporarily show external icon for amalgamate and continue in
        if (nrRequestActionCd === NrRequestActionCodes.AMALGAMATE ||
          nrRequestActionCd === NrRequestActionCodes.MOVE) {
          return true
        }
        // temporarily show external icon for restore/reinstate for some entity types
        if (nrRequestActionCd === NrRequestActionCodes.RESTORE ||
          nrRequestActionCd === NrRequestActionCodes.RENEW) {
          return !isSupportedRestorationEntities(item)
        }
        return false
      }

      // check for business
      return !isModernizedEntity(item)
    }

    const goToRegister = async (item: Business): Promise<void> => {
      if (isModernizedEntity(item)) {
        const businessIdentifier = await createBusinessRecord(item)
        goToDashboard(businessIdentifier)
      } else if (isSocieties(item)) {
        goToSocieties()
      } else if (isOtherEntities(item)) {
        goToFormPage()
      } else {
        goToCorpOnline()
      }
    }

    const getTooltipTargetDescription = (item: Business): string => {
      return isSocieties(item) ? 'Societies Online' : 'Corporate Online'
    }

    /** Handler for draft IA creation and navigation */
    const useNameRequest = async (item: Business) => {
      switch (item.nameRequest.target) {
        case NrTargetTypes.LEAR: {
          // Create new IA if the selected item is Name Request
          if (item.corpType.code === CorpTypes.NAME_REQUEST) {
            const businessIdentifier = await createBusinessRecord(item)
            goToDashboard(businessIdentifier)
          } else {
            goToDashboard(item.businessIdentifier)
          }
          break
        }
        case NrTargetTypes.ONESTOP:
          goToOneStop()
          break
        case NrTargetTypes.COLIN:
          goToCorpOnline()
          break
      }
    }

    // Refactor this is duplicated.
    const isCurrentOrganization = (orgId: number) => {
      return orgId === orgStore.currentOrganization.id
    }

    const showAffiliationInvitationNewRequestButton = (business: Business): boolean => {
      const affiliationInvitation = business?.affiliationInvites?.[0]
      if (!affiliationInvitation) { return false }
      return isCurrentOrganization(affiliationInvitation.fromOrg.id) &&
          business.affiliationInvites[0].status !== AffiliationInvitationStatus.Accepted &&
          business.affiliationInvites[0].type === AffiliationInvitationType.REQUEST
    }

    /** Remove business/nr affiliation or affiliation invitation. */
    const removeAffiliationOrInvitation = async (business: Business): Promise<void> => {
      if (business.affiliationInvites?.length > 0) {
        const affiliationInviteInfo = business.affiliationInvites[0]
        const invitationStatus = affiliationInviteInfo.status
        if ([AffiliationInvitationStatus.Pending, AffiliationInvitationStatus.Failed,
          AffiliationInvitationStatus.Expired].includes(invitationStatus as AffiliationInvitationStatus)) {
          const success = await AffiliationInvitationService.removeAffiliationInvitation(affiliationInviteInfo.id)
          if (!success) {
            context.emit('unknown-error')
          }
          context.emit('remove-affiliation-invitation')
          return
        }
      }
      context.emit('remove-business', {
        orgIdentifier: orgStore.currentOrganization.id,
        business
      })
    }

    const disableTooltip = (item: Business): boolean => {
      if (isOpenExternal(item)) {
        if (isNameRequest(item)) {
          const nrRequestActionCd = item.nameRequest?.requestActionCd
          if (nrRequestActionCd === NrRequestActionCodes.NEW_BUSINESS && isOtherEntities(item)) {
            return true
          }
        }
        return false
      }
      return true
    }

    const getNrRequestDescription = (item: Business): string => {
      const nrRequestActionCd = item.nameRequest?.requestActionCd
      switch (nrRequestActionCd) {
        case NrRequestActionCodes.AMALGAMATE:
          return 'Amalgamate Now'
        case NrRequestActionCodes.CONVERSION:
          return 'Alter Now'
        case NrRequestActionCodes.CHANGE_NAME:
          return 'Change Name Now'
        case NrRequestActionCodes.MOVE:
          return 'Continue In Now'
        case NrRequestActionCodes.NEW_BUSINESS:
          return isOtherEntities(item) ? 'Download Form' : 'Register Now'
        case NrRequestActionCodes.RESTORE:
          return isForRestore(item) ? 'Restore Now' : 'Reinstate Now'
        case NrRequestActionCodes.RENEW:
          return 'Restore Now'
        default:
          return 'Open Name Request'
      }
    }

    // Actions
    const getPrimaryAction = (item: Business): string => {
      const affiliationInviteInfo = item?.affiliationInvites?.[0]
      if ([AffiliationInvitationStatus.Pending,
        AffiliationInvitationStatus.Expired,
        AffiliationInvitationStatus.Failed].includes(affiliationInviteInfo?.status)) {
        // checks for affiliation invitation
        switch (true) {
          case affiliationInviteInfo.type === AffiliationInvitationType.EMAIL &&
          [AffiliationInvitationStatus.Pending, AffiliationInvitationStatus.Expired].includes(affiliationInviteInfo?.status):
            return 'Resend Email'

          case affiliationInviteInfo.type === AffiliationInvitationType.REQUEST &&
          AffiliationInvitationStatus.Pending === affiliationInviteInfo?.status &&
          isCurrentOrganization(item.affiliationInvites[0].fromOrg.id) :
            return 'Cancel Request' // 'Cancel<br>Request'

          case affiliationInviteInfo.type === AffiliationInvitationType.REQUEST &&
          AffiliationInvitationStatus.Failed === affiliationInviteInfo?.status:
            return 'Remove from list' // 'Remove<br>from list'
        }
      }

      if (isTemporaryBusiness(item)) {
        return 'Resume Draft'
      }
      if (isNameRequest(item)) {
        const nrStatus = status(item)
        switch (nrStatus) {
          case NrDisplayStates.APPROVED:
            return getNrRequestDescription(item)
          case NrDisplayStates.REJECTED:
          case NrDisplayStates.CONSUMED:
          case NrDisplayStates.CANCELLED:
          case NrDisplayStates.REFUND_REQUESTED:
            return 'Remove From Table'
          default:
            return 'Open Name Request'
        }
      }
      return 'Manage Business'
    }

    const isShowRemoveAsPrimaryAction = (item: Business): boolean => {
      return isNameRequest(item) &&
      [NrDisplayStates.REJECTED, NrDisplayStates.CONSUMED,
        NrDisplayStates.CANCELLED, NrDisplayStates.REFUND_REQUESTED].includes(status(item) as NrDisplayStates)
    }

    const showRemoveButton = (item: Business): boolean => {
      return !isShowRemoveAsPrimaryAction(item) && !showAffiliationInvitationNewRequestButton(item)
    }

    const handleTemporaryBusinessRedirect = (item): boolean => {
      if (isTemporaryBusiness(item)) {
        goToDashboard(item.businessIdentifier)
        return true
      }
      return false
    }

    const handleApprovedNameRequestRenew = (item: Business): void => {
      if (!isSupportedRestorationEntities(item)) {
        goToCorpOnline()
      } else if (isBusinessAffiliated(item.nameRequest?.corpNum)) {
        goToDashboard(item.nameRequest?.corpNum)
      } else {
        const action = isForRestore(item) ? 'restore' : 'reinstate'
        context.emit('business-unavailable-error', action)
      }
    }

    const handleApprovedNameRequestChangeName = (item: Business, nrRequestActionCd: NrRequestActionCodes): void => {
      if (isBusinessAffiliated(item.nameRequest?.corpNum)) {
        goToDashboard(item.nameRequest?.corpNum)
      } else {
        let action = ''
        if (nrRequestActionCd === NrRequestActionCodes.CONVERSION) {
          action = 'alter'
        } else if (nrRequestActionCd === NrRequestActionCodes.CHANGE_NAME) {
          action = 'change name'
        }
        context.emit('business-unavailable-error', action)
      }
    }

    const handleApprovedNameRequest = (item: Business, nrRequestActionCd: NrRequestActionCodes): void => {
      switch (nrRequestActionCd) {
        case NrRequestActionCodes.AMALGAMATE:
          // For now, go to COLIN with external link + icon + matching hover text
          // Future gotoAmagamate
          goToCorpOnline()
          break
        case NrRequestActionCodes.MOVE:
          // Future - Relocate - Continue In
          goToCorpOnline()
          break
        case NrRequestActionCodes.CONVERSION:
        case NrRequestActionCodes.CHANGE_NAME:
          handleApprovedNameRequestChangeName(item, nrRequestActionCd)
          break
        case NrRequestActionCodes.RESTORE:
        case NrRequestActionCodes.RENEW:
          handleApprovedNameRequestRenew(item)
          break
        case NrRequestActionCodes.NEW_BUSINESS: {
          goToRegister(item)
          break
        }
        default:
          goToNameRequest(item.nameRequest)
          break
      }
    }

    const handleNameRequestRedirect = (item: Business): boolean => {
      if (!isNameRequest(item)) {
        return false
      }
      if (status(item) === NrDisplayStates.APPROVED) {
        const nrRequestActionCd = item.nameRequest?.requestActionCd
        handleApprovedNameRequest(item, nrRequestActionCd)
        return true
      } else {
        goToNameRequest(item.nameRequest)
        return true
      }
    }

    const handleBusinessRedirect = (item): boolean => {
      if (isNameRequest(item)) {
        return false
      }
      if (isModernizedEntity(item)) {
        goToDashboard(item.businessIdentifier)
        return true
      } else if (isSocieties(item)) {
        goToSocieties()
        return true
      } else {
        goToCorpOnline()
        return true
      }
    }

    const redirect = (item: Business): boolean => {
      if (handleTemporaryBusinessRedirect(item)) {
        return
      }
      if (handleNameRequestRedirect(item)) {
        return
      }
      handleBusinessRedirect(item)
    }

    const action = async (item: Business): Promise<void> => {
      const affiliationInviteInfo = item?.affiliationInvites?.[0]
      if ([AffiliationInvitationStatus.Pending,
        AffiliationInvitationStatus.Expired,
        AffiliationInvitationStatus.Failed].includes(affiliationInviteInfo?.status as AffiliationInvitationStatus)) {
        switch (true) {
          case affiliationInviteInfo.type === AffiliationInvitationType.EMAIL &&
          [AffiliationInvitationStatus.Pending, AffiliationInvitationStatus.Expired]
            .includes(affiliationInviteInfo?.status as AffiliationInvitationStatus):
            context.emit('resend-affiliation-invitation', item)
            return

          case affiliationInviteInfo.type === AffiliationInvitationType.REQUEST &&
          AffiliationInvitationStatus.Pending === affiliationInviteInfo?.status &&
          isCurrentOrganization(item.affiliationInvites[0].fromOrg.id) :
            await removeAffiliationOrInvitation(item)
            return

          case affiliationInviteInfo.type === AffiliationInvitationType.REQUEST &&
          AffiliationInvitationStatus.Failed === affiliationInviteInfo?.status:
            await removeAffiliationOrInvitation(item)
            return
        }
      }

      if (isShowRemoveAsPrimaryAction(item)) {
        removeAffiliationOrInvitation(item)
      } else {
        redirect(item)
      }
    }

    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const showAmalgamateShortForm = (item: Business): boolean => {
      // reserve for changes in the future
      return false
    }

    // This is called when an affiliation invitation request already exists.
    const openNewAffiliationInvite = (business: Business) => {
      businessStore.setRemoveExistingAffiliationInvitation(true)
      context.emit('show-manage-business-dialog', business)
    }

    const showOpenButton = (item: Business): boolean => {
      return isNameRequest(item) &&
      ![NrDisplayStates.HOLD,
        NrDisplayStates.EXPIRED,
        NrDisplayStates.PROCESSING,
        NrDisplayStates.DRAFT].includes(status(item) as NrDisplayStates)
    }

    const showAffiliationInvitationCancelRequestButton = (item: Business): boolean => {
      return item.affiliationInvites?.length > 0 &&
        item.affiliationInvites[0].status !== AffiliationInvitationStatus.Accepted &&
          item.affiliationInvites[0].type === AffiliationInvitationType.EMAIL
    }

    return {
      affiliations,
      action,
      disableTooltip,
      actionDropdown,
      getPrimaryAction,
      getTooltipTargetDescription,
      goToNameRequest,
      showAffiliationInvitationCancelRequestButton,
      showAffiliationInvitationNewRequestButton,
      isOpenExternal,
      isShowRemoveAsPrimaryAction,
      isTemporaryBusiness,
      open,
      openNewAffiliationInvite,
      redirect,
      removeAffiliationOrInvitation,
      showRemoveButton,
      showAmalgamateShortForm,
      tempDescription,
      useNameRequest,
      showOpenButton,
      isCurrentOrganization,
      AffiliationInvitationStatus,
      AffiliationInvitationType
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';

.action-cell {
    max-width: 0;
    max-height: 30px !important;
    text-align: center;
  }

  .actions {
    height:30px;
    width: 140px;

    .open-action {
      border-right: 1px solid $gray1;
    }

    .open-action-btn {
      font-size: .875rem;
      box-shadow: none;
      border-top-right-radius: 0;
      border-bottom-right-radius: 0;
      margin-right: 1px;
      max-height: 36px !important;
      min-height: 36px !important;
    }

    .more-actions-btn {
      box-shadow: none;
      border-top-left-radius: 0;
      border-bottom-left-radius: 0;
      max-height: 36px !important;
      min-height: 36px !important;
    }

    .v-btn + .v-btn {
      margin-left: 0.5rem;
    }
  }

  .new-actions {
    height:30px;
    width: 240px;

    .open-action {
      border-right: 1px solid $gray1;
    }

    .open-action-btn {
      font-size: .875rem;
      box-shadow: none;
      border-top-right-radius: 0;
      border-bottom-right-radius: 0;
      margin-right: 1px;
      width: 170px;
    }

    .more-actions-btn {
      box-shadow: none;
      border-top-left-radius: 0;
      border-bottom-left-radius: 0;
    }

    .v-btn + .v-btn {
      margin-left: 0.5rem;
    }
  }

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

// For the dropdown text color.
::v-deep .theme--light.v-list-item .v-list-item__action-text, .theme--light.v-list-item .v-list-item__subtitle {
  color: $app-blue;
  .v-icon.v-icon {
    color: $app-blue;
  }
}

</style>
