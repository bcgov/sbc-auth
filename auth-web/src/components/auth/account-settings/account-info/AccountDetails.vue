<template>
  <div>
    <v-form ref="editAccountForm">
      <v-card elevation="0">
        <div class="account-label">
          <div class="nav-list-title font-weight-bold" data-test="title">Account Details</div>
          <div v-if="isLoading" class="loading-inner-container loading-center">
            <v-progress-circular
              size="50"
              width="5"
              color="primary"
              :indeterminate="isLoading"
            />
          </div>

          <div class="details" v-else>
            <div v-if="viewOnlyMode" class="view-only">
              <div class="with-change-icon">
                <div>
                  <span class="font-weight-bold">Account Name:</span>
                  {{ orgName }}
                </div>
                <div
                  v-can:CHANGE_ORG_NAME.disable
                  v-if="nameChangeAllowed && viewOnlyMode"
                >
                  <span
                    class="primary--text cursor-pointer"
                    @click="emitViewOnly({ component: 'account', mode: false })"
                    data-test="btn-edit"
                  >
                    <v-icon color="primary" size="20"> mdi-pencil</v-icon>
                    Change
                  </span>
                </div>
              </div>
              <div v-if="isAccountTypeBusiness">
                <span class="font-weight-bold">Branch/Division:</span>
                {{ branchName != '' ? branchName : '-' }}
              </div>

              <div v-if="isAccountTypeBusiness">
                <span class="font-weight-bold">Business Type:</span>
                {{ getBusinessTypeLabel }}
              </div>

              <div v-if="isAccountTypeBusiness">
                <span class="font-weight-bold">Business Size:</span>
                {{ getBusinessSizeLabel }}
              </div>
            </div>
            <div v-else>
              <account-business-type
                :saving="false"
                @update:org-business-type="updateOrgBusinessType"
                @valid="updateIsOrgBusinessTypeValid($event)"
                :isEditAccount="true"
              >
              </account-business-type>

              <v-card-actions class="pt-1 pr-0">
                <v-spacer></v-spacer>
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
                  @click="emitViewOnly()"
                  data-test="reset-button"
                  >Cancel</v-btn
                >
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
import { useStore } from 'vuex-composition-helpers'

export interface AccountDetailsI {
  orgName: string
  branchName: string
  isAccountTypeBusiness: boolean
  isOrgBusinessTypeValid: boolean
  isLoading: boolean
  orgBusinessType: OrgBusinessType
}

export default defineComponent({
  name: 'AccountDetails',
  components: { AccountBusinessType },
  emits: ['update:updateAndSaveAccountDetails', 'update:viewOnlyMode'],
  props: {
    accountDetails: { default: null as OrgBusinessType },
    isBusinessAccount: { default: true },
    nameChangeAllowed: { default: true },
    viewOnlyMode: { default: true }
  },
  setup (props, { emit }) {
    // refs
    const editAccountForm = ref(null as HTMLFormElement)
    // store stuff
    const store = useStore()
    const businessSizeCodes = computed(() => store.state.codes.businessSizeCodes as Code[])
    const businessTypeCodes = computed(() => store.state.codes.businessTypeCodes as Code[])
    const getBusinessSizeCodes = (): Promise<Code[]> => store.dispatch('codes/getBusinessSizeCodes')
    const getBusinessTypeCodes = (): Promise<Code[]> => store.dispatch('codes/getBusinessTypeCodes')

    const localVars = (reactive({
      orgName: '',
      branchName: '',
      isAccountTypeBusiness: false,
      isOrgBusinessTypeValid: false,
      isLoading: false,
      orgBusinessType: { businessType: '', businessSize: '' }
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
      // to show businsss type value need to get all code
      await getBusinessTypeCodes()
      await getBusinessSizeCodes()
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
