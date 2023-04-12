<template>
  <v-container class="view-container pt-0">
    <!-- Loading status -->
    <v-fade-transition>
      <div class="loading-container" v-if="isLoading">
        <v-progress-circular size="50" width="5" color="primary" :indeterminate="isLoading"/>
      </div>
    </v-fade-transition>

    <div v-if="!isLoading">
      <!-- Breadcrumbs / Back Navigation -->
      <nav class="crumbs py-6">
        <div>
            <router-link :to="task.relationshipStatus === TaskRelationshipStatusEnum.REJECTED ? pagesEnum.STAFF_DASHBOARD_REJECTED: pagesEnum.STAFF_DASHBOARD_REVIEW">
              <v-icon small color="primary" class="mr-1">mdi-arrow-left</v-icon>
              <span>Back to Staff Dashboard</span>
            </router-link>
        </div>
      </nav>
      <div class="view-header flex-column">
        <h1 class="view-header__title">{{title}}</h1>
        <p class="mt-2 mb-0">Review and verify details for this account.</p>
      </div>
      <v-card class="mt-8" flat>
        <v-row class="mr-0 ml-0">

          <!-- Components list will come here -->
          <v-col class="main-col col-12 col-md-8 pa-6 pa-md-8">
            <template v-for="(component, idx) in componentList">
              <component
                :key="component.id"
                :is="component.component"
                v-bind="component.props"
                v-on="component.events"
                :ref="component.ref"
              />

              <v-divider class="mt-11 mb-8" :key="`divider-${component.id}`"  v-if="idx !== componentList.length-1"></v-divider>
            </template>

            <template v-if="canSelect">
              <v-divider class="mt-11 mb-8" ></v-divider>
              <div class="form-btns d-flex justify-end" >

                <div v-display-mode="!canEdit ? viewOnly : false ">
                  <v-btn large color="primary" class="font-weight-bold mr-2 select-button" @click="openModal()" >
                    <span v-if="isTaskRejected">Re-Approve</span>
                    <span v-else>Approve</span>
                  </v-btn>
                  <v-btn v-if="!isTaskRejected" large outlined color="primary" class="font-weight-bold white--text select-button" @click="openModal(true)"  >
                    <span v-if="isAffidavitReview && !isTaskOnHold">Reject/On Hold</span>
                    <span v-else>Reject</span>
                  </v-btn>
                  <v-btn v-else large outlined color="primary" class="font-weight-bold white--text select-button" @click="openModal(false, false, false, true)"  >
                    <span>Move to pending</span>
                  </v-btn>
                </div>
              </div>
            </template>
          </v-col>

          <!-- Account Status Column -->
          <v-col class="col-12 col-md-4 pl-0 pt-8 pr-8 d-flex">
            <v-divider vertical class="mb-0 mr-8"></v-divider>
            <div class="flex-grow-1">
            <AccountStatusTab
              :taskDetails="task"
              :isPendingReviewPage="isPendingReviewPage"
            />
            </div>
          </v-col>
        </v-row>
        <!-- approve / reject confirmation modals -->
        <AccessRequestModal
          ref="accessRequest"
          :isConfirmationModal="isConfirmationModal"
          :isRejectModal="isRejectModal"
          :isTaskRejected="isTaskRejected"
          :isOnHoldModal="isOnHoldModal"
          :isMoveToPendingModal="isMoveToPendingModal"
          :isSaving="isSaving"
          :orgName="accountUnderReview.name"
          @approve-reject-action="saveSelection"
          @after-confirm-action="goBack()"
          :accountType="taskRelationshipType"
          :taskName="task.type"
          :onholdReasonCodes="onholdReasonCodes"
          />

      </v-card>
    </div>
  </v-container>
</template>

