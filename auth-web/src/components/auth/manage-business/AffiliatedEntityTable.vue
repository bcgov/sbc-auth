<template>
  <div id="affiliated-entity-section">
    <v-card flat>
      <div class="table-header">
        <v-row
          no-gutters
          class="mb-n8"
        >
          <v-col class="pt-3 pl-1">
            <label><strong>My List </strong>({{ entityCount }})</label>
          </v-col>
          <v-col class="column-actions">
            <v-select
              v-model="selectedColumns"
              dense
              multiple
              class="column-selector pb-2 pr-2"
              background-color="white"
              label="Columns to Show"
              :items="columns"
              :menu-props="{ bottom: true, offsetY: true }"
              @change="getHeaders($event)"
            >
              <template #selection />
            </v-select>
          </v-col>
        </v-row>
      </div>
      <base-v-data-table
        id="affiliated-entity-table"
        :clearFiltersTrigger="clearFiltersTrigger"
        itemKey="businessIdentifier"
        loadingText="Loading Affiliation Records..."
        noDataText="No Affiliation Records"
        :loading="affiliations.loading"
        :setHeaders="headers"
        :setItems="affiliations.results"
        :totalItems="affiliations.totalResults"
        :filters="affiliations.filters"
        :updateFilter="updateFilter"
        :height="entityCount > 5 ? '32rem' : null"
        :pageHide="true"
        :fixedHeader="true"
        :highlight-index="highlightIndex"
        highlight-class="base-table__item-row-green"
      >
        <template #header-filter-slot-Actions>
          <v-btn
            v-if="affiliations.filters.isActive"
            class="clear-btn mx-auto mt-auto"
            color="primary"
            outlined
            @click="clearFilters()"
          >
            Clear Filters
            <v-icon class="ml-1 mt-1">
              mdi-close
            </v-icon>
          </v-btn>
        </template>
        <!-- Name Request Name(s) / Business Name -->
        <template #item-slot-Name="{ item }">
          <span>
            <b
              v-if="isNameRequest(item)"
              class="col-wide gray-9"
            >
              <b
                v-for="(name, i) in item.nameRequest.names"
                :key="`nrName: ${i}`"
                class="pb-1 names-block"
              >
                <v-icon
                  v-if="isRejectedName(name)"
                  color="red"
                  class="names-text pr-1"
                  small
                >mdi-close</v-icon>
                <v-icon
                  v-if="isApprovedName(name)"
                  color="green"
                  class="names-text pr-1"
                  small
                >mdi-check</v-icon>
                <div class="names-text font-weight-bold">{{ name.name }}</div>
              </b>
            </b>
            <b
              v-else
              class="col-wide gray-9 font-weight-bold"
            >{{ name(item) }}</b>
          </span>

          <span
            v-if="!!item.affiliationInvites"
            id="affiliationInvitesStatus"
          >
            <p style="font-size: 12px">
              <v-icon
                x-small
                color="primary"
              >mdi-account-cog</v-icon>
              <span v-html="getRequestForAuthorizationStatusText(item.affiliationInvites)" />
            </p>
          </span>
        </template>

        <!-- Number -->
        <template #item-slot-Number="{ item }">
          <span>{{ number(item) }}</span>
        </template>

        <!-- Type -->
        <template #item-slot-Type="{ item }">
          <div class="gray-9 font-weight-bold d-inline-block">
            {{ type(item) }}
          </div>
          <!-- Need to keep the NR type separate or else the table filter treats each distinctly. See PR 2389 -->
          <div
            v-if="enableNameRequestType && isNameRequest(item)"
            class="gray-9 font-weight-bold d-inline-block ml-1"
          >
            {{ nameRequestType(item) }}
          </div>
          <div>{{ typeDescription(item) }}</div>
        </template>

        <!-- Status -->
        <template #item-slot-Status="{ item }">
          <span>{{ status(item) }}</span>
          <EntityDetails
            v-if="isExpired(item) ||
              isFrozed(item) ||
              isBadstanding(item) ||
              isDissolution(item) "
            icon="mdi-alert"
            :showAlertHeader="true"
            :details="getDetails(item)"
          />
          <EntityDetails
            v-if="isProcessing(status(item))"
            icon="mdi-information-outline"
            :details="[EntityAlertTypes.PROCESSING]"
          />
        </template>

        <!-- Actions -->
        <template #item-slot-Actions="{ item, index }">
          <div
            :id="`action-menu-${index}`"
            class="new-actions mx-auto"
          >
            <!--  tech debt ticket to improve this piece of code. https://github.com/bcgov/entity/issues/17132 -->
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
                  v-model="dropdown[index]"
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
                      <v-icon>{{ dropdown[index] ? 'mdi-menu-up' : 'mdi-menu-down' }}</v-icon>
                    </v-btn>
                  </template>
                  <v-list>
                    <template v-if="!!item.affiliationInvites && isCurrentOrganization(item.affiliationInvites[0].fromOrg.id)">
                      <v-list-item
                        v-if="item.affiliationInvites[0].status === 'ACCEPTED'"
                        v-can:REMOVE_BUSINESS.disable
                        class="actions-dropdown_item my-1"
                        data-test="remove-button"
                        @click="removeBusiness(item)"
                      >
                        <v-list-item-subtitle v-if="isTemporaryBusiness(item)">
                          <v-icon small>mdi-delete-forever</v-icon>
                          <span class="pl-1">Delete {{ tempDescription(item) }}</span>
                        </v-list-item-subtitle>
                        <v-list-item-subtitle v-else>
                          <v-icon small>mdi-delete</v-icon>
                          <span class="pl-1">Remove From Table</span>
                        </v-list-item-subtitle>
                      </v-list-item>
                      <v-list-item
                        v-else
                        class="actions-dropdown_item my-1"
                        @click="openNewAffiliationInvite(item)"
                      >
                        <v-list-item-subtitle>
                          <v-icon small>mdi-file-certificate-outline</v-icon>
                          <span class="pl-1">New Request</span>
                        </v-list-item-subtitle>
                      </v-list-item>
                    </template>
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
                      class="actions-dropdown_item my-1"
                      data-test="remove-button"
                      @click="removeBusiness(item)"
                    >
                      <v-list-item-subtitle v-if="isTemporaryBusiness(item)">
                        <v-icon small>mdi-delete-forever</v-icon>
                        <span class="pl-1">Delete {{ tempDescription(item) }}</span>
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
      </base-v-data-table>
    </v-card>
  </div>
