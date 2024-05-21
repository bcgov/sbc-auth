<template>
  <div>
    <v-form ref="editAccountForm">
      <v-card elevation="0">
        <div class="account-label">
          <div
            class="nav-list-title font-weight-bold"
            data-test="title"
          >
            Account Details
          </div>
          <div
            v-if="isLoading"
            class="loading-inner-container loading-center"
          >
            <v-progress-circular
              size="50"
              width="5"
              color="primary"
              :indeterminate="isLoading"
            />
          </div>

          <div
            v-else
            class="details"
          >
            <div
              v-if="viewOnlyMode"
              class="view-only"
            >
              <div class="with-change-icon">
                <div>
                  <span class="font-weight-bold">Account Name:</span>
                  {{ orgName }}
                </div>
                <div
                  v-if="canOrgChange"
                  v-can:CHANGE_ORG_NAME.hide
                >
                  <span
                    class="primary--text cursor-pointer"
                    data-test="btn-edit"
                    @click="emitViewOnly({ component: 'account', mode: false })"
                  >
                    <v-icon
                      color="primary"
                      size="20"
                    > mdi-pencil</v-icon>
                    Change
                  </span>
                </div>
              </div>
              <div v-if="isAccountTypeBusiness">
                <span class="font-weight-bold">Branch/Division:</span>
                {{ branchName != '' ? branchName : '-' }}
              </div>

              <div v-if="isAccountTypeBusiness">
                <span class="font-weight-bold">{{ accountTypeLabel }}</span>
                {{ getBusinessTypeLabel }}
              </div>

              <div v-if="isAccountTypeBusiness">
                <span class="font-weight-bold">{{ accountSizeLabel }}</span>
                {{ getBusinessSizeLabel }}
              </div>
            </div>
            <div v-else>
              <AccountBusinessType
                :saving="false"
                :isEditAccount="true"
                @update:org-business-type="updateOrgBusinessType"
                @valid="updateIsOrgBusinessTypeValid($event)"
              />

              <v-card-actions class="pt-1 pr-0">
                <v-spacer />
                <v-btn
                  large
                  class="save-btn px-9"
                  color="primary"
                  :loading="false"
                  aria-label="Save Account Information"
                  @click="emitUpdateAndSaveAccount()"
                >
                  <span class="save-btn__label">Save</span>
                </v-btn>
                <v-btn
                  outlined
                  large
                  depressed
                  class="ml-2 px-9"
                  color="primary"
                  aria-label="Cancel Account Information"
                  data-test="reset-button"
                  @click="emitViewOnly({ component: 'account', mode: true})"
                >
                  Cancel
                </v-btn>
              </v-card-actions>
            </div>
          </div>
        </div>
      </v-card>
    </v-form>
  </div>
</template>
<script lang="ts">
import { computed, defineComponent, onMounted, reactive, ref, toRefs, watch } from '@vue/composition-api'
import AccountBusinessType from '@/components/auth/common/AccountBusinessType.vue'
import { Code } from '@/models/Code'
import { OrgBusinessType } from '@/models/Organization'
import { useCodesStore } from '@/stores/codes'
import { useOrgStore } from '@/stores/org'

export interface AccountDetailsI {
  orgName: string
  branchName: string
  isAccountTypeBusiness: boolean
  isOrgBusinessTypeValid: boolean
  isLoading: boolean
  orgBusinessType: OrgBusinessType
  isGovnOrg: boolean
  accountTypeLabel: string
  accountSizeLabel: string
  canOrgChange: boolean
}