<script lang="ts">
import { AccessType, AffidavitStatus, DisplayModeValues, OnholdOrRejectCode, Pages, TaskAction, TaskRelationshipStatus, TaskRelationshipType, TaskStatus, TaskType } from '@/util/constants'
import { AccountFee, GLInfo, OrgProduct, OrgProductFeeCode } from '@/models/Organization'
import { Ref, computed, defineComponent, getCurrentInstance, onMounted, ref } from '@vue/composition-api'
// import { mapActions, mapGetters, mapState } from 'vuex'
import AccessRequestModal from '@/components/auth/staff/review-task/AccessRequestModal.vue'
import AccountAdministrator from '@/components/auth/staff/review-task/AccountAdministrator.vue'
import { AccountInformation } from '@/components/auth/staff/review-task'
import AccountStatusTab from '@/components/auth/staff/review-task/AccountStatus.vue'
import { Address } from '@/models/address'
import { AffidavitInformation } from '@/models/affidavit'
import AgreementInformation from '@/components/auth/staff/review-task/AgreementInformation.vue'
import { Code } from '@/models/Code'
import Component from 'vue-class-component'
import { Contact } from '@/models/contact'
import DocumentService from '@/services/document.services'
import DownloadAffidavit from '@/components/auth/staff/review-task/DownloadAffidavit.vue'
import NotaryInformation from '@/components/auth/staff/review-task/NotaryInformation.vue'
import PaymentInformation from '@/components/auth/staff/review-task/PaymentInformation.vue'
import ProductFee from '@/components/auth/staff/review-task/ProductFee.vue'
import { Prop } from 'vue-property-decorator'
import StaffModuleStore from '@/store/modules/staff'
import { Task } from '@/models/Task'
import { User } from '@/models/user'

import { getModule } from 'vuex-module-decorators'
import { useStore } from 'vuex-composition-helpers'