</template>

<script lang='ts'>
import { AffiliationInvitationStatus, AffiliationInviteInfo } from '@/models/affiliation'
import {
  AffiliationTypes,
  CorpTypes,
  EntityAlertTypes,
  FilingTypes,
  LDFlags,
  NrDisplayStates,
  NrState,
  NrTargetTypes,
  SessionStorageKeys
} from '@/util/constants'
import { Business, NameRequest, Names } from '@/models/business'
import { Organization, RemoveBusinessPayload } from '@/models/Organization'
import { SetupContext, computed, defineComponent, ref } from '@vue/composition-api'
import { BaseVDataTable } from '@/components'
import ConfigHelper from '@/util/config-helper'
import DateMixin from '@/components/auth/mixins/DateMixin.vue'
import EntityDetails from './EntityDetails.vue'
import { NrRequestActionCodes } from '@bcrs-shared-components/enums'
import OrgService from '@/services/org.services'
import { appendAccountId } from 'sbc-common-components/src/util/common-util'
import launchdarklyServices from 'sbc-common-components/src/services/launchdarkly.services'
import { useAffiliations } from '@/composables'
import { useStore } from 'vuex-composition-helpers'

export default defineComponent({
  name: 'AffiliatedEntityTable',
  components: { EntityDetails, BaseVDataTable },
  mixins: [DateMixin],
  props: {
    loading: { default: false },
    highlightIndex: { default: -1 }
  },
  emits: ['add-unknown-error', 'remove-affiliation-invitation'],
  setup (props, context: SetupContext) {
    const isloading = false
    const store = useStore()
    const { loadAffiliations, affiliations, entityCount, clearAllFilters,
      getHeaders, headers, type, status, updateFilter, typeDescription,
      isNameRequest, nameRequestType, number, name, canUseNameRequest, tempDescription,
      isTemporaryBusiness, getEntityType } = useAffiliations()

    const currentOrganization = computed(() => store.state.org.currentOrganization as Organization)

    const selectedColumns = ['Number', 'Type', 'Status']
    const columns = ['Number', 'Type', 'Status']

    const createNamedBusiness = ({ filingType, business }: { filingType: FilingTypes, business: Business}) => {
      return store.dispatch('business/createNamedBusiness', { filingType, business })
    }

    /** V-model for dropdown menus. */
    const dropdown: Array<boolean> = []

    /** Returns true if the name is rejected. */
    const isRejectedName = (name: Names): boolean => {
      return (name.state === NrState.REJECTED)
    }

    /** Returns true if the name is approved. */
    const isApprovedName = (name: Names): boolean => {
      return (name.state === NrState.APPROVED)
    }

    const isDraft = (state: string): boolean => {
      return NrState.DRAFT === state.toUpperCase()
    }

    const isIA = (type: string): boolean => {
      return (type === AffiliationTypes.INCORPORATION_APPLICATION || type === AffiliationTypes.REGISTRATION)
    }

    const isProcessing = (state: string): boolean => {
      return NrDisplayStates.PROCESSING === state
    }

    /** Draft IA with Expired NR */
    const isExpired = (item: Business): boolean => {
      return isDraft(status(item)) && (item.nameRequest && (item.nameRequest.expirationDate !== null) &&
        (new Date(item.nameRequest.expirationDate) < new Date())) && isIA(type(item))
    }

    const isFrozed = (item: Business): boolean => {
      return item.adminFreeze
    }
    const isBadstanding = (item: Business) => {
      return !item.goodStanding
    }

    /** Returns true if the business is dissolved. */
    const isDissolution = (item: Business) => {
      return item.dissolved
    }

    const getDetails = (item: Business): EntityAlertTypes[] => {
      const details = []
      if (isExpired(item)) {
        details.push(EntityAlertTypes.EXPIRED)
      }
      if (isFrozed(item)) {
        details.push(EntityAlertTypes.FROZEN)
      }
      if (isBadstanding(item)) {
        details.push(EntityAlertTypes.BADSTANDING)
      }
      if (isDissolution(item)) {
        details.push(EntityAlertTypes.DISSOLUTION)
      }
      return details
    }

    /** Create a business record in LEAR. */
    const createBusinessRecord = async (business: Business): Promise<string> => {
      const regTypes = [CorpTypes.SOLE_PROP, CorpTypes.PARTNERSHIP]
      const iaTypes = [CorpTypes.BENEFIT_COMPANY, CorpTypes.COOP, CorpTypes.BC_CCC, CorpTypes.BC_COMPANY,
        CorpTypes.BC_ULC_COMPANY]

      let filingResponse = null
      if (regTypes.includes(business.nameRequest?.legalType)) {
        filingResponse = await createNamedBusiness({ filingType: FilingTypes.REGISTRATION, business })
      } else if (iaTypes.includes(business.nameRequest?.legalType)) {
        filingResponse = await createNamedBusiness({ filingType: FilingTypes.INCORPORATION_APPLICATION, business })
      }

      if (filingResponse?.errorMsg) {
        context.emit('add-unknown-error')
        return ''
      }
      return filingResponse.data.filing.business.identifier
    }

    /** Navigation handler for entities dashboard. */
    const goToDashboard = (businessIdentifier: string): void => {
      ConfigHelper.addToSession(SessionStorageKeys.BusinessIdentifierKey, businessIdentifier)
      let redirectURL = `${ConfigHelper.getBusinessURL()}${businessIdentifier}`
      window.location.href = appendAccountId(decodeURIComponent(redirectURL))
    }

    /** Navigation handler for Name Request application. */
    const goToNameRequest = (nameRequest: NameRequest): void => {
      ConfigHelper.setNrCredentials(nameRequest)
      window.location.href = appendAccountId(`${ConfigHelper.getNameRequestUrl()}nr/${nameRequest.id}`)
    }

    /** Handler for open action */
    const open = (item: Business): void => {
      if ((item.corpType?.code || item.corpType) === CorpTypes.NAME_REQUEST) {
        goToNameRequest(item.nameRequest)
      } else {
        goToDashboard(item.businessIdentifier)
      }
    }

    /** Navigation handler for OneStop application */
    const goToOneStop = (): void => {
      window.location.href = appendAccountId(ConfigHelper.getOneStopUrl())
    }

    /** Navigation handler for Corporate Online application */
    const goToCorpOnline = (): void => {
      window.open(appendAccountId(ConfigHelper.getCorporateOnlineUrl()), '_blank')
    }

    /** Navigation handler for Societies Online */
    const goToSocieties = (): void => {
      window.open(appendAccountId(ConfigHelper.getSocietiesUrl()), '_blank')
    }

    /** Handler for draft IA creation and navigation */
    const useNameRequest = async (item: Business) => {
      switch (item.nameRequest.target) {
        case NrTargetTypes.LEAR:
        // Create new IA if the selected item is Name Request
          let businessIdentifier = item.businessIdentifier
          if (item.corpType.code === CorpTypes.NAME_REQUEST) {
            businessIdentifier = await createBusinessRecord(item)
          }
          goToDashboard(businessIdentifier)
          break
        case NrTargetTypes.ONESTOP:
          goToOneStop()
          break
        case NrTargetTypes.COLIN:
          goToCorpOnline()
          break
      }
    }

    /** Emit business/nr information to be unaffiliated. */
    const removeBusiness = (business: Business): RemoveBusinessPayload => {
      const payload = {
        orgIdentifier: currentOrganization.value.id,
        business
      }

      context.emit('remove-business', payload)
      return payload
    }

    // clear filters
    const clearFiltersTrigger = ref(0)
    const clearFilters = () => {
      // clear values in table
      clearFiltersTrigger.value++
      // clear affiliation state filters and trigger search
      clearAllFilters()
    }

    const isCurrentOrganization = (orgId: number) => {
      return orgId === store.state.org.currentOrganization.id
    }

    const actionHandler = (business: Business) => {
      const affiliationInviteInfo = business.affiliationInvites[0]
      const invitationStatus = affiliationInviteInfo.status
      if ([AffiliationInvitationStatus.Pending, AffiliationInvitationStatus.Failed].includes(invitationStatus)) {
        OrgService.removeAffiliationInvitation(affiliationInviteInfo.id)
          .then(() => {
            context.emit('remove-affiliation-invitation')
          })
      } else if (invitationStatus === AffiliationInvitationStatus.Accepted) {
        open(business)
      } else {
        // do nothing
      }
    }
    const actionButtonText = (business: Business) => {
      const invitationStatus = business.affiliationInvites[0].status
      if (invitationStatus === AffiliationInvitationStatus.Pending) {
        return 'Cancel<br>Request'
      } else if (invitationStatus === AffiliationInvitationStatus.Failed) {
        return 'Remove<br>from list'
      } else if (invitationStatus === AffiliationInvitationStatus.Accepted) {
        return 'Open'
      } else {
        return ''
      }
    }
    const openNewAffiliationInvite = () => {
      // todo: open modal when modal is created
      // ticket to wrap it up: https://github.com/bcgov/entity/issues/17134
      alert('not implemented')
    }

    const getRequestForAuthorizationStatusText = (affiliationInviteInfos: AffiliationInviteInfo[]) => {
      if (isCurrentOrganization(affiliationInviteInfos[0].toOrg.id)) {
        // incoming request for access
        const getAlwaysSameOrderArr = affiliationInviteInfos.slice().sort()
        const andOtherAccounts = affiliationInviteInfos.length > 1 ? ` and ${affiliationInviteInfos.length - 1} other account(s)` : ''
        return `Request for Authorization to manage from: ${getAlwaysSameOrderArr[0].fromOrg.name}${andOtherAccounts}`
      } else {
        let statusText = ''
        // outgoing request for access
        switch (affiliationInviteInfos[0].status) {
          case AffiliationInvitationStatus.Pending:
            statusText = 'Request sent, pending authorization'
            break
          case AffiliationInvitationStatus.Accepted:
            statusText = '<strong>Authorized</strong> - you can now manage this business.'
            break
          case AffiliationInvitationStatus.Failed:
            statusText = '<strong>Not Authorized</strong>. Your request to manage this business has been declined.'
            break
          case AffiliationInvitationStatus.Expired:
          default:
            statusText = ''
        }
        return `Authorization to manage: ${statusText}`
      }
    }

    const isModernizedEntity = (item: Business): boolean => {
      const entityType = getEntityType(item)
      const supportedEntityFlags = launchdarklyServices.getFlag(LDFlags.IaSupportedEntities)?.split(' ') || []
      return supportedEntityFlags.includes(entityType)
    }

    const isSocieties = (item: Business): boolean => {
      const entityType = getEntityType(item)
      return (entityType === CorpTypes.CONT_IN_SOCIETY ||
        entityType === CorpTypes.SOCIETY ||
        entityType === CorpTypes.XPRO_SOCIETY)
    }

    const isOtherEntities = (item: Business): boolean => {
      const entityType = getEntityType(item)
      return (entityType === CorpTypes.FINANCIAL ||
        entityType === CorpTypes.PRIVATE_ACT ||
        entityType === CorpTypes.PARISHES)
    }

    const isSupportedRestorationEntities = (item: Business): boolean => {
      const entityType = getEntityType(item)
      const supportedEntityFlags = launchdarklyServices.getFlag(LDFlags.SupportRestorationEntities)?.split(' ') || []
      return supportedEntityFlags.includes(entityType)
    }

    const isForRestore = (item: Business): boolean => {
      const entityType = getEntityType(item)
      return (entityType === CorpTypes.BC_COMPANY ||
        entityType === CorpTypes.BC_CCC ||
        entityType === CorpTypes.BC_ULC_COMPANY ||
        entityType === CorpTypes.COOP ||
        entityType === CorpTypes.BENEFIT_COMPANY)
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
        case NrRequestActionCodes.NEW_BUSINESS: {
          if (isOtherEntities(item)) {
            return 'Download Form'
          }
          return 'Register Now'
        }
        case NrRequestActionCodes.RESTORE: {
          return isForRestore(item) ? 'Restore Now' : 'Reinstate Now'
        }
        case NrRequestActionCodes.RENEW:
          return 'Restore Now'
        default:
          return 'Open Name Request'
      }
    }

    const getPrimaryAction = (item: Business): string => {
      if (isTemporaryBusiness(item)) {
        return 'Resume Draft'
      } else if (isNameRequest(item)) {
        const nrStatus = status(item)
        switch (nrStatus) {
          case NrDisplayStates.APPROVED: {
            return getNrRequestDescription(item)
          }
          case NrDisplayStates.REJECTED:
          case NrDisplayStates.CONSUMED:
          case NrDisplayStates.CANCELLED:
          case NrDisplayStates.REFUND_REQUESTED:
            return 'Remove From Table'
          default:
            return 'Open Name Request'
        }
      } else {
        return 'Manage Business'
      }
    }

    const isOpenExternal = (item: Business): boolean => {
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

    const isBusinessAffiliated = (businessIdentifier: string): boolean => {
      return affiliations.results.some(business => businessIdentifier === business.businessIdentifier)
    }

    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const goToAmalgamate = (item: Business): void => {
      // For now, go to COLIN with external link + icon + matching hover text
      goToCorpOnline()
    }

    // Continue In
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const goToRelocate = (item: Business): void => {
      goToCorpOnline()
    }

    const goToFormPage = (): void => {
      window.open(ConfigHelper.getCorpFormsUrl(), '_blank')
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

    const redirect = (item: Business): void => {
      if (isTemporaryBusiness(item)) {
        goToDashboard(item.businessIdentifier)
      } else if (isNameRequest(item)) {
        if (status(item) === NrDisplayStates.APPROVED) {
          const nrRequestActionCd = item.nameRequest?.requestActionCd
          switch (nrRequestActionCd) {
            case NrRequestActionCodes.AMALGAMATE:
              goToAmalgamate(item)
              break
            case NrRequestActionCodes.MOVE:
              goToRelocate(item)
              break
            case NrRequestActionCodes.CONVERSION:
            case NrRequestActionCodes.CHANGE_NAME: {
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
              break
            }
            case NrRequestActionCodes.RESTORE:
            case NrRequestActionCodes.RENEW: {
              if (!isSupportedRestorationEntities(item)) {
                goToCorpOnline()
              } else {
                if (isBusinessAffiliated(item.nameRequest?.corpNum)) {
                  goToDashboard(item.nameRequest?.corpNum)
                } else {
                  const action = isForRestore(item) ? 'restore' : 'reinstate'
                  context.emit('business-unavailable-error', action)
                }
              }
              break
            }
            case NrRequestActionCodes.NEW_BUSINESS: {
              goToRegister(item)
              break
            }
            default:
              goToNameRequest(item.nameRequest)
              break
          }
        } else {
          goToNameRequest(item.nameRequest)
        }
      } else {
        // For business
        if (isModernizedEntity(item)) {
          goToDashboard(item.businessIdentifier)
        } else if (isSocieties(item)) {
          goToSocieties()
        } else {
          goToCorpOnline()
        }
      }
    }

    const isShowRemoveAsPrimaryAction = (item: Business): boolean => {
      if (isNameRequest(item) &&
       (status(item) === NrDisplayStates.REJECTED ||
        status(item) === NrDisplayStates.CONSUMED ||
        status(item) === NrDisplayStates.CANCELLED ||
        status(item) === NrDisplayStates.REFUND_REQUESTED)) {
        return true
      }
      return false
    }

    const action = (item: Business): void => {
      if (isShowRemoveAsPrimaryAction(item)) {
        removeBusiness(item)
      } else {
        redirect(item)
      }
    }

    const showRemoveButton = (item: Business): boolean => {
      return !isShowRemoveAsPrimaryAction(item)
    }

    const showOpenButton = (item: Business): boolean => {
      if (isNameRequest(item) &&
      status(item) !== NrDisplayStates.HOLD &&
      status(item) !== NrDisplayStates.EXPIRED &&
      status(item) !== NrDisplayStates.PROCESSING) {
        return true
      }
      return false
    }

    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const showAmalgamateShortForm = (item: Business): boolean => {
      // reserve for changes in the future
      return false
    }

    const getTooltipTargetDescription = (item: Business): string => {
      if (isSocieties(item)) {
        return 'Societies Online'
      }
      return 'Corporate Online'
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

    // feature flags
    const enableNameRequestType = (): boolean => {
      return launchdarklyServices.getFlag(LDFlags.EnableNameRequestType) || false
    }

    return {
      selectedColumns,
      columns,
      actionHandler,
      actionButtonText,
      openNewAffiliationInvite,
      isCurrentOrganization,
      getRequestForAuthorizationStatusText,
      clearFiltersTrigger,
      clearFilters,
      isloading,
      headers,
      affiliations,
      entityCount,
      enableNameRequestType,
      getHeaders,
      isNameRequest,
      isRejectedName,
      isApprovedName,
      nameRequestType,
      name,
      open,
      number,
      type,
      status,
      isProcessing,
      isDraft,
      typeDescription,
      loadAffiliations,
      updateFilter,
      dropdown,
      canUseNameRequest,
      useNameRequest,
      removeBusiness,
      isTemporaryBusiness,
      tempDescription,
      EntityAlertTypes,
      isExpired,
      getDetails,
      isFrozed,
      isBadstanding,
      isDissolution,
      getPrimaryAction,
      isOpenExternal,
      action,
      showRemoveButton,
      showOpenButton,
      goToNameRequest,
      showAmalgamateShortForm,
      getTooltipTargetDescription,
      disableTooltip
    }
  }
})

</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';

#affiliated-entity-section {
  .column-selector {
    float: right;
    width: 200px;
    border-radius: 4px;
  }
  .table-header {
    display: flex;
    background-color: $app-lt-blue;
    padding: .875rem;
  }

  .table-filter {
    color: $gray7;
    font-weight: normal;
    font-size: $px-14;
  }

  .clear-btn {
    width: 130px;
  }

  .names-block {
    display: table;
  }

  .names-text {
    display: table-cell;
    vertical-align: top;
  }

  tbody {
    tr {
      vertical-align: top;

      &:hover {
        background-color: transparent !important;
      }

      td {
        height: 80px !important;
        color: $gray7;
        line-height: 1.125rem;
      }

      td:first-child {
        width: 250px;
      }

      .col-wide {
        width: 325px !important;
      }

      td:not(:first-child):not(:last-child) {
        max-width: 8rem;
      }

      .type-column {
        min-width: 12rem;
      }
    }
  }

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
}

.text-input-style-above {
  label {
    font-size: 0.875rem !important;
    color: $gray7 !important;
    padding-left: 6px;
  }
  span {
    padding-left: 6px;
    font-size: 14px;
    color: $gray7;
  }
}

#table-title {
  font-size: 1rem;
}

