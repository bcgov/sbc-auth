<template>
  <div>
    <v-form ref="accountAccessTypeForm">
      <v-card elevation="0">
        <div class="account-label">
          <div
            class="nav-list-title font-weight-bold pl-3"
            data-test="title"
          >
            Access Type
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
                  <span data-test="txt-selected-access-type">{{ getAccessTypeText }}</span>
                </div>
                <div
                  v-if="isChangeButtonEnabled"
                >
                  <span
                    class="primary--text cursor-pointer"
                    data-test="btn-edit"
                    @click="
                      $emit('update:viewOnlyMode', {
                        component: 'accessType',
                        mode: false
                      })
                    "
                  >
                    <v-icon
                      color="primary"
                      size="20"
                    > mdi-pencil</v-icon>
                    Change
                  </span>
                </div>
              </div>
            </div>
            <div v-else>
              <v-radio-group
                v-model="selectedAccessType"
                class="mt-0"
                req
                :rules="[selectedAccessTypeRules]"
              >
                <v-radio
                  :key="AccessType.REGULAR"
                  label="Regular Access"
                  :value="AccessType.REGULAR"
                  data-test="radio-regular-access"
                />
                <v-radio
                  :key="AccessType.GOVN"
                  label="Government agency (other than BC provincial)"
                  :value="AccessType.GOVN"
                  data-test="radio-govn"
                />
              </v-radio-group>
              <div
                v-if="!isPad"
                class="d-flex pb-3"
              >
                <v-icon
                  size="30"
                  color="error"
                  class="mt-1 mr-4"
                >
                  mdi-alert-circle-outline
                </v-icon>
                <span class="error-text">{{ $t('accountAccessTypeUpdateWarning') }}</span>
              </div>

              <v-card-actions class="px-0 pt-0">
                <v-row>
                  <v-col
                    cols="12"
                    class="form__btns py-0 d-inline-flex"
                  >
                    <v-spacer />
                    <v-btn
                      large
                      class="save-btn px-9"
                      color="primary"
                      :loading="false"
                      aria-label="Save Account Access Type"
                      @click="updateDetails()"
                    >
                      <span class="save-btn__label">Save</span>
                    </v-btn>
                    <v-btn
                      outlined
                      large
                      depressed
                      class="ml-2 px-9"
                      color="primary"
                      aria-label="Cancel Account Access Type"
                      data-test="reset-button"
                      @click="cancelEdit()"
                    >
                      Cancel
                    </v-btn>
                  </v-col>
                </v-row>
              </v-card-actions>
            </div>
          </div>
        </div>
      </v-card>
    </v-form>
  </div>
</template>

<script lang="ts">
import { AccessType, Account, PaymentTypes } from '@/util/constants'
import { Component, Emit, Prop, Vue, Watch } from 'vue-property-decorator'
import { Organization } from '@/models/Organization'

@Component({
})
export default class AccountAccessType extends Vue {
  @Prop({ default: undefined }) organization: Organization
  @Prop({ default: true }) viewOnlyMode: boolean
  @Prop({ default: false }) canChangeAccessType: boolean
  @Prop({ default: undefined }) currentOrgPaymentType: string

  $refs: {
    accountAccessTypeForm: HTMLFormElement,
    selectedAccessType: HTMLFormElement
  }
  private selectedAccessType: string = undefined
  public AccessType = AccessType
  public isLoading = false

  public get isPad (): boolean {
    return this.currentOrgPaymentType && this.currentOrgPaymentType === PaymentTypes.PAD
  }

  public get isChangeButtonEnabled (): boolean {
    // Check access type and orgtype must be premium
    const accessType: any = this.organization.accessType
    const isAllowedAccessType = this.organization.orgType === Account.PREMIUM && [AccessType.REGULAR, AccessType.EXTRA_PROVINCIAL, AccessType.REGULAR_BCEID].includes(accessType)
    return isAllowedAccessType && this.canChangeAccessType // canChangeAccessType is the role based access pasased as property
  }

  public get getAccessTypeText (): string {
    let accessTypeText = 'Regular Access'
    if (this.organization.accessType === AccessType.GOVN) {
      accessTypeText = 'Government agency (other than BC provincial)'
    } else if (this.organization.accessType === AccessType.GOVM) {
      accessTypeText = 'BC Government Ministry'
    }
    return accessTypeText
  }

  // Watch property access type and update model
  @Watch('organization', { deep: true, immediate: true })
  onOrganizationChange () {
    this.selectedAccessType = this.organization.accessType === AccessType.GOVN ? AccessType.GOVN : AccessType.REGULAR
  }

  // Custom rules for selectedAccessType v-model in form
  public selectedAccessTypeRules (): any {
    return this.selectedAccessType === AccessType.GOVN ? true : 'Please select Government agency'
  }

  // Currently, there is only one way change from Regular access type accounts to GovN. Not the other way around
  public updateDetails () {
    if (this.isPad && this.$refs.accountAccessTypeForm.validate()) {
      this.$emit('update:updateAndSaveAccessTypeDetails', this.selectedAccessType)
    }
  }

  @Emit('update:viewOnlyMode')
  cancelEdit () {
    this.selectedAccessType = this.organization.accessType === AccessType.GOVN ? AccessType.GOVN : AccessType.REGULAR
    return {
      component: 'accessType',
      mode: true
    }
  }
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';
.form__btns {
  display: flex;
  justify-content: flex-end;
}
.error-text{
  color: var(--v-error-base) !important;
}

</style>