export default defineComponent({
  name: 'ReviewAccountView',
  props: {
    orgId: String
  },
  components: {
    AccessRequestModal,
    AccountStatusTab
  },
  setup (props) {
    const store = useStore()
    const instance = getCurrentInstance()
    const _staffStore = getModule(StaffModuleStore, store)
    const isLoading: Ref<boolean> = ref(true)
    const isSaving: Ref<boolean> = ref(false)
    const pagesEnum = Pages
    const TaskRelationshipStatusEnum = TaskRelationshipStatus
    const isConfirmationModal: Ref<boolean> = ref(false)
    const isRejectModal: Ref<boolean> = ref(false)
    const isOnHoldModal: Ref<boolean> = ref(false)
    const isMoveToPendingModal: Ref<boolean> = ref(false)
    const task: Ref<Task> = ref(null)
    const taskRelationshipType: Ref<string> = ref('')
    const productFeeFormValid: Ref<boolean> = ref(false)
    const viewOnly = DisplayModeValues.VIEW_ONLY
    const accountInfoAccessType = ref(null)
    const accountInfoValid: Ref<boolean> = ref(true)
    const showAccountInfoValidations: Ref<boolean> = ref(false)

    const accessRequest: Ref<typeof AccessRequestModal> = ref(null)
    const productFeeRef: Ref<HTMLFormElement> = ref(null)

    const getTaskById = async (orgId: number): Promise<Task> => {
      return store.dispatch('task/getTaskById', orgId)
    }

    const accountUnderReview = computed(() => {
      return store.state.staff.accountUnderReview
    })

    const accountUnderReviewAdmin = computed(() => {
      return store.state.staff.accountUnderReviewAdmin
    })

    const accountUnderReviewAddress = computed(() => {
      return store.state.staff.accountUnderReviewAddress
    })

    const accountUnderReviewAdminContact = computed(() => {
      return store.state.staff.accountUnderReviewAdminContact
    })

    const accountUnderReviewAffidavitInfo = computed(() => {
      return store.state.staff.accountUnderReviewAffidavitInfo
    })

    const accountNotaryName = computed(() => {
      return store.getters['staff/accountNotaryName']
    })

    const syncTaskUnderReview = async (task: Task): Promise<void> => {
      return store.dispatch('staff/syncTaskUnderReview', task)
    }

    const approveAccountUnderReview = async (task: Task): Promise<void> => {
      return store.dispatch('staff/approveAccountUnderReview', task)
    }

    const rejectorOnHoldAccountUnderReview = async (task: any): Promise<void> => {
      return store.dispatch('staff/rejectorOnHoldAccountUnderReview', task)
    }

    const fetchCurrentOrganizationGLInfo = async (accountId: number): Promise<any> => {
      return store.dispatch('org/fetchCurrentOrganizationGLInfo', accountId)
    }

    const currentOrgGLInfo = computed(() => {
      return store.state.org.currentOrgGLInfo
    })

    const fetchOrgProductFeeCodes = async (): Promise<OrgProductFeeCode> => {
      return store.dispatch('org/fetchOrgProductFeeCodes')
    }

    const getOrgProducts = async (accountId: number): Promise<OrgProduct[]> => {
      return store.dispatch('org/getOrgProducts', accountId)
    }

    const createAccountFees = async (accoundId: number): Promise<any> => {
      return store.dispatch('org/createAccountFees', accoundId)
    }

    const syncCurrentAccountFees = async (accoundId: number): Promise<AccountFee[]> => {
      return store.dispatch('org/syncCurrentAccountFees', accoundId)
    }

    const resetCurrentAccountFees = (): void => {
      store.commit('org/resetCurrentAccountFees')
    }

    const updateOrganizationAccessType = async ({ accessType, orgId, syncOrg }): Promise<boolean> => {
      return store.dispatch('org/updateOrganizationAccessType', { accessType, orgId, syncOrg })
    }

    const getOnholdReasonCodes = async (): Promise<Code[]> => {
      return store.dispatch('codes/getOnholdReasonCodes')
    }

    const onholdReasonCodes = computed(() => {
      return store.state.codes.onholdReasonCodes
    })

    const isTaskOnHold = computed(() => {
      return task.value.status === TaskStatus.HOLD
    })

    const isTaskRejected = computed(() => {
      return task.value.relationshipStatus === TaskRelationshipStatus.REJECTED
    })

    const canSelect = computed(() => {
      return (task.value.relationshipStatus === TaskRelationshipStatus.PENDING_STAFF_REVIEW ||
        (task.value.relationshipType === TaskRelationshipType.PRODUCT &&
        task.value.relationshipStatus === TaskRelationshipStatus.REJECTED))
    })

    const isPendingReviewPage = computed(() => {
      return task.value.relationshipStatus === TaskRelationshipStatus.PENDING_STAFF_REVIEW
    })

    const isAffidavitReview = computed(() => {
      return task.value.action === TaskAction.AFFIDAVIT_REVIEW
    })

    const isGovNAccountReview = computed(() => {
      return task.value.type === TaskType.GOVN_REVIEW
    })

    const title = computed(() => {
      let title = 'Review Account'
      if (taskRelationshipType.value === TaskRelationshipType.PRODUCT) {
        title = `Access Request (${task.value.type})`
      } else if (taskRelationshipType.value === TaskRelationshipType.USER) {
        // For now, Task with relationship type as user is for BCeID Admin request
        title = 'Review BCeID Admin'
      }
      return title
    })

    const accountNotaryContact = (): Contact => {
      return accountUnderReviewAffidavitInfo.value?.contacts?.length > 0 && accountUnderReviewAffidavitInfo.value?.contacts[0]
    }

    const productFeeChange = (isFormValid): void => {
      productFeeFormValid.value = isFormValid
    }

    const canEdit = () => {
      return task.value.status === TaskStatus.OPEN || isTaskOnHold.value ||
        (task.value.status === TaskStatus.COMPLETED && task.value.relationshipStatus === TaskRelationshipStatus.REJECTED)
    }

    const formattedComponent = (tabNumber, id, component, props, event = null, ref = null) => {
      return {
        id: id,
        component: component,
        props: {
          tabNumber: tabNumber,
          ...props
        },
        events: { ...event },
        ref: ref
      }
    }

    const downloadAffidavit = async (): Promise<void> => {
      // Invoke document service to get affidavit for current organization
      await DocumentService.getSignedAffidavit(
        accountUnderReviewAffidavitInfo.value?.documentUrl,
        `${accountUnderReview.value?.name}-affidavit`
      )
    }

    const compDownloadAffidavit = (tabNumber = 1) => {
      let subTitle = 'Download the notarized affidavit associated with this account to verify the account creators identity and associated information.'
      if (accountUnderReviewAffidavitInfo.value?.status === AffidavitStatus.APPROVED) {
        subTitle = 'Download the notarized affidavit associated with this account that has been reviewed and approved.'
      }
      return formattedComponent(
        tabNumber,
        `download-affidavit-${tabNumber}`,
        DownloadAffidavit,
        {
          title: 'Download Affidavit',
          subTitle: subTitle,
          affidavitName: accountUnderReview.value?.name
        },
        { 'emit-download-affidavit': downloadAffidavit }
      )
    }

    const componentAccountInformation = (tabNumber = 1) => {
      return formattedComponent(
        tabNumber,
        `account-info-${tabNumber}`,
        AccountInformation,
        {
          title: 'Account Information',
          accountUnderReview: accountUnderReview.value,
          accountUnderReviewAddress: accountUnderReviewAddress.value,
          isGovnReview: isGovNAccountReview.value,
          showValidations: showAccountInfoValidations.value
        },
        {
          'emit-access-type': (event) => { accountInfoAccessType.value = event },
          'emit-valid': (event) => { accountInfoValid.value = event }
        }
      )
    }

    const componentAccountAdministrator = (tabNumber:number = 1) => {
      return formattedComponent(
        tabNumber,
        `account-administration-${tabNumber}`,
        AccountAdministrator,
        {
          title: 'Account Administrator',
          accountUnderReviewAdmin: accountUnderReviewAdmin.value,
          accountUnderReviewAdminContact: accountUnderReviewAdminContact.value
        }
      )
    }

    const componentNotaryInformation = (tabNumber:number = 1) => {
      return formattedComponent(tabNumber,
        `notary-info-${tabNumber}`,
        NotaryInformation,
        {
          title: 'Notary Information',
          accountNotaryContact: accountNotaryContact(),
          accountNotaryName: accountUnderReviewAffidavitInfo.value?.issuer || '-'
        }
      )
    }

    const componentAgreementInformation = (tabNumber:number = 1) => {
      return formattedComponent(tabNumber,
        `agreement-info-${tabNumber}`,
        AgreementInformation,
        {
          title: 'Agreement',
          isTOSAlreadyAccepted: true,
          orgName: accountUnderReview.value?.name,
          userName: `${accountUnderReviewAdmin.value.firstname} ${accountUnderReviewAdmin.value.lastname}`
        }
      )
    }

    const componentPaymentInformation = (tabNumber:number = 1) => {
      return formattedComponent(tabNumber,
        `payment-info-${tabNumber}`,
        PaymentInformation,
        {
          title: 'Payment Information',
          currentOrganizationGLInfo: currentOrgGLInfo.value
        }
      )
    }

    const componentProductFee = (tabNumber:number = 1) => {
      return formattedComponent(tabNumber,
        `product-fee-${tabNumber}`,
        ProductFee,
        {
          title: 'Product Fee',
          canSelect: canSelect.value
        },
        { 'emit-product-fee-change': productFeeChange },
        'productFeeRef'
      )
    }

    /*
      5 types of Tasks:
      1. New BCeId Account creation -> TaskType.NEW_ACCOUNT_STAFF_REVIEW and TaskRelationshipType.ORG and AFFIDAVIT_REVIEW action
      2. Product request access -> TaskType.PRODUCT and taskRelationshipType === TaskRelationshipType.PRODUCT and PRODUCT_REVIEW action
      3. GovM review -> TaskType.GOVM and TaskRelationshipType.ORG and ACCOUNT_REVIEW action
      4. BCeId admin review -> TaskType.BCeID Admin and TaskRelationshipType.USER and ACCOUNT_REVIEW action
      5. GovN review -> 1. Bcsc flow: TaskType.GOVN_REVIEW and TaskRelationshipType.ORG and ACCOUNT_REVIEW action
                        2. Bceid flow: TaskType.GOVN_REVIEW and TaskRelationshipType.ORG and AFFIDAVIT_REVIEW action
    */

    const componentList = computed(() => {
      const taskType = task.value?.type
      switch (taskType) {
        case TaskType.GOVM_REVIEW:
          return [
            { ...componentAccountInformation(1) },
            { ...componentAccountAdministrator(2) },
            { ...componentPaymentInformation(3) },
            { ...componentProductFee(4) }
          ]
        case TaskType.NEW_ACCOUNT_STAFF_REVIEW:
          return [
            { ...compDownloadAffidavit(1) },
            { ...componentAccountInformation(2) },
            { ...componentAccountAdministrator(3) },
            { ...componentNotaryInformation(4) }
          ]
        case TaskType.BCEID_ADMIN_REVIEW:
          return [
            { ...compDownloadAffidavit(1) },
            { ...componentAccountInformation(2) },
            { ...componentAccountAdministrator(3) },
            { ...componentNotaryInformation(4) }
          ]
        case TaskType.GOVN_REVIEW:
          let list = []
          if (task.value?.action === TaskAction.ACCOUNT_REVIEW) {
            list = [
              { ...componentAccountInformation(1) },
              { ...componentAccountAdministrator(2) },
              { ...componentProductFee(3) }
            ]
          } else {
            list = [
              { ...compDownloadAffidavit(1) },
              { ...componentAccountInformation(2) },
              { ...componentAccountAdministrator(3) },
              { ...componentNotaryInformation(4) },
              { ...componentProductFee(5) }
            ]
          }
          // if account access type was changed to regular remove the product fee comp
          if (accountInfoAccessType.value === AccessType.REGULAR) list.pop()
          return list
        default:
          // Since task of Product type has variable Task Type (eg, Wills Registry, PPR ) we specify in default.
          // Also, we double check by task relationship type
          if (taskRelationshipType.value === TaskRelationshipType.PRODUCT) {
            return [
              { ...componentAccountInformation(1) },
              { ...componentAccountAdministrator(2) },
              { ...componentAgreementInformation(3) }
            ]
          }
          break
      }
    })

    onMounted(async () => {
      try {
        task.value = await getTaskById(props.orgId)
        taskRelationshipType.value = task.value.relationshipType
        await syncTaskUnderReview(task.value)

        // If the task type is GOVM or GOVN, then need to populate product fee codes
        if (task.value.type === TaskType.GOVM_REVIEW || task.value.type === TaskType.GOVN_REVIEW) {
          const accountId = task.value.relationshipId
          await fetchCurrentOrganizationGLInfo(accountId)
          await fetchOrgProductFeeCodes()
          await getOrgProducts(accountId)
          // For rejected accounts view
          if (!canSelect.value) {
            await syncCurrentAccountFees(accountId)
          } else {
            resetCurrentAccountFees()
          }
        }

        // Tasks with Affidavit action can be put on hold. Therefore, populate on hold reasons
        if (isAffidavitReview.value && (!onholdReasonCodes.value || onholdReasonCodes.value?.length === 0)) {
          await getOnholdReasonCodes()
        }
      } catch (ex) {
        // eslint-disable-next-line no-console
        console.error(ex)
      } finally {
        isLoading.value = false
      }
    })

    const toggleAccessRequestModal = (hasConfirmationModal: boolean) => {
      if (hasConfirmationModal) {
        accessRequest.value.close()
        accessRequest.value.openConfirm()
      } else {
        accessRequest.value.open()
        accessRequest.value.closeConfirm()
      }
    }

    const openModal = (
      isRejectModalArg: boolean = false,
      isConfirmationModalArg: boolean = false,
      rejectConfirmationModalArg: boolean = false,
      isMoveToPendingModalArg: boolean = false
    ): boolean => {
      if (!accountInfoValid.value) {
        showAccountInfoValidations.value = true
        window.scrollTo({ top: 200, behavior: 'smooth' })
        return false
      }

      if (task.value.type === TaskType.GOVM_REVIEW && !productFeeFormValid.value) {
        // validate form before showing pop-up
        (productFeeRef.value[0] as any).validateNow()
        if (!productFeeFormValid.value) {
          return false
        }
      }

      isConfirmationModal.value = isConfirmationModalArg

      const isRejectModalWhileOnHold = isRejectModalArg && isTaskOnHold.value

      if (rejectConfirmationModalArg || isRejectModalWhileOnHold) {
        isRejectModal.value = true
        isOnHoldModal.value = false
      } else if (!isMoveToPendingModalArg) {
        isRejectModal.value = isAffidavitReview.value ? false : isRejectModalArg
        isOnHoldModal.value = isAffidavitReview.value ? isRejectModalArg : false
      } else {
        isMoveToPendingModal.value = true
      }

      toggleAccessRequestModal(isConfirmationModal.value)

      return true
    }

    const saveSelection = async (reason) => {
      const { isValidForm, accountToBeOnholdOrRejected, onholdReasons } = reason

      if (!isValidForm) return

      isSaving.value = true
      const isApprove = !isRejectModal.value && !isOnHoldModal.value && !isMoveToPendingModal.value
      const isRejecting = isRejectModal.value || accountToBeOnholdOrRejected === OnholdOrRejectCode.REJECTED
      const isMoveToPending = isMoveToPendingModal.value || accountToBeOnholdOrRejected === OnholdOrRejectCode.ONHOLD

      try {
        if (accountInfoAccessType.value && accountInfoAccessType.value !== accountUnderReview.value.accessType) {
          const success = await updateOrganizationAccessType({ accessType: accountInfoAccessType.value as string, orgId: accountUnderReview.value.id, syncOrg: false })
          if (!success) throw new Error('Error updating account access type prevented review completion.')
        }
        if (isApprove) {
          await approveAccountUnderReview(task.value)
        } else {
          await rejectorOnHoldAccountUnderReview({ task: task.value, isRejecting, remarks: onholdReasons })
        }
        const taskType: any = task.value.type

        if (
          [TaskType.GOVM_REVIEW, TaskType.GOVN_REVIEW].includes(taskType) &&
          (!accountInfoAccessType.value || [AccessType.GOVN, AccessType.GOVM].includes(accountInfoAccessType.value))
        ) {
          await createAccountFees(task.value.relationshipId)
        }
        openModal(!isApprove, true, isRejecting, isMoveToPending)
      } catch (error) {
        // eslint-disable-next-line no-console
        console.log(error)
      } finally {
        isSaving.value = false
      }
    }

    const goBack = () => {
      instance.proxy.$router.push(pagesEnum.STAFF_DASHBOARD)
    }

    return {
      isLoading,
      isSaving,
      pagesEnum,
      TaskRelationshipStatusEnum,
      isConfirmationModal,
      isRejectModal,
      isOnHoldModal,
      isMoveToPendingModal,
      task,
      taskRelationshipType,
      productFeeFormValid,
      viewOnly,
      accountInfoAccessType,
      accountInfoValid,
      showAccountInfoValidations,
      accessRequest,
      productFeeRef,
      getTaskById,
      accountUnderReview,
      accountUnderReviewAdmin,
      accountUnderReviewAddress,
      accountUnderReviewAdminContact,
      accountUnderReviewAffidavitInfo,
      accountNotaryName,
      syncTaskUnderReview,
      rejectorOnHoldAccountUnderReview,
      fetchCurrentOrganizationGLInfo,
      currentOrgGLInfo,
      fetchOrgProductFeeCodes,
      getOrgProducts,
      createAccountFees,
      syncCurrentAccountFees,
      resetCurrentAccountFees,
      updateOrganizationAccessType,
      getOnholdReasonCodes,
      onholdReasonCodes,
      isTaskOnHold,
      isTaskRejected,
      canSelect,
      isPendingReviewPage,
      isAffidavitReview,
      isGovNAccountReview,
      title,
      accountNotaryContact,
      productFeeChange,
      canEdit,
      formattedComponent,
      downloadAffidavit,
      compDownloadAffidavit,
      componentAccountInformation,
      componentAccountAdministrator,
      componentNotaryInformation,
      componentAgreementInformation,
      componentPaymentInformation,
      componentProductFee,
      componentList,
      openModal,
      saveSelection,
      goBack
    }
  }
})
</script>

<style lang="scss" scoped>

  .select-button {
    width: 8.75rem;
  }

  .crumbs a {
    font-size: 0.875rem;
    text-decoration: none;

    i {
      margin-top: -2px;
    }
  }

  .crumbs a:hover {
    span {
      text-decoration: underline;
    }
  }
</style>