.column-selector {
  width: 200px;
  height: 10% !important;
  z-index: 1;
}

// Vuetify Overrides
::v-deep {
  .column-actions {
    .v-input__slot {
      height: 42px !important;
      min-height: 42px !important;
    }
    .v-input .v-label {
      transform: translateX(10px) translateY(-25px) scale(1);
      top: 30px;
      color: $gray7;
      font-size: .875rem;
    }
  }
}
::v-deep .theme--light.v-list-item:not(.v-list-item--active):not(.v-list-item--disabled) {
  &:hover {
    background-color: $app-background-blue;
  }
}

::v-deep .v-data-table--fixed-header thead th {
  position: sticky;
  padding-top: 20px;
  padding-bottom: 20px;
  color: $gray9 !important;
  font-size: 0.875rem;
  z-index: 1;
}

::v-deep .theme--light.v-list-item .v-list-item__action-text, .theme--light.v-list-item .v-list-item__subtitle {
  color: $app-blue;
  .v-icon.v-icon {
    color: $app-blue;
  }
}

::v-deep label {
  font-size: $px-14;
}

// Class binding a vuetify override.
// To handle the sticky elements overlap in the custom scrolling data table.
.header-high-layer {
  ::v-deep {
    th {
      z-index: 2 !important;
    }
  }
}

::v-deep .theme--light.v-data-table .v-data-table__empty-wrapper {
  color: $gray7;
  &:hover {
    background-color: transparent;
  }
}

// Custom Scroll bars
#affiliated-entity-table {
  ::v-deep .v-menu__content {
    margin-left: -5rem;
    margin-right: 1rem;
    text-align: left;
    position: sticky;
    max-width: none;
    z-index: 1 !important;
  }

  ::v-deep .v-data-table__wrapper::-webkit-scrollbar {
    width: .625rem;
    overflow-x: hidden
  }

  ::v-deep .v-data-table__wrapper::-webkit-scrollbar-track {
    margin-top: 60px;
    box-shadow: inset 0 0 2px rgba(0,0,0,.3);
    overflow: auto;
  }

  ::v-deep .v-data-table__wrapper::-webkit-scrollbar-thumb {
    border-radius: 10px;
    background-color: lightgray;
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
</style>