export default defineComponent({
  name: 'AccountDetails',
  components: { AccountBusinessType },
  props: {
    accountDetails: { default: null as OrgBusinessType },
    isBusinessAccount: { default: true },
    nameChangeAllowed: { default: true },
    viewOnlyMode: { default: true }
  },
  emits: ['update:updateAndSaveAccountDetails', 'update:viewOnlyMode'],
  setup (props, { emit }) {
    // refs
    const editAccountForm = ref(null as HTMLFormElement)
    const codeStore = useCodesStore()
    const businessSizeCodes = computed(() => codeStore.businessSizeCodes)
    const businessTypeCodes = computed(() => codeStore.businessTypeCodes)
    const orgStore = useOrgStore()

    const localVars = (reactive({
      orgName: '',
      branchName: '',
      isAccountTypeBusiness: false,
      isOrgBusinessTypeValid: false,
      isLoading: false,
      orgBusinessType: { businessType: '', businessSize: '' },
      isGovnOrg: orgStore.isGovnOrg,
      accountTypeLabel: '',
      accountSizeLabel: '',
      canOrgChange: false
    }) as unknown) as AccountDetailsI
    watch(() => props.isBusinessAccount, (val: boolean) => { localVars.isAccountTypeBusiness = val })

    const updateIsOrgBusinessTypeValid = (isValid: boolean) => {
      localVars.isOrgBusinessTypeValid = !!isValid
    }
    const updateOrgBusinessType = (orgBusinessType: OrgBusinessType) => {
      localVars.orgBusinessType = orgBusinessType
    }

    const updateAccountDetails = () => {
      localVars.orgName = props.accountDetails?.name
      localVars.branchName = props.accountDetails?.branchName
      localVars.orgBusinessType.businessType = props.accountDetails?.businessType
      localVars.orgBusinessType.businessSize = props.accountDetails?.businessSize
      localVars.isAccountTypeBusiness = props.isBusinessAccount
      localVars.accountTypeLabel = localVars.isGovnOrg ? 'Government Agency Type:' : 'Business Type:'
      localVars.accountSizeLabel = localVars.isGovnOrg ? 'Government Agency Size:' : 'Business Size:'
      localVars.canOrgChange = props.nameChangeAllowed && props.viewOnlyMode && !localVars.isGovnOrg
    }
    watch(() => props.accountDetails, () => updateAccountDetails(), { deep: true })

    const getCodeLabel = (codeList: Code[], code: string) => {
      const codeArray = codeList.filter(type => type.code === code)
      return (codeArray && codeArray[0] && codeArray[0]?.desc) || ''
    }
    const getBusinessTypeLabel = computed(() => {
      return getCodeLabel(businessTypeCodes.value, localVars.orgBusinessType.businessType)
    })
    const getBusinessSizeLabel = computed(() => {
      return getCodeLabel(businessSizeCodes.value, localVars.orgBusinessType.businessSize)
    })

    const emitViewOnly = (val: { component: string, mode: boolean }) => {
      updateAccountDetails()
      emit('update:viewOnlyMode', val)
    }

    const emitUpdateAndSaveAccount = () => {
      if (localVars.isOrgBusinessTypeValid) {
        emit('update:updateAndSaveAccountDetails', localVars.orgBusinessType)
      }
    }

    onMounted(async () => {
      localVars.isLoading = true
      // to show business type value need to get all code
      await codeStore.fetchAllBusinessTypeCodes()
      await codeStore.getBusinessTypeCodes()
      await codeStore.getBusinessSizeCodes()
      updateAccountDetails()
      localVars.isLoading = false
    })

    return {
      editAccountForm,
      getBusinessTypeLabel,
      getBusinessSizeLabel,
      updateIsOrgBusinessTypeValid,
      updateOrgBusinessType,
      emitViewOnly,
      emitUpdateAndSaveAccount,
      ...toRefs(localVars)
    }
  }
})
</script>
<style lang="scss" scoped>
@import '$assets/scss/theme.scss';
.business-radio {
  display: flex;
  width: 90%;
  .v-radio {
    padding: 10px;
    background-color: rgba(0, 0, 0, 0.06);
    min-width: 50%;
    border: 1px rgba(0, 0, 0, 0.06) !important;
  }

  .v-radio.theme--light.v-item--active {
    border: 1px solid var(--v-primary-base) !important;
    background-color: $BCgovInputBG !important;
  }
}
</style>
